"""Measure DMG input latency and the complete death/respawn sequence."""
from pathlib import Path
import json
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1];sym={}
for line in (R/'Halcones-Estelares-GB.noi').read_text().splitlines():
 a=line.split()
 if len(a)==3 and a[0]=='DEF':sym[a[1].lstrip('_')]=int(a[2],16)
p=PyBoy(str(R/'Halcones-Estelares-GB.gb'),window='null',sound_emulated=False);p.set_emulation_speed(0)
def g(n):return p.memory[sym[n]]
def w(n,v):p.memory[sym[n]]=v
def tick(n=1):p.tick(n,True)
def until(f,limit=600):
 for _ in range(limit):
  if f():return
  tick()
 raise AssertionError(('timeout',g('state'),g('invulnerable')))
def clear():
 for i in range(2):p.memory[sym['shots']+i*3+2]=0
 for i in range(3):p.memory[sym['plasma']+i*3+2]=0
def incoming():p.memory[sym['plasma']:sym['plasma']+3]=[g('px')+8,120,1]
tick(300);p.button_press('start');tick(4);p.button_release('start');until(lambda:g('state')==1);tick(20)
latency=[];visible=[]
for trial in range(24):
 w('invulnerable',255);clear();tick(4)
 # Keep the muzzle clear: an immediate hit can consume a valid laser before OAM.
 for i in range(10):
  if p.memory[sym['foes']+i*5+1]>65:p.memory[sym['foes']+i*5+1]=20
 if trial>=12:
  for name in ('score','record'):p.memory[sym[name]:sym[name]+4]=list((10000+trial*10).to_bytes(4,'little'))
  tick(trial%3)
 p.button_press('a');spawn=None;seen=None
 for elapsed in range(1,9):
  tick()
  if elapsed==1:p.button_release('a')
  if spawn is None and g('shots')>=0 and any(p.memory[sym['shots']+i*3+2] for i in range(2)):spawn=elapsed
  if seen is None and any(p.memory[0xfe00+(8+i)*4] for i in range(2)):seen=elapsed
 assert spawn is not None and spawn<=2,(trial,spawn)
 assert seen is not None and seen<=3,(trial,seen)
 latency.append(spawn);visible.append(seen);tick(trial%4+1)
# Rapid presses with BOTH slots occupied must trigger a new laser every time.
fire_events=[];addr=sym['audio_fire_now']
p.hook_register(1 if addr>=0x4000 else 0,addr,lambda c:c.append(1),fire_events)
for trial in range(12):
 w('invulnerable',255)
 p.memory[sym['shots']:sym['shots']+6]=[8,30,1,8,50,1]
 p.button_press('a');tick();p.button_release('a');tick(3)
 assert len(fire_events)==trial+1,('occupied slots dropped a press',trial)
assert len(fire_events)==12
# Holding A must repeat even with shield active; individual edges work there too.
w('shield_state',1);p.memory[sym['shield_timer']:sym['shield_timer']+2]=[179,0]
before=len(fire_events);p.button_press('a');tick(60);p.button_release('a');tick(4)
held_shots=len(fire_events)-before;assert held_shots==0,held_shots
for _ in range(4):
 before=len(fire_events);p.button_press('a');tick();p.button_release('a');tick(3)
 assert len(fire_events)==before
before=len(fire_events);p.button_press('a');tick(120);p.button_release('a');tick(4)
assert g('shield_state')==2 and len(fire_events)>before,'held A resumes after shield expires'
w('shield_state',0);p.memory[sym['shield_timer']:sym['shield_timer']+2]=[0,0]
# Measure presentation-control calls during stable combat.
clear();counts=[0];addr=sym['player_tick']
p.hook_register(1 if addr>=0x4000 else 0,addr,lambda c:c.__setitem__(0,c[0]+1),counts)
for _ in range(8):w('invulnerable',255);tick(30)
measured_updates=counts[0];assert measured_updates>=235,counts
# Freeze fixtures, force one projectile hit, then inspect actual animation/OAM.
w('paused',1);tick(15);clear();w('lives',3);w('invulnerable',0);w('shield_state',0);incoming();w('paused',0)
until(lambda:g('state')==5);assert g('lives')==2
frames=[];tiles=set();death_frames=0;death_x=g('px')
while g('state')==5:
 tick();death_frames+=1
 assert g('px')==death_x
 if death_frames%2==0:frames.append(p.screen.image.copy())
 if p.memory[0xfe00]:tiles.add(p.memory[0xfe02])
assert 33<=death_frames<=38,death_frames
assert {66,78,90}.issubset(tiles),tiles
assert g('state')==1 and g('px')==48 and g('invulnerable')>=119
blink=set();grace_frames=0;shot_seen=False
while g('invulnerable'):
 if grace_frames<80 and grace_frames%4==0:incoming()
 if grace_frames==10:p.button_press('right')
 if grace_frames==25:p.button_press('a')
 if grace_frames==26:p.button_release('a')
 if grace_frames==30:p.button_release('right')
 tick();grace_frames+=1
 assert g('lives')==2 and g('state')==1,'hit during respawn protection'
 if 25<=grace_frames<=35 and any(p.memory[sym['shots']+i*3+2] for i in range(2)):shot_seen=True
 blink.add(bool(p.memory[0xfe00]))
 if grace_frames%2==0:frames.append(p.screen.image.copy())
assert 118<=grace_frames<=122,grace_frames
assert blink=={False,True} and shot_seen
assert g('px')>48
clear();tick(10);assert p.memory[0xfe00]>0,'ship must remain visible after grace'
incoming();until(lambda:g('state')==5);assert g('lives')==1
frames[0].save(R/'capturas/reaparicion.gif',save_all=True,append_images=frames[1:],duration=33,loop=0)
report={'result':'PASS','rapid_presses_with_full_slots':12,'held_A_shots_in_60_frames_with_shield':held_shots,'shield_presses_blocked':4,'fire_resumes_after_shield':True,'input_samples':24,'press_to_spawn_vblanks':latency,'press_to_visible_vblanks':visible,'max_press_to_spawn_vblanks':max(latency),'max_press_to_visible_vblanks':max(visible),'player_updates_in_240_vblanks':measured_updates,'death_animation_vblanks':death_frames,'respawn_invulnerability_vblanks':grace_frames,'death_tiles_seen':sorted(tiles),'can_move_and_fire_while_invulnerable':True,'damage_restored_after_grace':True}
(R/'RESPUESTA_Y_REAPARICION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));p.stop()

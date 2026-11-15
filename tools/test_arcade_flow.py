"""Actual ROM checks: varied sorties, seamless transitions, coherent OAM and songs.
Only phase/wave selection and collision setup are arranged in RAM.
"""
from pathlib import Path
import json
from collections import deque
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1];sym={}
for line in (R/'Halcones-Estelares-GB.noi').read_text().splitlines():
 a=line.split()
 if len(a)==3 and a[0]=='DEF':sym[a[1].lstrip('_')]=int(a[2],16)
p=PyBoy(str(R/'Halcones-Estelares-GB.gb'),window='null',sound_emulated=True);p.set_emulation_speed(0)
def g(n):return p.memory[sym[n]]
def w(n,v):p.memory[sym[n]]=v
def w16(n,v):p.memory[sym[n]:sym[n]+2]=list(v.to_bytes(2,'little'))
def tick(n=1):
 for _ in range(n):p.tick(1,True)
def until(f,n=1000):
 for _ in range(n):
  if f():return
  tick()
 raise AssertionError(('timeout',g('state'),g('wave')))
def foe(i):return list(p.memory[sym['foes']+i*5:sym['foes']+i*5+5])
def putfoe(i,v):p.memory[sym['foes']+i*5:sym['foes']+i*5+5]=v
def clear():
 for name,n in [('shots',2),('plasma',3)]:
  for i in range(n):p.memory[sym[name]+i*3+2]=0
def enter(wave):
 w('paused',1);tick(3);clear();w('wave',wave-1);w('state',4);w16('state_timer',0);w('paused',0)
 until(lambda:g('state')==1);w('invulnerable',255)

tick(300);p.button_press('start');tick(4);p.button_release('start');until(lambda:g('state')==1);tick(20)
frames=deque(maxlen=6);addr=sym['oam_commit'];shadow=sym['shadow_OAM']
p.hook_register(1 if addr>=0x4000 else 0,addr,lambda c:c.append(bytes(p.memory[shadow:shadow+160])),frames)
patterns={};coherent=0;gif=[]
for wave in range(1,7):
 enter(wave);pattern=g('pattern_id');seen=set();active_max=0;return_seen=False;bounds=True;staggered=False;bg=bytes(p.memory[0x9800:0x9c00]);reentries=0
 old_modes=[4]*10
 for f in range(650):
  if f%30==0:w('invulnerable',255)
  tick();rows=[foe(i) for i in range(10 if wave<3 else 6)]
  seen.update(e[3] for e in rows if e[2]);active_max=max(active_max,sum(e[2] and e[3] in (1,2,3,6) for e in rows))
  if any(e[3]==4 for e in rows) and any(e[3]==5 for e in rows):staggered=True
  for i,e in enumerate(rows):
   if old_modes[i]==3 and e[3]==0:reentries+=1
   old_modes[i]=e[3]
   if e[2]:assert 0<=e[0]<=102 and 0<=e[1]<=134,(wave,e)
  actual=bytes(p.memory[0xfe00:0xfea0])
  if frames:assert actual in frames,('partial OAM frame',wave,f);coherent+=1
  assert p.memory[0xff42]==p.memory[0xff43]==0
  assert bytes(p.memory[0x9800:0x9c00])==bg,'combat writes to static stars'
  if wave==2 and f<300 and f%4==0:gif.append(p.screen.image.copy())
 assert {0,1,3,4,5}.issubset(seen),(wave,seen)
 assert staggered and reentries>0 and active_max>=2,(wave,active_max,reentries)
 if pattern in (3,4):assert 2 in seen,'feint must occur'
 if pattern in (2,3,5):assert 6 in seen,'escorts must launch at staggered times'
 patterns[wave]={'pattern':pattern,'modes':sorted(seen),'max_active':active_max,'visible_returns':reentries,'staggered_entry':staggered}
gif[0].save(R/'capturas/crow_parejas.gif',save_all=True,append_images=gif[1:],duration=67,loop=0)
# Every family can draw all six patterns, independently of its artwork.
family_patterns={}
for family_wave in (1,3,5):
 choices=set();previous=None
 for attempt in range(120):
  enter(family_wave);chosen=g('pattern_id');assert 1<=chosen<=6
  previous=chosen;choices.add(chosen)
  if len(choices)==6:break
 assert choices==set(range(1,7)),(family_wave,choices)
 family_patterns[family_wave]=sorted(choices)
# Kill through the actual laser path; both hardware halves must disappear.
enter(3);tick(100);w('paused',1);tick(3);clear()
for i in range(10):putfoe(i,[90,20,0,0,1])
putfoe(0,[70,50,1,0,1]);putfoe(1,[90,20,1,0,1])
for i,x,y in [(0,70,50),(1,90,20)]:p.memory[sym['home_x']+i]=x;p.memory[sym['home_y']+i]=y
w('attack_cd',255);w('formation_drift',0);p.memory[sym['shots']:sym['shots']+3]=[74,56,1];w('paused',0)
until(lambda:foe(0)[2]==0);tick(3)
assert p.memory[0xfe00+13*4]==p.memory[0xfe00+14*4]==0,'dead enemy halves must be hidden'
# Clear the last enemy, while watching the complete live transition.
w('paused',1);tick(3);clear();putfoe(1,[70,50,1,0,1]);p.memory[sym['home_x']+1]=70;p.memory[sym['home_y']+1]=50
p.memory[sym['shots']:sym['shots']+3]=[74,56,1];w('paused',0);until(lambda:g('state')==4)
start_x=g('px');shield=g('shield_state');w('invulnerable',0);p.button_press('right');transition_frames=[];count=0
while g('state')==4:
 tick();count+=1
 assert p.memory[0xff40]&0x80 and p.memory[0xff40]&0x20,'LCD and HUD must remain on'
 assert p.memory[0xfe00]>0,'ship must stay visible during wave interlude'
 if count%2==0:transition_frames.append(p.screen.image.copy())
p.button_release('right');assert 55<=count<=65,count
assert g('px')>start_x and g('wave')==4
for _ in range(35):w('invulnerable',255);tick(2);transition_frames.append(p.screen.image.copy())
transition_frames[0].save(R/'capturas/transicion_suave.gif',save_all=True,append_images=transition_frames[1:],duration=[40 if i%3==0 else 30 for i in range(len(transition_frames))],loop=0)
# One continuous gameplay theme across every wave.
songs=[]
for wave in range(1,8):
 enter(wave);wanted=0
 until(lambda:g('music_song')==wanted,150);songs.append(g('music_song'));assert g('music_on')==1
assert songs==[0,0,0,0,0,0,0]
# Game Over melody plays once and finishes, with main soundtrack stopped.
enter(1);tick(80);clear();w('paused',1);tick(3);w('lives',1);w('invulnerable',0);w('shield_state',0)
p.memory[sym['plasma']:sym['plasma']+3]=[g('px')+8,120,1];p.memory[sym['plasma_dx']]=0;w('paused',0)
until(lambda:g('state')==2);notes=set()
for _ in range(160):tick();notes.add(g('over_note'))
assert g('music_on')==0 and g('over_note')==5 and g('over_clock')==0
assert {1,2,3,4,5}.issubset(notes)
report={'result':'PASS','patterns':patterns,'all_patterns_per_family':family_patterns,'coherent_oam_frames_checked':coherent,'dead_enemy_removed':True,'transition_vblanks':count,'ship_moves_through_transition':True,'songs_by_wave':songs,'game_over_notes':sorted(notes),'limitations':'PyBoy DMG, prepared wave/collision fixtures; not a physical-console test.'}
(R/'PATRONES_Y_TRANSICIONES.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));p.stop()

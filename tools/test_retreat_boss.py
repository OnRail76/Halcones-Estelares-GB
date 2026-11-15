"""Actual ROM regressions: repeated retreat, survivor preservation, sustained summons."""
from pathlib import Path
from collections import deque
import json,re
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1]
s={a[1].lstrip('_'):int(a[2],16) for l in (R/'Halcones-Estelares-GB.noi').read_text().splitlines() if len(a:=l.split())==3 and a[0]=='DEF'}
p=PyBoy(str(R/'Halcones-Estelares-GB.gb'),window='null');p.set_emulation_speed(0)
def g(n):return p.memory[s[n]]
def w(n,v):p.memory[s[n]]=v
def w16(n,v):p.memory[s[n]:s[n]+2]=list(v.to_bytes(2,'little'))
def tick(n=1):
 for _ in range(n):w('invulnerable',255);p.tick(1,True)
def until(fn,n=2500):
 for _ in range(n):
  if fn():return
  tick()
 raise AssertionError(('timeout',g('state'),g('wave')))
def f(i):return s['foes']+i*5
def foe(i):return list(p.memory[f(i):f(i)+5])
def clear():
 for name,count in [('shots',2),('plasma',3)]:
  for i in range(count):p.memory[s[name]+i*3+2]=0

def enter(wave,phase=1):
 w('paused',1);tick(3);clear();w('phase',phase);w('wave',wave-1);w('state',4);w16('state_timer',0);w('paused',0);until(lambda:g('state')==1)

tick(300);p.button_press('start');tick(4);p.button_release('start');until(lambda:g('state')==1);tick(30)
# Actual loaded font must equal the former packed alphabet, byte for byte.
old=(R.parent/'Halcones-GameBoy-0.15-respaldo/src/assets.h').read_text()
a=list(map(int,re.search(r'font_data_rle\[\] = \{([^}]+)',old)[1].split(',')));out=[];i=0
while i<len(a):
 n=a[i];i+=1;k=(n&127)+1
 if n&128:out.extend([a[i]]*k);i+=1
 else:out.extend(a[i:i+k]);i+=k
assert bytes(p.memory[0x9000:0x9000+len(out)])==bytes(out)
retreats={};gif=[]
for count in (1,4,10):
 while True:
  enter(1)
  if g('pattern_id')==7:break
 w('paused',1);tick(3)
 for i in range(10):p.memory[f(i)+2]=int(i>=10-count)
 w('paused',0);cycles=0;was=0;max_y=0;up=0
 for frame in range(1800):
  previous=[foe(i)[1] for i in range(10)];tick()
  now=g('inv_retreat');cycles+=bool(was and not now);was=now
  assert sum(foe(i)[2] for i in range(10))==count
  assert g('state')==1 and g('pattern_id')==7
  for i in range(10):
   e=foe(i)
   if e[2]:
    max_y=max(max_y,e[1]);assert e[1]<=102
    if previous[i]>e[1]:up+=1;assert previous[i]-e[1]<=3,'teleport instead of retreat'
  if count==10 and frame<960 and frame%4==0:gif.append(p.screen.image.copy())
  if frame==200:
   w('paused',1);tick(3);before=bytes(p.memory[s['foes']:s['foes']+50]);drop=g('inv_drop');tick(60)
   assert before==bytes(p.memory[s['foes']:s['foes']+50]) and drop==g('inv_drop');w('paused',0)
 assert cycles>=3 and up>0,(count,cycles,up)
 retreats[count]={'complete_retreats':cycles,'max_y':max_y,'survivors_preserved':True}
gif[0].save(R/'capturas/crow_reagrupacion.gif',save_all=True,append_images=gif[1:],duration=67,loop=0)
# Scaling and six simultaneous CROW, repeatedly replenished through actual bag draws.
hp={}
for phase in (1,2,5,11,99):
 enter(7,phase);assert g('boss_max_hp')==48+min(phase-1,10)*8;hp[phase]=g('boss_max_hp')
enter(7);until(lambda:g('moai_intro')==0);total=0;boss_frames=[]
for cycle in range(3):
 until(lambda:all(foe(i)[2] for i in range(6)))
 assert not any(foe(i)[2] for i in range(6,10));total+=6
 if cycle==0:
  tick(12);p.screen.image.save(str(R/'capturas/moai_seis_crow.png'))
  # Both OAM coherence and controls while all six helpers remain active.
  frames=deque(maxlen=6);addr=s['oam_commit'];shadow=s['shadow_OAM'];p.hook_register(addr//0x4000,addr,lambda q:q.append(bytes(p.memory[shadow:shadow+160])),frames)
  for frame in range(240):
   tick();assert bytes(p.memory[0xfe00:0xfea0]) in frames
   if frame%3==0:boss_frames.append(p.screen.image.copy())
  p.hook_deregister(addr//0x4000,addr)
 # Destroy all six with the laser collision path, including slots 2..5.
 w('paused',1);tick(3);w('boss_left',0);w('fire_cd',255)
 for i in range(6):
  w('paused',1);tick(3);clear()
  for j in range(6):
   if foe(j)[2]:p.memory[f(j)]=96;p.memory[f(j)+1]=20
  p.memory[f(i)]=8;p.memory[f(i)+1]=80;p.memory[f(i)+3]=1
  p.memory[s['shots']:s['shots']+3]=[12,83,1];w('paused',0);until(lambda:not foe(i)[2],8)
 assert not any(foe(i)[2] for i in range(6));w('fire_cd',0)
assert total==18
# Death clears every helper, not just the original pair.
until(lambda:all(foe(i)[2] for i in range(6)))
w('paused',1);tick(3);clear();w('boss_hp',1)
for i in range(6):p.memory[f(i)]=96;p.memory[f(i)+1]=20
p.memory[s['shots']:s['shots']+3]=[60,60,1];w('paused',0);until(lambda:g('state')==6)
assert not any(foe(i)[2] for i in range(10))
boss_frames[0].save(R/'capturas/moai_seis_crow.gif',save_all=True,append_images=boss_frames[1:],duration=50,loop=0)
report={'result':'PASS','invader_survivors':retreats,'pause_preserves_retreat':True,'font_identical_to_015':True,'boss_hp_by_phase':hp,'boss_crow_limit':6,'summons_observed':total,'summon_batches_fully_destroyed':3,'all_six_laser_hitboxes_checked':True,'boss_death_clears_all_helpers':True,'six_crow_oam_frames':240,'limits':'PyBoy DMG; prepared phases, invulnerability and laser collisions in RAM.'}
(R/'REAGRUPACION_Y_MOAI.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));p.stop()

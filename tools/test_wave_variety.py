"""Actual ROM selection, reinforcement and invasion regression tests.
Prepared wave entries / collisions; no unassisted-playthrough claim.
"""
from pathlib import Path
from collections import Counter,deque
import json
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1]
s={a[1].lstrip('_'):int(a[2],16) for l in (R/'Halcones-Estelares-GB.noi').read_text().splitlines() if len(a:=l.split())==3 and a[0]=='DEF'}
p=PyBoy(str(R/'Halcones-Estelares-GB.gb'),window='null');p.set_emulation_speed(0)
def g(n):return p.memory[s[n]]
def w(n,v):p.memory[s[n]]=v
def w16(n,v):p.memory[s[n]:s[n]+2]=list(v.to_bytes(2,'little'))
def u16(n):return int.from_bytes(bytes(p.memory[s[n]:s[n]+2]),'little')
def tick(n=1):p.tick(n,True)
def until(fn,n=500):
 for _ in range(n):
  if fn():return
  tick()
 raise AssertionError(('timeout',g('state'),g('wave')))
def foe(i):return list(p.memory[s['foes']+5*i:s['foes']+5*i+5])
def put(i,v):p.memory[s['foes']+5*i:s['foes']+5*i+5]=v
def clear():
 for name,count in [('shots',2),('plasma',3)]:
  for i in range(count):p.memory[s[name]+3*i+2]=0

def enter(wave):
 w('paused',1);tick(3);clear();w('wave',wave-1);w('state',4);w16('state_timer',0);w('paused',0);until(lambda:g('state')==1);w('invulnerable',255)

tick(300);p.button_press('start');tick(4);p.button_release('start');until(lambda:g('state')==1);tick(60)
# Verify actual routine's state transitions, not just a Python PRNG simulation.
rng=[];addr=s['flight_random'];p.hook_register(addr//0x4000,addr,lambda a:a.append(u16('wave_rng')),rng)
patterns=Counter();compositions=Counter();cross=Counter();first_phase=[]
for loop in range(256):
 appeared=False
 for wave in range(1,7):
  enter(wave);pat=g('pattern_id');comp=g('composition_id');patterns[pat]+=1
  rows=[foe(i) for i in range(10)];alive=[e for e in rows if e[2]]
  assert len(alive)==(10 if comp==3 else 6)
  assert sum(bool(e[4]) for e in alive)==(0 if comp==3 else 6-2*comp)
  if wave>=3 and pat<7:compositions[comp]+=1;cross[(pat,comp)]+=1
  if pat==7:assert all(e[4]==0 for e in alive);appeared=True
 first_phase.append(appeared)
assert set(patterns)==set(range(1,8)) and min(patterns.values())>100,patterns
assert set(compositions)=={0,1,2} and len(cross)==18,(compositions,cross)
assert any(first_phase) and not all(first_phase)
for a,b in zip(rng,rng[1:]):assert b==((a>>1)^(0xb400 if a&1 else 0)),(a,b)
p.hook_deregister(addr//0x4000,addr)
v=1;period=0
while True:
 v=(v>>1)^(0xb400 if v&1 else 0);period+=1
 if v==1:break
 assert period<=65535
assert period==65535
# Authentic visual samples from selected current-ROM formations.
for comp in range(3):
 while True:
  enter(3)
  if g('composition_id')==comp and g('pattern_id')<7:break
 for _ in range(160):w('invulnerable',255);tick()
 p.screen.image.save(str(R/f'capturas/combinacion_{comp}.png'))
# Each CROW hitbox is 8 pixels even in later waves.
for offset,hit in [(10,False),(7,True)]:
 enter(3);w('paused',1);tick(3);clear();w('pattern_id',1);w('crow_budget',0)
 for i in range(10):put(i,[80,10,0,0,1])
 put(0,[40,50,1,0,0]);put(1,[85,15,1,0,1]);p.memory[s['home_x']]=40;p.memory[s['home_y']]=50
 w('formation_drift',0);w('attack_cd',255);w('sim_phase',0)
 p.memory[s['shots']:s['shots']+3]=[40+offset,53,1];w('paused',0);tick(2)
 assert (foe(0)[2]==0)==hit,('crow hitbox',offset,foe(0))
# Last big enemy must not skip reinforcements; cover batches of 1..4.
batches=set();total_spawned=0
for trial in range(48):
 enter(3);w('paused',1);tick(3);clear();w('pattern_id',1)
 for i in range(10):put(i,[80,10,0,0,1])
 put(0,[40,50,1,0,1]);p.memory[s['home_x']]=40;p.memory[s['home_y']]=50
 w('formation_drift',0);w('attack_cd',255);p.memory[s['shots']:s['shots']+3]=[44,53,1];w('paused',0)
 until(lambda:g('crow_budget')<4);spawned=4-g('crow_budget');batches.add(spawned);total_spawned+=spawned
 assert g('state')==1 and sum(e[2] for e in [foe(i) for i in range(10)])==spawned
 assert all(foe(i)[3]==4 for i in range(10) if foe(i)[2]),'reinforcements need hidden warning entry'
 # A queued/offscreen CROW already blocks another batch.
 w('paused',1);tick(3);clear();put(9,[40,50,1,0,1]);p.memory[s['home_x']+9]=40;p.memory[s['home_y']+9]=50
 before=g('crow_budget');p.memory[s['shots']:s['shots']+3]=[44,53,1];w('paused',0);until(lambda:foe(9)[2]==0)
 assert g('crow_budget')==before,'CROW queue must block more summons'
 # Exhaust the remaining budget through actual kills, clearing previous CROW fixtures.
 while g('crow_budget'):
  w('paused',1);tick(3);clear()
  for i in range(10):put(i,[80,10,0,0,1])
  put(0,[40,50,1,0,1]);p.memory[s['home_x']]=40;p.memory[s['home_y']]=50
  before=g('crow_budget');p.memory[s['shots']:s['shots']+3]=[44,53,1];w('paused',0);until(lambda:g('crow_budget')<before)
 w('paused',1);tick(3);clear()
 for i in range(10):put(i,[80,10,0,0,1])
 put(0,[40,50,1,0,1]);p.memory[s['shots']:s['shots']+3]=[44,53,1];w('paused',0);until(lambda:g('state')==4)
 assert g('crow_budget')==0,'budget exhaustion allows normal transition'
assert batches=={1,2,3,4},batches
# Shield kill uses the same reinforcement path.
enter(3);w('paused',1);tick(3);clear();w('pattern_id',1)
for i in range(10):put(i,[80,10,0,0,1])
put(0,[g('px')+4,120,1,0,1]);p.memory[s['home_x']]=g('px')+4;p.memory[s['home_y']]=120
w('formation_drift',0);w('shield_state',1);w16('shield_timer',170);w('paused',0);until(lambda:g('crow_budget')<4)
# CROW-only invaders: collective reversal/descent, acceleration, all ten slots,
# coherent OAM, static background, firing/shield while active.
while True:
 enter(1)
 if g('pattern_id')==7:break
w('shield_state',0);w16('shield_timer',0)
frames=deque(maxlen=6);addr=s['oam_commit'];shadow=s['shadow_OAM'];p.hook_register(addr//0x4000,addr,lambda q:q.append(bytes(p.memory[shadow:shadow+160])),frames)
base=bytes(p.memory[0x9800:0x9c00]);directions=set();gif=[];shots=0;updates=u16('ticks')
for f in range(720):
 w('invulnerable',255)
 if f%60==0:p.button_press('a')
 if f%60==1:p.button_release('a')
 tick();directions.add(g('inv_direction'));shots+=sum(p.memory[s['shots']+3*i+2] for i in range(2))
 assert g('state')==1
 assert bytes(p.memory[0x9800:0x9c00])==base
 assert bytes(p.memory[0xfe00:0xfea0]) in frames
 for i in range(10):
  e=foe(i)
  if e[2]:assert e[4]==0 and 0<=e[0]<=102 and 0<=e[1]<=130
 if f%4==0:gif.append(p.screen.image.copy())
 if f==180:p.screen.image.save(str(R/'capturas/crow_invaders.png'))
assert directions=={1,255} and g('inv_drop')>0 and shots>0
p.button_press('b');tick(2);p.button_release('b');assert g('shield_state')==1
assert 285<=u16('ticks')-updates<=305
p.hook_deregister(addr//0x4000,addr)
gif[0].save(R/'capturas/crow_invaders.gif',save_all=True,append_images=gif[1:],duration=67,loop=0)
# Maximum reinforcement load: five big enemies plus four CROW.
while True:
 enter(3)
 if g('composition_id')==0:break
w('paused',1);tick(3);clear();w('pattern_id',1);w('shield_state',0);w16('shield_timer',0);w('attack_cd',255)
put(0,[40,50,1,0,1]);p.memory[s['home_x']]=40;p.memory[s['home_y']]=50
w16('wave_rng',6);p.memory[s['shots']:s['shots']+3]=[44,53,1];w('paused',0);until(lambda:g('crow_budget')==0)
assert sum(foe(i)[2] for i in range(10))==9
updates=[];addr=s['player_tick'];p.hook_register(addr//0x4000,addr,lambda q:q.append(1),updates)
for _ in range(8):w('invulnerable',255);tick(30)
worst_updates=len(updates);assert worst_updates>=235,worst_updates
p.hook_deregister(addr//0x4000,addr)
fires=[];addr=s['audio_fire_now'];p.hook_register(addr//0x4000,addr,lambda q:q.append(1),fires)
for trial in range(24):
 before=len(fires);p.button_press('a');tick(1);p.button_release('a');tick(1)
 assert len(fires)>before,('reinforcement load input',trial)
 tick(4);w('invulnerable',255)
p.hook_deregister(addr//0x4000,addr)
p.button_press('b');tick(2);p.button_release('b');assert g('shield_state')==1
report={'result':'PASS','selection_samples':sum(patterns.values()),'patterns':dict(patterns),'large_wave_compositions':dict(compositions),'all_18_pattern_composition_pairs':len(cross)==18,'first_phase_trials':len(first_phase),'with_invaders':sum(first_phase),'without_invaders':len(first_phase)-sum(first_phase),'rng_period':period,'actual_rng_transitions_checked':len(rng)-1,'refill_batch_sizes':sorted(batches),'reinforcement_limit_per_wave':4,'queued_crows_block_refill':True,'laser_and_shield_kills_tested':True,'crow_hitbox_in_late_wave':8,'max_load_enemies':9,'max_load_player_updates_per_240':worst_updates,'max_load_short_fire_presses':24,'max_load_shield_response_vblanks':2,'invaders_oam_frames':720,'invaders_control_and_static_background':True,'limitations':'PyBoy DMG; wave, collision and protection RAM fixtures; no physical-console verification.'}
(R/'VARIEDAD_OLEADAS.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));p.stop()

"""Run the real DMG routines: loop escalation, interlude preservation and APU pause.
RAM fixtures select phases and trigger a final hit; no gameplay rules are emulated here.
"""
from pathlib import Path
import json
from statistics import mean
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1];sym={}
for line in (R/'Halcones-Estelares-GB.noi').read_text().splitlines():
 a=line.split()
 if len(a)==3 and a[0]=='DEF':sym[a[1].lstrip('_')]=int(a[2],16)
p=PyBoy(str(R/'Halcones-Estelares-GB.gb'),window='null',sound_emulated=True);p.set_emulation_speed(0)
frame=[0];fires=[]
def g(n):return p.memory[sym[n]]
def w(n,v):p.memory[sym[n]]=v
def w16(n,v):p.memory[sym[n]:sym[n]+2]=list(v.to_bytes(2,'little'))
def u16(n):return int.from_bytes(bytes(p.memory[sym[n]:sym[n]+2]),'little')
def w32(n,v):p.memory[sym[n]:sym[n]+4]=list(v.to_bytes(4,'little'))
def u32(n):return int.from_bytes(bytes(p.memory[sym[n]:sym[n]+4]),'little')
def tick(n=1):
 for _ in range(n):p.tick(1,True);frame[0]+=1
def until(f,n=1000):
 for _ in range(n):
  if f():return
  tick()
 raise AssertionError(('timeout',g('state'),g('wave'),g('phase')))
def enter(phase,wave):
 w('paused',1);tick(3);w('phase',phase);w('wave',wave-1);w16('state_timer',0);w('state',4);w('paused',0)
 until(lambda:g('state')==1);w('invulnerable',255)
def clear():
 for i in range(3):p.memory[sym['plasma']+i*3+2]=0
 for i in range(2):p.memory[sym['shots']+i*3+2]=0

tick(300);p.button_press('start');tick(4);p.button_release('start');until(lambda:g('state')==1);tick(10)
assert g('music_on')==1 and p.memory[0xff47]==0x1b
p.button_press('start');tick(4);p.button_release('start');tick(4)
assert g('paused')==1;step=g('music_step');tick(50);assert g('music_step')==step
assert p.memory[0xff1c]&0x60==0,'wave must be silent while paused'
p.button_press('start');tick(4);p.button_release('start');tick(50)
assert not g('paused') and g('music_step')!=step
periods={}
for phase in [1,2,3,5,10,20,99]:
 row=[]
 for wave in [1,3,5,7]:
  enter(phase,wave)
  while wave!=7 and g('pattern_id')==7:enter(phase,wave)
  row.append(g('fire_period'));assert 6<=g('fire_period')<=70
 periods[phase]=row
for a,b in zip([1,2,3,5],[2,3,5,10]):assert all(x>y for x,y in zip(periods[a],periods[b])),(a,b,periods)
# Attack variety and scaling, observed in actual boss logic.
measured={}
for phase in [1,2,3,10,99]:
 enter(phase,7);until(lambda:g('moai_intro')==0)
 assert g('boss_hp')==48+min(phase-1,10)*8
 measured[phase]=g('boss_hp')
enter(1,7);seen=set();summoned=False;boss_controls={};fires=[]
addr=sym['audio_fire_now'];p.hook_register(1 if addr>=0x4000 else 0,addr,lambda c:c.append(1),fires)
for i in range(2000):
 if i%30==0:w('invulnerable',255)
 clear();tick()
 if g('boss_attack')<4:
  attack=g('boss_attack');seen.add(attack)
  if attack not in boss_controls:
   saved_target=g('boss_target');w('px',4);w('shield_state',0);w16('shield_timer',0)
   before=len(fires);p.button_press('a');p.button_press('b');tick();p.button_release('a');p.button_release('b');tick(2)
   assert len(fires)==before and g('shield_state')==1,('boss input',attack,before,len(fires),g('shield_state'),g('state'),g('paused'),g('input_now'),g('keys'),g('pressed'))
   assert g('boss_target')==saved_target,'aim must retain last known position'
   boss_controls[attack]='B activates; simultaneous A blocked during shield'

 if all(p.memory[sym['foes']+j*5+2] for j in range(6)):summoned=True
assert seen=={0,1,2,3} and summoned,(seen,summoned)
# Full collapse -> full-screen victory -> next loop; stats and recharge survive.
enter(4,7);until(lambda:g('moai_intro')==0);clear();w('paused',1);tick(4);w32('score',12340);w32('record',12340);w('lives',2);w('life_hits',0)
w('shield_state',2);w16('shield_timer',200);w('boss_hp',1)
p.memory[sym['shots']:sym['shots']+3]=[60,60,1];w('paused',0)
until(lambda:g('state')==6);until(lambda:g('state')==3)
assert g('moai_blocks')==0 and p.memory[0xff40]&32==0
assert g('phase')==4 and u32('score')==12350 and g('lives')==2
charge=u16('shield_timer');tick(60);assert u16('shield_timer')==charge
p.screen.image.save(R/'capturas/victoria_moai.png')
until(lambda:g('state')==1)
assert g('phase')==5 and g('wave')==1 and u32('score')==12350 and g('lives')==2
assert g('shield_state')==2 and charge-4<=u16('shield_timer')<=charge
assert g('invulnerable')>=118 and g('music_on')==1
w('phase',99);w('state',3);w16('state_timer',0);until(lambda:g('state')==1)
assert g('phase')==99 and g('wave')==1
report={'result':'PASS','fire_period_logic_ticks_by_phase':periods,'boss_hp_by_phase':measured,'four_attacks_observed':sorted(seen),'six_crows_summoned':summoned,'controls_during_each_attack':boss_controls,'music_pauses_and_resumes':True,'victory_preserves_score_lives_recharge':True,'next_loop_returns_to_wave_1':True,'phase_99_saturates':True,'limits':'Prepared RAM scenarios in PyBoy DMG; cadence measured with projectile slots cleared.'}
(R/'BUCLES_Y_MUSICA.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));p.stop()

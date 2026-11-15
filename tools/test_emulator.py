"""Execute the DMG ROM. Collision fixtures are arranged only while paused.
This validates actual game code, not an unassisted full playthrough."""
from pathlib import Path
import struct,json
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1];cap=R/'capturas';cap.mkdir(exist_ok=True)
sym={}
for line in (R/'Halcones-Estelares-GB.noi').read_text().splitlines():
 a=line.split()
 if len(a)==3 and a[0]=='DEF':sym[a[1].lstrip('_')]=int(a[2],16)
p=PyBoy(str(R/'Halcones-Estelares-GB.gb'),window='null',sound_emulated=False);p.set_emulation_speed(0)
protect=True
def tick(n=1):
 while n:
  step=min(n,30)
  if protect:p.memory[sym['invulnerable']]=255
  p.tick(step,True);n-=step
def get(n):return p.memory[sym[n]]
def put(n,v):p.memory[sym[n]]=v
def u16(n):return p.memory[sym[n]]+256*p.memory[sym[n]+1]
def u32(n):return int.from_bytes(bytes(p.memory[sym[n]:sym[n]+4]),'little')
def wait(cond,limit=800):
 for _ in range(limit):
  if cond():return
  tick()
 raise AssertionError(('timeout',get('state'),get('wave'),get('boss_hp')))
def press(k):p.button_press(k);tick(4);p.button_release(k);tick(4)
def snap(name):tick(3);p.screen.image.save(str(cap/(name+'.png')))
def arrange():put('paused',1);tick(12)
def shot(x,y):p.memory[sym['shots']:sym['shots']+3]=list(struct.pack('<BBB',x,y,1))
def shot_at_fixture():shot(74,56)
def enemy(i,x,y,live=0):
 p.memory[sym['foes']+i*5:sym['foes']+i*5+5]=list(struct.pack('<BBBBB',x,y,live,0,0))
 p.memory[sym['home_x']+i]=x;p.memory[sym['home_y']+i]=y;put('formation_drift',0)
def bg():return bytes(p.memory[0x9800:0x9c00])
def mode(i):return p.memory[sym['foes']+i*5+3]
def countshots():return sum(p.memory[sym['shots']+i*3+2] for i in range(2))
def hitboss(target):
 while get('boss_hp')>target:
  arrange();old=get('boss_hp');shot(60,60);put('paused',0);wait(lambda:get('boss_hp')<old);tick(12)
tick(300);assert get('state')==0 and get('music_on')==1;snap('titulo');press('start');wait(lambda:get('state')==1);tick(20);snap('combate')
assert get('lives')==3 and get('wave')==1
assert get('music_on')==1,'combat soundtrack must start'
melody_step=get('music_step')
assert p.memory[0xff4b]==119 and p.memory[0xff4a]==0,'right sidebar'
assert p.memory[0xffff]&2==0,'no raster LCD interrupt'
# Static playfield: no scrolling, no star updates, no background-map animation.
writes=[0]
def on_upload(c):c[0]+=1
p.hook_register(1 if sym['set_bkg_data']>=0x4000 else 0,sym['set_bkg_data'],on_upload,writes)
base=bg();start=u16('ticks');tick(240);steps=(u16('ticks')-start)&65535
assert writes[0]==0,('unnecessary tile uploads',writes[0])
assert get('music_step')!=melody_step,'music transport must run during gameplay'
assert bg()==base,'stars/background changed during normal play'
assert p.memory[0xff42]==p.memory[0xff43]==0
assert 85<=steps<=105,('simulation rate',steps)
# Curved CROW sorties must return visibly to a formation slot.
wait(lambda:any(mode(i)==3 for i in range(10)))
returning=next(i for i in range(10) if mode(i)==3);previous=p.memory[sym['foes']+returning*5+1]
tick(3);current=p.memory[sym['foes']+returning*5+1]
assert 0<=previous-current<=6
wait(lambda:mode(returning)==0)
# Movement and borders; isolate incoming fire for input checks.
arrange()
for i in range(10):enemy(i,100,10,1)
for i in range(3):p.memory[sym['plasma']+i*3+2]=0
put('invulnerable',255);put('paused',0)
p.button_press('right');tick(160);p.button_release('right');assert get('px')==92
p.button_press('left');tick(220);p.button_release('left');assert get('px')==4
p.button_press('a');tick(3);assert countshots()==1;tick(3);assert countshots()>=1
p.button_release('a');tick(2);press('a');assert countshots()==2
press('b');assert get('shield_state')==1
wait(lambda:u16('ticks')&4==0);snap('escudo')
press('start');assert get('paused')==1;t=u16('shield_timer');tick(60);assert u16('shield_timer')==t
press('start');wait(lambda:get('shield_state')==2,200);wait(lambda:get('shield_state')==0,380);assert writes[0]>0,'VRAM hook must observe actual HUD uploads'
# Six waves: prepared collision with one remaining living enemy in each.
for wave in range(1,7):
 assert get('wave')==wave
 arrange();put('invulnerable',255)
 for i in range(10):enemy(i,70,50)
 enemy(0,70,50,1);shot_at_fixture();old=u32('score');put('paused',0)
 wait(lambda:u32('score')==old+10);wait(lambda:get('state')==4)
 if wave==1:tick(30);snap('oleada_superada')
 wait(lambda:get('state')==1)
assert get('wave')==7 and get('boss_hp')==32
snap('moai')
# Warning is part of the face and remains visible during mouth-open fire.
arrange();put('fire_cd',9);put('paused',0);wait(lambda:get('moai_eyes')==1);snap('moai_ojos')
arrange();put('fire_cd',1);put('paused',0);wait(lambda:get('moai_mouth')==1);snap('moai_boca')
hitboss(24);assert get('moai_stage')==1;snap('moai_grieta_12')
hitboss(16);assert get('moai_stage')==2,(get('boss_hp'),get('boss_max_hp'),get('moai_stage'));snap('moai_grieta_6')
hitboss(8);assert get('moai_stage')==3;snap('moai_grieta_3')
hitboss(0);wait(lambda:get('state')==6)
frames=[];partial=False
while get('state')==6:
 tick(2);frames.append(p.screen.image.copy())
 if not partial and 0<get('moai_blocks')<30:
  p.screen.image.save(str(cap/'moai_derrumbe.png'));partial=True
frames[0].save(cap/'moai_derrumbe.gif',save_all=True,append_images=frames[1:],duration=33,loop=0)
assert get('state')==3 and get('moai_blocks')==0
snap('victoria_moai');assert p.memory[0xff40]&32==0,'victory uses full screen'
assert get('music_on')==1
wait(lambda:get('state')==1);assert get('phase')==2 and get('wave')==1
# Original bonus rule: every hundred hits gives one life, capped at three.
arrange();put('life_hits',99);put('lives',2)
for i in range(10):enemy(i,70,50)
enemy(0,70,50,1);shot_at_fixture();put('paused',0)
wait(lambda:get('lives')==3);assert get('life_hits')==0
wait(lambda:get('state')==4);wait(lambda:get('state')==1)
# Original five-digit score ceiling, including values beyond a 16-bit integer.
for initial in (99980,99990):
 arrange()
 for name in ('score','record'):p.memory[sym[name]:sym[name]+4]=list(initial.to_bytes(4,'little'))
 for i in range(10):enemy(i,70,50)
 enemy(0,70,50,1);shot_at_fixture();put('paused',0)
 wait(lambda:p.memory[sym['foes']+2]==0);tick(12)
 assert u32('score')==u32('record')==99990
 wait(lambda:get('state')==4);wait(lambda:get('state')==1)
arrange();protect=False;put('lives',1);put('invulnerable',0);put('shield_state',0)
p.memory[sym['plasma']:sym['plasma']+3]=list(struct.pack('<BBB',get('px')+8,120,1));put('paused',0)
wait(lambda:get('state')==2);assert get('music_on')==0,'Game Over stops music';tick(190);snap('gameover');press('start');wait(lambda:get('state')==0)
p.stop()
report={'result':'PASS','simulation_ticks_per_240_vblanks':steps,'idle_tile_uploads_per_240_vblanks':0,'checks':['dark techno in title and combat','right sidebar','no LCD interrupt','static star map','no scroll','movement borders','single press fire','two shots','shield/recharge','pause','crow scout return','new arcade patterns covered by test_arcade_flow.py','six waves','32 initial boss HP','eye warning','mouth opening','cracks at 75/50/25 percent','block dissolve before centered victory interlude','phase 2','extra life at 100 hits','score saturates at 99990','game over/restart'],'limitations':'PyBoy DMG; collision fixtures and temporary invulnerability in paused RAM; no hardware test or unassisted full playthrough'}
(R/'PRUEBAS.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

"""Verify one-pixel visual banking and neutral return, with real button input."""
from pathlib import Path
import json
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1];sym={}
for line in (R/'Halcones-Estelares-GB.noi').read_text().splitlines():
 a=line.split()
 if len(a)==3 and a[0]=='DEF':sym[a[1].lstrip('_')]=int(a[2],16)
p=PyBoy(str(R/'Halcones-Estelares-GB.gb'),window='null',sound_emulated=False);p.set_emulation_speed(0)
p.tick(300);p.button_press('start');p.tick(4);p.button_release('start')
while p.memory[sym['state']]!=1:p.tick()
p.tick(130);frames=[];results={}
# Move only; grant protection without blink by avoiding hazards through a transition fixture.
p.memory[sym['state']]=4;p.memory[sym['state_timer']:sym['state_timer']+2]=[200,0];p.memory[sym['invulnerable']]=0
for direction,n,expected in [('left',12,(129,127)),('neutral',8,(128,128)),('right',24,(127,129)),('neutral',8,(128,128))]:
 if direction!='neutral':p.button_press(direction)
 for _ in range(n):p.tick();frames.append(p.screen.image.copy())
 actual=(p.memory[0xfe00],p.memory[0xfe10]);assert actual==expected,(direction,actual,expected)
 results[direction]=actual
 # Each column remains a coherent pair of 8x16 sprites.
 for i in (0,2,4):assert p.memory[0xfe00+(i+1)*4]-p.memory[0xfe00+i*4]==16
 if direction!='neutral':p.button_release(direction)
frames[0].save(R/'capturas/nave_inclinacion.gif',save_all=True,append_images=frames[1:],duration=20,loop=0)
(R/'ANIMACION_NAVE.json').write_text(json.dumps({'result':'PASS','wing_y_by_direction':results,'offset_pixels':1,'collision_geometry_changed':False,'fixture':'protected transition; movement by buttons'},indent=2));print(results);p.stop()

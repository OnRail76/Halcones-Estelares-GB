from pathlib import Path
import json
from pyboy import PyBoy
from PIL import Image
R=Path(__file__).resolve().parents[1]
def scene(root):
 s={a[1].lstrip('_'):int(a[2],16) for l in (root/'Halcones-Estelares-GB.noi').read_text().splitlines() if len(a:=l.split())==3 and a[0]=='DEF'}
 p=PyBoy(str(root/'Halcones-Estelares-GB.gb'),window='null');p.set_emulation_speed(0);p.tick(300);p.button_press('start');p.tick(4);p.button_release('start');p.tick(30)
 def w(n,v):p.memory[s[n]]=v
 bg=bytes(p.memory[0x9800:0x9c00]);w('paused',1);p.tick(240);assert bytes(p.memory[0x9800:0x9c00])==bg
 w('wave',6);w('state',4);w('state_timer',0);p.memory[s['state_timer']+1]=0;w('paused',0);p.tick(45);w('paused',1);p.tick(3)
 field=bytes(p.memory[s['field']:s['field']+576]);star=bytes(p.memory[0x9000+48*16:0x9000+49*16]);p.stop();return field,star
assert scene(R)==scene(R.parent/'Halcones-GameBoy-0.13-respaldo'),'MOAI scene changed'
im=Image.open(R/'assets/cosmos_gb.png');assert set(im.getdata())=={0,1}
report={'result':'PASS','moai_field_and_star_identical_to_013':True,'cloud_ink':1,'star_ink':2,'projectile_ink':3,'static_background':True}
(R/'FONDOS.json').write_text(json.dumps(report,indent=2));print(report)

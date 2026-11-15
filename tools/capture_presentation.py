"""Unmodified gameplay capture: buttons only, no RAM fixtures."""
from pathlib import Path
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1];p=PyBoy(str(R/'Halcones-Estelares-GB.gb'),window='null',sound_emulated=False);p.set_emulation_speed(0)
p.tick(300);p.screen.image.save(str(R/'capturas/titulo.png'))
frames=[]
for i in range(128):
 p.tick(2);frames.append(p.screen.image.copy())
frames[0].save(R/'capturas/titulo-arcade.gif',save_all=True,append_images=frames[1:],duration=33,loop=0)
p.button_press('start');p.tick(4);p.button_release('start');p.tick(180)
p.screen.image.save(str(R/'capturas/combate.png'))
p.button_press('b');p.tick(6);p.button_release('b');p.tick(8)
p.screen.image.save(str(R/'capturas/escudo.png'));p.stop()

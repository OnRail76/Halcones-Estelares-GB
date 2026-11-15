"""Capture real DMG APU output from the ROM; no external audio mixed in."""
from pathlib import Path
import wave,json
import numpy as np
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1];out=R/'audio';out.mkdir(exist_ok=True)
p=PyBoy(str(R/'Halcones-Estelares-GB.gb'),window='null',sound_emulated=True);p.set_emulation_speed(0)
sym={}
for line in (R/'Halcones-Estelares-GB.noi').read_text().splitlines():
 a=line.split()
 if len(a)==3 and a[0]=='DEF':sym[a[1].lstrip('_')]=int(a[2],16)
p.tick(300)
def capture(name,frames,buttons=False):
 chunks=[]
 for i in range(frames):
  if buttons:
   if i%30==0:p.memory[sym['invulnerable']]=255
   if i%30==0:p.button_press('a')
   if i%30==5:p.button_release('a')
  p.tick(1);chunks.append(p.sound.ndarray.copy())
 raw=np.concatenate(chunks);pcm=raw.astype(np.int16)*256
 assert np.ptp(pcm)>0
 with wave.open(str(out/name),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(p.sound.sample_rate);w.writeframes(pcm.astype('<i2').tobytes())
 return {'frames':frames,'samples':len(pcm),'rate':p.sound.sample_rate,'peak':int(abs(pcm.astype(np.int32)).max())}
report={'title':capture('Eurodance noventero.wav',880)}
p.button_press('start');p.tick(4);p.button_release('start');p.tick(180)
assert p.memory[sym['music_on']]==1
step=p.memory[sym['music_step']]
report['gameplay']=capture('Tecno oscuro 1.wav',448,True)
assert p.memory[sym['music_step']]!=step
# Isolated cues still execute the ROM's APU sequencer, with music disabled in RAM.
p.memory[sym['music_on']]=0;p.memory[sym['state']]=3
p.memory[sym['state_timer']:sym['state_timer']+2]=[0xff,0x7f]
for reg in (0xff12,0xff17,0xff1c,0xff21):p.memory[reg]=0
chunks=[]
for effect in (1,2,4,5,6,7,8,9):
 p.memory[sym['fx_id']]=effect;p.memory[sym['fx_index']]=0;p.memory[sym['fx_wait']]=0
 for _ in range(60):p.tick(1);chunks.append(p.sound.ndarray.copy())
raw=np.concatenate(chunks).astype(np.int16)*256
with wave.open(str(out/'efectos-gb.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(p.sound.sample_rate);w.writeframes(raw.astype('<i2').tobytes())
report['isolated_effects']={'samples':len(raw),'rate':p.sound.sample_rate,'peak':int(abs(raw.astype(np.int32)).max()),'sequence':['laser','enemy','explosion','hit','shield','ready','life','death'],'fixture':'music disabled and cue IDs selected in RAM; sequencer runs in ROM'}
# One-shot Game Over phrase, with the same cue state set by audio_over().
p.memory[sym['music_on']]=0;p.memory[sym['fx_id']]=0
for reg in (0xff12,0xff17,0xff1c,0xff21):p.memory[reg]=0
p.memory[sym['state']]=2;p.memory[sym['over_note']]=0;p.memory[sym['over_clock']]=1
p.memory[sym['state_timer']:sym['state_timer']+2]=[180,0]
report['game_over']=capture('Tonadilla de Game Over.wav',160)
assert p.memory[sym['over_note']]==5 and p.memory[sym['over_clock']]==0
(out/'captura.json').write_text(json.dumps(report,indent=2));print(report);p.stop()

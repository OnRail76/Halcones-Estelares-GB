"""Compare audio_tick register writes for identical non-title states, old/new ROM."""
from pathlib import Path
import json
from pyboy import PyBoy
R=Path(__file__).resolve().parents[1]
def run(root,state,song):
 sym={}
 for line in (root/'Halcones-Estelares-GB.noi').read_text().splitlines():
  a=line.split()
  if len(a)==3 and a[0]=='DEF':sym[a[1].lstrip('_')]=int(a[2],16)
 p=PyBoy(str(root/'Halcones-Estelares-GB.gb'),window='null',sound_emulated=True);p.set_emulation_speed(0);p.tick(300)
 def w(n,v):p.memory[sym[n]]=v
 # Keep scene logic idle while the actual audio ISR runs.
 w('state',3 if state!=2 else 2);p.memory[sym['state_timer']:sym['state_timer']+2]=[255,127]
 for n in ('music_clock','music_step','bass_drop','fx_id','fire_voice','noise_hold','paused'):w(n,0)
 w('music_song',song);w('music_pending',song);w('music_on',state!=2);w('over_clock',1);w('over_note',0)
 for a in range(0xff10,0xff26):p.memory[a]=0
 p.memory[0xff24]=0x77;p.memory[0xff25]=0xff
 trace=[];addr=sym['audio_tick']
 p.hook_register(1 if addr>=0x4000 else 0,addr,lambda c:c.append(bytes(p.memory[0xff10:0xff26])),trace)
 p.tick(500);p.stop();return trace[2:450]
old=R.parent/'Halcones-GameBoy-0.13-respaldo';results={}
a=(old/'src/audio.h').read_text();b=(R/'src/audio.h').read_text()
assert a[a.index('const uint16_t trance_arp'):a.index('void audio_tick')]==b[b.index('const uint16_t trance_arp'):b.index('void audio_tick')]
results['title']='Eurodance notes and playback unchanged'
for name,state,song in [('techno_1',3,0),('game_over',2,0)]:
 a=run(old,state,song);b=run(R,state,song);assert a==b,(name,len(a),len(b));results[name]='identical APU register trace'
(R/'MUSICA_TITULO.json').write_text(json.dumps({'result':'PASS','non_title_comparison':results},indent=2));print(results)

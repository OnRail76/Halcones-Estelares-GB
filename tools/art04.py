# Executed by assets.py with its tile encoder and output accumulator.
import ast
# Original HUD faces, imported as literal data without executing ZX tooling.
tree=ast.parse((A/'hud_zx133.py').read_text())
face=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FACE' for t in n.targets))
im=Image.new('L',(48,144));d=ImageDraw.Draw(im)
def band(y,name):
 d.rectangle((0,y,47,y+7),fill=2);label(im,(48-len(name)*6+1)//2,y,name,0)
def rail(y0,y1):
 d.line((0,y0,0,y1),fill=1);d.line((47,y0,47,y1),fill=1)
band(0,'PUNTOS');rail(8,23);label(im,3,18,'REC',2)
band(32,'VIDAS');rail(40,61)
band(64,'ESCUDO');rail(72,95)
band(100,'FASE');rail(108,121)
band(124,'OLEADA');rail(132,143)
emit('sidebar_data',gbtiles(im));im.point(lambda x:x*85).save(A/'sidebar_gb.png')
emit('pixel_font',[int(''.join('1' if c=='#' else '0' for c in row),2) for ch in chars for row in F[ch]])
emit('big_font',[int(''.join('1' if c=='#' else '0' for c in row),2) for ch in '0123456789' for row in zfont['BIG'][ch]])
emit('tiny_digits',[int(''.join('1' if c=='#' else '0' for c in row),2) for ch in '0123456789' for row in zfont['T3'][ch]])
faces=[]
for key in ('feliz','apurado','vacia'):
 f=Image.new('1',(14,14))
 for y,row in enumerate(face[key]):
  for x,c in enumerate(row):f.putpixel((x,y),c=='#')
 f=f.resize((11,11),Image.Resampling.NEAREST)
 faces.extend(int(''.join('1' if f.getpixel((x,y)) else '0' for x in range(11)),2) for y in range(11))
# Two bytes per row, MSB first.
emit('face_rows',[v for row in faces for v in (row>>8,row&255)])
# Exact 1.3.3 mask, scaled to forty by seventy-two. Two-pixel fissures
# follow the original starts and seeded zigzag algorithm (fixed art seed).
base=Image.open(A/'moai_zx133.png').convert('1').resize((40,72),Image.Resampling.NEAREST)
im=Image.new('L',(40,72))
for y in range(72):
 for x in range(40):
  if base.getpixel((x,y)):im.putpixel((x,y),3 if x==0 or not base.getpixel((max(0,x-1),y)) else 2)
# Dark sockets retained until warning/fire; actual eye glow uses the same pixels.
d=ImageDraw.Draw(im)
for x in (7,26):d.rectangle((x,14,x+6,19),fill=0)
all_stages=[]
for stage in range(4):
 if stage:
  xx,yy,length=[(26,1,24),(12,30,30),(34,36,34)][stage-1];seed=0x33
  for dy in range(length):
   x=round(xx*40/48);y=round((yy+dy)*72/88)
   d.line((max(0,x),y,min(39,x+1),y),fill=0)
   seed=(seed*5+17)&255;v=((seed<<2)|(seed>>6))&3;xx+=-1 if v==0 else (1 if v==3 else 0)
   xx=max(2,min(44,xx))
 all_stages+=gbtiles(im)
 im.point(lambda v:v*85).save(A/f'moai_damage_{stage}.png')
emit('moai_stages',all_stages)

moon=Image.new('L',(8,16))
mask=[0x38,0x7c,0xfe,0xfe,0xfe,0x7c,0x38]
art=[0x38,0x5c,0xee,0xfa,0xbe,0x74,0x38]
for y in range(7):
 for x in range(8):moon.putpixel((x,y),3 if art[y]&(128>>x) else (1 if mask[y]&(128>>x) else 0))
emit('moon_data',gbtiles(moon))
# Dedicated 24x24 player death frames in six 8x16 hardware sprites.
ship_blast=[]
original=runpy.run_path(str(A/'original_sprites.py'))
for frame in original['EXPLO']:
 im=Image.new('1',(16,16))
 for y,row in enumerate(frame):
  for x,c in enumerate(row):im.putpixel((x,y),c=='#')
 expanded=Image.new('1',(24,32));expanded.paste(im.resize((24,24),Image.Resampling.NEAREST),(0,0))
 ship_blast+=tiles(expanded,True)
emit('ship_blast_data',ship_blast)

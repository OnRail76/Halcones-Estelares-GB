"""Convert original artwork into DMG tiles. Python 3 + Pillow."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import runpy
R=Path(__file__).resolve().parents[1]; A=R/'assets'
out=[]
def pack(b):
 data=[];i=0
 while i<len(b):
  j=i+1
  while j<len(b) and b[j]==b[i] and j-i<128:j+=1
  if j-i>=3:data.extend([128|(j-i-1),b[i]]);i=j
  else:
   start=i;i+=1
   while i<len(b) and i-start<128:
    if i+2<len(b) and b[i]==b[i+1]==b[i+2]:break
    i+=1
   data.append(i-start-1);data.extend(b[start:i])
 return data
def emit(name,b):
 if name in ('font_data','sprite_data','cosmos_a','cosmos_b','title_data','gameover_data','victory_data','sidebar_data','waveclear_data','ship_blast_data'):
  name+='_rle';b=pack(b)
 out.append('const unsigned char '+name+'[] = {'+','.join(map(str,b))+'};')
def tiles(im,sprite=False):
 b=[]
 coords=([(x,y) for x in range(0,im.width,8) for y in range(0,im.height,8)] if sprite else [(x,y) for y in range(0,im.height,8) for x in range(0,im.width,8)])
 for x,y in coords:
  for dy in range(8):
   row=sum((128>>dx) for dx in range(8) if im.getpixel((x+dx,y+dy)))
   b.extend((row,row))
 return b
# Original ZX pixel alphabet; native 5x7 strokes, no font rasterisation.
chars=' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:-.!/'
zfont=runpy.run_path(str(A/'zx_font.py')); F=zfont['F5']
forfont=Image.new('1',(8*len(chars),8))
for i,c in enumerate(chars):
 for y,row in enumerate(F[c]):
  for x,ch in enumerate(row):forfont.putpixel((i*8+1+x,y),ch=='#')
emit('font_data',tiles(forfont));out.append('#define FONT_COUNT '+str(len(chars)))
s=runpy.run_path(str(A/'original_sprites.py'))
ims=[]
im=Image.open(A/'esf_interceptor.png').resize((16,16),Image.Resampling.NEAREST); ims.append(im)
for key in ('CUERVO','CAZADOR','HALCON'):
 for frame in s[key]:
  im=Image.new('1',(16,16))
  for y,row in enumerate(frame):
   for x,c in enumerate(row): im.putpixel((x,y),c=='#')
  ims.append(im)
for frame in s['EXPLO']:
 im=Image.new('1',(16,16))
 for y,row in enumerate(frame):
  for x,c in enumerate(row): im.putpixel((x,y),c=='#')
 ims.append(im)
# 0..39 ship, birds and explosions; 40 bullet,42 plasma,44 shield left/right.
b=[]
for im in ims:b+=tiles(im,True)
for kind in range(3):
 im=Image.new('1',(16 if kind==2 else 8,16)); d=ImageDraw.Draw(im)
 if kind==0:d.rectangle((3,0,4,5),fill=1)
 if kind==1:d.polygon([(3,0),(6,3),(3,6),(0,3)],fill=1)
 if kind==2:
  d.arc((0,0,15,15),180,360,fill=1,width=2)
 b+=tiles(im,True)
emit('sprite_data',b);out.append('#define SPRITE_COUNT '+str(len(b)//16))
# Boss: source conversion, nearest-neighbour; no newly drawn replacement.
im=Image.open(A/'MOAI_REFERENCIA_USUARIO.jpg').convert('L').point(lambda p:255 if p>128 else 0)
im=im.crop(im.getbbox()).resize((40,64),Image.Resampling.NEAREST).convert('1'); im.save(A/'moai_gb.png')
# Four-tone screens composed for 160x144, retaining original logo and artwork.
def gbtiles(im):
 out=[]
 for y in range(0,im.height,8):
  for x in range(0,im.width,8):
   for dy in range(8):
    row=[im.getpixel((x+dx,y+dy)) for dx in range(8)]
    out.extend((sum((v&1)<<(7-i) for i,v in enumerate(row)),sum(((v>>1)&1)<<(7-i) for i,v in enumerate(row))))
 return out
def zx(name):
 raw=(A/name).read_bytes(); im=Image.new('L',(256,192))
 for y in range(192):
  off=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
  for x in range(256):
   at=raw[6144+(y//8)*32+x//8]; c=(at&7) if raw[off+x//8]&(128>>(x&7)) else ((at>>3)&7)
   # All colored inks remain visible on DMG; cyan/yellow are the brightest.
   im.putpixel((x,y),0 if c==0 else (3 if c in (3,5,6,7) else 2))
 return im
def label(im,x,y,text,ink=3,scale=1):
 for c in text:
  for yy,row in enumerate(F[c]):
   for xx,v in enumerate(row):
    if v=='#':ImageDraw.Draw(im).rectangle((x+xx*scale,y+yy*scale,x+(xx+1)*scale-1,y+(yy+1)*scale-1),fill=ink)
  x+=6*scale
def screen(name,im):
 raw=gbtiles(im);unique=[];mapping=[]
 for i in range(0,len(raw),16):
  t=raw[i:i+16]
  if t not in unique:unique.append(t)
  mapping.append(unique.index(t))
 assert len(unique)<=(255 if name=='title' else 212),(name,len(unique))
 emit(name+'_data',sum(unique,[]));emit(name+'_map',mapping);out.append('#define '+name.upper()+'_COUNT '+str(len(unique)))
 im.point(lambda v:v*85).save(A/(name+'_gb.png'))
# Convert the supplied robot adaptation to hardware 2bpp and compose the title.
im=Image.new('L',(160,144));d=ImageDraw.Draw(im)
src=zx('title_zx133.scr')
im.paste(src.crop((45,9,211,61)).resize((144,32),Image.Resampling.NEAREST),(8,3))
label(im,(160-len('EUROPEAN SPACE FORCE')*6+1)//2,39,'EUROPEAN SPACE FORCE',2)
robot=Image.open(A/'robot_titulo_referencia.png').convert('L')
robot=robot.crop(robot.point(lambda v:255 if v>45 else 0).getbbox()).resize((144,68),Image.Resampling.NEAREST)
robot=robot.point(lambda v:0 if v<45 else (1 if v<145 else (2 if v<225 else 3)))
im.paste(robot,(8,49))
d.rectangle((29,122,130,133),fill=3);label(im,47,124,'PRESS START',0)
label(im,26,136,'2026 TONY C. WARE',2);screen('title',im)
im=Image.new('L',(160,144));d=ImageDraw.Draw(im)
label(im,71,6,'ESF',2);d.line((8,18,151,18),fill=1)
label(im,27,25,'GAME OVER',3,2);d.line((8,43,151,43),fill=2)
src=zx('gameover_zx133.scr');im.paste(src.crop((60,67,202,116)).resize((112,40),Image.Resampling.NEAREST),(24,49))
label(im,26,110,'MISION TERMINADA',2);screen('gameover',im)
# HUD: inverted letters and original ZX bold digits, a smiley and charge cells.
b=[]
for i in range(len(chars)):
 im=Image.new('L',(8,8),3)
 for y,row in enumerate(F[chars[i]]):
  for x,c in enumerate(row):
   if c=='#':im.putpixel((x+1,y),0)
 b+=gbtiles(im)

b=[]
for c in '0123456789':
 im=Image.new('L',(8,8),3)
 for y,row in enumerate(zfont['BIG'][c]):
  for x,v in enumerate(row):
   if v=='#':im.putpixel((x,y),0)
 b+=gbtiles(im)

b=[]
for kind in range(4):
 im=Image.new('L',(8,8),3);d=ImageDraw.Draw(im)
 if kind==0:
  d.ellipse((0,0,6,6),fill=0);d.point((2,2),fill=3);d.point((4,2),fill=3);d.line((2,4,4,4),fill=3)
 if kind==1:d.rectangle((1,1,6,6),outline=1)
 if kind==2:d.rectangle((1,1,6,6),fill=0);d.line((2,2,5,2),fill=2)
 if kind==3:d.line((0,7,7,7),fill=0)
 b+=gbtiles(im)

# Original 8x8 CROW, padded to the GB 8x16 sprite hardware format.
crows=[['#......#','##....##','.##..##.','..####..','.#.##.#.','..####..','...##...','...##...'],['........','...##...','..####..','########','#.#..#.#','..####..','.#.##.#.','...##...']]
crow_bytes=[]
for frame in crows:
 im=Image.new('1',(8,16))
 for y,row in enumerate(frame):
  for x,c in enumerate(row):im.putpixel((x,y),c=='#')
 crow_bytes+=tiles(im,True)
emit('crow_data',crow_bytes)
raw=(A/'jupiter_bitmap_v20.bin').read_bytes();im=Image.new('1',(56,56))
for y in range(56):
 for x in range(56):im.putpixel((x,y),bool(raw[y*7+x//8]&(128>>(x%8))))
im=im.resize((32,32),Image.Resampling.NEAREST);emit('jupiter_data',tiles(im))
im=Image.new('1',(24,32));im.paste(Image.open(A/'esf_interceptor.png'),(0,0));emit('ship_native',tiles(im,True))
runpy.run_path(str(R/'tools/art04.py'),init_globals=globals())
runpy.run_path(str(R/'tools/art06.py'),init_globals=globals())
cosmos=Image.open(A/'cosmos_gb.png').convert('L')
emit('cosmos_a',gbtiles(cosmos.crop((0,0,32,32))))
emit('cosmos_b',gbtiles(cosmos.crop((32,0,64,32))))
(R/'src/assets.h').write_text('\n'.join(out)+'\n')

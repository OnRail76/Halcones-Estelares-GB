from pathlib import Path
import re
from PIL import Image
r=Path(__file__).resolve().parents[1];out=r/'documentacion/recursos';s=(r/'src/assets.h').read_text()
def data(name):
 if name+'[]' not in s and name+'_rle[]' in s:name+='_rle'
 a=list(map(int,re.search(r'const unsigned char '+name+r'\[\] = \{([^}]+)',s)[1].split(',')))
 if name.endswith('_rle'):
  o=[];i=0
  while i<len(a):
   n=a[i];i+=1;k=(n&127)+1
   if n&128:o.extend([a[i]]*k);i+=1
   else:o.extend(a[i:i+k]);i+=k
  return o
 return a
def render(name,b,w,h,column=False):
 im=Image.new('RGB',(w,h));coords=[(x,y) for x in range(0,w,8) for y in range(0,h,8)] if column else [(x,y) for y in range(0,h,8) for x in range(0,w,8)]
 for j,(x,y) in enumerate(coords):
  for yy in range(8):
   a,c=b[j*16+yy*2:j*16+yy*2+2]
   for xx in range(8):
    v=((a>>(7-xx))&1)+2*((c>>(7-xx))&1);im.putpixel((x+xx,y+yy),(v*85,)*3)
 im.resize((w*8,h*8),Image.Resampling.NEAREST).save(out/(name+'.png'))
a=data('sprite_data_rle')
for name,start in [('cazador_a',12),('cazador_b',16),('kamikaze_a',20),('kamikaze_b',24)]:render(name,a[start*16:(start+4)*16],16,16,True)
a=data('crow_data');render('crow_a',a[:32],8,16);render('crow_b',a[32:],8,16)
render('nave',data('ship_native'),24,32,True)
for name,start,w in [('laser',40,8),('plasma',42,8),('escudo',44,16)]:render(name,data('sprite_data_rle')[start*16:],w,16,True)
for i in range(3):render('explosion_'+str(i),data('ship_blast_data_rle')[i*192:(i+1)*192],24,32,True)

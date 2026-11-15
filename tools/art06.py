# Static arcade interludes: generated once, no font rendering during combat.
def metal(im,text,y,scale=2):
 width=len(text)*6*scale-scale+2
 x=(im.width-width)//2
 for c in text:
  for yy,row in enumerate(F[c]):
   skew=(6-yy)//3
   ink=3 if yy<3 else (1 if yy==3 else 2)
   for xx,v in enumerate(row):
    if v=='#':
     ImageDraw.Draw(im).rectangle((x+xx*scale+skew,y+yy*scale,x+(xx+1)*scale-1+skew,y+(yy+1)*scale-1),fill=ink)
  x+=6*scale
im=Image.new('L',(112,48));d=ImageDraw.Draw(im)
d.line((8,1,103,1),fill=1);d.line((8,46,103,46),fill=1)
metal(im,'OLEADA',6);metal(im,'SUPERADA',27)
raw=gbtiles(im);unique=[];mapping=[]
for i in range(0,len(raw),16):
 tile=raw[i:i+16]
 if tile not in unique:unique.append(tile)
 mapping.append(64+unique.index(tile))
assert len(unique)<=64,len(unique)
emit('waveclear_data',sum(unique,[]));emit('waveclear_map',mapping)
out.append('#define WAVECLEAR_COUNT '+str(len(unique)))
im.point(lambda v:v*85).save(A/'oleada_gb.png')
im=Image.new('L',(160,144));d=ImageDraw.Draw(im)
d.rectangle((4,5,155,138),outline=1)
label(im,(160-14*6+1)//2,15,'HAS DERROTADO A',3)
metal(im,'MOAI',35);metal(im,'MONOLITH',55)
d.line((24,78,135,78),fill=2)
label(im,(160-15*6+1)//2,87,'ENTRANDO EN FASE',2)
label(im,16,119,'PUNTOS',2);label(im,16,129,'VIDAS',2)
screen('victory',im)

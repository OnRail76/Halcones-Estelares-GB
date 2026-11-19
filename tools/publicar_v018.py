#!/usr/bin/env python3
"""Publica ROM GB 0.18 exacta, fuentes del plasma PTCH y documentos actuales."""
from pathlib import Path
import hashlib, json, re, shutil, zipfile, subprocess, sys
R=Path(__file__).resolve().parents[1]
V17='e263b5fa77a78e483857f3d200a35cd81f5bd2053db0172575ce12403af07e8c'
V18='a9cb44a5b985d15906857c51d6985e93173b65ff8e0f82253614fceb9a8ac393'
MESSAGE='Cañón de Plasma: nuevo sonido de disparo comprimido de la ESF-01, chasquido eléctrico seguido de soplido seco.'
def sha(data): return hashlib.sha256(data).hexdigest()
def read(p): return (R/p).read_text(encoding='utf-8')
def write(p,s):
 f=R/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s,encoding='utf-8')

# ROM autorizada por el usuario. No recompilar, no reinterpretar el sonido.
base=R/'rom/Halcones-Estelares-GB-0.17.gb'
new=R/'rom/Halcones-Estelares-GB-0.18.gb'
if not new.exists():
 data=bytearray(base.read_bytes())
 assert len(data)==32768 and sha(data)==V17, 'La ROM de partida NO es la v0.17 oficial'
 changes={
  0x014e:('8ec5','7c8d'),
  0x347b:('2140c67eb7280135','cd407f0000000000'),
  0x7f06:('38','39'),
  0x7f0e:('35','15'),
  0x7f16:('02','83'),
  0x7f40:('ff'*31,'2140c67efe8320133e39e0203e61e0213e45e0223ec0e0233603c9b7c835c9'),
 }
 for off,(old,hx) in changes.items():
  a,b=bytes.fromhex(old),bytes.fromhex(hx)
  assert len(a)==len(b) and data[off:off+len(a)]==a, f'Parche no seguro en {off:#06x}'
  data[off:off+len(a)]=b
 assert sha(data)==V18, 'ERROR: el binario NO coincide con el plasma PTCH aprobado'
 new.write_bytes(data)
assert len(new.read_bytes())==32768 and sha(new.read_bytes())==V18
print('ROM CAÑÓN DE PLASMA APROBADA: OK',V18)

# Fuente equivalente: primero un ruido crujiente, luego uno más grave en VBlank.
source=read('src/audio.h')
if 'noise_hold=0x83;fire_voice=2;' not in source:
 start=source.index('/* 0.17:',0) if '/* 0.17:' in source else source.index('/* 0.17 PFF')
 end=source.index('void audio_stop_music(void)',start)
 source=source[:start]+'''/* 0.18: CAÑON DE PLASMA ESF-01. Dos etapas en canal de ruido 4.
   Descarga inicial + soplido más grave al siguiente VBlank.
   Ninguna nota ni oscilador tonal en el disparo. */
void audio_fire_now(void){CRITICAL {
 NR12_REG=0x00; /* silenciar canal tonal anterior */
 NR41_REG=0x39;NR42_REG=0xf1;NR43_REG=0x15;NR44_REG=0xc0;
 noise_hold=0x83;fire_voice=2;
}}
'''+source[end:]
 old='if(noise_hold)noise_hold--;'
 assert source.count(old)==1
 source=source.replace(old,'''if(noise_hold==0x83){
   /* Fase 2: cola de plasma más suave y grave. */
   NR41_REG=0x39;NR42_REG=0x61;NR43_REG=0x45;NR44_REG=0xc0;
   noise_hold=3;
  }else if(noise_hold)noise_hold--;''')
 source=source.replace('/* A fresh laser is immediate; other pitched signals resume after its chirp. */','/* El disparo de plasma es inmediato; otros efectos tonales esperan su ataque. */')
 assert source.count('void audio_fire_now(void)')==1 and source.count('if(noise_hold==0x83)')==1
 write('src/audio.h',source)

# Historial preservado; la edición nueva pasa a ser la oficial.
readme=read('README.md')
readme=readme.replace('**Versión 0.17 ·','**Versión 0.18 ·')
readme=readme.replace('[**ROM oficial 0.17**](rom/Halcones-Estelares-GB-0.17.gb)','[**ROM oficial 0.18**](rom/Halcones-Estelares-GB-0.18.gb)')
readme=readme.replace('## Novedades 0.17','''## Novedades 0.18 — Cañón de Plasma definitivo

- **'''+MESSAGE+'''**
- Primero un chasquido de ruido brillante y luego un soplido más grave y apagado, sin pitido agudo.
- Se conserva **byte por byte** la ROM experimental «Plasma PTCH» aprobada por Tony C. Ware.
- Música, gráficos, patrones de oleadas, controles y jugabilidad de la v0.17 intactos.

## Novedades 0.17''',1)
readme=readme.replace('[Manual ilustrado 0.17](docs/Manual-ilustrado-GB-0.17.pdf)','[Manual ilustrado 0.18](docs/Manual-ilustrado-GB-0.18.pdf)')
readme=readme.replace('[Atlas visual y memoria 0.17](docs/Atlas-y-memoria-GB-0.17.pdf)','[Atlas visual y memoria 0.18](docs/Atlas-y-memoria-GB-0.18.pdf)')
assert V17 in readme
readme=readme.replace(V17,V18)
write('README.md',readme)
cl=read('CHANGELOG.md')
if '## v0.18' not in cl:
 cl=cl.replace('## v0.17',f'''## v0.18 · 19 noviembre 2026 — edición final Cañón de Plasma

- **{MESSAGE}**
- Dos fases solo en el canal 4 de ruido (chasquido brillante y soplido grave).
- ROM exactamente igual a la variante experimental aprobada. El resto de 0.17 se conserva.

## v0.17''',1)
 cl=cl.replace('en el atlas de las ediciones 0.16 y 0.17.','en el atlas actualizado de 0.18; 0.16 y 0.17 quedan en el historial.')
write('CHANGELOG.md',cl)
leeme=read('LEEME.md')
if '# Halcones Estelares — Game Boy 0.17' in leeme:
 leeme=leeme.replace('# Halcones Estelares — Game Boy 0.17','# Halcones Estelares — Game Boy 0.18',1)
if '## Novedades 0.18 — Cañón de Plasma' not in leeme:
 pos=leeme.index('## Novedades 0.17')
 leeme=leeme[:pos]+f'''## Novedades 0.18 — Cañón de Plasma definitivo

**{MESSAGE}**

El disparo ahora tiene dos fases de ruido pseudoaleatorio: chasquido brillante durante aproximadamente un fotograma (16,7 ms) y cola más grave y tenue de unos 27 ms. No se utiliza un tono de pulso para el disparo. El cambio se realiza con una nueva transición sincronizada con VBlank.

La ROM es idéntica a la prueba «Plasma PTCH» que escuchó y aprobó el autor (SHA-256 {V18}). Se mantienen exactamente los gráficos, las melodías y la jugabilidad de 0.17. Los WAV que ya había en audio/ son capturas históricas, no un registro del disparo 0.18.

'''+leeme[pos:]
write('LEEME.md',leeme)
write('CAMBIOS_0.18.md',f'# Halcones Estelares GB v0.18 — Versión Final: Cañón de Plasma\n\n{MESSAGE}\n\nROM exacta aprobada por Tony C. Ware; ningún cambio en gráficos, música, enemigos ni controles.\n\nSHA-256: {V18}\n')

# La maquetación se actualiza, pero los datos históricos de versiones previas se conservan.
doc='tools/build_documents.py'
s=read(doc)
s=s.replace('release 0.17 (historical','release 0.18 (historical')
s=s.replace('GB 0.17','GB 0.18')
s=s.replace('GAME BOY 0.17','GAME BOY 0.18')
s=s.replace('0.17.pdf','0.18.pdf')
s=s.replace('Versión publicada 0.17','Versión publicada 0.18')
s=s.replace('Composición vigente en la versión 0.17','Composición vigente en la versión 0.18')
s=s.replace("d.h('Sonido de la 0.17')","d.h('Sonido de la 0.18')")
s=s.replace('El disparo ESF-01 ahora suena como un «pff» seco de ruido de 31 ms (canal 4), próximo al carácter del beeper ZX; los demás efectos se conservan.','El Cañón de Plasma de la ESF-01 suena «ptch»: chasquido eléctrico y cola grave de ruido, sin pitido tonal.')
s=s.replace('Documentación 02 · 16 de noviembre de 2026 · Juego GB 0.18','Documentación 03 · 19 de noviembre de 2026 · Juego GB 0.18')
s=s.replace('Este atlas documenta la edición 0.17:','Este atlas documenta la edición 0.18:')
s=s.replace('Estas reglas se mantienen en la 0.17.','Estas reglas se mantienen en la 0.18.')
s=s.replace('un breve ruido tipo «pff» como homenaje al beeper original.','un breve ruido tipo «pff» como homenaje al beeper original. En la 0.18 el nuevo Cañón de Plasma añade un chasquido brillante y una cola grave de ruido, sin alterar el juego.')
s=s.replace('Uso en la edición 0.17','Uso en la edición 0.18')
s=s.replace('El disparo de 0.17 utiliza solo ruido (canal 4), sin tono.','El Cañón de Plasma de 0.18 utiliza dos fases de ruido (canal 4) sin tono.')
s=s.replace('Pruebas heredadas de 0.16; disparo nuevo aprobado en 0.17','Pruebas heredadas de 0.16; Cañón de Plasma aprobado en 0.18')
s=s.replace('El nuevo disparo de 0.17 fue aprobado tras escucharlo el autor.','El Cañón de Plasma de 0.18 fue aprobado tras escucharlo el autor.')
s=s.replace('SHA-256 de la ROM 0.17:','SHA-256 de la ROM 0.18:')
s=s.replace('Edición 02 · 16/11/2026','Edición 03 · 19/11/2026')
s=s.replace("R/'rom/Halcones-Estelares-GB-0.17.gb'","R/'rom/Halcones-Estelares-GB-0.18.gb'")
assert 'Manual-ilustrado-GB-0.18.pdf' in s and 'Atlas-y-memoria-GB-0.18.pdf' in s
assert "R/'rom/Halcones-Estelares-GB-0.18.gb'" in s
write(doc,s)

for p in ['docs/Manual-ilustrado-GB-0.17.pdf','docs/Atlas-y-memoria-GB-0.17.pdf']:
 (R/p).unlink(missing_ok=True)
(R/'docs').mkdir(parents=True,exist_ok=True)
subprocess.run([sys.executable,doc],check=True,cwd=R)

# Solo una edición vigente en main; v0.17 queda disponible a través de su tag/release.
base.unlink(missing_ok=True)
assets=['rom/Halcones-Estelares-GB-0.18.gb','docs/Manual-ilustrado-GB-0.18.pdf','docs/Atlas-y-memoria-GB-0.18.pdf','portada/Halcones_Estelares_GB_Caratula_Oficial.png']
assert all((R/x).is_file() for x in assets)
write('SHA256SUMS.txt',''.join(f'{sha((R/x).read_bytes())}  {x}\n' for x in assets))
write('SHA256.txt',f'{V18}  Halcones-Estelares-GB-0.18.gb\n')
write('documentacion/VERIFICACION.json',json.dumps({'version':'0.18','rom_sha256':V18,'manual_sha256':sha((R/assets[1]).read_bytes()),'atlas_sha256':sha((R/assets[2]).read_bytes())},indent=2,ensure_ascii=False)+'\n')
write('VERIFICACION_PLASMA_0.18.json',json.dumps({'version':'0.18','rom_sha256':V18,'rom_original_0_17_sha256':V17,'disparo':'Cañón de Plasma PTCH','canal':'4 - ruido','fases':['chasquido eléctrico, aproximadamente un VBlank','soplido grave, aproximadamente 27 ms'],'aprobado_por_el_autor':True,'rom_identica_a_experimento':True,'otras_mecanicas_conservadas':True},indent=2,ensure_ascii=False)+'\n')

# Paquete integral para publicación.
dist=R/'dist';dist.mkdir(exist_ok=True)
for x in assets:shutil.copy2(R/x,dist/Path(x).name)
with zipfile.ZipFile(dist/'Halcones-Estelares-GameBoy-0.18.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 includes=['src','tools','assets','capturas','audio','documentacion','docs','rom','portada']
 for folder in includes:
  for file in sorted((R/folder).rglob('*')):
   if not file.is_file() or any(x in file.parts for x in ('__pycache__','.pytest_cache')) or file.suffix in ('.pyc','.pyo'):continue
   z.write(file,'Halcones-GameBoy/'+str(file.relative_to(R)))
 for file in sorted(R.iterdir()):
  if file.is_file() and file.suffix in ('.md','.txt','.json') or file.is_file() and file.name in ('Makefile','LICENSE'):
   z.write(file,'Halcones-GameBoy/'+file.name)
with zipfile.ZipFile(dist/'Halcones-Estelares-GameBoy-0.18.zip') as z:
 assert z.testzip() is None
 assert any(x.endswith('/rom/Halcones-Estelares-GB-0.18.gb') for x in z.namelist())
write('SHA256_RELEASE_v0.18.txt',''.join(f'{sha(f.read_bytes())}  {f.name}\n' for f in sorted(dist.iterdir()) if f.is_file()))
shutil.copy2(R/'SHA256_RELEASE_v0.18.txt',dist/'SHA256_RELEASE_v0.18.txt')
for f in sorted(dist.iterdir()):print('ASSET',f.name,f.stat().st_size,sha(f.read_bytes()))
print('PUBLICACION v0.18 LISTA')

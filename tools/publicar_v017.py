#!/usr/bin/env python3
"""Publicación reproducible GB 0.17: ROM exacta aprobada y documentos actuales."""
from pathlib import Path
import hashlib, json, shutil, zipfile, subprocess, sys

R=Path(__file__).resolve().parents[1]
CHANGE="Cambios: Sonido del disparo del ESF-01 mas adecuado a su origen en ZX Spectrum"
OLD="2156d5293d321d1579201830a97c0dc544ad911d703237c109e8d149ff4eaefa"
NEW="e263b5fa77a78e483857f3d200a35cd81f5bd2053db0172575ce12403af07e8c"
def sha(x): return hashlib.sha256(x).hexdigest()
def read(p): return (R/p).read_text(encoding="utf-8")
def write(p,s):
    f=R/p
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(s,encoding="utf-8")
def edit(p,subs):
    s=read(p)
    for old,new in subs:
        if old in s: s=s.replace(old,new)
        elif new not in s: raise RuntimeError(f"No se encuentra texto en {p}: {old[:90]}")
    write(p,s)

# La ROM nunca se recompila: se aplican exactamente los 57 bytes aprobados.
before=R/"rom/Halcones-Estelares-GB-0.16.gb"
after=R/"rom/Halcones-Estelares-GB-0.17.gb"
if not after.exists():
    data=bytearray(before.read_bytes())
    assert len(data)==32768 and sha(data)==OLD,"ROM base incorrecta"
    for offset,hx in [
        (0x014e,"8ec5"),
        (0x317e,"c3007f"),
        (0x36c0,"cd7e31c3a63700000000000000000000000000"),
        (0x7f00,"f33e00e0123e38e0203ef1e0213e35e0223ec0e0233e02ea40c63e02ea3cc6fbc9"),
    ]:
        part=bytes.fromhex(hx);data[offset:offset+len(part)]=part
    assert sha(data)==NEW,"No coincide la ROM aprobada"
    after.write_bytes(data)
assert sha(after.read_bytes())==NEW

newfire="""/* 0.17: disparo ESF-01, solo ruido canal 4, 31,25 ms.
   Sin pulso, sin nota y sin barrido tonal. */
void audio_fire_now(void){CRITICAL {
 NR12_REG=0x00;
 NR41_REG=0x38;
 NR42_REG=0xf1;
 NR43_REG=0x35;
 NR44_REG=0xc0;
 noise_hold=2;fire_voice=2;
}}"""
edit("src/audio.h",[
    ("void audio_fire_now(void){CRITICAL {audio_pulse(1946,0x82,54);NR10_REG=0x1d;fire_voice=4;}}",newfire),
    ("case FX_SHOT:audio_pulse(1946,0x82,54);NR10_REG=0x1d;break;","case FX_SHOT:audio_fire_now();break;")
])

# Actualizar el generador documental previo, conservando su contenido histórico.
edit("tools/build_documents.py",[
    ("' — GB 0.16'","' — GB 0.17'"),
    ("' · GB 0.16'","' · GB 0.17'"),
    ("GAME BOY 0.16 · EDICIÓN DOCUMENTAL 01","GAME BOY 0.17 · EDICIÓN DOCUMENTAL 01"),
    ("Manual-ilustrado-GB-0.16.pdf","Manual-ilustrado-GB-0.17.pdf"),
    ("Atlas-y-memoria-GB-0.16.pdf","Atlas-y-memoria-GB-0.17.pdf"),
    ("Versión publicada 0.16","Versión publicada 0.17"),
    ("Composición de la versión 0.16","Composición vigente en la versión 0.17"),
    ("d.h('Sonido de la 0.16')","d.h('Sonido de la 0.17')"),
    ("Disparo, escudo y explosiones usan los canales de sonido de Game Boy.","El disparo ESF-01 ahora suena como un «pff» seco de ruido de 31 ms (canal 4), próximo al carácter del beeper ZX; los demás efectos se conservan."),
    ("Documentación 01 · 15 de noviembre de 2026 · Juego GB 0.16","Documentación 02 · 16 de noviembre de 2026 · Juego GB 0.17"),
    ("Este atlas documenta la edición publicada 0.16:","Este atlas documenta la edición 0.17:"),
    ("Estas reglas se mantienen en la 0.16.","Estas reglas se mantienen en la 0.17."),
    ("Se conservan los siete patrones y las composiciones de la 0.15.","Se conservan los siete patrones y las composiciones de la 0.15. En la 0.17 cambia únicamente el sonido de disparo: un breve ruido tipo «pff» como homenaje al beeper original."),
    ("Uso en la edición 0.16","Uso en la edición 0.17"),
    ("Canal de pulso 1: efectos y melodía de título. Pulso 2 y onda: acompañamiento y música. Ruido: percusión y explosiones, con prioridad para efectos.","El disparo de 0.17 utiliza solo ruido (canal 4), sin tono. Pulso 1: otros efectos y melodía de título. Pulso 2 y onda: música. El ruido se comparte con la percusión y las explosiones."),
    ("Pruebas de la ROM publicada, no de un prototipo posterior","Pruebas heredadas de 0.16; disparo nuevo aprobado en 0.17"),
    ("Resultado de la 0.16","Resultado validado en la 0.16"),
    ("Pendientes: contraste y experiencia sonora en consola física, y observación prolongada en distintos emuladores.","El nuevo disparo de 0.17 fue aprobado tras escucharlo el autor. Pendientes: consola física y observación prolongada en distintos emuladores."),
    ("<b>Capturas:</b> carpeta capturas/ de la versión 0.16.","<b>Capturas:</b> carpeta capturas/ conservada de la versión 0.16."),
    ("SHA-256 de la ROM 0.16:","SHA-256 de la ROM 0.17:"),
    ("Edición 01 · 15/11/2026","Edición 02 · 16/11/2026"),
    ("R/'Halcones-Estelares-GB.gb'","R/'rom/Halcones-Estelares-GB-0.17.gb'"),
])
if not (R/"docs/Manual-ilustrado-GB-0.17.pdf").exists():
    subprocess.run([sys.executable,"tools/build_documents.py"],cwd=R,check=True)
    for name in ("Manual-ilustrado-GB-0.17.pdf","Atlas-y-memoria-GB-0.17.pdf"):
        if not (R/"docs"/name).exists():
            shutil.copy2(R/"documentacion"/name,R/"docs"/name)

# Referencias de la edición principal.
edit("README.md",[
    ("**Versión 0.16 ·","**Versión 0.17 ·"),
    ("[**ROM oficial 0.16**](rom/Halcones-Estelares-GB-0.16.gb)","[**ROM oficial 0.17**](rom/Halcones-Estelares-GB-0.17.gb)"),
    ("## Novedades 0.15–0.16","## Novedades 0.17\n\n- **"+CHANGE+"**\n- Efecto de disparo «pff» corto, seco y sin pitido; canal 4 de ruido de Game Boy. El resto de la 0.16 se conserva.\n\n## Novedades 0.15–0.16"),
    ("[Manual ilustrado 0.16](docs/Manual-ilustrado-GB-0.16.pdf)","[Manual ilustrado 0.17](docs/Manual-ilustrado-GB-0.17.pdf)"),
    ("[Atlas visual y memoria 0.16](docs/Atlas-y-memoria-GB-0.16.pdf)","[Atlas visual y memoria 0.17](docs/Atlas-y-memoria-GB-0.17.pdf)"),
    (OLD,NEW)
])
edit("CHANGELOG.md",[
    ("## v0.16 · 15 noviembre 2026","## v0.17 · 16 noviembre 2026\n\n- **"+CHANGE+"**\n- Disparo «pff» de ruido seco, sin pitido tonal. ROM exacta aprobada por el autor.\n- Gráficos, músicas y mecánicas sin cambios.\n\n## v0.16 · 15 noviembre 2026"),
    ("en el atlas de la edición 0.16.","en el atlas de las ediciones 0.16 y 0.17.")
])
edit("LEEME.md",[
    ("# Halcones Estelares — Game Boy 0.16","# Halcones Estelares — Game Boy 0.17"),
    ("Los efectos dejan de imitar el beeper: usan timbres nativos GB, breves y pulidos.","El disparo de 0.17 recupera el carácter del beeper: «pff» seco en canal de ruido 4. Los demás efectos conservan sus timbres nativos de Game Boy."),
    ("Disparo con caída de tono, impactos cortos, explosión de ruido escalonada y","Impactos cortos, explosión de ruido escalonada y"),
    ("con sonido inmediato en el canal de efectos tonales.","con sonido inmediato de ruido en el canal 4."),
])
s=read("LEEME.md")
if "## Novedades 0.17 — disparo ESF-01" not in s:
    insert="\n## Novedades 0.17 — disparo ESF-01\n\n**"+CHANGE+"**\n\nAhora la ESF-01 produce un «pff» breve de ruido (canal 4, 31 ms), en homenaje al beeper ZX Spectrum. El autor escuchó y aprobó la ROM de prueba, publicada sin cambiar ningún byte de su código máquina. No se alteran melodías, gráficos ni mecánicas. Los WAV incluidos son capturas históricas de la 0.16, no del nuevo disparo.\n"
    s=s.replace("\n## Novedades 0.16",insert+"\n## Novedades 0.16",1)
    write("LEEME.md",s)
write("CAMBIOS_0.17.md","# Halcones Estelares GB — versión 0.17\n\n**"+CHANGE+"**\n\nDisparo «pff» de ruido seco (canal 4 de Game Boy), sin pitido tonal. La ROM es idéntica a la prueba aprobada por Tony C. Ware; los demás aspectos del juego se conservan.\n")
write("SHA256.txt",NEW+"  Halcones-Estelares-GB-0.17.gb\n")
for p in ["rom/Halcones-Estelares-GB-0.16.gb","docs/Manual-ilustrado-GB-0.16.pdf","docs/Atlas-y-memoria-GB-0.16.pdf"]:
    (R/p).unlink(missing_ok=True)
assets=[
    "rom/Halcones-Estelares-GB-0.17.gb",
    "docs/Manual-ilustrado-GB-0.17.pdf",
    "docs/Atlas-y-memoria-GB-0.17.pdf",
    "portada/Halcones_Estelares_GB_Caratula_Oficial.png",
]
write("SHA256SUMS.txt","".join(sha((R/p).read_bytes())+"  "+p+"\n" for p in assets))
write("VERIFICACION_PFF_RUIDO.json",json.dumps({"version":"0.17","rom_sha256":NEW,"canal":"ruido 4","duracion_ms":31.25,"cambio":CHANGE,"aprobado_por_autor":True},ensure_ascii=False,indent=2)+"\n")
write("documentacion/VERIFICACION.json",json.dumps({"version":"0.17","rom_sha256":NEW,"manual_sha256":sha((R/assets[1]).read_bytes()),"atlas_sha256":sha((R/assets[2]).read_bytes())},ensure_ascii=False,indent=2)+"\n")

# Assets y ZIP de fuentes/documentación para la Release.
dist=R/"dist";dist.mkdir(exist_ok=True)
for p in assets: shutil.copy2(R/p,dist/Path(p).name)
with zipfile.ZipFile(dist/"Halcones-Estelares-GameBoy-0.17.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for folder in ("assets","audio","capturas","documentacion/recursos","src","tools"):
        for f in sorted((R/folder).rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts and f.suffix not in (".pyc",".pyo"):
                z.write(f,arcname="Halcones-GameBoy/"+str(f.relative_to(R)))
    for p in ["ANIMACION_NAVE.json","BUCLES_Y_MUSICA.json","FONDOS.json","MUSICA_TITULO.json","PATRONES_Y_TRANSICIONES.json","PRUEBAS.json","PRUEBAS.txt","REAGRUPACION_Y_MOAI.json","REFERENCIA.json","RESPUESTA_Y_REAPARICION.json","VARIEDAD_OLEADAS.json","README.md","LEEME.md","HISTORIA.md","BANDA_SONORA.md","LICENSE","LICENSE_ES.md","LICENSE_PORT.txt","LICENCIA_GRAFICOS.md","Makefile","CAMBIOS_0.17.md","CHANGELOG.md","SHA256.txt","SHA256SUMS.txt",*assets]:
        if (R/p).exists():z.write(R/p,arcname="Halcones-GameBoy/"+p)
for f in sorted(dist.iterdir()):
    if f.is_file():print(f.name,f.stat().st_size,sha(f.read_bytes()))
print("ROM 0.17 EXACTA, PROYECTO Y DOCUMENTOS LISTOS")

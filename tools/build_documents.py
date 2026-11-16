"""Build illustrated A5 PDFs from project assets and verified release 0.16."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image
import hashlib,json
R=Path(__file__).resolve().parents[1];D=R/'docs';A=R/'assets';C=R/'capturas';G=R/'documentacion'/'recursos'
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
W,H=419.528,595.276;M=30;CW=W-2*M
INK='#14232a';ACC='#175c77';PAPER='#f5f3e9'
class Doc:
 def __init__(self,name,label):
  self.c=canvas.Canvas(str(D/name),pagesize=(W,H));self.c.setTitle('Halcones Estelares — '+label+' — GB 0.17');self.c.setAuthor('Tony C. Ware · documentación con asistencia de OpenAI Codex');self.label=label;self.n=0
 def cover(self):
  self.n+=1;c=self.c;c.setFillColor(HexColor('#081b48'));c.rect(0,0,W,H,fill=1,stroke=0)
  im=Image.open(G/'portada.png');scale=min(W/im.width,(H-30)/im.height);w,h=im.width*scale,im.height*scale
  c.drawImage(str(G/'portada.png'),(W-w)/2,30+(H-30-h)/2,w,h)
  c.setFillColor(HexColor('#ffffff'));c.setFont('Bold',10);c.drawCentredString(W/2,12,self.label.upper()+' · GB 0.17');c.showPage()
 def page(self,title,sub=''):
  self.n+=1;c=self.c;c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor(ACC));c.rect(M,H-28,24,3,fill=1,stroke=0)
  c.setFont('Bold',7);c.drawString(M+32,H-28,'HALCONES ESTELARES / '+self.label.upper());c.setFillColor(HexColor(INK));c.setFont('Bold',20);c.drawString(M,H-65,title)
  self.y=H-80
  if sub:self.p(sub,9,12,color=ACC)
  c.setStrokeColor(HexColor('#c4ccc9'));c.line(M,29,W-M,29);c.setFillColor(HexColor(ACC));c.setFont('Body',7);c.drawString(M,17,'GAME BOY 0.17 · EDICIÓN DOCUMENTAL 01');c.drawRightString(W-M,17,f'{self.n:02}')
 def p(self,text,size=9.4,leading=14,color=INK):
  st=ParagraphStyle('p',fontName='Body',fontSize=size,leading=leading,textColor=HexColor(color));p=Paragraph(text,st);w,h=p.wrap(CW,1000);assert self.y-h>40,(self.label,self.n,self.y,h,text[:35]);p.drawOn(self.c,M,self.y-h);self.y-=h+10
 def h(self,text):self.p(text,11,15,ACC)
 def images(self,items,height=160):
  # Pixel resources enlarged with nearest neighbour for crisp PDF rendering.
  gap=12;cell=(CW-gap*(len(items)-1))/len(items);top=self.y
  for i,(path,caption) in enumerate(items):
   im=Image.open(path).convert('RGB');scale=min(cell/im.width,height/im.height);w,h=im.width*scale,im.height*scale
   if im.width<320:im=im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST)
   x=M+i*(cell+gap)+(cell-w)/2;self.c.drawImage(ImageReader(im),x,top-h,w,h)
   st=ParagraphStyle('cap',fontName='Body',fontSize=7.2,leading=10,textColor=HexColor(ACC));p=Paragraph(caption,st);pw,ph=p.wrap(cell,100);p.drawOn(self.c,M+i*(cell+gap),top-height-8-ph)
  self.y=top-height-42;assert self.y>40,(self.label,self.n,'images')
 def table(self,rows,widths=None):
  st=ParagraphStyle('cell',fontName='Body',fontSize=8.3,leading=12,textColor=HexColor(INK));cells=[[Paragraph(str(v),st) for v in row] for row in rows];t=Table(cells,colWidths=widths or [CW/len(rows[0])]*len(rows[0]));t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#d9e4e3')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,-1),.4,HexColor('#c4ccc9'))]));w,h=t.wrap(CW,1000);assert self.y-h>40,(self.label,self.n,'table',h);t.drawOn(self.c,M,self.y-h);self.y-=h+12
 def end(self):self.c.showPage()
 def save(self):self.c.save()

def manual():
 d=Doc('Manual-ilustrado-GB-0.17.pdf','Manual de instrucciones');d.cover()
 d.page('Tu misión','Guía de juego · Versión publicada 0.17')
 d.images([(C/'titulo.png','Pantalla de título real de la versión Game Boy.')],120)
 d.p('Pilota el interceptor ESF, supera seis oleadas de aves mecánicas y derrota a MOAI MONOLITH. Después del jefe comienza una nueva fase con mayor presión enemiga. Las partidas continúan por ciclos.')
 d.table([['Contenido','Página'],['Controles y primera partida','3'],['Marcador y supervivencia','4'],['Familias y oleadas','5'],['Cómo atacan','6'],['MOAI MONOLITH','7'],['Victoria, derrota y consejos','8'],['Uso, créditos y edición','9']],[CW-65,65]);d.end()
 d.page('A los mandos','Responde al ataque. Reserva el escudo para el peligro.')
 d.table([['Control','Acción'],['Izquierda / derecha','Desplazar la nave horizontalmente.'],['A','Disparar. Mantener para fuego continuo.'],['B','Activar el escudo cuando está LISTO.'],['START','Comenzar desde el título; pausar o reanudar la partida.']],[105,CW-105])
 d.images([(C/'combate.png','Combate.'),(C/'escudo.png','Medio arco de protección sobre la nave.')],130)
 d.p('Puedes mantener un máximo de dos láseres. Una nueva pulsación sustituye al más adelantado si ambos siguen en pantalla, para que el botón responda. El fuego mantenido repite aproximadamente cada seis fotogramas.')
 d.p('El escudo dura unos <b>tres segundos</b> y necesita <b>seis segundos</b> de recarga. Mientras está activo no salen nuevos disparos. Si mantienes A, el fuego vuelve al terminar la protección.');d.end()
 d.page('Lee el marcador','Toda la información permanece a la derecha del combate.')
 d.images([(C/'combate.png','Captura de la partida: campo de 112 × 144 y marcador lateral.')],150)
 d.table([['Indicador','Qué significa'],['PUNTOS / REC','Puntuación actual y récord de esta sesión.'],['VIDAS','Caritas que representan las vidas restantes.'],['ESCUDO','Barra y estado: LISTO, ACTIVO o CARGANDO.'],['FASE','Ciclo actual; aumenta tras derrotar al MOAI.'],['OLEADA','Tramo actual del ciclo, de 1 a 7.']],[105,CW-105])
 d.p('Empiezas con tres vidas. Cada enemigo eliminado o impacto al MOAI suma 10 puntos. Cada 100 impactos puntuables recibes una vida si tienes menos de tres. El máximo de puntuación es 99.990. No hay guardado del récord al apagar.',8.8,13);d.end()
 d.page('Las siete oleadas','Composición vigente en la versión 0.17')
 d.images([(G/'crow_a.png','CROW · figura de 8 × 8.'),(G/'cazador_a.png','Cazador · 16 × 16.'),(G/'kamikaze_a.png','Kamikaze / halcón · 16 × 16.')],100)
 d.table([['Oleadas','Enemigos'],['1 y 2','Diez CROW por formación.'],['3 y 4','6 cazadores; 4 + 2 CROW; o 2 + 4 CROW.'],['5 y 6','6 kamikazes; 4 + 2 CROW; o 2 + 4 CROW.'],['1 a 6: opción especial','Diez CROW rápidos en formación tipo Space Invaders.'],['7','MOAI MONOLITH; puede mantener seis CROW y reponer bajas.']],[90,CW-90])
 d.p('Los seis patrones clásicos se combinan con estas formaciones. La séptima opción es una invasión solo de CROW que puede aparecer o no desde la primera fase. Las elecciones pueden repetirse.')
 d.p('Destruir un enemigo grande sin CROW activos ni pendientes provoca una tanda de 1 a 4 CROW. Entran por turnos, tras una breve espera; hay un máximo de cuatro refuerzos por oleada. El MOAI conserva su invocación propia.');d.end()
 d.page('Aprende sus movimientos','Siete coreografías propias inspiradas en los arcades clásicos')
 d.table([['Patrón','Lo que debes observar'],['Picados curvos · Galaxian','Hasta dos atacantes salen de la formación y regresan por los flancos.'],['Parejas · Galaga','Entradas escalonadas y trayectorias en S. La segunda ave llega después.'],['Amago · Moon Cresta','Salidas por columnas; pausa y segunda acometida con nuevo objetivo.'],['Suspensión · Phoenix','Formación dispersa, oscilación vertical, pausa y caída con disparo.'],['Escoltas · Galaga','Un líder y dos acompañantes despegan separados hacia objetivos distintos.'],['Carrusel · Moon Cresta / Phoenix','Zigzag, elección tardía de objetivo y ataques continuos.'],['Invasión · Space Invaders','Diez CROW marchan y descienden. Aceleran al quedar cuatro; al llegar abajo suben, se reagrupan y repiten.']],[125,CW-125])
 d.p('Son patrones adaptados al campo de Game Boy, no reproducciones literales de esos juegos. Los últimos tres enemigos reducen sus pausas. No des por terminada una oleada porque queden pocos.')
 d.images([(C/'crow_invaders.png','Invasión CROW: captura real con protección de prueba.')],65);d.end()
 d.page('MOAI MONOLITH','Observa los ojos. No todos los ataques tienen el mismo ritmo.')
 d.images([(C/'moai_ojos.png','Los ojos avisan del ataque.'),(C/'moai_boca.png','La boca cambia durante la descarga.')],110)
 d.table([['Ataque','Respuesta útil'],['Ráfaga','Tres disparos alternando ojos. Evita quedarte alineado.'],['Apuntado','Dos disparos dirigidos a la posición fijada al preparar el ataque. Desplázate después del aviso.'],['Abanico','Tres proyectiles se abren desde el rostro. Busca el espacio entre ellos.'],['Invocación','Hasta seis CROW entran por los lados. Repone las bajas en nuevas invocaciones hasta morir.']],[90,CW-90])
 d.p('Los cuatro ataques se barajan por grupos. El jefe comienza con <b>48 impactos</b> de resistencia y añade ocho por fase, hasta 128. Las grietas aparecen al quedar el 75 %, 50 % y 25 % de vida. Se mantienen tres proyectiles enemigos como máximo.',9,13);d.end()
 d.page('Vuelve al combate','Explosión, reaparición y nuevo ciclo')
 d.images([(C/'victoria_moai.png','Victoria sobre MOAI MONOLITH.'),(C/'gameover.png','Fin de la partida.')],130)
 d.h('Si pierdes una vida')
 d.p('La nave explota y reaparece centrada con aproximadamente dos segundos de invulnerabilidad. Parpadea mientras dura la protección y ya puedes moverte y disparar. Aprovecha ese margen para separarte de la siguiente trayectoria enemiga.')
 d.h('Si derrotas al MOAI')
 d.p('El rostro se rompe por bloques. Tras el mensaje de victoria comienza la fase siguiente, conservando puntos, vidas y recarga. Aumenta la frecuencia de disparo; los proyectiles también ganan velocidad en las fases 3 y 7.')
 d.h('Tres hábitos útiles')
 d.p('Mantén A para concentrarte en las trayectorias. Mueve la nave después de los avisos de disparo dirigido. Activa el escudo para salir de una zona cerrada, recordando que durante su uso no puedes disparar.');d.end()
 d.page('Tu edición de Game Boy','Instalación, música y créditos')
 d.p('Abre <b>Halcones-Estelares-GB.gb</b> en un emulador compatible con Game Boy clásica. Para jugar en consola necesitas un cartucho flash compatible y su procedimiento de copia. La ROM ocupa 32 KiB y no usa SRAM ni controlador de bancos.')
 d.h('Sonido de la 0.17')
 d.p('Eurodance noventero en el título; tecno oscuro 1 durante toda la partida; tonadilla breve al llegar a Game Over. El tema de combate 2 se retiró. El disparo ESF-01 ahora suena como un «pff» seco de ruido de 31 ms (canal 4), próximo al carácter del beeper ZX; los demás efectos se conservan.')
 d.images([(A/'title_gb.png','Recurso real del título convertido a cuatro tonos.')],130)
 d.p('Juego original y recursos originales: <b>Tony C. Ware</b>. Basado en Halcones Estelares ZX 1.3.3. Adaptación y documentación con asistencia de OpenAI Codex. Portada aportada por el usuario e incorporada sin redibujar.')
 d.p('Las ilustraciones interiores proceden de los recursos y capturas del proyecto. Algunas capturas del jefe utilizan escenarios preparados en el emulador. Pruebas en PyBoy DMG; la comprobación en consola física sigue pendiente. Consulta las licencias incluidas con el proyecto.',8.3,12)
 d.p('Documentación 02 · 16 de noviembre de 2026 · Juego GB 0.17',8,11);d.end();d.save()

def atlas():
 d=Doc('Atlas-y-memoria-GB-0.17.pdf','Atlas visual y memoria');d.cover()
 d.page('Archivo de una adaptación','Del ZX Spectrum 1.3.3 a Game Boy 0.16')
 d.p('Este atlas documenta la edición 0.17: sus recursos visuales, la adaptación al hardware DMG y las decisiones tomadas durante el proyecto. No describe como terminadas las funciones propuestas para versiones futuras.')
 d.images([(C/'titulo.png','Título real.'),(C/'combate.png','Combate real con fondo cósmico.')],100)
 d.table([['Sección','Página'],['Identidad y pantalla','3'],['Interceptor, escudo y explosión','4'],['Bestiario y formaciones','5'],['MOAI: relieve y fractura','6'],['Escenarios y transiciones','7'],['Memoria del desarrollo','8–9'],['Arquitectura y sonido','10'],['Verificación y continuidad','11'],['Procedencia y reproducibilidad','12']],[CW-65,65]);d.end()
 d.page('Identidad y lectura','Redibujar para 160 × 144 píxeles')
 d.images([(A/'title_gb.png','Título: robot alado, rótulo y llamada a START.'),(A/'gameover_gb.png','Recurso base de Game Over; los números se añaden en ejecución.')],130)
 d.p('El título conserva el rótulo del proyecto y adapta el robot aportado por el usuario a 144 × 68 píxeles. EUROPEAN SPACE FORCE queda centrado. Los destellos cambian tonos intermedios de la paleta para dar iluminación de arcade.')
 d.images([(A/'sidebar_gb.png','Plantilla del marcador sin valores dinámicos.'),(C/'combate.png','La plantilla en uso: puntos, caritas, barra y fase.')],135)
 d.p('La ventana de hardware reserva 48 píxeles al marcador. Se retiraron el emblema ESF y la estrella para ganar separación y legibilidad. El campo restante mide 112 × 144.',8.6,12);d.end()
 d.page('El interceptor','Recursos decodificados de los datos usados por la ROM')
 d.images([(G/'nave.png','Nave · 24 × 24 visibles en lienzo 24 × 32.'),(G/'escudo.png','Escudo · medio arco.'),(G/'laser.png','Láser.'),(G/'plasma.png','Proyectil enemigo.')],105)
 d.p('La nave se compone de seis sprites de 8 × 16. Su movimiento inclina las alas un píxel de forma opuesta; al detenerse vuelve a la posición neutra. La geometría de colisión no cambia con la inclinación.')
 d.images([(G/'explosion_0.png','Explosión / fase 1.'),(G/'explosion_1.png','Explosión / fase 2.'),(G/'explosion_2.png','Explosión / fase 3.')],105)
 d.p('La muerte dura 36 VBlank: tres fases de explosión, reaparición centrada y protección de 120 VBlank aproximadamente. El parpadeo permite leer la invulnerabilidad sin bloquear el control.')
 d.p('Los lienzos de 8 × 16 y 24 × 32 incluyen padding por el formato de sprites. Las ampliaciones son de píxel entero, sin suavizado ni redibujo.',8.6,12);d.end()
 d.page('Bestiario','Dos cuadros de animación por familia')
 d.images([(G/'crow_a.png','CROW / A.'),(G/'crow_b.png','CROW / B.'),(G/'cazador_a.png','Cazador / A.'),(G/'cazador_b.png','Cazador / B.')],80)
 d.images([(G/'kamikaze_a.png','Kamikaze / A.'),(G/'kamikaze_b.png','Kamikaze / B.')],85)
 d.p('El CROW ocupa 8 × 8 píxeles visibles dentro de un sprite 8 × 16. Cazadores y kamikazes ocupan 16 × 16 y usan dos sprites de hardware. Se conservan las siluetas del proyecto al asignar coreografías nuevas.')
 d.table([['Tramo del ciclo','Composición publicada'],['Oleadas 1–2','10 CROW'],['Oleadas 3–4','6 cazadores; 4 + 2 CROW; o 2 + 4 CROW'],['Oleadas 5–6','6 kamikazes; 4 + 2 CROW; o 2 + 4 CROW'],['Opción especial 1–6','10 CROW en invasión rápida'],['Oleada 7','MOAI y hasta 6 CROW, con reposición']],[155,CW-155]);d.end()
 d.page('El rostro se rompe','MOAI: de la máscara ZX a una figura de 40 × 72')
 d.images([(A/'moai_damage_0.png','Íntegro.'),(A/'moai_damage_1.png','Primera grieta.'),(A/'moai_damage_2.png','Segunda grieta.'),(A/'moai_damage_3.png','Tercera grieta.')],130)
 d.p('La conversión parte de la máscara 48 × 88 utilizada por el original 1.3.3. Relieve claro, cuencas oscuras y fisuras acumuladas distinguen las etapas sin añadir colores. Las grietas siguen recorridos adaptados del original con una semilla fija reproducible.')
 d.images([(C/'moai_ojos.png','Ojos luminosos antes de atacar.'),(C/'moai_derrumbe.png','Disolución por bloques tras el último impacto.')],120)
 d.p('El retrato ocupa 45 tiles. Su final combina destellos y borrado en orden salteado. Ojos y boca se actualizan mediante máscaras de bits; los cambios ordinarios se reparten por filas para contener el coste gráfico.',8.8,13);d.end()
 d.page('Espacio y continuidad','Fondos estáticos y lectura del combate')
 d.images([(C/'combinacion_1.png','Formación mixta sobre el fondo cósmico.'),(C/'crow_invaders.png','CROW rápidos: desplazamiento colectivo y descenso.')],130)
 d.p('La 0.14 añadió arte cósmico tenue a las oleadas normales. Las nubes usan gris oscuro; las estrellas, gris medio; proyectiles y enemigos conservan el blanco más brillante. El centro y la zona de la nave quedan mayoritariamente negros.')
 d.images([(C/'oleada_superada.png','Rótulo de transición dentro del campo.'),(C/'victoria_moai.png','Interludio centrado antes del siguiente ciclo.')],120)
 d.p('No hay scroll ni animación del fondo cósmico. El mapa conservado en RAM restaura lo que tapa el rótulo. Entre oleadas normales se mantiene el LCD encendido, la música y el control. El jefe dispone de su propia entrada progresiva por filas.',8.8,13);d.end()
 d.page('Memoria / primera etapa','Fidelidad visual, legibilidad y respuesta')
 d.h('Referencia: ZX Spectrum 1.3.3')
 d.p('La referencia se fijó en el TAP adjuntado por el usuario. El archivo reconstruido desde los fuentes coincide byte por byte. El objetivo es una adaptación nativa: Game Boy ejecuta código propio, no emula el Z80 del Spectrum.')
 d.h('Construir una pantalla legible')
 d.p('El marcador pasó a un lateral y conservó información, cifras y caritas del original. Los gráficos se redimensionaron para cuatro tonos. La figura del MOAI recibió relieve, ojos más visibles, grietas acumulativas y una destrucción por bloques que precede al cambio de fase.')
 d.h('Corregir la respuesta')
 d.p('Las primeras iteraciones expusieron retrasos al disparar. Se separó la actualización frecuente de nave y láser de la lógica enemiga; se registraron pulsaciones a 256 Hz. La edición 0.8 corrigió también el caso de los dos huecos de disparo ocupados.')
 d.h('Dar tiempo tras una muerte')
 d.p('Se incorporaron tres cuadros de explosión, reaparición centrada y dos segundos de invulnerabilidad con parpadeo. El jugador puede actuar durante la protección. Estas reglas se mantienen en la 0.17.')
 d.p('Esta memoria resume cambios comprobables en los fuentes, el manual histórico y las pruebas conservadas. No atribuye fechas independientes a iteraciones sin registro fechado.',8.3,12);d.end()
 d.page('Memoria / consolidación','De la 0.7 a la edición documentada')
 d.table([['Hito','Decisión conservada o sustituida'],['0.7','Transiciones suaves, seis coreografías, marcador despejado y comprobación de sprites completos.'],['0.8','Cada pulsación obtiene disparo aunque ambos láseres estén ocupados.'],['0.9','Cuatro ataques del MOAI y resistencia creciente; respuesta durante sus ataques.'],['0.10','Escudo activo impide nuevos disparos. Todas las familias pueden elegir los seis patrones.'],['0.11–0.12','Exploración de trance para el título; registro más grave e inclinación sutil de la nave.'],['0.13','El título adopta Eurodance original con progresión Am–F–C–G.'],['0.14','Tecno oscuro 1, fondo cósmico fijo y estrellas más legibles.'],['0.15','Generador de ciclo largo, composiciones mixtas, refuerzos y formación CROW tipo Space Invaders.']],[76,CW-76])
 d.p('El requisito musical evolucionó durante el proyecto: primero música solo en el título y después también durante la partida. El resultado vigente es Eurodance de título, un único tema de combate y cierre propio para Game Over.')
 d.p('En la 0.16 la invasión CROW se retira y reagrupa al llegar abajo. El MOAI empieza con 48 impactos y repone hasta seis CROW simultáneos durante todo el combate. Se conservan los siete patrones y las composiciones de la 0.15. En la 0.17 cambia únicamente el sonido de disparo: un breve ruido tipo «pff» como homenaje al beeper original.',8.6,12);d.end()
 d.page('Dentro del cartucho','Presupuesto de hardware y estructura')
 d.table([['Recurso','Uso en la edición 0.17'],['ROM','32 KiB, ROM ONLY, sin MBC ni SRAM.'],['Pantalla','160 × 144, cuatro tonos; campo 112 + marcador 48.'],['Sprites','Formato 8 × 16; presentación mediante páginas OAM terminadas.'],['Disparos','2 láseres propios y 3 proyectiles enemigos.'],['Temporización','Nave por fotograma; lógica enemiga a 25 pasos por 60 VBlank. Entrada muestreada a 256 Hz.'],['Arte comprimido','PackBits al cargar escenas, fuentes y sprites; sin descompresión continua en combate.']],[92,CW-92])
 d.h('Reparto del sonido')
 d.p('El disparo de 0.17 utiliza solo ruido (canal 4), sin tono. Pulso 1: otros efectos y melodía de título. Pulso 2 y onda: música. El ruido se comparte con la percusión y las explosiones. Secuenciador en VBlank, sin esperas activas.')
 d.p('Módulos principales: main.c coordina estados; player.h controla nave y láser; waves.h define vuelos; boss.h selecciona ataques; moai.h dibuja el rostro; hud.h mantiene el marcador; audio.h secuencia música y efectos.',8.6,12);d.end()
 d.page('Lo que se ha comprobado','Pruebas heredadas de 0.16; disparo nuevo aprobado en 0.17')
 d.table([['Prueba','Resultado validado en la 0.16'],['24 pulsaciones breves','Láser creado en 1–2 VBlank; visible en 1–3.'],['Dos huecos ocupados','12 pulsaciones rápidas respondieron.'],['Escudo + A','Cero disparos nuevos en 60 fotogramas; el fuego vuelve al terminar.'],['Movimiento','238 actualizaciones en 240 VBlank; 240 con cinco grandes y cuatro CROW.'],['Sprites','3.900 fotogramas de patrones clásicos y 720 de invasión CROW coherentes.'],['Fondos','Cero cargas de tiles de fondo en 240 VBlank de combate estable.'],['Música','Tecno 1 en las siete oleadas; título y Game Over conservados.'],['MOAI','Mapa y estrella idénticos a la 0.13; cuatro ataques y ciclos crecientes verificados.']],[115,CW-115])
 d.p('Las pruebas usan PyBoy DMG. Algunas preparan colisiones, oleadas o invulnerabilidad en RAM: no equivalen a una partida completa sin asistencia. El nuevo disparo de 0.17 fue aprobado tras escucharlo el autor. Pendientes: consola física y observación prolongada en distintos emuladores.',8.6,12)
 d.p('Retirada probada con 1, 4 y 10 supervivientes, conservando bajas y pausa. MOAI: tres tandas de seis CROW destruidas y repuestas; los seis reciben impactos y desaparecen al morir el jefe. Disparo y escudo probados durante sus cuatro ataques.',8.6,12);d.end()
 d.page('Procedencia y archivo','Material del proyecto · sin mockups')
 d.p('<b>Portada:</b> PNG aportado por el usuario en «Halcones Estelares_ Arcade Espacial Retro.zip». Se incluye íntegro, sin regeneración ni retoque; la identificación del documento queda fuera de la ilustración.')
 d.p('<b>Capturas:</b> carpeta capturas/ conservada de la versión 0.16. Título, combate y escudo se obtienen con botones. Las formaciones, invasión, jefe, victoria y transiciones usan escenarios preparados en RAM.')
 d.p('<b>Sprites ampliados:</b> decodificados de src/assets.h, incluidos datos PackBits. El lienzo de hardware y los espacios transparentes se muestran sobre negro. No son reinterpretaciones de los personajes.')
 d.p('<b>Arte:</b> assets/title_gb.png, gameover_gb.png, sidebar_gb.png y moai_damage_0…3.png. Son recursos generados por las herramientas del propio proyecto. El fondo cósmico fue incorporado como arte nuevo en la 0.14.')
 d.h('Cómo reproducir y verificar')
 d.p('GBDK 4.4: ejecutar make para construir la ROM; tools/assets.py regenera sus datos gráficos. Los informes JSON de la raíz registran respuesta, patrones, bucles, música y fondos. tools/build_documents.py compone estos PDF con ReportLab, Pillow y fuentes DejaVu.')
 sha=hashlib.sha256((R/'rom/Halcones-Estelares-GB-0.17.gb').read_bytes()).hexdigest()
 d.p('SHA-256 de la ROM 0.17:<br/>'+sha[:32]+'<br/>'+sha[32:],8,12)
 d.p('Original © 2026 Tony C. Ware. Código y herramientas según las licencias del proyecto; las licencias de código no conceden derechos sobre el arte. Documentación con asistencia de OpenAI Codex. Edición 02 · 16/11/2026.',8,12);d.end();d.save()
manual();atlas();print('Built manual (9 pages) and atlas (12 pages).')

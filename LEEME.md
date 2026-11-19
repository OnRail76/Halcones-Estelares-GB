# Halcones Estelares — Game Boy 0.18

Adaptación nativa para Game Boy clásica (DMG) del juego de Tony C. Ware.
Referencia comprobada: el TAP **HALCONES_ESTELARES_1_3_3.tap** adjuntado por el
usuario coincide byte por byte con el TAP reconstruido desde los fuentes 1.3.3.
SHA-256: `0db551592d01900287f0dad4754b840589075fb50ae3e7405ea66dbf21266ddf`.


## Argumento y música

La historia original completa figura en [HISTORIA.md](HISTORIA.md). Las grabaciones actuales se identifican como **Eurodance noventero**, **Tecno oscuro 1** y **Tonadilla de Game Over**; consultar [BANDA_SONORA.md](BANDA_SONORA.md).

## Novedades 0.18 — Cañón de Plasma definitivo

**Cañón de Plasma: nuevo sonido de disparo comprimido de la ESF-01, chasquido eléctrico seguido de soplido seco.**

El disparo ahora tiene dos fases de ruido pseudoaleatorio: chasquido brillante durante aproximadamente un fotograma (16,7 ms) y cola más grave y tenue de unos 27 ms. No se utiliza un tono de pulso para el disparo. El cambio se realiza con una nueva transición sincronizada con VBlank.

La ROM es idéntica a la prueba «Plasma PTCH» que escuchó y aprobó el autor (SHA-256 a9cb44a5b985d15906857c51d6985e93173b65ff8e0f82253614fceb9a8ac393). Se mantienen exactamente los gráficos, las melodías y la jugabilidad de 0.17. Los WAV que ya había en audio/ son capturas históricas, no un registro del disparo 0.18.

## Novedades 0.17 — disparo ESF-01

**Cambios: Sonido del disparo del ESF-01 mas adecuado a su origen en ZX Spectrum**

Ahora la ESF-01 produce un «pff» breve de ruido (canal 4, 31 ms), en homenaje al beeper ZX Spectrum. El autor escuchó y aprobó la ROM de prueba, publicada sin cambiar ningún byte de su código máquina. No se alteran melodías, gráficos ni mecánicas. Los WAV incluidos son capturas históricas de la 0.16, no del nuevo disparo.

## Novedades 0.16 — retirada CROW y MOAI reforzado

La invasión abandona la zona baja: al llegar a su umbral los supervivientes
suben suavemente, se reagrupan arriba y repiten el patrón. Conservan las bajas,
no se teletransportan ni reaparecen enemigos destruidos. Funciona también con
un único CROW; la pausa detiene el ascenso.

MOAI comienza con 48 impactos (+50 %), suma ocho por fase y llega a 128.
Cada invocación repone los huecos hasta seis CROW simultáneos, en tres pares
con posiciones de salida distintas. No hay límite total de invocaciones:
continúan mientras el jefe viva. Al morir se eliminan todos los acompañantes.
Se mantienen tres proyectiles enemigos y la prioridad de los controles.

Para conservar los 32 KiB, los tiles del alfabeto se reconstruyen durante la
carga de escena usando el mismo alfabeto del marcador. Los píxeles resultantes
son idénticos a los anteriores; no se añade trabajo al bucle de combate.

Ver REAGRUPACION_Y_MOAI.json: ciclos completos con 1, 4 y 10 CROW; tres tandas
de seis CROW del jefe eliminadas y repuestas; colisiones y limpieza final.

## Novedades 0.15 — oleadas variables y refuerzos

- Siete patrones: los seis anteriores y una invasión rápida de diez CROW con
  marcha lateral colectiva, descenso al invertir y aceleración al quedar cuatro.
  Puede sustituir cualquier oleada normal 1–6, desde la primera fase, sin garantía
  de aparecer en cada ciclo. El MOAI sigue ocupando la séptima oleada.
- Oleadas 3–6: elección entre seis grandes, cuatro grandes y dos CROW, o
  dos grandes y cuatro CROW. El tipo grande conserva su tramo: cazador o kamikaze.
- Al destruir un grande sin CROW activos ni pendientes, entran de uno a cuatro
  CROW por turnos después de una espera breve. Presupuesto máximo: cuatro
  refuerzos por oleada. La oleada no termina hasta eliminarlos. Los impactos
  de láser y las destrucciones con escudo activan la misma regla.
- Tamaño, colisión de láser, dibujo y origen del disparo dependen del enemigo.
- Generador de oleadas: LFSR de 16 bits, ciclo 65.535, sembrado al iniciar una
  partida. Se elimina la secuencia corta de 17 estados y la resiembra por oleada.
  Selección acotada con rechazo; se permiten repeticiones, sin listas forzadas.
- La ROM conserva 32 KiB. Se comprimen más recursos de carga de escena sin
  alterar sus píxeles ni añadir descompresión al combate.

Pruebas: 1.536 selecciones, siete patrones y las 18 combinaciones clásicas;
239 actualizaciones de nave en 240 VBlank con cinco grandes más cuatro CROW,
24 pulsaciones respondidas y escudo activo en dos VBlank bajo esa carga.
La invasión apareció en 139 de 256 ciclos preparados. Ver VARIEDAD_OLEADAS.json.
PyBoy DMG; escenarios preparados en RAM, pendiente de consola física.

## Jugar

Abre `Halcones-Estelares-GB.gb` en un emulador de Game Boy. ROM de 32 KiB,
sin MBC ni SRAM. El récord se conserva durante la sesión, no después de apagar.

- Cruceta izquierda/derecha: mover la nave.
- A: disparar por pulsación o mantener para fuego continuo; máximo dos láseres.
- B: escudo de tres segundos, seguido de seis segundos de recarga.
- START: comenzar, pausar o reanudar.

Tres vidas. Diez puntos por enemigo o impacto al MOAI. Una vida extra cada
100 impactos si quedan entre una y dos vidas; máximo tres. Puntuación máxima
99.990. Se ha eliminado la bonificación de 200 puntos del jefe de las versiones
GB anteriores porque no estaba en el Z80 1.3.3.

## Pantalla y marcador

Campo de combate de 112×144 y marcador lateral de 48×144, adaptando la misma
información principal del ZX: PUNTOS, REC, VIDAS, ESCUDO, FASE y OLEADA.
En la 0.7 se retiran el emblema ESF y la estrella del marcador: los apartados
tienen más separación y FASE y OLEADA muestran cifras grandes y centradas.
Se conservan las cifras gruesas, caritas y bandas de sección, traducidas a los
cuatro tonos DMG. La barra se vacía al activar el escudo y se rellena en recarga;
el estado muestra LISTO, ACTIVO o CARGANDO. La nave mantiene 24×24 píxeles; su
núcleo de colisión es de 16×16. El escudo forma un medio arco de dos píxeles
de grosor sobre el morro. Los márgenes impiden invadir el marcador.

Las estrellas, la nebulosa y la galaxia son **fijas**: se cargan al entrar en escena. No hay
scroll, parpadeo de estrellas, coordenadas móviles ni trabajo de animación de
estrellas en CPU. El PPU sigue dibujando el fondo, como cualquier pantalla de GB.
Júpiter es estático; la pequeña luna con cráteres cruza durante el jefe.

El título sustituye el halcón anterior por el robot alado aportado por el usuario,
adaptado a cuatro tonos y 144×68 píxeles. Mantiene el texto
EUROPEAN SPACE FORCE centrado, PRESS START y destellos de paleta sobre los tonos
intermedios. Game Over conserva la nave de perfil y la puntuación final.

## Oleadas y transiciones — 0.7

Se conserva la secuencia de seis oleadas y MOAI, pero por petición del usuario
la coreografía evoluciona hacia patrones propios inspirados en clásicos arcade.
No es una reproducción literal de los patrones de esos juegos.
Desde la 0.10, cada oleada seleccionaba uno de los seis patrones al azar: CROW,
cazadores y kamikazes pueden recibir cualquiera. Se conservan sus gráficos,
cantidad, tamaño y colisiones. Al ser aleatorio, un patrón puede repetirse.

| Patrón | Inspiración | Comportamiento |
| --- | --- | --- |
| 1 | Galaxian | Dos picadores simultáneos, curvas hacia un objetivo elegido al salir y regreso por los flancos. |
| 2 | Galaga | Parejas escalonadas, trayectorias en S, hasta tres atacantes y disparos durante el picado. |
| 3 | Moon Cresta | Salidas por columnas, pausa de amago a media altura y segunda acometida con nuevo objetivo. |
| 4 | Phoenix | Formación dispersa con aleteo vertical, suspensión breve, disparo y caída. |
| 5 | Galaga | Líder y dos escoltas, despegue separado y trayectorias curvas hacia objetivos distintos. |
| 6 | Moon Cresta / Phoenix | Ataques continuos en carrusel, zigzag, selección tardía del objetivo y regreso visible. |

Los atacantes se eligen con una pequeña secuencia pseudoaleatoria inicializada
con el momento de entrada y la fase. Los últimos tres supervivientes acortan
sus pausas. En los seis patrones clásicos regresan físicamente a su posición; ya no se teletransportan
al borde superior. Los proyectiles normales pueden salir en diagonal hacia la
posición de la nave al disparar. Se conservan los tres proyectiles enemigos
simultáneos y los disparos rectos alternos de los ojos del MOAI.

Cada nueva formación entra por turnos desde los bordes. El cartel OLEADA
SUPERADA se revela y retira por filas durante aproximadamente un segundo.
La nave sigue visible y puede moverse y disparar; el marcador y la música
continúan. No se apaga el LCD ni se reconstruye toda la pantalla al pasar
entre oleadas. El MOAI aparece progresivamente por filas.

Los periodos de disparo se reducen con cada vuelta al superar al MOAI. Tienen
un suelo de seguridad de 10/8/6/10 pasos para CROW/cazador/halcón/MOAI. La
velocidad de los proyectiles enemigos sube en las fases 3 y 7, hasta cuatro
píxeles por paso. Las distancias se adaptan al campo de 112 píxeles.

## MOAI

Usa la máscara de 48×88 realmente compilada en la 1.3.3, adaptada a 40×72 con
relieve en grises y cuencas oscuras. Los ojos se iluminan antes de disparar y
mientras abre la boca. Dispara alternando ojos, con tres proyectiles como máximo.

Tiene 48 puntos de vida al inicio, ocho más por vuelta hasta 128. Las grietas
se acumulan al quedar el 75%, 50% y 25% de resistencia,
partiendo de los recorridos del código original. Para reproducibilidad, el
serpenteo usa una semilla fija; en ZX dependía del instante de impacto.

Tras el último impacto se eliminan los proyectiles y la luna, la cara destella
ocho veces y desaparece por bloques en orden salteado, tres por actualización.
Se adaptan los 66 bloques del ZX a los 45 tiles del retrato GB. Se pasa de fase
solo después de terminar el derrumbe y una pantalla de victoria de tres segundos.
Muestra HAS DERROTADO A / MOAI / MONOLITH y ENTRANDO EN FASE, todo centrado.
Se conservan vidas, puntos, récord y recarga del escudo; empieza la primera
oleada de la fase siguiente, con dos segundos de protección. La fase llega a 99
sin desbordarse. OLEADA SUPERADA usa un rótulo metálico e inclinado centrado en
el campo de 112 píxeles, sin tapar el marcador.

## Sonido

Por indicación posterior del usuario, la restricción antigua de música solo en
el título queda sustituida: el título usa Eurodance noventero. Las partidas
usan únicamente **tecno oscuro 1**, a unos 132 BPM, sin alternar canciones.
Se conserva la tonadilla de Game Over.

El disparo de 0.17 recupera el carácter del beeper: «pff» seco en canal de ruido 4. Los demás efectos conservan sus timbres nativos de Game Boy.
Impactos cortos, explosión de ruido escalonada y
arpegios suaves para escudo, recarga y vida extra. Son composiciones originales;
no se han extraído sonidos de otros juegos. El láser responde inmediatamente.

Canal 1 para efectos tonales; canal 2 y onda para música; el ruido se comparte
con prioridad para impactos y explosiones. La melodía baja durante los efectos
importantes, y la percusión cede su canal. Secuenciador en VBlank, sin esperas
activas. `audio/` contiene sonido real de la APU capturado por PyBoy: título,
combate, Game Over y efectos aislados. Las muestras aisladas
seleccionan las señales y estados del secuenciador en RAM; los efectos usan
la música desactivada para permitir escucharlas por separado.

## Optimización y organización

- Oleadas a 25 pasos por 60 VBlank, manteniendo su coreografía. Nave, disparo
  y proyectiles propios se procesan cada fotograma, con objetivo de 59,73 Hz.
  El bucle consume un VBlank ocurrido durante el dibujo sin añadir otra espera.
  En las 24 pruebas de la 0.7 el láser se creó en dos VBlank y fue visible en
  dos o tres, también con música y actualizaciones del marcador.
- Lectura de botones y registro de pulsaciones en VBlank para no perder entradas
  breves durante una actualización gráfica.
- Dos páginas de sprites terminados alternan para DMA; el búfer de trabajo
  nunca se presenta a medio dibujar. La nave y el escudo ocupan los primeros
  lugares de prioridad. La muerte de un enemigo oculta inmediatamente sus dos
  mitades; la entrada espera oculta hasta que le corresponde salir. Se validaron
  3.900 fotogramas completos de OAM y la eliminación de enemigos.
- Ilustraciones y pantallas estáticas comprimidas con PackBits para mantener
  la ROM de 32 KiB. Solo se descomprimen al cargar escenas, nunca en la lógica
  de combate.
- Ventana de hardware lateral: se elimina la interrupción LCD por línea del HUD
  superior de las versiones anteriores.
- Marcador con caché por cifra, escrituras directas de bits y un trabajo por
  fotograma. Se transfiere como máximo una fila de tiles del HUD por fotograma;
  los cambios del retrato vivo del MOAI también se distribuyen por filas. En 240 VBlank de combate estable,
  la prueba instrumentada registró **cero llamadas a cargar tiles de fondo**.
- Temporizadores del escudo basados en VBlank; se congelan en pausa.
- `src/main.c`: estados, entradas y colisiones; `hud.h`: marcador;
  `moai.h`: cara, daños y derrumbe; `waves.h`: coreografía;
  `audio.h`: música de título y efectos; `player.h`: controles, láser y muerte;
  `assets.h`: gráficos generados; `sprites.h`: presentación completa de sprites;
  `packed.h`: carga de ilustraciones comprimidas.

## Recompilar y verificar

Instala GBDK-2020 4.4.0 y ejecuta:

```sh
make GBDK_HOME=/ruta/a/gbdk
```

Los gráficos ya están generados. Para regenerarlos, instala Pillow y ejecuta
`make assets`; no requiere fuentes tipográficas externas. `tools/art04.py`
y `tools/art06.py` se ejecutan desde `tools/assets.py`.

Con PyBoy instalado:

```sh
python3 tools/test_emulator.py
python3 tools/test_response_death.py
python3 tools/test_loops_music.py
python3 tools/test_arcade_flow.py
python3 tools/capture_presentation.py
python3 tools/capture_audio.py
```

`PRUEBAS.json` detalla los resultados. Las pruebas usan botones, posiciones
preparadas en RAM e invulnerabilidad temporal para aislar colisiones y progresión;
no representan una partida completa ganada sin ayudas. Las imágenes de título, combate y escudo se capturan además con botones
únicamente, sin modificar RAM. Las demostraciones de patrones y transiciones
seleccionan oleadas y preparan colisiones; la muestra sonora de combate protege
la nave temporalmente para grabar el tema completo.

Se comprueban marcador lateral, fondo inmóvil, ausencia de scroll, ritmo de
simulación, controles, escudo, música de fondo y pausa, regreso del explorador,
patrones y regresos de las seis oleadas, ojos y boca del MOAI,
grietas, derrumbe completo, fase siguiente, vida extra, techo de puntuación y
Game Over/reinicio. `BUCLES_Y_MUSICA.json` incluye cadencias de disparo observadas en el MOAI,
transición de fase, conservación de estadísticas y límite de fase 99.
`PATRONES_Y_TRANSICIONES.json` añade modos de vuelo, entradas escalonadas,
coherencia de sprites, movimiento entre oleadas, canciones y tonadilla final.
La ROM y sus checksums se validan al empaquetar.

## Límites y créditos

Probada en PyBoy DMG; pendiente de consola física y prueba de escucha en altavoz
real. Pantalla, distancias, escudo y timbres se adaptan al hardware GB. No se
promete equivalencia exacta de cada fotograma ni de la dificultad original.

© 2026 Tony C. Ware: juego, concepto, dirección creativa y gráficos originales.
Asistencia original: OpenAI GPT y Anthropic Claude. Adaptación GB: OpenAI Codex.
Se conservan las licencias originales. El código nuevo tiene `LICENSE_PORT.txt`;
los gráficos y sus conversiones conservan sus derechos, según `LICENCIA_GRAFICOS.md`.

## Respuesta y reaparición — conservadas desde 0.5

El disparo deja de esperar al paso de las oleadas. Cada pulsación de A crea un
proyectil: desde la 0.8, si los dos huecos están ocupados, sustituye al láser
más adelantado en lugar de descartar la pulsación, con sonido inmediato de ruido en el canal 4. Se conservan dos proyectiles simultáneos. Nacen por delante
del morro y avanzan cinco píxeles por fotograma (antes eran cuatro por paso de
oleada). Esto reduce la ocupación de los dos huecos y permite disparar con mayor
frecuencia. La colisión comprueba el recorrido vertical para no saltarse aves.

La nave responde cada fotograma y se desplaza aproximadamente a 90 px/s. En 24
ensayos de pulsación breve, incluyendo cambios de marcador, el disparo se creó
en 1–2 VBlank y fue visible en 2–3 VBlank. Son mediciones en emulador, no latencia
del mando, pantalla o sistema operativo del usuario.

Cada muerte retira la nave y muestra una explosión propia de 24×24, con tres
fases durante 36 VBlank (unos 0,6 segundos). Se limpian los proyectiles y se
pausan las oleadas durante esa explosión. Si quedan vidas, la nave reaparece
en el centro y comienza entonces una protección de 120 VBlank (unos 2 segundos),
con parpadeo. Puede moverse y disparar durante la protección. Al terminar vuelve
a recibir daño y se muestra de forma continua. Con cero vidas se completa la
misma explosión antes de Game Over.

Las coordenadas de enemigos y proyectiles usan ocho bits dentro de sus límites
de pantalla. El marcador evita divisiones repetidas de 32 bits y solo redibuja
las cifras que cambian. `RESPUESTA_Y_REAPARICION.json` registra las mediciones y
`capturas/reaparicion.gif` muestra la secuencia ejecutada con un impacto preparado.

## Corrección 0.8: pulsaciones con los dos láseres ocupados

Se conserva el máximo de dos láseres. Cada pulsación nueva de A reutiliza el
láser más adelantado si no hay un hueco libre; no se acumulan disparos pendientes.
En la 0.10 el escudo activo bloquea los nuevos disparos. Las 12 pulsaciones rápidas con
ambos huecos ocupados activaron el láser; las 24 mediciones normales crearon
el disparo en dos VBlank (visible en dos o tres). Verificado en PyBoy DMG.

## 0.9 — controles y MOAI

Los botones se muestrean a 256 Hz mediante temporizador, conservando las
pulsaciones pendientes; A se lee también directamente en el bucle principal.
Ojos y boca del MOAI usan máscaras de bits para evitar redibujos costosos. Una pulsación inicia un
láser y mantener A repite cada seis fotogramas. No se puede disparar con el escudo activo;
B sigue activando el escudo cuando está listo. Si los dos láseres están ocupados,
se reutiliza el más adelantado. No se acumulan pulsaciones en una cola.

El MOAI dispone de cuatro ataques mezclados en una bolsa pseudoaleatoria por
encuentro: ráfaga de tres disparos alternando ojos; dos disparos apuntados a la
última posición registrada; abanico de tres proyectiles; invocación de dos CROW.
Los ojos avisan durante doce pasos antes de la acción. El apuntado guarda su
objetivo antes del aviso y calcula una trayectoria fija hasta la altura de la
nave: no hay persecución posterior. Los CROW pueden destruirse, regresan por los
flancos y desaparecen al morir el MOAI. Nunca hay más de dos invocados ni de tres
proyectiles enemigos simultáneos. La resistencia es 32, 40, 48… hasta 112.

Las pruebas verifican A+B simultáneos en los cuatro ataques, pulsaciones rápidas
con ambos láseres ocupados, fuego mantenido con escudo, resistencia por fase,
variedad de ataques y limpieza al derrotar al jefe. La secuencia usa el momento
del encuentro, la fase, puntuación y posición para variar el orden.

## Hito 0.10

Solo cambian dos reglas: el escudo activo bloquea nuevos disparos, tanto por
pulsación como por fuego mantenido, y cada familia elige aleatoriamente entre
los seis patrones arcade. Mantener A reanuda el fuego al finalizar el escudo;
las pulsaciones soltadas durante la protección no quedan pendientes. Los láseres
ya lanzados siguen su recorrido. Se han verificado los seis patrones en cada
familia y el bloqueo y reanudación del disparo. El MOAI permanece como en 0.9.

## 0.11 — trance exclusivo del título

El título tiene una melodía original de trance noventero a unos 138 BPM, con
voz principal, arpegio de semicorcheas y bajo a contratiempo sobre Am/F/C/G.
Al comenzar la partida se mantiene el tecno 1/2 y su alternancia; Game Over
conserva su tonadilla. No cambian los controles, las reglas ni los ataques.
`MUSICA_TITULO.json` verifica trazas idénticas de registros de audio para ambos
temas de partida y Game Over frente a la 0.10. Para repetir esa comparación,
`tools/test_title_music.py` requiere la 0.10 descomprimida como carpeta hermana
`Halcones-GameBoy-0.10-respaldo`, incluyendo ROM y símbolos `.noi`.

## 0.12 — trance más grave e inclinación de la nave

Se mantienen los 138 BPM del título, pero melodía y arpegios bajan una octava.
La voz principal sostiene más las notas, el arpegio usa un pulso más redondo
y los agudos de percusión tienen menos volumen. Tecno 1, tecno 2 y Game Over
conservan su secuencia de registros APU, comprobada frente a la 0.10.

Al desplazarse, las alas de la nave se desfasan verticalmente un píxel en
sentidos opuestos, y vuelven a su altura al parar. No cambia su posición lógica,
velocidad ni caja de colisión. La explosión conserva su alineación original.
`ANIMACION_NAVE.json` verifica izquierda, derecha, reposo y las parejas de sprites.

## 0.13 — Eurodance noventero en el título

Nueva composición original para el título, a unos 132 BPM, sobre Am/F/C/G.
Melodía diatónica con estribillo de ocho compases, acompañamiento más espaciado
y bajo a contratiempo. La afinación de los canales de pulso y onda se calcula
por separado desde notas musicales exactas (La4 = 440 Hz). La partitura está en
`audio/PARTITURA_TITULO.json`. No cambia la música de las partidas, Game Over,
los controles ni la animación de la nave. La comparación APU mantiene trazas
idénticas para tecno 1, tecno 2 y Game Over.


## 0.14 — Espacio cósmico y tecno 1 continuo

Nebulosa y galaxia en gris oscuro, con estrellas de dos píxeles en gris medio.
Los proyectiles y enemigos conservan el blanco brillante. El centro y la zona
de la nave quedan despejados. Fondos fijos, sin scroll ni actualizaciones durante
el combate; el rótulo de oleada restaura el dibujo desde el mapa de fondo.
El escenario del MOAI conserva su mapa y estrellas anteriores.

Eliminado el tema 2 de la ROM. Eurodance del título, tecno 1 y Game Over
conservan sus notas y reproducción. Fuentes y sprites se descomprimen al cargar,
sin trabajo extra durante el juego. ROM de 32 KiB. Comprobado en PyBoy;
la legibilidad final en una pantalla DMG física queda pendiente de probar.

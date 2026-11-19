# HALCONES ESTELARES — GAME BOY

![Carátula oficial de Halcones Estelares GB](portada/Halcones_Estelares_GB_Caratula_Oficial.png)

**Versión 0.18 · Game Boy clásica (DMG) · © 2026 Tony C. Ware**

*Arcade de pájaros espaciales portátil.* Adaptación nativa de **Halcones Estelares 1.3.3** para ZX Spectrum 48K. No es un emulador del Spectrum: es código para Game Boy, desarrollado con GBDK 4.4.

## Historia

**1988. El futuro.** La recién formada **Fuerza Espacial Europea** detecta señales de radio y pulsos de energía procedentes de **Europa**, la luna de Júpiter. Varias sondas desaparecen y llega la hora de estrenar el caza **ESF-01**.

Pero en el vacío sideral esperan **aves cósmicas que solo quieren invadir, destruir y COMER**. ¿Qué o quién las dirige?

**Sube a bordo del ESF-01, piloto. Es el momento de luchar. Sus gritos se oirán en el Cosmos.**

[Leer la historia original completa](HISTORIA.md).

## Jugar

[**ROM oficial 0.18**](rom/Halcones-Estelares-GB-0.18.gb) · 32 KiB, sin MBC ni SRAM. Compatible con emuladores de Game Boy clásica y cartuchos flash compatibles. El récord se pierde al apagar.

| Botón | Función |
|---|---|
| ← / → | Mover ESF-01 |
| A | Disparar; puede mantenerse pulsado |
| B | Escudo (unos 3 s, 6 s para recargar) |
| START | Comenzar / pausar / reanudar |

Tres vidas iniciales. Dos disparos propios como máximo. Marcador lateral de 48 píxeles y campo de juego de 112 × 144.

## Edición definitiva — Cañón de Plasma

El disparo de la **ESF-01** utiliza dos etapas de ruido en el canal 4: un chasquido eléctrico corto y un soplido grave y seco. No contiene el antiguo pitido agudo. La ROM que se distribuye es byte por byte idéntica a la aprobada por el autor.

El juego incluye siete patrones de oleadas, formaciones mixtas, ataques de CROW que se retiran y reagrupan, y el jefe MOAI MONOLITH con resistencia progresiva e invocación de refuerzos. Se conservan sus músicas, controles, escudo, gráficos y mecánicas originales.

## Banda sonora original

**Eurodance noventero** (título), **Tecno oscuro 1** (partida) y **Tonadilla de Game Over** (derrota). Los WAV oficiales están en [BANDA_SONORA.md](BANDA_SONORA.md), junto con la explicación de las capturas de la APU; no se incluyen grabaciones musicales antiguas descartadas.

## Documentación y recursos auténticos

- [Manual ilustrado 0.18](docs/Manual-ilustrado-GB-0.18.pdf) — 9 páginas.
- [Atlas visual y memoria 0.18](docs/Atlas-y-memoria-GB-0.18.pdf) — 12 páginas.
- [Carátula oficial original](portada/Halcones_Estelares_GB_Caratula_Oficial.png).
- [Capturas y animaciones de la ROM](capturas/), incluyendo CROW, invasión, reagrupación y MOAI con seis refuerzos. Algunas escenas están preparadas en RAM para comprobaciones; no son mockups.
- [Memoria técnica detallada](LEEME.md), [nota de la edición](CHANGELOG.md) y [herramientas de prueba](tools/).

## Compilación

Requiere **GBDK 4.4** y `make`:

```bash
make GBDK_HOME=/ruta/a/gbdk
```

El binario generado estará en la raíz `Halcones-Estelares-GB.gb`. La ROM publicada de referencia se encuentra en `rom/`; no es necesario compilarla para jugar. Las herramientas de prueba pueden necesitar PyBoy, NumPy y ficheros auxiliares de la compilación.

**ROM oficial SHA-256:**

```text
a9cb44a5b985d15906857c51d6985e93173b65ff8e0f82253614fceb9a8ac393
```

Verificaciones efectuadas con PyBoy en modo DMG; las pruebas sobre consola física no están acreditadas.

## Autoría y licencias

**© 2026 Tony C. Ware.** Desarrollo y documentación con asistencia de herramientas de IA (OpenAI Codex / ASTRA). Código y herramientas bajo [MIT](LICENSE). La [licencia artística](LICENCIA_GRAFICOS.md) protege separadamente portada, sprites, logo, fondos y recursos visuales. Proyecto independiente y no oficial, sin afiliación con Nintendo.

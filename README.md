# HALCONES ESTELARES — GAME BOY

![Carátula oficial de Halcones Estelares GB](portada/Halcones_Estelares_GB_Caratula_Oficial.png)

**Versión 0.17 · Game Boy clásica (DMG) · © 2026 Tony C. Ware**

*Arcade de pájaros espaciales portátil.* Adaptación nativa de **Halcones Estelares 1.3.3** para ZX Spectrum 48K. No es un emulador del Spectrum: es código para Game Boy, desarrollado con GBDK 4.4.

## Historia

**1988. El futuro.** La recién formada **Fuerza Espacial Europea** detecta señales de radio y pulsos de energía procedentes de **Europa**, la luna de Júpiter. Varias sondas desaparecen y llega la hora de estrenar el caza **ESF-01**.

Pero en el vacío sideral esperan **aves cósmicas que solo quieren invadir, destruir y COMER**. ¿Qué o quién las dirige?

**Sube a bordo del ESF-01, piloto. Es el momento de luchar. Sus gritos se oirán en el Cosmos.**

[Leer la historia original completa](HISTORIA.md).

## Jugar

[**ROM oficial 0.17**](rom/Halcones-Estelares-GB-0.17.gb) · 32 KiB, sin MBC ni SRAM. Compatible con emuladores de Game Boy clásica y cartuchos flash compatibles. El récord se pierde al apagar.

| Botón | Función |
|---|---|
| ← / → | Mover ESF-01 |
| A | Disparar; puede mantenerse pulsado |
| B | Escudo (unos 3 s, 6 s para recargar) |
| START | Comenzar / pausar / reanudar |

Tres vidas iniciales. Dos disparos propios como máximo. Marcador lateral de 48 píxeles y campo de juego de 112 × 144.

## Novedades 0.17

- **Cambios: Sonido del disparo del ESF-01 mas adecuado a su origen en ZX Spectrum**
- Efecto de disparo «pff» corto, seco y sin pitido; canal 4 de ruido de Game Boy. El resto de la 0.16 se conserva.

## Novedades 0.15–0.16

- **Siete patrones de oleada**, incluido el asalto colectivo CROW inspirado en Space Invaders.
- **Oleadas mixtas**: cazadores o kamikazes acompañados de CROW, con hasta cuatro refuerzos extra en situaciones concretas.
- **Invasión CROW que se retira y reagrupa** tras llegar a la parte baja, conservando las bajas.
- **MOAI MONOLITH reforzado:** 48 impactos iniciales, +8 por fase hasta 128; invoca hasta seis CROW simultáneos y repone sus bajas hasta su destrucción.
- Generador pseudoaleatorio LFSR de 16 bits para mayor variedad de partidas.
- Se mantienen música, controles, escudo y gráficos de la edición vigente; ROM de **32 KiB**.

## Banda sonora original

**Eurodance noventero** (título), **Tecno oscuro 1** (partida) y **Tonadilla de Game Over** (derrota). Los WAV oficiales están en [BANDA_SONORA.md](BANDA_SONORA.md), junto con la explicación de las capturas de la APU; no se incluyen grabaciones musicales antiguas descartadas.

## Documentación y recursos auténticos

- [Manual ilustrado 0.17](docs/Manual-ilustrado-GB-0.17.pdf) — 9 páginas.
- [Atlas visual y memoria 0.17](docs/Atlas-y-memoria-GB-0.17.pdf) — 12 páginas.
- [Carátula oficial original](portada/Halcones_Estelares_GB_Caratula_Oficial.png).
- [Capturas y animaciones de la ROM](capturas/), incluyendo CROW, invasión, reagrupación y MOAI con seis refuerzos. Algunas escenas están preparadas en RAM para comprobaciones; no son mockups.
- [Memoria técnica detallada](LEEME.md), [historial de cambios](CHANGELOG.md) y [herramientas de prueba](tools/).

## Compilación

Requiere **GBDK 4.4** y `make`:

```bash
make GBDK_HOME=/ruta/a/gbdk
```

El binario generado estará en la raíz `Halcones-Estelares-GB.gb`. La ROM publicada de referencia se encuentra en `rom/`; no es necesario compilarla para jugar. Las herramientas de prueba pueden necesitar PyBoy, NumPy y ficheros auxiliares de la compilación.

**ROM oficial SHA-256:**

```text
e263b5fa77a78e483857f3d200a35cd81f5bd2053db0172575ce12403af07e8c
```

Verificaciones efectuadas con PyBoy en modo DMG; las pruebas sobre consola física no están acreditadas.

## Autoría y licencias

**© 2026 Tony C. Ware.** Desarrollo y documentación con asistencia de herramientas de IA (OpenAI Codex / ASTRA). Código y herramientas bajo [MIT](LICENSE). La [licencia artística](LICENCIA_GRAFICOS.md) protege separadamente portada, sprites, logo, fondos y recursos visuales. Proyecto independiente y no oficial, sin afiliación con Nintendo.

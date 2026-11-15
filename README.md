# HALCONES ESTELARES — GAME BOY

![Carátula oficial](portada/Halcones_Estelares_GB_Caratula_Oficial.png)

**Versión 0.14 · Nintendo Game Boy clásica (DMG) · © 2026 Tony C. Ware**

Adaptación nativa para Game Boy clásica de **Halcones Estelares 1.3.3**, originalmente creado para ZX Spectrum 48K. Un arcade de pájaros espaciales: pilota el interceptor **ESF-01**, supera seis oleadas y enfréntate a **MOAI MONOLITH**. Cada victoria inicia una nueva fase de dificultad creciente.

> Proyecto independiente, sin afiliación ni aprobación de Nintendo. Game Boy es una marca de Nintendo.

## Jugar

**[ROM Game Boy 0.14](rom/Halcones-Estelares-GB-0.14.gb)** — 32 KiB, ROM ONLY, sin MBC ni SRAM. Usa un emulador compatible con Game Boy DMG o un cartucho flash compatible. No hay guardado permanente del récord.

| Mando | Función |
|---|---|
| Cruceta izquierda / derecha | Mover ESF-01 |
| A | Disparar (pulsar o mantener para fuego continuo) |
| B | Escudo temporal (3 s; recarga 6 s) |
| START | Empezar / pausar / continuar |

Tres vidas iniciales, escudo y un máximo de dos disparos propios en pantalla. La pantalla DMG de 160 × 144 píxeles reserva 112 píxeles para combate y 48 para el marcador. Se incluyen **seis patrones de ataque** y cuatro maniobras del MOAI.

## Documentación y material gráfico

- [Manual ilustrado · edición 0.14](docs/Manual-ilustrado-GB-0.14.pdf) — 9 páginas.
- [Atlas visual y memoria · edición 0.14](docs/Atlas-y-memoria-GB-0.14.pdf) — 12 páginas.
- [Carátula oficial PNG](portada/Halcones_Estelares_GB_Caratula_Oficial.png).
- [Capturas y animaciones reales](capturas/) — proceden del juego o de estados preparados de emulador; no son mockups.
- [Notas técnicas originales de ASTRA](LEEME.md) y [resultados de pruebas](PRUEBAS.txt).

## Código fuente y compilación

El juego está programado para el procesador LR35902 de Game Boy, utilizando **GBDK 4.4**. `src/` contiene el código C, gráficos codificados y módulos de juego; `assets/` conserva recursos; `tools/` incluye generación de assets y pruebas.

```sh
make GBDK_HOME=/ruta/a/gbdk
```

Esto genera `Halcones-Estelares-GB.gb` en la raíz del proyecto. Para regenerar los datos gráficos: `make assets`. **No es necesario recompilar para jugar:** el binario oficial está en `rom/`.

Las pruebas automatizadas usan PyBoy DMG; algunas requieren el fichero `.noi` generado por GBDK y preparan estados de RAM. La verificación en hardware Game Boy físico permanece pendiente. No se afirma que esta publicación haya sido recompilada de nuevo aquí.

## Audio

`audio/` contiene capturas auténticas del audio de emulación. La versión 0.14 usa música eurodance original en título, tecno oscuro en partida y cierre en Game Over. `audio/historico/` conserva capturas de temas descartados, **no utilizados** por la ROM 0.14.

## Integridad

**SHA-256 ROM 0.14:**

```text
d47bc5f3150d8de58d0737718badc62ba37b7dc0ada7c6b8205209ad2e12f2f7
```

Las comprobaciones de otras entregas están en `SHA256SUMS.txt`.

## Créditos y licencias

**Autor y copyright: © 2026 Tony C. Ware.** Adaptación y documentación desarrolladas con asistencia de OpenAI Codex (ASTRA). La carátula oficial se incorpora **sin redibujar**. Código y herramientas bajo [MIT](LICENSE), con [traducción de cortesía](LICENSE_ES.md). **Sprites, ilustraciones, portada, logo y recursos artísticos no están cubiertos por MIT**: consultar [licencia gráfica](LICENCIA_GRAFICOS.md).

Los títulos de Nintendo, Game Boy y otros clásicos mencionados como referencia pertenecen a sus respectivos titulares.

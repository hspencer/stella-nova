# Stella Nova — para diseñadoras y diseñadores

Guía para intervenir el sistema visual del skin sin tocar PHP ni
configuración de MediaWiki. Si vienes del Taller de Diseño y solo
quieres cambiar colores, tipografía o componer una pantalla nueva,
este doc te basta.

Doctrina general en [`ARCHITECTURE.md`](ARCHITECTURE.md); mapa visual de
los layouts en [`LAYOUTS.md`](LAYOUTS.md); recursos editoriales que el
wikitexto puede usar en [`WIKITEXTO.md`](WIKITEXTO.md).

## Dónde tocar cada cosa

Todo el sistema visual vive en [`resources/`](../resources/) (más
[`includes/templates/`](../includes/templates/) para el orden del DOM).
Mapa:

| Quiero cambiar… | En qué archivo está |
|---|---|
| **Variables / tokens** (color, espaciado, tipografía, sombras, radios, movimiento; claro/oscuro; las 5 preferencias por `data-attribute`) | [`resources/tokens.css`](../resources/tokens.css) |
| **Layout y componentes** (cabecera, pie, menús, panel de preferencias, "página de papel"…) | [`resources/stella-nova.css`](../resources/stella-nova.css) |
| **Impresión** | [`resources/print.css`](../resources/print.css) |
| **Estilos de extensiones** (22 extensiones absorbidas, sin reestructurar su DOM) | [`resources/skinStyles/`](../resources/skinStyles/) — ver [`EXTENSIONES.md`](EXTENSIONES.md) |
| **Íconos** (sprite Feather inline; símbolos `#sn-i-*`) | [`includes/templates/SnIcons.mustache`](../includes/templates/SnIcons.mustache) |
| **Isotipo / logotipo** (SVG editable, monocromo, colorizable con `currentColor`; enlaza a portada; el wordmark va dentro) | [`resources/casiopea.svg`](../resources/casiopea.svg) (wordmark) y [`resources/casiopea-icon.svg`](../resources/casiopea-icon.svg) (glifo compacto) |
| **Estructura/orden del chrome** | [`includes/templates/skin.mustache`](../includes/templates/skin.mustache) (+ [parciales](../includes/templates/)) |
| **Textos de interfaz** | [`i18n/es.json`](../i18n/es.json), [`i18n/en.json`](../i18n/en.json) |

## Cómo iterar sin pelearse con la caché

ResourceLoader de MediaWiki **cachea agresivamente** los CSS/JS. Para
ver los cambios al instante:

- **Por URL (recomendado, no requiere editar config):** añadir
  `?debug=true` a cualquier URL de la wiki. CSS y JS se sirven sin
  minificar y sin caché.
- **Global durante desarrollo:** en `LocalSettings.php`:
  ```php
  $wgResourceLoaderDebug = true;
  ```
  No olvidar quitarlo en producción.

## Tipografía

**IBM Plex Sans** (sans del cuerpo · UI · todas las cabeceras h1–h6;
**variable**, dos ejes wght 100–700 + wdth 75–100) · **Roboto Serif**
(serif del cuerpo cuando el lector la elige desde el menú, citas y
`<poem>` por defecto; **variable**, cuatro ejes wght 100–900 + wdth
75–100 + opsz 8–60 + GRAD −50–100) · **IBM Plex Mono** (código).

Todas auto-alojadas (sin CDN en runtime): `@font-face` en
[`resources/fonts.css`](../resources/fonts.css), archivos `woff2` en
[`resources/fonts/`](../resources/fonts/). Subset `latin` (U+0000-00FF)
cubre el español sin `latin-ext`.

Dos capas de tokens en [`tokens.css`](../resources/tokens.css):
**primitivas** (las dos familias reales) y **semánticas** (alias que
consume el resto del skin, y que el menú del usuario invierte para
alternar la familia del cuerpo entre sans y serif).

- `--sn-font-sans` (primitiva) — IBM Plex Sans.
- `--sn-font-serif` (primitiva) — Roboto Serif.
- `--sn-font-mono` (primitiva) — IBM Plex Mono.
- `--sn-font-text` = `var(--sn-font-sans)` por defecto. Cambia a
  `var(--sn-font-serif)` cuando `data-sn-family="serif"`. Lo consumen el
  cuerpo, el chrome, los botones, los menús y las cabeceras.
- `--sn-font-display` = `var(--sn-font-text)`. Alias: la doctrina del
  skin es "todo sans en cabeceras". Si en el futuro quieres reintroducir
  un display distinto, cambia la línea del alias y nada más.
- `--sn-font-quote` = `var(--sn-font-serif)` por defecto. Cambia a
  `var(--sn-font-sans)` cuando `data-sn-family="serif"`. Lo consumen
  `<blockquote>` y `.poem` para mantener el contraste editorial frente
  al cuerpo (siempre a ancho natural, `font-stretch: 100%`).
- `--sn-serif-grade` (eje GRAD de Roboto Serif) — engrosa el trazo de la
  serif sin mover la caja del texto. Aplicado a toda la cascada vía
  `font-variation-settings: "GRAD"` en `:root` (sans/mono ignoran el eje).
  `0` en claro; `30` en oscuro para compensar el aclaramiento óptico del
  texto claro sobre fondo negro.

**Ancho del cuerpo (`--sn-text-width`, default 80%).** Las dos familias de
texto declaran el mismo rango `wdth 75–100`, así que el cuerpo condensa por
igual elija el lector sans o serif. Las cabeceras y las citas/`<poem>` se
resetean a `100%` (la condensada es solo del cuerpo corrido). Mono no tiene
eje de ancho → lo ignora.

El alternador (botón "Aa / Aa" con specimens en cada familia) vive en
el menú del usuario junto al tema y al tamaño de letra; persiste como
opción de cuenta `stellanova-family` para registrados y en localStorage
(`sn-pref-family`) para anónimo/temporal. La resolución antes del primer
paint la hace el script de pre-pintado en
[`Hooks.php`](../includes/Hooks.php#L284-L302).

## Íconos

Feather, como sprite SVG inline en
[`SnIcons.mustache`](../includes/templates/SnIcons.mustache). Se usan
así:

```html
<svg class="sn-i"><use href="#sn-i-NOMBRE"/></svg>
```

Color por política global (tokens `--sn-icon` / `--sn-icon-active`):
tinta al ~55 % en reposo → tinta plena al hover/foco; **nunca carmín**.
La nova (`--sn-nova`) se reserva para foco de controles, isotipo,
`firstHeading` y selected/active de menús.

El ícono de "enlace externo" es el token `--sn-ext-icon` (máscara
SVG inline) en `tokens.css`; se aplica con `mask: var(--sn-ext-icon)`
sobre un `::after` teñido con `currentColor`.

## Color

El sistema cromático vive en tres capas, en el orden Material 3
(*reference → system → component*). La regla operativa: **tocá la capa
más alta que resuelva tu problema**. Cambiar primitivas afecta todo el
skin; cambiar semánticas reasigna un rol sin tocar la paleta; cambiar
componentes ajusta un widget sin tocar nada más.

### 1. Primitivas (paleta agnóstica del tema)

Nombradas por **qué es el color**, no por su uso. Stops 50–950 donde
el número crece con la oscuridad. Familias:

| Familia | Qué es | Stops |
|---|---|---|
| **papel** | neutros cálidos claros (la hoja, sus pliegues) | 50–800 |
| **tinta** | neutros cálidos oscuros (pizarra y tinta china del atelier) | 300–950 |
| **rojo** | la sangre del carmín (nova y links del claro) | 500–900 |
| **coral** | el rosa cálido del modo noche | 300–400 |
| **azul** | único frío del skin (link en oscuro) | 200–300 |
| **malva** | gris-violeta del visitado en oscuro | 400 |
| **verde** | la "ok" del taller | 400–500 |
| **masking** | la cinta amarilla del taller (warn, notice) | 300–900 |
| **blanco** | papel químicamente puro (solo nova-ink claro) | (sin stop) |

Se definen una sola vez en `:root`. **No agregar primitivas
especulativas** — solo si el color ya existe en otra parte del archivo
y conviene ponerle nombre. Si vas a cambiar la paleta, este es el lugar.

### 2. Semánticas (roles del skin)

Cada rol del skin (`--sn-paper`, `--sn-ink`, `--sn-nova`, `--sn-link`,
`--sn-danger`, …) apunta a **una primitiva por tema**, con
`light-dark()` resolviendo el flip:

```css
--sn-paper: light-dark(var(--sn-papel-50), var(--sn-tinta-800));
--sn-link:  light-dark(var(--sn-rojo-500), var(--sn-azul-300));
```

El conmutador es `color-scheme`. El skin lo decide en cuatro selectores:

- **Sin preferencia guardada** → claro (decisión de producto; diverge
  del comportamiento "seguir al SO siempre").
- `data-sn-theme="light"` → claro forzado.
- `data-sn-theme="dark"`  → oscuro forzado (el SO no participa).
- `data-sn-theme="auto"`  → `color-scheme: light dark`; `light-dark()`
  sigue al `prefers-color-scheme` del SO.

Tocá esta capa cuando quieras **reasignar un rol** sin cambiar la paleta:
por ejemplo, si decidís que el danger del claro pase de `--sn-rojo-600`
a `--sn-rojo-500` para igualarlo a la nova. Una línea, sin tocar
primitivas, sin tocar componentes.

Cuatro tokens — `--sn-field-grain` y los tres `--sn-lift*` — varían
**geometría** además de color entre temas, así que no encajan en
`light-dark()`. Quedan duplicados (4 declaraciones) en los selectores
`[data-sn-theme="dark"]` y `@media (prefers-color-scheme: dark)
[data-sn-theme="auto"]` al final del archivo. Es la única duplicación
intencional del sistema.

### 3. Componentes (controles + Codex)

Tokens de control (`--sn-btn-*`, `--sn-field-*`, `--sn-on-*`,
`--sn-opt-*`, `--sn-focus-*`) y la capa de alias Codex / WikimediaUI
(`--color-*`, `--background-color-*`, `--border-color-*`). Consumen
**variables semánticas, nunca primitivas directas**. Heredan el flip de
tema automáticamente.

La capa Codex existe porque OOUI (oojs-ui-core/widgets/windows) y
algunas extensiones consumen `var(--color-base, #202122)` etc.; si la
variable no está definida en el documento, cae al hex hardcodeado y NO
respeta el tema. Acá los aliasamos a los tokens semánticos. Si añadís
un control OOUI nuevo y queda con color hardcodeado, posiblemente falte
un alias en esta capa.

### Contratos externos (no romper)

Los nombres `--sn-*` semánticos y los alias Codex los consumen los
TemplateStyles por plantilla (`Plantilla:X/style.css`), un espejo en
producción de `MediaWiki:Common.css` y OOUI. **No renombrar ni eliminar
ninguno**. La capa primitiva es puramente aditiva por debajo.

## Espécimen gráfico — mini-sitio para iterar

Mini-sitio estático autocontenido para iterar el sistema visual **sin
levantar la wiki ni tocar PHP**. Navegable en línea:

**[hspencer.github.io/stella-nova/specimen/](https://hspencer.github.io/stella-nova/specimen/)**

Localmente en [`docs/specimen/`](specimen/) (también empaquetado como
`stella-nova-specimen-v<version>.zip` listo para enviar al taller de
diseño). Tres páginas:

- `index.html` — tokens, escalas, sombras (auto-generadas desde
  `tokens.css`).
- `components.html` — botones, inputs, toolbar, washes, TOC.
- `layout.html` — página simulada completa.

Las tres cargan los CSS reales del skin y exponen un bloque
`<style id="overrides">` para redefinir variables en vivo, más un
`notes.md` para anotar libremente.

Regenerarlo tras cambiar tokens o componentes:

```bash
python3 scripts/build-specimen.py
```

Idempotente; **preserva `notes.md` entre rebuilds** (los `overrides`
de los HTML se reescriben — cópialos al CSS fuente cuando los
aceptes). Documentación completa del flujo diseñador ↔ mantenedor en
[`docs/specimen/README.md`](specimen/README.md).

## Antes de añadir una clase o un token nuevos

El set de tokens y de clases opt-in se mantiene **chico a propósito**.
Bootstrap nos enseñó qué pasa cuando crece sin freno. Antes de añadir:

1. ¿Lo cubre un token existente (`--sn-s-*`, `--sn-fs-*`,
   `--sn-baseline*`, `--sn-link`, `--sn-ink-soft`…)?
2. ¿Lo cubre una clase existente (`.full-width`, `.grilla.cols-N`,
   `.plantilla`, `.img-circle`, `.sn-notice`)?
3. Si la respuesta a ambas es no, conversar antes — no a regañadientes,
   simplemente para mantener coherencia.

> **Ritmo vertical en TemplateStyles.** Los tokens `--sn-baseline`,
> `--sn-baseline-half`, `--sn-baseline-2` y `--sn-baseline-3` son la unidad del
> baseline grid (interlínea del cuerpo × múltiplo). El relleno vertical que debe
> compensar **media interlínea** para que una caja cierre en un número entero de
> baselines —típico de tarjetas de plantilla como `.dm` (Documento miniatura) o
> `.curso-listado`— usa `var(--sn-baseline-half)`, **nunca** un valor de la escala
> de espaciado (`--sn-s-*`): esa escala es fija en `rem` y no sigue a
> `--sn-font-scale`, así que aproximarla deriva de la retícula cuando el lector
> cambia el tamaño de letra. El submúltiplo se calcula en la skin (donde `calc()`
> está permitido) y las TemplateStyles lo consumen como `var()` desnudo, porque el
> sanitizador de MediaWiki no admite dividir dentro de `calc()`.

Si vas a tocar un color, además decidí **en qué capa**:

- **¿El color que necesitás ya existe en otra parte del archivo?** No
  agregues una primitiva nueva: reusá la que ya está.
- **¿Estás reasignando un rol del skin** (p. ej. cambiar a qué primitiva
  apunta `--sn-danger`)? Es la capa semántica. Una línea, sin tocar
  paleta ni componentes.
- **¿Es un acento específico de un widget** (un botón, un campo)? Es la
  capa de componentes; consumí variables semánticas, nunca primitivas
  directas.

Si la primitiva genuinamente no existe (un hue nuevo que el taller
necesita), añadirla con el siguiente stop libre de su familia (50–950)
y dejar comentado dónde se consume.

Para ver las clases editoriales actuales, [`WIKITEXTO.md`](WIKITEXTO.md) §2.
Para ver las variables, [`tokens.css`](../resources/tokens.css) (todas
documentadas en sus comentarios in-place).

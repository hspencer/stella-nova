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
**variable**, dos ejes wght 100–700 + wdth 75–100) · **Source Serif 4**
(serif del cuerpo cuando el lector la elige desde el menú, citas y
`<poem>` por defecto; **variable**, eje wght 200–900) · **IBM Plex
Mono** (código).

Todas auto-alojadas (sin CDN en runtime): `@font-face` en
[`resources/fonts.css`](../resources/fonts.css), archivos `woff2` en
[`resources/fonts/`](../resources/fonts/). Subset `latin` (U+0000-00FF)
cubre el español sin `latin-ext`.

Dos capas de tokens en [`tokens.css`](../resources/tokens.css):
**primitivas** (las dos familias reales) y **semánticas** (alias que
consume el resto del skin, y que el menú del usuario invierte para
alternar la familia del cuerpo entre sans y serif).

- `--sn-font-sans` (primitiva) — IBM Plex Sans.
- `--sn-font-serif` (primitiva) — Source Serif 4.
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
  al cuerpo.

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

Acento único (la *nova*, carmín) en `--sn-nova`; tinta y campo en
`--sn-ink*` / `--sn-field` / `--sn-paper`. Light/dark se resuelven en
[`tokens.css`](../resources/tokens.css) con `prefers-color-scheme`
+ `[data-sn-theme]`:

- **Sin preferencia guardada** → claro (decisión de producto;
  diverge del comportamiento "seguir al SO siempre").
- `data-sn-theme="dark"` → oscuro forzado.
- `data-sn-theme="light"` → claro forzado.
- `data-sn-theme="auto"` → sigue al SO.

Variables Codex / WikimediaUI están aliasadas a los tokens del skin en
el bloque "Capa de compatibilidad Codex" de `tokens.css`: cuando OOUI
pide `var(--color-base, #202122)` lee `var(--sn-ink)` y voltea con el
tema automáticamente. Si añades un nuevo control de OOUI y queda con
color hardcodeado, posiblemente falte un alias ahí.

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

1. ¿Lo cubre un token existente (`--sn-s-*`, `--sn-fs-*`, `--sn-link`,
   `--sn-ink-soft`…)?
2. ¿Lo cubre una clase existente (`.full-width`, `.grilla.cols-N`,
   `.plantilla`, `.img-circle`, `.sn-notice`)?
3. Si la respuesta a ambas es no, conversar antes — no a regañadientes,
   simplemente para mantener coherencia.

Para ver las clases editoriales actuales, [`WIKITEXTO.md`](WIKITEXTO.md) §2.
Para ver las variables, [`tokens.css`](../resources/tokens.css) (todas
documentadas en sus comentarios in-place).

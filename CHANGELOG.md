# Changelog

Todos los cambios notables de **Stella Nova** se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Mientras el skin esté en `0.x`, el versionado es **`0.MINOR.PATCH`**: `MINOR`
sube con cambios de comportamiento o estructura; `PATCH`, con correcciones y
ajustes editoriales. La fuente de verdad del comportamiento es
[`specs/stella-nova.allium`](specs/stella-nova.allium); cada entrada que toque
comportamiento debería reflejarse también ahí.

## [0.6.17] — 2026-07-20

### Added
- **Token `--sn-edit-surface`** (`resources/tokens.css`): superficie propia del
  área de escritura, definida como **lavado** (`color-mix(in oklab,
  var(--sn-ink) 3%, var(--sn-paper))`) y no como peldaño de la escala papel.
  Voltea sola con el tema porque sus dos ingredientes ya voltean, así que no
  necesita override en los selectores `[data-sn-theme]`. La consumen las
  cuatro superficies de escritura: textarea desnudo, textarea envuelto por
  WikiEditor, `.ace-tm` (CodeEditor, que estaba en `--sn-paper`) y el fallback
  FOUC de Ace. Un solo número para calibrar el despegue del papel.

### Changed
- **`--sn-lift` reformulado** (`resources/tokens.css`, `resources/stella-nova.css`):
  el gesto de elevación pasa de sombra difusa a sombra **corta y desplazada**
  — `0 1px 1px` de contacto + `0 8px 6px -3px` de elevación, en vez de los
  `8px 24px` (claro) y la tercera capa de `24px 60px` (oscuro). Blur ~6px y
  spread negativo: el objeto se lee levantado, no rodeado de halo. En oscuro
  sube la opacidad (.45/.6) para compensar el menor desenfoque. Afecta a los
  seis puntos donde se declara el token (base + overrides de tema en
  `tokens.css`; `.fondo-noche`/`.fondo-dia`/media-query en `stella-nova.css`).
  `--sn-lift-paper` y `--sn-lift-soft` **no cambian**. Consumidores: menú de
  usuario, sugerencias de PageForms, jQuery UI, notificaciones, tooltips SMW,
  InlineComments.
- **El textarea de edición se iguala al bloque de código**
  (`resources/stella-nova.css`, `resources/skinStyles/wikieditor.css`,
  `resources/skinStyles/codeeditor.css`): cuerpo **`--sn-fs-sm`** (antes
  `--sn-fs-base`) e interlínea **1.5** (antes 1.65) — los mismos valores que
  `.sn-body pre`, con la misma monoespaciada que ya compartían. Editar
  wikitexto es escribir código, así que el editor hereda la materia del
  código y deja de ser un bloque blanco y grande frente a la
  previsualización. La superficie NO se igualó a la de `pre`: el pozo
  `--sn-sunk` funciona en una caja de cinco líneas pero a pantalla completa
  es una mancha, así que el fondo va por `--sn-edit-surface` (arriba), mucho
  más leve. Cubre las tres rutas: textarea desnudo (CSS/JS/JSON),
  envuelto por WikiEditor, y el fallback FOUC de CodeEditor mientras Ace
  carga. El cromo (toolbar, tabs, cinta de controles) sigue en `--sn-paper`,
  que ahora contrasta con el pozo del textarea.

## [0.6.16] — 2026-07-16

### Added
- **Escala completa de `fw-*`** (`resources/stella-nova.css`): las clases de
  ancho de fuente ahora van **de 10 en 10 entre `fw-50` y `fw-150`** (`fw-50`
  `fw-60` `fw-70` `fw-80` `fw-90` `fw-100` `fw-110` `fw-120` `fw-130` `fw-140`
  `fw-150`), en vez del rango 80–100 de v0.6.14. Los pasos de 5 previos
  (`fw-75` `fw-85` `fw-95`) **siguen publicados** para no romper el wikitexto
  que ya los usa. Motivo del rango declarado: es el eje `wdth` de Roboto Serif
  upstream, y así el wikitexto no hay que reescribirlo si algún día se
  reconstruye la fuente sin recortar el eje.

### Documentation
- **Documentado el clamp de `fw-*`** (`docs/WIKITEXTO.md`, comentario del CSS y
  espécimen), que es la parte no obvia: **la escala declarada es más ancha que
  lo que las fuentes saben renderizar** y el navegador clampa en silencio al eje
  del `woff2`, que **depende de la familia** — IBM Plex Sans `wdth` 75–100 (la
  fuente entera: no tiene ancho expandido, no es el subset), Roboto Serif
  62.5–100 en nuestro build (upstream 50–150; recortado en v0.2.4 para bajar la
  familia de ~1.6 MB a ~0.9 MB). Hoy, en la práctica, **solo 75–100 se ve**.
  Además, **la familia la elige el LECTOR** (preferencia `family`, default sans,
  aplicada por `skin.js` como `data-sn-family`), así que un mismo `fw-130` puede
  clampar para un lector y expandir para otro: fuera de 75–100 el wikitexto debe
  fijar la familia en el elemento (`class="serif fw-130"`).

## [0.6.15] — 2026-07-16

### Fixed
- **Diff en modo oscuro** (`skinStyles/diff.css`, `+mediawiki.diff.styles`): las
  celdas de comparación de revisiones/historial/deshacer/previsualización
  quedaban en cajas blancas ilegibles. El core hornea desde LESS a hex claro
  (`.diff-context{background:#f8f9fa;color:#202122;border:#c8ccd1}` + bordes de
  añadido/quitado) en tiempo de build, así que **no** consume el remap de
  `--background-color-content-*` de `tokens.css`. Se revisten con tokens que
  voltean: contexto=`--sn-sunk`, añadido=`--sn-ok`, quitado=`--sn-danger`,
  ins/del inline y línea vacía=`ok/danger-wash`.
- **Campos "tokens" de PageForms (Select2) en modo oscuro** (`skinStyles/select2.css`,
  `+ext.pageforms.select2.styles`): los `pfTokens` (multiselect Select2) traían
  caja blanca, pills `#e4e4e4` y opción resaltada `#2A4B8D` horneados; Select2 no
  conmuta con el tema, así que solo el texto (hereda `--sn-ink` volteado) se
  aclaraba → texto claro sobre pill claro, ilegible. Se revisten con tokens de
  campo: caja=`--sn-field-*`, pills=`--sn-sunk`/`--sn-hairline`/`--sn-ink`,
  dropdown resaltado=`--sn-on-bg`/`--sn-on-fg`.
- **Ícono de ayuda en modo oscuro** (`skinStyles/helplink.css`, `+mediawiki.helplink`):
  el indicador "?" (`#mw-indicator-mw-helplink .mw-helplink-icon`) es un
  `mask-image` de Codex teñido por `background-color:#222` (horneado oscuro) →
  negro sobre negro. Se re-tiñe con `--sn-icon` (voltea con el tema).

### Changed
- **TOC sin filete** (`resources/stella-nova.css`): se retira el `box-shadow`
  inset propio y se anula el `border:1px solid #aaa` que el core
  (`mediawiki.skinning`) mete dentro de `@media screen` — nuestra regla ganaba en
  especificidad pero no declaraba `border`. La caja queda delimitada solo por el
  relleno hundido. Con `box-sizing:border-box` (global) el borde no afectaba el
  alto exterior, así que la retícula de baseline se mantiene intacta.
- **TOC: toda la barra de título togglea** (`resources/stella-nova.css`): el
  `<label for=toctogglecheckbox>` se estira sobre toda la `.toctitle`
  (`position:absolute; inset:0`), con el cheurón alineado a la derecha. Ahora un
  click en cualquier parte de la barra colapsa/descolapsa el índice, no solo el
  cheurón. Mecanismo nativo del `for`, sin JS.

## [0.6.14] — 2026-07-13

### Added
- **Clases helper de ancho de fuente `fw-*`** (`resources/stella-nova.css`):
  `fw-100 fw-95 fw-90 fw-85 fw-80`, donde `fw-NN` = `font-stretch: NN%` sobre el
  eje `wdth` de las fuentes variables. Opt-in desde wikitexto/plantillas
  (`class="fw-90"`), combinables con los helpers tipográficos. **Motivo:** el
  sanitizador de TemplateStyles (css-sanitizer v5.5.0) solo acepta `font-stretch`
  con palabras clave, no con porcentaje, así que las plantillas no podían
  condensar por `%` en su propio `styles.css`; la skin no está sanitizada y
  expone el ancho como clase. Scope `.sn-body .fw-NN`; `font-stretch` hereda a
  los bloques internos. **Rango 80–100**: el cuerpo ya corre a 80%
  (`--sn-text-width`), que es el piso por diseño → `fw-80` = cuerpo, `fw-100`
  restaura ancho normal; no hay `fw-` bajo 80. Para valores fuera de la escala,
  la plantilla puede usar `font-stretch: var(--prop)` (var() sí pasa el
  sanitizador). Documentado en `WIKITEXTO.md` §2 y demostrado en el espécimen.

## [0.6.13] — 2026-07-13

### Added
- **Token `--sn-baseline-half`** (`resources/tokens.css`, junto a
  `--sn-baseline-2/-3`): `calc(var(--sn-baseline) / 2)`, media interlínea. Existe
  para que las TemplateStyles de la wiki cierren cajas (tarjetas) en un número
  entero de baselines **sin dividir dentro de `calc()`** — el sanitizador de
  MediaWiki no lo admite, así que la división ocurre en la skin y la plantilla lo
  consume como `var()` desnudo. Cuarta regla del bloque "Baseline grid": el
  relleno vertical que compensa media interlínea usa este token, **nunca**
  `--sn-s-*` (fijo en `rem`, no sigue a `--sn-font-scale` → deriva de la
  retícula). Antes las plantillas `Documento miniatura` (`.dm`) y `Listado de
  Cursos` (`.curso-listado`) aproximaban con `--sn-s-3` (0.75&nbsp;rem), corto
  ~0.1–0.24&nbsp;rem por tarjeta, con error acumulado en columnas largas.
  Migración de esas plantillas pendiente **en la wiki** (no en el repo).

### Changed
- **Espécimen** (`scripts/build-specimen.py`): documenta el token nuevo en el
  grupo "Baseline grid" (`index.html`) y añade dos secciones de componentes
  fieles a las plantillas reales —`.dm` (Documento miniatura) y `.curso-listado`
  (Listado de Cursos)— demostrando el relleno `var(--sn-baseline-half) var(--sn-s-3)`
  tal como la wiki lo usará (una columna que cierra en la retícula).
- **Docs**: `DISENO.md` documenta los tokens `--sn-baseline*` y la regla del
  medio baseline en TemplateStyles; `WIKITEXTO.md` corrige la referencia obsoleta
  a Mpdf en `noprint` (el PDF se hace por la previsualización Vivliostyle);
  `README.md` completa la lista de clases opt-in (`fondo-*`, `wiki-btn`).

## [0.4.8] — 2026-06-19

### Changed
- **Menú único de pantalla completa (`.sn-md-fs`) ahora es un _top-sheet_.**
  Antes cubría todo el viewport (`height: 100dvh`); ahora se ancla arriba a
  ancho completo pero ocupa **solo la altura que necesita su contenido** (con
  tope `max-height: 100dvh` y scroll interno si lo excede). Lleva filete
  inferior (`--sn-hairline`) y una sombra suave para despegarlo del lienzo.
- **Enlaces de Navegación del menú de pantalla completa → nav-pills.** La
  sección Navegación (Portada + subgrupos del `Sidebar`) dejó de renderizar
  como lista inline separada por comas y ahora usa las mismas cápsulas
  (`.sn-fs-pills`) que las secciones "Esta página" y "Usuario". Se eliminó el
  bloque CSS muerto `.sn-fs-menu .sn-fs-links`.
- **`h1` del cuerpo ahora en rojo (`--sn-nova`), no en tinta negra.** Iguala el
  color del `firstHeading` (que ya era nova); el `h1` interno (`=…=`) deja de
  pintarse `--sn-ink`.
- **Referencias (`.reference-text`) un grado más pequeñas** (`--sn-fs-sm` →
  `--sn-fs-xs`, tracking `0.0483ex` → `0.03ex`). Además se fija
  `font-size: var(--sn-fs-xs)` en `ol.references` para que la **numeración
  (`::marker`)** herede ese mismo tamaño y deje de verse más grande que el
  texto de la nota.
- **Sección toggle expandida: se retira el borde vertical derecho** (la
  afordancia EXPERIMENTAL de 0.4.7). Al expandir, cabecera y cuerpo siguen
  pegados y sin filete inferior (se leen como un bloque), pero ya no comparten
  el borde `--sn-hair` por la derecha ni el `padding-right` que lo despejaba.

### Added
- **Click fuera del menú de pantalla completa lo cierra.** Al ser ahora un
  top-sheet hay un "fuera" debajo: una activación (click/tap) sobre el lienzo
  cierra el menú, además del botón ✕ y de Escape. Realiza el invariante
  `DismissableByOutsideActivation` de `TransientPanel`, antes excluido para
  `.sn-md-fs` por presentarse a viewport completo.

### Fixed
- **Flecha de retorno (`↑`) de las referencias reaparece en pantalla.** La regla
  `.mw-cite-backlink { display: none }` provenía del módulo `ext.cite.print`
  (servido solo en `@media print`), pero al capturar el snapshot de Cite se
  perdió el envoltorio `@media print` y el backlink quedaba oculto también en
  pantalla — sin forma de volver desde la nota a la cita en el texto. Restaurado
  el `@media print`: la flecha se ve en pantalla y solo se oculta al imprimir.

## [0.4.7] — 2026-06-19

### Added
- **Afordancia de estado expandido en las secciones colapsables (EXPERIMENTAL).**
  Cuando el `.mw-collapsible` hermano deja de estar `.mw-collapsed`: (1) el filete
  inferior de la cabecera desaparece, y (2) cabecera y cuerpo comparten un borde
  vertical derecho (`var(--sn-hair)`, misma ley que el filete y el `<hr>`) que
  corre continuo y los aúna como bloque, sin fondo ni esquinas redondeadas.
  Marcado EXPERIMENTAL en el CSS; puede revertirse.

### Changed
- **Icono de cabecera toggle al expandir:** pasa de `minus` a `arrow-down`
  (flecha completa) — "esto está abierto / hay contenido debajo".
- **Placeholder del buscador de la barra superior:** ahora usa `--sn-hairline`,
  el mismo color que el borde del campo (antes `--sn-ink-faint`).

### Fixed
- **Enlace "Herramientas" del pie desalineado verticalmente** respecto a los
  enlaces de sitio de su misma fila. Raíz: el `<summary>` es `inline-flex` con
  `align-items: center`, así que ningún item exponía línea base y el contenedor
  sintetizaba su baseline desde el borde de la caja (que el icono de 13px hacía
  más alta que el texto). Se cambia el summary y `.sn-foot-places` a
  `align-items: baseline` (el icono se recentra con `align-self: center`) y la
  fila del grid `.sn-foot-line` a `align-items: baseline`. Sin nudges en px:
  escala con la tipografía.

## [0.4.6] — 2026-06-19

### Added
- **Filete inferior en las cabeceras de sección colapsables.** La cabecera que
  contiene `.title-toggle` dibuja un `::after` a todo el ancho, asentado dentro de
  su `margin-bottom` (centrado en el hueco de 1 baseline), para distinguir los
  títulos "que abren algo" sin gastar una fila de la retícula. Reemplaza a los
  `<hr>` entre secciones, que metían un baseline propio y descuadraban el grid.

### Changed
- **Aro de hover del botón de pantalla completa (`.sn-fs-trigger::after`):** pasa
  de un hilo sólido (~0.75px, recortado con `mask` radial) a un `border: 2px
  dotted var(--sn-nova)`. Más legible como afordancia y más simple de mantener.

### Fixed
- **Switch de Familia (tipografía) más chato que los de Tema y Tamaño en el menú
  de usuario.** Los segmentos de Tema (`.sn-seg-icon`) y Tamaño (`.sn-seg-sz`)
  recibían `min-height` + centrado flex, pero el de Familia (`.sn-seg-fam`) no, y
  encima su `padding: 0` lo achataba. Se mueve el alto uniforme y el centrado a la
  base `.sn-seg button` (`min-height: 1.9rem`, padding vertical 0 dominado por el
  min-height) para que los tres switches queden igual de holgados sin importar el
  alto del glifo.

## [0.4.5] — 2026-06-17

### Fixed
- **Divisor colgando al final del menú de Página (barra superior).** El último
  grupo (`data-variants`, cuando la página no tiene variantes de idioma) se emite
  como `<ul class="sn-mm-grp"></ul>` vacío pero seguía contando como
  `.sn-mm-grp + .sn-mm-grp` y arrastraba el `border-top`, dejando un filete sin
  nada debajo. Se ocultan los grupos vacíos (`.sn-mm-grp:empty { display:none }`).
- **El canvas full-width de la portada no topaba arriba (bleed-top no disparaba).**
  La portada corre en modo pantalla completa y su hero es el Widget P5
  (`<div id="p5" class="full-width">`). El Widget emite su `<script>` inline y MW
  lo envuelve en un `<p>` que queda como `:first-child` de `.mw-parser-output`,
  justo antes del canvas. Ese `<p>` es invisible pero **no** es `mw-empty-elt`
  (contiene `<script>`, no es whitespace puro), así que ni la regla base de
  bleed-top ni la variante `mw-empty-elt` (0.4.4) disparaban: el bleed horizontal
  funcionaba pero el vertical no, dejando el canvas a `--sn-paper-py` del borde.
  Se añade una variante que reconoce el `<p>` líder solo-scripts vía
  `p:first-child:has(> script):not(:has(> :not(script)))` y aplica el mismo
  `margin-block-start` negativo + radios de esquina. El `:not(:has(…))` evita el
  caso legítimo «párrafo de texto + imagen full-width a media página».
  Como el `<p>` de scripts **no** es `display:none` (a diferencia de
  `.mw-empty-elt`), seguía ocupando caja y dejando el hueco aunque el margen
  negativo aplicara; se le añade `display:none` (el `<script>` se ejecuta igual)
  para que el `.full-width` sea el primer elemento de flujo y el bleed alcance el
  borde.

### Changed
- **Disparador del menú a pantalla completa (`.sn-fs-trigger`).** Se elimina el
  halo blanco fijo (`drop-shadow` rgba blanco) que no escalaba con el fondo ni
  con claro/oscuro. El glifo de la constelación pasa a ser el **negativo del
  cielo**: `backdrop-filter: invert(1)` invierte el backdrop real (lienzo P5,
  órbitas, papel) y un `mask` con la silueta de la constelación lo recorta —
  oscuro sobre fondo claro, claro sobre fondo oscuro, color complementario sobre
  las órbitas. Contraste garantizado sin variante por tema. (Se descartó
  `mix-blend-mode: difference`: queda atrapado en el stacking context del
  `.sn-fs-md` fijo y blendea contra transparente, no contra el lienzo —
  verificado en headless. `backdrop-filter` sí muestrea el backdrop compuesto a
  través del `fixed`.) Fallback temático plano (`currentColor`/`--sn-ink`) bajo
  `@supports` para navegadores sin `backdrop-filter`.
  El hover ya no tiñe el glifo de rojo. La afordancia de hover son DOS capas
  circulares (110% del botón vía `inset` negativo, entran escalando): un
  **frost** sin relleno de color (`::before` con `backdrop-filter: saturate(1.6)
  blur(2px)`, el mismo cristal de la barra de menú, que se nota aunque no haya
  disco) y, encima, un **aro finísimo** (~0.75px) en `--sn-nova` (`::after`,
  color recortado a anillo con `mask` radial). (Se descartaron los rellenos
  opacos previos: `--sn-field` al 60% caía en el gris medio sobre el lienzo
  casi-negro y, al invertirlo el glifo, daba contraste nulo; un relleno oscuro
  arreglaba el lienzo oscuro pero pesaba sobre fondos claros — de ahí el frost
  sin color.)

## [0.4.4] — 2026-06-17

### Fixed
- **`<p class="mw-empty-elt">` de Widgets abría hueco y rompía el bleed-top.** Los
  Widgets emiten un salto de línea inicial y MW deja un `<p>` vacío como primer
  hijo de `.mw-parser-output`, desplazando al `.full-width` del slot `:first-child`.
  Se reconoce el patrón `p.mw-empty-elt:first-child + .full-width` en cada nivel de
  wrapper para que el bleed-top siga disparando.

## [0.4.3] — 2026-06-15

### Fixed
- **Fichas (`table.plantilla`/`.template`) volvían a ancho de contenido.** La
  regla de tablas de datos responsivas (`table.wikitable…{display:block}`)
  alcanzaba también a las fichas (que son `wikitable` + `plantilla`); con
  `display:block`, el `width:100%` solo estiraba la caja y las celdas se
  encogían. Se reafirma `display:table` en las fichas verticales clave→valor
  (no necesitan scroll horizontal) para que llenen el 100% otra vez.

## [0.4.2] — 2026-06-15

### Changed
- **Pie de miniatura de galería (`.gallerytext`).** Baja al grado más pequeño
  del skin (`--sn-fs-xs`), ganando al `font-size: 94%` del core por
  especificidad (`.sn-body .gallerytext`).

## [0.4.1] — 2026-06-15

### Added
- **Tablas de datos responsivas.** Las tablas anchas (`wikitable`, `smwtable`,
  `broadtable`) se vuelven una caja de scroll horizontal propia en viewport
  angosto (`display: block; overflow-x: auto`), con ancho mínimo de celda
  (`min-width`) y sin partición de palabra dentro de celdas. En teléfono ya no
  se estrujan apilando el texto letra a letra; el scroll vertical de la página
  no se ve afectado.

### Changed
- **Metadatos en `Special:Version`.** El autor pasa a la columna *Authors* como
  enlace con su filiación (e[ad] Escuela de Arquitectura y Diseño, PUCV); la
  descripción (`stellanova-desc`, es/en) se reescribe sin el nombre del autor y
  conservando el enlace al repositorio.

## [0.4.0] — 2026-06-13

### Added
- **Marcos de imagen, miniaturas y galerías en modo oscuro.** Afinado del
  tratamiento de imágenes (marcos, thumbnails y galerías) bajo tema oscuro.

## [0.3.1] — 2026-06-12

### Added
- **Grilla `flujo-v` en columnas (multicol).** El modificador de pila vertical
  ahora fluye su contenido en columnas reales, y se permite posicionar
  imágenes dentro del flujo.
- **Pie y cromo del core afinados.** Vestimenta Stella Nova para
  notificaciones (Echo), leyendas de páginas especiales, el escritorio y el
  menú «Herramientas».

### Changed
- **Cuerpo de las referencias (`.reference-text`).** Vuelve al ancho pleno
  (`font-stretch: 100%`) frente al cuerpo condensado del skin, baja al grado
  `--sn-fs-sm` y suma un pelo de tracking (`letter-spacing: .0483ex`) sobre
  `--sn-ink`.

### Fixed
- **`full-width` bleed-top con `<style>` líder de TemplateStyles.** Cuando el
  contenido arranca con un `<style>` inyectado por `<templatestyles>`, ese
  nodo ocupaba el `:first-child` y rompía la cadena del sangrado superior. Un
  selector `style:first-child + *` reconoce el `<style>` líder y dispara el
  bleed-top sobre la imagen-hero que le sigue.

## [0.3.0] — 2026-06-10

### Added
- **`grid` / `grilla` como framework de layout.** La mini-grilla utilitaria se
  amplía a un sistema de layout semántico con modificadores combinables:
  `cols-1…6` y nuevo `cols-auto` (auto-fit de tarjetas ≥ 16 rem), `cols1-2` /
  `cols2-1` (tercios), `gap-0/s/m/l` (espaciado por instancia vía
  `--sn-grid-gap`), `flujo-v` / `stack` (pila vertical), `align-top/center/
  bottom/baseline` (+ alias `arriba/centro/abajo`), `sin-margen` / `flush`
  (margen) y `full` / `completa` (full-bleed a todo el campo, técnica de
  `.full-width`).

### Changed
- **Nombres de clase bilingües.** Se añaden alias en inglés como nombre
  canónico, manteniendo el español por retrocompatibilidad (nada se rompe en
  páginas existentes): `.grid` ↔ `.grilla`, `table.template` ↔
  `table.plantilla`. Los selectores pasan a `:is(.grid, .grilla)` y
  `table:is(.template, .plantilla)`. (La magic word `__FULLSCREEN__` ya existía
  junto a `__PANTALLACOMPLETA__`.)
- **`__PANTALLACOMPLETA__` — contenido absolutamente libre.** El cuerpo
  (`.sn-canvas-body`) deja de centrarse y limitarse a `--sn-shell`: ocupa todo
  el canvas, con el único margen del padding básico. El pie de pantalla
  completa (`.sn-fs-footer-inner`) pasa de centrado a la lectura a **alineado a
  la izquierda** con el mismo margen básico. La prosa ya no se acota al ancho de
  lectura: se maqueta con el framework `grid`.
- **Enlaces rojos en ambos temas.** En modo oscuro los enlaces dejan de ser
  azules y pasan a coral rojo (`--sn-coral-400`); el `:hover` aclara y el
  `:visited` es un coral apagado (mezcla con negro), levemente más oscuro que el
  enlace base, igual que en claro (vino `--sn-rojo-900`).
- **Páginas inexistentes en rosado pálido.** Los redlinks (`a.new`) usan un
  rosa pálido en ambos temas (`--sn-rosa-400` en claro, `--sn-rosa-300` en
  oscuro), reemplazando el gris apagado (claro) y el coral (oscuro). No se
  oscurecen al visitarse (`a.new:visited` mantiene el rosa).
- **Pie del color de la hoja.** `.sn-footer` toma el tono de la hoja
  (`--sn-paper`) en lugar del campo (`--sn-field`); más notorio en modo oscuro,
  donde página y pie quedan del mismo color.

## [0.2.9] — 2026-06-09

### Added
- **Achicado de tablas unificado por token.** Nuevo `--sn-fs-table`
  (`calc(--sn-fs-base * .8)`, ≈80% de base, ABSOLUTO): única fuente del tamaño
  de todas las tablas de contenido. `table.plantilla` y
  `wikitable/smwtable/broadtable` lo comparten (antes la ficha iba a
  `--sn-fs-xs` y las generales a `80%` relativo, que componía en anidación).
- **Affordance de colapso en cabeceras de sección.** Las secciones colapsables
  (`mw-customtoggle` + `.title-toggle`) muestran un signo feather `+`/`−` tras
  el título según estado, con `:hover`. Se keyea con `:has(+ .mw-collapsible…)`
  sobre el colapsable hermano, porque `makeCollapsible` no marca el toggler
  a medida con clases de estado.
- **Disclosure animado genérico.** Todo `<details>` del skin anima
  apertura/cierre vía `::details-content` + `interpolate-size: allow-keywords`
  (degrada a toggle instantáneo donde no haya soporte; la duración se apaga con
  `prefers-reduced-motion` vía `--sn-motion`).

### Changed
- **`.plantilla` afinada.** Cabeceras `th` en gris neutro, `font-weight: 355`,
  sin el padding que desalineaba el texto con la fila; tamaño y line-height
  reajustados. `.smwpre` (p. ej. campo Código) despojado a texto monospaced
  del skin, sin la caja/borde/fondo `#f9f9f9` que le pone SMW.
- **Pie — primera columna tipográficamente uniforme.** Herramientas, enlaces de
  sitio, licencia y el summary leen igual que `.sn-foot-lastedit`
  (`--sn-fs-xs`, peso 400, stretch normal). El toollist ya no añade margen al
  expandir, que rompía la interlínea.
- **Menú de pantalla completa — enlaces de navegación.** `enlace + ','` se trata
  como unidad indivisible (enlace `white-space: nowrap`, coma pegada en el
  `::after` con espacio ESCAPADO `\0020` para sobrevivir al minificador de
  ResourceLoader); ninguna fila empieza con coma. Tamaño y `font-stretch`
  igualados con los nav-pills (`--sn-fs-xs`).
- **Enlaces a páginas inexistentes (`a.new`) menos pálidos** en claro:
  `--sn-link-new` sube de 42% a 55% de opacidad.
- **Barra superior en móvil: íconos equidistantes.** Los grupos se aplanan con
  `display: contents` para que cada ícono sea ítem directo de la barra y
  `space-between` los reparta con gaps iguales.

### Fixed
- **Menús y búsqueda modales en móvil que congelaban la página.** El
  `backdrop-filter` del header sticky lo convertía en bloque contenedor de los
  modales `position: fixed`, que se abrían fuera del viewport (anclados al
  origen del sticky) con el scroll bloqueado al estar desplazado hacia abajo.
  Se anula el filtro mientras hay un modal abierto (`html[data-sn-modal]`), así
  el `fixed` vuelve a ser relativo al viewport.
- **`<hr>` con caja gris `#aaa` del core.** El separador del menú
  (`.sn-menu-sep`) neutraliza `height`/`background` del `hr` por defecto de
  `elements.less`; deduplicada la regla `.sn-body hr`.

## [0.2.8] — 2026-06-08

### Added
- **Formularios HTMLForm legacy tokenizados** (`skinStyles/htmlform.css` ←
  `+mediawiki.htmlform.styles`). `Especial:SubirArchivo` y demás páginas no-OOUI
  rendían el form con los controles por defecto del navegador; ahora: `<fieldset>`
  sin recuadro, `<legend>` en versalitas, campos `--sn-field-*`, file picker y
  botón de envío con `--sn-btn-*` (envío = primario), casillas con
  `accent-color: --sn-nova`, pistas en voz secundaria. Acotado a
  `.mw-htmlform:not(.mw-htmlform-ooui)` para no tocar los forms OOUI.

## [0.2.7] — 2026-06-08

### Changed
- **Pie: «Herramientas» como disclosure nativo en toda página.** El pie normal
  envuelve las herramientas en `<details>`/`<summary>` NATIVO (sin JS, como el
  de pantalla completa) al comienzo de la línea de enlaces de sitio; antes iban
  siempre expandidas y un intento con toggle JS solo rendía donde el módulo
  estaba fresco. En `.sn-footer-main` el `<details>` es `column-reverse` para
  que la lista crezca hacia arriba; el toollist pasa al mismo tamaño que los
  enlaces de sitio.

## [0.2.6] — 2026-06-08

### Added
- **Editor de CSS/JS/JSON tokenizado.** `skinStyles/edit.css` (←
  `+mediawiki.action.edit.styles`) reparte el cromo del core del editor
  (`.editOptions`, `.mw-editTools`, `.previewnote`, `.templatesUsed`,
  `#wpSummary`), antes mal anclado en `wikieditor.css` (solo cargaba en
  wikitexto). `skinStyles/codeeditor.css` (← `+ext.codeEditor.styles`) reescribe
  la paleta Ace `.ace-tm` con `light-dark()` y la conmuta por `[data-sn-theme]`,
  sin depender de la detección rota de CodeEditor. El `<textarea>` `#wpTextbox1`
  trae su marco tokenizado y lo cede cuando WikiEditor lo envuelve.

## [0.2.5] — 2026-06-06

### Added
- **Pie en pantalla completa (`__PANTALLACOMPLETA__`).** Antes el modo
  canvas no tenía pie; ahora lleva uno sobre el mismo papel, al ancho de
  lectura (`--sn-measure`), en una sola columna a todo el ancho (sin columna
  derecha ni "última edición"). Herramientas en un `<details>` discreto
  rotulado «Herramientas» (mensaje nuevo `stellanova-tools`), luego enlaces
  de sitio y licencia.
- **Licencia de la wiki en el pie.** Tras los enlaces de sitio
  (`.sn-foot-places`) se muestra el copyright de MediaWiki (item
  `footer-info-copyright` del grupo `data-info`, que respeta `$wgRights*`),
  expuesto como `sn-license` en `getTemplateData()` y renderizado como
  `<p class="sn-foot-license">`. Sin la fecha de última modificación (el
  skin ya la emite aparte como `sn-lastedit`). Si no hay licencia
  configurada, la sección no se pinta.

### Changed
- **Formularios (PageForms) armonizados.** Las etiquetas `<th>` van a la
  derecha y a `--sn-fs-xs` — con prefijo `.skin-stellanova` para ganarle a la
  regla propia de PageForms `.formtable th { text-align: left }` (misma
  especificidad, ganaba por orden). Los checkboxes/radios (`.checkboxLabel`,
  envueltos en widget OOUI): etiqueta a `--sn-fs-xs`, AIRE entre la casilla y
  el texto (el `&nbsp;` solo no bastaba) y separación entre opciones. Los
  campos: `box-sizing: border-box`, alto uniforme (`min-height: --sn-ctl`) en
  los de una línea, y `max-width: 100%` en todo. La causa de los desbordes
  era `table-layout: auto`: un input con `size=100`/`size=35` o un token con
  `width:600px` inline estiraba su columna más allá del 100% y arrastraba la
  tabla fuera de la página; se fija con `table-layout: fixed` + columna de
  etiqueta al 28%, de modo que cada campo se acota a su celda.
- **Editar con formulario sin perder el menú de página.** El lápiz de
  edición con formulario (PageForms) ahora enlaza a la acción `formedit`
  sobre el PROPIO artículo (`?action=formedit`) en vez de a
  `Especial:FormEdit/<form>/<page>`. La página especial es otro título y
  perdía las pestañas del artículo (espacios, historial, "Editar código"…);
  la acción in-page conserva el contexto completo del artículo, incluido
  "Editar código" en el menú `.sn-pagemenu`.
- **`__PANTALLACOMPLETA__` ya no implica ocultar el título.** Antes la rama
  de pantalla completa nunca renderizaba el título; ahora lo muestra salvo
  que la página declare además `__NOTITLE__` (control explícito, más limpio).
  El skin lee la page-prop `notitle` (`Hooks::onOutputPageParserOutput` →
  `stellanova-notitle` → dato `sn-notitle`) y la plantilla omite el título
  solo en ese caso; así un hero `.full-width` con `__NOTITLE__` sigue siendo
  el primer hijo y conserva su bleed a tope. El estilo de `firstHeading` se
  extiende a `.sn-canvas`. La sección Usuario del menú de pantalla completa
  incorpora los controles de lectura (Tema · Tamaño · Familia).
- **Pantalla completa: isotipo sobrepuesto y menú traslúcido.** El isotipo
  (única afordancia) ya no vive en una "barra fantasma": su riel
  (`.sn-fs-md`) es ahora un contenedor fijo, full-width, `pointer-events:
  none`, alineado a la columna de lectura, que deja el glifo SOBREPUESTO y
  EN FRENTE del contenido (un hero `.full-width` queda a tope arriba y a los
  lados, con el glifo encima, un poco más abajo del borde). El glifo
  conserva su tamaño (2.5rem) y gana un "cuño seco" (`drop-shadow` blanca
  dura 1px). El menú desplegado pasa a traslúcido con `blur`+`saturate`
  (mismo lenguaje que la barra superior); el buscador del modal usa el mismo
  input tipo pill que la barra y las pills van un punto más chicas.
- **Categorías del pie redistinguidas por estado.** La que existe: fondo
  igual al campo fuera de la hoja (`--sn-field`) y texto en color de enlace
  (`--sn-link`). La que no existe (redlink `a.new`): fondo muy pálido casi
  blanco (`color-mix(--sn-ink 5%, --sn-paper)`) y texto gris claro
  (`--sn-ink-faint`).
- **La skin es dueña del estilo de TODAS las tablas.** Sistema unificado
  para tablas regulares (`wikitable`) y de resultados semánticos
  (`smwtable`/`broadtable`): sin contorno exterior, solo filetes
  horizontales — filete normal (`--sn-hairline`) bajo las cabeceras y
  filetes muy finos (`--sn-hairline-soft`) entre filas, nunca verticales;
  texto al 80% del cuerpo y alineación a la izquierda en celdas y
  cabeceras. El estilo visual de las tablas SMW se centraliza en
  `stella-nova.css`; `skinStyles/smw.css` conserva solo el desbordamiento
  por contenedor. La ficha vertical `table.plantilla` se porta desde
  `MediaWiki:Common.css` a la skin (etiqueta a la derecha, versalita
  tenue, sin filetes).
- **Cabeceras ordenables con íconos Feather y hover.** Se reemplaza el
  cromo de flechas de `jquery.tablesorter` (SVG `sort_*.svg` del core, con
  variantes invertidas para oscuro) por chevrons Feather pintados como
  `mask` + `background-color` tokenizado — se adaptan solos a claro/oscuro.
  Estado neutro = doble chevron tenue (afford. de ordenable); activo =
  chevron arriba (ascendente) / abajo (descendente) a tinta plena. Las
  `th.headerSort` ganan estado `:hover`.
- **Tablas alineadas al baseline grid.** El `line-height` de celda pasa de
  `1.65` unitless (que con el font al 80% daba `0.8 × baseline` por línea,
  fuera de retícula) a `--sn-baseline` absoluto: cada línea de celda ocupa
  un baseline y toda fila —de una o varias líneas— cae en la grilla. El
  padding vertical se anula (el aire lo da el medio-interlineado del
  baseline) y los filetes pasan de `border` a `box-shadow inset` para que
  el 1px no ocupe layout ni desplace la retícula fila a fila. Margen de
  bloque de la tabla = `--sn-baseline-2`. Alto mínimo de celda = 1
  baseline.
- **Verso (`<poem>`) con voz editorial propia.** Deja de compartir el
  tratamiento de la cita: ahora usa columna más estrecha que el cuerpo
  (`--sn-poem-width: 77%` vía `font-stretch`), tamaño algo menor
  (`--sn-poem-size: 85%`, % del cuerpo → respeta la preferencia FontSize) y
  peso medio (`--sn-poem-weight: 500`). `line-height` sigue en el baseline
  para no romper el ritmo. La cita (`<blockquote>`) se mantiene a ancho
  natural. Tres tokens nuevos `--sn-poem-*` agrupan el ajuste.
- **Chrome sin filetes (doctrina "sin reglas horizontales").** Se eliminan
  las tres líneas finas horizontales que el skin dibujaba de forma
  automática en cada página: el `border-bottom` de la barra superior
  (`.sn-header` — ahora se separa del cuerpo solo por el fondo translúcido +
  `blur`), el `border-top` sobre la sección de categorías (`.catlinks` — la
  separación la da el aire `margin-top`/`padding-top`) y el `border-top` del
  pie (`.sn-footer` — se distingue por su fondo y `margin-top`). Las
  cabeceras de sección (`== ==`) y el título de página ya estaban libres de
  filete (reset de `.sn-body`/chrome sobre el `1px solid #aaa` del core); se
  conservan los separadores funcionales internos de los overlays (cabecera
  del modal de menú y barra de búsqueda a pantalla completa).

## [0.2.4] — 2026-06-06

### Changed
- **Serif del skin: Source Serif 4 → Roboto Serif** (cambio global; se
  regeneró todo, incluido el especimen). Roboto Serif es **variable de
  cuatro ejes**: peso `wght 100–900`, ancho `wdth 75–100`, óptico
  `opsz 8–60` y grado `GRAD −50–100`. La woff2 se construyó desde el TTF
  OFL de Google Fonts con `fonttools`, subset latin (U+0000-00FF), e
  **instanciando** `opsz`/`wdth` de sus rangos completos (8–144 / 50–150)
  a los que el skin realmente usa, para no cargar masters de despliegue ni
  anchos extremos (la familia bajó de ~1.6 MB a ~0.9 MB). Normal e itálica
  reales. Archivos `robotoserif-latin-wghtwdthgrad-{normal,italic}.woff2`;
  se retiraron los `sourceserif4-latin-wght-*.woff2`.
- **El cuerpo serif ahora condensa con el sans.** A diferencia de Source
  Serif 4 (sin eje de ancho), Roboto Serif declara `wdth 75–100` —el mismo
  rango que IBM Plex Sans—, así que `--sn-text-width` (default 80%) aplica
  por igual elija el lector sans o serif. Las citas y `<poem>` se resetean
  a `font-stretch: 100%` para leer el contraste a ancho natural en ambos
  modos.

### Added
- **Token `--sn-serif-grade` (eje GRAD de Roboto Serif).** Engrosa el trazo
  de la serif sin mover la caja del texto. Aplicado a toda la cascada vía
  `font-variation-settings: "GRAD"` en `:root` (sans y mono ignoran el eje
  inexistente). `0` en tema claro; **`30` en oscuro** para compensar el
  aclaramiento óptico del texto claro sobre fondo negro (quinto token
  no-color que varía por tema, junto a `--sn-field-grain` y los tres
  `--sn-lift*`).

## [0.2.3] — 2026-06-03

### Changed
- **Sistema de tokens en tres capas (refactor de `tokens.css`).** Material 3
  aplicado al sistema cromático: **primitivas** (paleta agnóstica del tema,
  nombrada por hue en castellano de taller: `papel`, `tinta`, `rojo`,
  `coral`, `azul`, `malva`, `verde`, `masking`, `blanco`; stops 50–950
  donde el número crece con la oscuridad), **semánticas** (roles del skin:
  `--sn-paper`, `--sn-ink`, `--sn-nova`, `--sn-link`, … cada rol → una
  primitiva por tema vía `light-dark()`) y **componente** (`--sn-btn-*`,
  `--sn-field-*`, capa Codex/WikimediaUI: consumen semánticas, nunca
  primitivas). 36 primitivas para 22 roles semánticos de color. Sin
  renombres ni eliminaciones en los nombres públicos del skin: capa
  primitiva **puramente aditiva** por debajo.
- **Conmutación de tema con `light-dark()`.** Los dos bloques duplicados de
  modo oscuro (`[data-sn-theme="dark"]` + `@media (prefers-color-scheme:
  dark) [data-sn-theme="auto"]`, 14 declaraciones idénticas con riesgo de
  desincronización) se reducen a tres líneas de `color-scheme`. El mapeo
  rol → primitiva por tema vive una sola vez en `:root`. Quedan duplicadas
  sólo las 4 declaraciones no-color (grano del campo + tres sombras) que
  varían geometría además de color con el tema.
- **`--sn-nova` claro unificado con `--sn-link` claro** (`#b22f1e` →
  `#ae2d13`). La diferencia de 4 puntos en R era imperceptible; el carmín
  del foco/firstHeading y el del link son la misma sangre en claro. En
  oscuro siguen divergiendo a propósito (nova = coral cálido, link = azul
  frío) para preservar identidad y afordancia de link.
- **`--sn-nova-ink` y `--sn-warn-ink` oscuros unificados** (`#1a0b0d` y
  `#1a140a` → `#1a0f0b`, promedio). Ambos eran "casi-negro cálido para
  texto sobre acento saturado"; un solo color cubre los dos casos.

### Added
- **`docs/DISENO.md`**: sección "Color" reescrita para documentar las tres
  capas (qué es cada una, cuándo tocar cuál) y los nombres de la paleta.
  Nueva guía en "Antes de añadir un token" sobre cómo elegir la capa
  correcta.
- Espécimen regenerado con secciones nuevas (`Primitiva · papel`,
  `Primitiva · tinta`, …) que listan los 36 swatches navegables; los
  grupos semánticos quedan visibles aparte para diferenciar las capas a
  primera vista.

## [0.2.1] — 2026-06-02

### Added
- **Íconos del pie para herramientas de usuario/admin**: `t-contributions`
  (user-plus), `t-log` (file-text), `t-blockip` (user-x), `t-userrights`
  (users) y `t-smwbrowselink` (book-open). Cinco símbolos Feather nuevos en
  el sprite (`SnIcons.mustache`).
- **`skinStyles/jquery.ui.css`**: re-tematiza los diálogos de jQuery UI
  (tema "smoothness") usados por WikiEditor — Buscar/Reemplazar, Insertar
  tabla, Insertar enlace/archivo. Fuera Verdana y texturas PNG; superficies,
  campos y botones por tokens del skin. Iconos PNG (cerrar, resize) se
  invierten en oscuro.

### Changed
- **`.wiki-btn`** afinado: borde 1px (era 2px), forma de píldora, padding
  mayor, **todo color tokenizado** y variante `.blue` **eliminada** (sin token
  equivalente, sin uso). Ahora voltea claro/oscuro.
- **`.sn-subtitle`** en versalitas: `text-transform: uppercase`,
  `font-stretch: condensed`, `letter-spacing`.
- **Enlaces visitados en oscuro** más sobrios: `--sn-link-visited`
  `#c2a6e0` → `#a99cae` (lila grisáceo apagado).

### Fixed
- **El logo NUNCA se ve morado.** El `<svg>` del isotipo se colorea directo
  con `--sn-icon` en vez de heredar del `<a>`: los navegadores ignoran
  colores con alfa en `:visited`, y el logo caía al morado de enlace
  visitado. El SVG no es enlace → inmune al estado link/visited.
- **WikiEditor en modo oscuro**: fondo de la toolbar tokenizado
  (`--sn-sunk`), íconos OOUI (SVG monocromos por `background-image`)
  invertidos con `filter` en oscuro, y arreglo de cascada — los overrides
  perdían por orden de fuente ante el módulo grande `ext.wikiEditor`; ahora
  prefijados con `.skin-stellanova` para ganar siempre. Bordes a
  `--sn-hairline`, textos negros `#222` a `--sn-ink`.
- **Sin azul en el cromo del editor.** Links de toolbar/booklet/copyright y
  acentos OOUI `progressive` (botones Guardar/Previsualizar) redefinidos a
  la **nova** en el scope del editor; el azul de `--sn-link` queda solo para
  enlaces de contenido.
- **Filete `#aaa` de core bajo h1/h2** neutralizado también en la chrome
  (pie editable, modales, drawer), no solo en el cuerpo del artículo.

## [0.2.0] — 2026-06-02

### Changed
- **El logo del skin SIEMPRE gana.** Se retiró el override de `$wgLogos`
  (`WikiOverride`): el isotipo embebido del skin se usa siempre, ignorando
  LocalSettings. En producción `$wgLogos` traía el logo del skin viejo y
  tapaba el de Stella Nova.

### Fixed
- **Cache-busting de la CSS crítica, sin acceso al servidor.** La CSS del skin
  ya no viaja en el `<link>` combinado de MediaWiki (que va **sin `version`** y
  una caché HTTP por-URL servía rancio hasta 1 h tras cada deploy, rompiendo las
  fuentes). Ahora la carga `Hooks::onBeforePageDisplay` con su propio `<link>`
  cuyo `version` = hash de contenido de ResourceLoader → caché larga inmutable
  (30 días) **y** bust automático en cada cambio de CSS. `skin.json` `styles`
  queda vacío a propósito.

### Added
- **`.wiki-btn`** (botón de contenido outline, variantes red/green/blue)
  migrado desde `Common.css` de producción al tema, tokenizado (azul literal).
- **Especimen**: documentación de las clases de wikitexto `.full-width`,
  `.wiki-btn` y `.grilla`.
- **`CHANGELOG.md`** y **`CONTRIBUTING.md`**.
- Spec Allium sincronizada con el código (prefs 5→2, aviso descartable
  `SiteNotice`, favicon, logo siempre-skin); `allium check`/`analyse` sin
  findings.

## [0.1.0] — 2026-06-01

### Added
- **Rutas de assets robustas al nombre de carpeta.** Los módulos
  `skins.stellanova.styles` / `.scripts` se registran en PHP
  (`Hooks::onResourceLoaderRegisterModules`) calculando su `remoteSkinPath` del
  directorio real donde el wiki sirve el skin. Basta clonar en cualquier
  carpeta (`StellaNova`, `stella-nova`, symlink) y las URLs de las fuentes
  resuelven solas.

### Changed
- El enlace de patrullaje nativo de MediaWiki ("Marcar esta página como
  verificada", `div.patrollink > button.cdx-button`) se re-viste como nav-pill,
  acotado a `.patrollink` para no alterar otros botones Codex.
- `skin.json` deja de declarar `ResourceModules` / `ResourceFileModulePaths`
  (ahora en PHP). Docs (README, ARCHITECTURE, DEVELOPMENT) actualizados.

## [0.0.9] — 2026-06-01

### Added
- **Favicon definido desde el skin** (`resources/favicon.svg`), autocontenido y
  adaptable claro/oscuro, inyectado sin tocar `$wgFavicon`.
- **Aviso de sitio descartable** (`Stella-Nova:Aviso`): banda full-bleed como
  primer elemento de la hoja, con botón de cerrar. El descarte se recuerda **por
  versión de revisión** (al editar el aviso, reaparece) y es por-navegador;
  oculto sin parpadeo vía pre-pintado.

### Changed
- **Preferencias de lectura: de panel aparte → sección del menú de usuario.**
  Reducidas a **tema** (claro/auto/oscuro, íconos sun/clock/moon) y **tamaño de
  letra** (S/M/L). Se retiraron como preferencia el índice, las secciones
  colapsables (eran *stubs* sin efecto) y el toggle de movimiento.
- El buscador inactivo recibe un filete tenue.
- Estilos de impresión: márgenes de página, sin menú superior ni pie.
- Pie: enlaces de sitio movidos a la columna principal; toolbox como enlaces
  comunes con ícono Feather.

### Fixed
- **Fuentes IBM Plex Sans versionadas en git.** La build variable de dos ejes
  (`plexsans-latin-wdthwght-*.woff2`) no estaba trackeada: al clonar, el tema
  caía a la fuente de sistema. Se versionó y se retiró la build `wght`-only.

### Removed
- Movimiento reducido como preferencia de usuario (se mantiene el respeto a
  `prefers-reduced-motion` del SO a nivel CSS).
- Botón "Restablecer" de preferencias.

## [0.0.8] — 2026-05-29

### Changed
- Tipografía a **IBM Plex** (Sans variable + Serif + Mono), itálicas reales.
- Pie a dos columnas; ajustes editoriales.

## [0.0.7] — 2026-05-26

### Changed
- Itálicas reales; overrides del editor (WikiEditor lee tokens del skin).
- Conjunto de preferencias reducido de 7 a 5 (fuera ContentWidth y LineHeight:
  participan del baseline grid).

## [0.0.6] — 2026-05-24

### Added
- Chrome responsive (mobile-first; dropdowns + hamburguesa).
- Contratos de accesibilidad del chrome y de panel emergente en el spec.
- `__PANTALLACOMPLETA__` rediseñado (lienzo experimental + afordancia de escape).

## [0.0.3] — 2026-05-18

### Added
- M1–M4: `skinStyles` por extensión, layout, tema claro/oscuro, tipografía y
  chrome administrable desde páginas wiki del namespace `Stella-Nova`.

## [0.0.1] — 2026-05-18

### Added
- Esqueleto inicial: `SkinMustache` + `skin.json` + `tokens.css`; spec Allium.

[0.1.0]: https://github.com/hspencer/stella-nova/releases/tag/v0.1.0
[0.0.9]: https://github.com/hspencer/stella-nova/releases/tag/v0.0.9
[0.0.8]: https://github.com/hspencer/stella-nova/releases/tag/v0.0.8
[0.0.7]: https://github.com/hspencer/stella-nova/releases/tag/v0.0.7
[0.0.6]: https://github.com/hspencer/stella-nova/releases/tag/v0.0.6
[0.0.3]: https://github.com/hspencer/stella-nova/releases/tag/v0.0.3
[0.0.1]: https://github.com/hspencer/stella-nova/releases/tag/v0.0.1

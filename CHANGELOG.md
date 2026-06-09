# Changelog

Todos los cambios notables de **Stella Nova** se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Mientras el skin esté en `0.x`, el versionado es **`0.MINOR.PATCH`**: `MINOR`
sube con cambios de comportamiento o estructura; `PATCH`, con correcciones y
ajustes editoriales. La fuente de verdad del comportamiento es
[`specs/stella-nova.allium`](specs/stella-nova.allium); cada entrada que toque
comportamiento debería reflejarse también ahí.

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

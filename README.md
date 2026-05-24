# Stella Nova

Skin para MediaWiki, especialmente diseñado y desarrollado para la wiki de la e[ad] PUCV desde cero (con `SkinMustache` + `skin.json`). 

Este skin está deliberadamente dedicado a **[Casiopea](https://wiki.ead.pucv.cl)** pero es fácilmente extendible a cualquier wiki con poco esfuerzo.

Está pensado desde la pantalla pequeña del teléfono en mente, con CSS moderno (que usa Grid/Flexbox, parámetros centralizados y variación de tema claro/oscuro), y con foco en accesibilidad WCAG 2.1 AA y con compatibilidad con Semantic MediaWiki.

![De nova stella](resources/img/Tycho_Cas_SN1572.jpg)

### Del nombre

El 11 de noviembre de 1572, el astrónomo danés **Tycho Brahe** observó una estrella nueva y brillante en la constelación de **Casiopea**. La llamó *stella nova* y documentó sus mediciones en *[De nova stella](https://library-harvard-edu.translate.goog/exhibits/tycho-brahes-new-star?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc)* (1573), el tratado que dio al mundo la palabra «nova».

Aquello no era una estrella naciendo sino muriendo: hoy se conoce como **[SN 1572](https://en.wikipedia.org/wiki/SN_1572)**, «la supernova de Tycho», una supernova de tipo Ia en el brazo de Perseo, a unos 8.000–13.000 años luz. Llegó a brillar como Venus (magnitud ≈ −4), fue visible a plena luz del día durante semanas y se apagó en marzo de 1574. Su mayor consecuencia no fue astronómica sino filosófica: demostró que los cielos —que la tradición aristotélica creía inmutables y perfectos— **cambian**. Fue una de las grietas por donde entró la revolución científica.

## Instalación

```php
wfLoadSkin( 'StellaNova' );
// opcional durante desarrollo:
// $wgDefaultSkin = 'stellanova';
```

Probar sin cambiar el default: añadir `?useskin=stellanova` a cualquier URL.

## Especificación y documentación

- [`specs/stella-nova.allium`](specs/stella-nova.allium) — **especificación de
  comportamiento** (Allium): resolución de las 7 preferencias de skin,
  chrome administrable desde el namespace `Stella-Nova`, modo pantalla
  completa para páginas experimentales, identidad tri-estado (anónimo /
  cuenta temporal 1.43 / registrado) y el contrato de fidelidad
  estructural con MediaWiki y sus extensiones.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — principios y doctrina
  (SkinMustache, skinStyles para SMW/SRF, mobile-first, WCAG 2.1 AA).
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — plan de desarrollo: estado,
  roadmap M0–M8, workflow local, checklist de verificación, decisiones.
- **Espécimen gráfico navegable:**
  [hspencer.github.io/stella-nova/specimen/](https://hspencer.github.io/stella-nova/specimen/)
  — tokens, componentes y layout en vivo, autogenerado desde `tokens.css`
  ([fuente](docs/specimen/)). Ver sección [Para diseñadoras y
  diseñadores](#para-diseñadoras-y-diseñadores) para el flujo de iteración.

## Para el Taller de Diseño

Dónde tocar los elementos gráficos:

 - Todo está en `resources/`, salvo plantillas e
i18n (traducciones). 
 - Si estás modificando la CCS y quieres ver los cambios reflejados, recarga con `?debug=true` en la URL (recomendado, porque es lo más fácil y rápido) o pon
`$wgResourceLoaderDebug = true;` en `LocalSettings.php` para ver los cambios al instante (ResourceLoader cachea agresivamente).

| Quiero cambiar… | En qué archivo está |
|---|---|
| **Variables / tokens** (color, espaciado, tipografía, sombras, radios, movimiento; claro/oscuro; las 7 preferencias por `data-attribute`) | [`resources/tokens.css`](resources/tokens.css) |
| **Layout y componentes** (cabecera, pie, menús, panel de preferencias, "página de papel"…) | [`resources/stella-nova.css`](resources/stella-nova.css) |
| **Impresión** | [`resources/print.css`](resources/print.css) |
| **Estilos de extensiones** (24 extensiones absorbidas, sin reestructurar su DOM) | [`resources/skinStyles/`](resources/skinStyles/) — ver [Compatibilidad con extensiones](#compatibilidad-con-extensiones) abajo |
| **Íconos** (sprite Feather inline; símbolos `#sn-i-*`) | [`includes/templates/SnIcons.mustache`](includes/templates/SnIcons.mustache) |
| **Isotipo / logotipo** (SVG editable, monocromo, colorizable con `currentColor`; enlaza a portada; el wordmark va dentro) | [`resources/casiopea.svg`](resources/casiopea.svg) |
| **Estructura/orden del chrome** | [`includes/templates/skin.mustache`](includes/templates/skin.mustache) (+ [parciales](includes/templates/)) |
| **Textos de interfaz** | [`i18n/es.json`](i18n/es.json), [`i18n/en.json`](i18n/en.json) |

**Tipografía.** **Work Sans** (cuerpo, UI) · **Newsreader** (titulares
h2/h3, citas, `<poem>` — serif editorial con eje óptico) · **IBM Plex
Mono** (código). Todas auto-alojadas (sin CDN): `@font-face` en
[`resources/fonts.css`](resources/fonts.css), `woff2` en
[`resources/fonts/`](resources/fonts/). Familias en los tokens
`--sn-font-text` / `--sn-font-display` / `--sn-font-mono`; la escala y
la medida de lectura en `--sn-fs-*` / `--sn-measure`
([`tokens.css`](resources/tokens.css)).

**Íconos.** Feather, como sprite SVG inline; se usan así:
`<svg class="sn-i"><use href="#sn-i-NOMBRE"/></svg>`. Color por política
global (tokens `--sn-icon` / `--sn-icon-active`): tinta al ~55 % en
reposo → tinta plena al hover/foco; **nunca carmín**. El ícono de enlace
externo es el token `--sn-ext-icon` (máscara) en
[`tokens.css`](resources/tokens.css).

**Color.** Acento único (la “nova”, carmín) en `--sn-nova`; tinta y
campo en `--sn-ink*` / `--sn-field` / `--sn-paper`. Light/dark se
resuelven en [`tokens.css`](resources/tokens.css) (`prefers-color-scheme`+ `[data-sn-theme]`).

**Espécimen gráfico.** Mini-sitio estático autocontenido para iterar el
sistema visual sin levantar la wiki ni tocar PHP — navegable en línea en
**[hspencer.github.io/stella-nova/specimen/](https://hspencer.github.io/stella-nova/specimen/)**
o localmente en [`docs/specimen/`](docs/specimen/) (también empaquetado como
`stella-nova-specimen-v<version>.zip` listo para enviar al taller de diseño).
Tres páginas — `index.html` (tokens, escalas, sombras, auto-generadas desde
`tokens.css`), `components.html` (botones, inputs, toolbar, washes, TOC…) y
`layout.html` (página simulada completa) — cargan los CSS reales del skin,
exponen un bloque `<style id="overrides">` para redefinir variables en vivo
y un `notes.md` para anotar libremente.
Regenerarlo tras cambiar tokens o componentes:

```bash
python3 scripts/build-specimen.py
```

Es idempotente y **preserva `notes.md`** entre rebuilds (los `overrides` en los
HTML se reescriben — copialos al CSS fuente cuando los aceptes). Documentación
completa del flujo diseñador ↔ mantenedor en
[`docs/specimen/README.md`](docs/specimen/README.md).

## Compatibilidad con extensiones

Stella Nova **absorbe** los estilos de las extensiones de MediaWiki en vez
de pelearse con ellos. El mecanismo es `ResourceModuleSkinStyles` en
[`skin.json`](skin.json) con prefijo `+`: el CSS del skin se carga
**después** del CSS de la extensión, y la cascada hace que las reglas del
skin ganen sin `!important`, sin parchear la extensión y sin forkearla.
La extensión sigue actualizándose por su cuenta; sólo cambia su apariencia.

Cada hoja en [`resources/skinStyles/`](resources/skinStyles/) cubre los
módulos CSS de una extensión. Hay dos niveles de absorción:

- **Reescrita a mano:** la hoja está expresada en el sistema visual del
  skin (tokens `var(--sn-*)`, escala `--sn-s-N`, tipografía `--sn-fs-X`,
  layout coherente con el «papel»).
- **Snapshot tokenizado:** la hoja es el CSS original de la extensión
  capturado literalmente y luego procesado por tres pasadas automáticas
  de tokenización (colores hex → tokens, `@codex-vars` → tokens, medidas
  según criterio horizontal/vertical). Los rincones con shorthands mixtos
  (`padding: 5px 0 5px 35px`) quedan marcados con `/* TODO tok */` para
  pulir caso por caso durante el uso real.

| Extensión | Hoja | Nivel |
|---|---|---|
| [Semantic MediaWiki](https://www.semantic-mediawiki.org/) | [`smw.css`](resources/skinStyles/smw.css) | reescrita a mano |
| [Semantic Result Formats](https://www.semantic-mediawiki.org/wiki/Extension:Semantic_Result_Formats) | [`srf.css`](resources/skinStyles/srf.css) | reescrita a mano |
| [PageForms](https://www.mediawiki.org/wiki/Extension:Page_Forms) | [`pageforms.css`](resources/skinStyles/pageforms.css) | reescrita a mano |
| OOUI (core MW, tema wikimediaui) | [`oojs-ui.css`](resources/skinStyles/oojs-ui.css) | snapshot tokenizado |
| [MsUpload](https://www.mediawiki.org/wiki/Extension:MsUpload) | [`msupload.less`](resources/skinStyles/msupload.less) | snapshot tokenizado |
| [SimpleBatchUpload](https://www.mediawiki.org/wiki/Extension:SimpleBatchUpload) | [`simplebatchupload.css`](resources/skinStyles/simplebatchupload.css) | snapshot tokenizado |
| [ConfirmEdit](https://www.mediawiki.org/wiki/Extension:ConfirmEdit) (+ hCaptcha bundled) | [`confirmedit.css`](resources/skinStyles/confirmedit.css) | snapshot tokenizado |
| [WikiEditor](https://www.mediawiki.org/wiki/Extension:WikiEditor) | [`wikieditor.css`](resources/skinStyles/wikieditor.css) | snapshot tokenizado |
| [InlineComments](https://www.mediawiki.org/wiki/Extension:InlineComments) | [`inlinecomments.css`](resources/skinStyles/inlinecomments.css) | snapshot tokenizado |
| [PageNotice](https://www.mediawiki.org/wiki/Extension:PageNotice) | [`pagenotice.css`](resources/skinStyles/pagenotice.css) | snapshot tokenizado |
| [EasyTimeline](https://www.mediawiki.org/wiki/Extension:EasyTimeline) | [`easytimeline.css`](resources/skinStyles/easytimeline.css) | snapshot tokenizado |
| [ImageMap](https://www.mediawiki.org/wiki/Extension:ImageMap) | [`imagemap.css`](resources/skinStyles/imagemap.css) | snapshot tokenizado |
| [3DAlloy](https://github.com/dolfinus/3DAlloy) | [`3dalloy.css`](resources/skinStyles/3dalloy.css) | snapshot tokenizado |
| [Mermaid](https://www.mediawiki.org/wiki/Extension:Mermaid) | [`mermaid.css`](resources/skinStyles/mermaid.css) | snapshot tokenizado |
| [CategoryTree](https://www.mediawiki.org/wiki/Extension:CategoryTree) | [`categorytree.less`](resources/skinStyles/categorytree.less) | snapshot tokenizado |
| [Cite](https://www.mediawiki.org/wiki/Extension:Cite) | [`cite.less`](resources/skinStyles/cite.less) | snapshot tokenizado |
| [Math](https://www.mediawiki.org/wiki/Extension:Math) | [`math.css`](resources/skinStyles/math.css) | snapshot tokenizado |
| [Maps](https://www.mediawiki.org/wiki/Extension:Maps) (Leaflet) | [`maps.base.css`](resources/skinStyles/maps.base.css) + [`maps.widgets.css`](resources/skinStyles/maps.widgets.css) | snapshot tokenizado |
| [Nuke](https://www.mediawiki.org/wiki/Extension:Nuke) | [`nuke.css`](resources/skinStyles/nuke.css) | snapshot tokenizado |
| [Echo](https://www.mediawiki.org/wiki/Extension:Echo) | [`echo.base.less`](resources/skinStyles/echo.base.less) + [`echo.widgets.less`](resources/skinStyles/echo.widgets.less) | snapshot tokenizado |
| [ReplaceText](https://www.mediawiki.org/wiki/Extension:ReplaceText) | [`replacetext.less`](resources/skinStyles/replacetext.less) | snapshot tokenizado |
| [TemplateData](https://www.mediawiki.org/wiki/Extension:TemplateData) | [`templatedata.css`](resources/skinStyles/templatedata.css) | snapshot tokenizado |

En total, **47 módulos CSS** de **22 extensiones** quedan absorbidos. Las
extensiones que no aparecen aquí —`VisualEditor`, `DiscussionTools`,
`MultimediaViewer`, `Scribunto`, `AbuseFilter`, `OATHAuth`, `CodeEditor`,
`CiteThisPage`, `Interwiki`, `SyntaxHighlight`, `TemplateDataGenerator`—
no se activan en la wiki de [Casiopea](https://wiki.ead.pucv.cl) de
producción y se omitieron del primer corte. Para integrarlas, repetir el
flujo: capturar el CSS de la extensión como snapshot en `skinStyles/`,
añadir el mapeo `+<modulo>` en `skin.json`, correr la pasada de
tokenización.

> Detalle completo del proceso, mapas de equivalencias y trazabilidad en
> el [Plan de Migración Stella Nova](https://wiki.ead.pucv.cl/Stella_Nova)

## Scripts

Todos los scripts del repo viven en [`scripts/`](scripts/) y se ejecutan
desde la raíz del skin (`cd skins/stella-nova/`). Son **idempotentes**:
correrlos dos veces seguidas no rompe nada.

| Script | Qué hace |
|---|---|
| [`scripts/build-specimen.py`](scripts/build-specimen.py) | Regenera el espécimen gráfico en [`docs/specimen/`](docs/specimen/) (tokens auto-extraídos de `tokens.css`, 3 páginas HTML autocontenidas, fuentes embebidas) y empaqueta `stella-nova-specimen-v<version>.zip`. Preserva `notes.md` entre rebuilds. |
| [`scripts/snapshot-oojs-ui.py`](scripts/snapshot-oojs-ui.py) | Captura el CSS fuente de OOUI (core + widgets + windows, tema wikimediaui) desde `w/resources/lib/ooui/` y lo escribe como `resources/skinStyles/oojs-ui.css` con header de atribución (versión, fecha, módulos). Se corre cuando OOUI sube versión. |
| [`scripts/apply-tokenization.py`](scripts/apply-tokenization.py) | Aplica las 3 pasadas de tokenización (hex → tokens, codex-vars → tokens, medidas → tokens) a las hojas snapshot de [`resources/skinStyles/`](resources/skinStyles/). Acepta argumento opcional para un solo archivo (`python3 scripts/apply-tokenization.py oojs-ui.css`). Crea backup `.pre-tok-<timestamp>` antes de escribir. |

**Comandos típicos:**

```bash
# Regenerar el espécimen gráfico (tras cambios en tokens o componentes)
python3 scripts/build-specimen.py

# Recapturar OOUI cuando suba versión en el wiki local
python3 scripts/snapshot-oojs-ui.py
python3 scripts/apply-tokenization.py oojs-ui.css

# Re-tokenizar todos los snapshots (raro; suele bastar al añadir un mapeo nuevo
# de hex/medida → token en apply-tokenization.py)
python3 scripts/apply-tokenization.py
```

## Licencia

GPL-2.0-or-later. Ver [`COPYING`](COPYING).

### Advertencia

Este proyecto está vivo, por lo que es cambiante e inestable, seguramente con fallas y aspectos incompletos. Tiene los bordes filosos, cuidado con cortarse los dedos.
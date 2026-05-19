# Stella Nova

Skin para MediaWiki, especialmente diseñado y desarrollado para la wiki de la e[ad] PUCV desde `SkinMustache` + `skin.json` desde cero. Este skin está deliberadamente dedicado a [Casiopea](https://wiki.ead.pucv.cl) pero es fácilmente extendible a cualquier wiki con poco esfuerzo.

Mobile-first, CSS moderno (Grid/Flexbox, custom properties, claro/oscuro), foco en ccesibilidad WCAG 2.1 AA y compatibilidad con Semantic MediaWiki.

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

## Para diseñadoras y diseñadores

Dónde tocar los elementos gráficos (todo en `resources/`, salvo plantillas e
i18n). En desarrollo, recarga con `?debug=true` en la URL o pon
`$wgResourceLoaderDebug = true;` en `LocalSettings.php` para ver los
cambios al instante (ResourceLoader cachea agresivamente).

| Quiero cambiar… | Archivo |
|---|---|
| **Variables / tokens** (color, espaciado, tipografía, sombras, radios, movimiento; claro/oscuro; las 7 preferencias por `data-attribute`) | [`resources/tokens.css`](resources/tokens.css) |
| **Layout y componentes** (cabecera, pie, menús, panel de preferencias, "página de papel"…) | [`resources/stella-nova.css`](resources/stella-nova.css) |
| **Impresión** | [`resources/print.css`](resources/print.css) |
| **Estilos de extensiones** (SMW · SRF · PageForms), sin reestructurar su DOM | [`smw.css`](resources/skinStyles/smw.css) · [`srf.css`](resources/skinStyles/srf.css) · [`pageforms.css`](resources/skinStyles/pageforms.css) |
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

## Licencia

GPL-2.0-or-later. Ver [`COPYING`](COPYING).

### Advertencia

Este proyecto está vivo, por lo que es cambiante e inestable, seguramente con fallas y aspectos incompletos. Tiene los bordes filosos, cuidado con cortarse los dedos.
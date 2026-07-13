# Stella Nova

Skin para MediaWiki, especialmente diseñado y desarrollado para la wiki
de la e[ad] PUCV desde cero (con `SkinMustache` + `skin.json`).

Este skin está deliberadamente dedicado a
**[Casiopea](https://wiki.ead.pucv.cl)** pero es fácilmente extendible
a cualquier wiki con poco esfuerzo.

Está pensado desde la pantalla pequeña del teléfono en mente, con CSS
moderno (que usa Grid/Flexbox, parámetros centralizados y variación de
tema claro/oscuro), y con foco en accesibilidad WCAG 2.1 AA y con
compatibilidad con Semantic MediaWiki.

![De nova stella](resources/img/Tycho_Cas_SN1572.jpg)

### Del nombre

El 11 de noviembre de 1572, el astrónomo danés **Tycho Brahe** observó
una estrella nueva y brillante en la constelación de **Casiopea**. La
llamó *stella nova* y documentó sus mediciones en
*[De nova stella](https://library-harvard-edu.translate.goog/exhibits/tycho-brahes-new-star?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc)*
(1573), el tratado que dio al mundo la palabra «nova».

Aquello no era una estrella naciendo sino muriendo: hoy se conoce como
**[SN 1572](https://en.wikipedia.org/wiki/SN_1572)**, «la supernova de
Tycho», una supernova de tipo Ia en el brazo de Perseo, a unos
8.000–13.000 años luz. Llegó a brillar como Venus (magnitud ≈ −4), fue
visible a plena luz del día durante semanas y se apagó en marzo de
1574. Su mayor consecuencia no fue astronómica sino filosófica:
demostró que los cielos —que la tradición aristotélica creía inmutables
y perfectos— **cambian**. Fue una de las grietas por donde entró la
revolución científica.

## Instalación

```php
wfLoadSkin( 'StellaNova' );
// opcional durante desarrollo:
// $wgDefaultSkin = 'stellanova';
```

Probar sin cambiar el default: añadir `?useskin=stellanova` a cualquier
URL.

**Nombre de carpeta:** `wfLoadSkin( 'X' )` carga `skins/X/skin.json`, así
que el argumento debe coincidir con la carpeta. Las **URLs de los assets
(fuentes incluidas) se calculan de la carpeta real** donde el wiki sirve el
skin (`Hooks::onResourceLoaderRegisterModules`), no de un nombre fijo: por
eso da igual clonar en `StellaNova`, `stella-nova` o vía symlink — basta que
el `wfLoadSkin` apunte a esa carpeta y los woff2 resuelven solos. (Antes,
`remoteSkinPath` estaba hardcodeado y las fuentes daban 404 si la carpeta no
se llamaba exactamente `StellaNova`.)

## Fundamentos y enfoque

Stella Nova sigue el camino oficial de MediaWiki para skins modernos:
**`SkinMustache` + `skin.json`**, separando datos (PHP) de presentación
(Mustache + CSS) y declarando todo en JSON.

- **[`skin.json`](skin.json)** declara el grueso: el nombre del skin, los
  `ResourceModuleSkinStyles` (estilos para extensiones), los `Hooks`, los
  `MessagesDirs`. **No hay archivo de bootstrap PHP** que llame a
  `wfLoadSkin`. La única salvedad: los `ResourceModules` del skin
  (`skins.stellanova.styles` / `.scripts`) se registran en PHP
  (`Hooks::onResourceLoaderRegisterModules`) en vez de declararse aquí, para
  calcular su `remoteSkinPath` de la carpeta real y que las fuentes resuelvan
  sin importar cómo se llame el directorio al clonar (ver *Instalación*).
- **[`includes/SkinStellaNova.php`](includes/SkinStellaNova.php)**
  extiende `SkinMustache`. Es la **única** clase PHP del skin (aparte
  de los hooks): el resto del trabajo lo hace la plantilla. Su única
  responsabilidad es emitir las *data keys* propias que el `.mustache`
  va a interpolar (`is-sn-fullscreen`, `sn-identity`, `sn-isotype`,
  `sn-prefs`, `sn-chrome.notice/sidebar/footer`).
- **[`includes/templates/skin.mustache`](includes/templates/skin.mustache)**
  es la plantilla raíz. Consume las data keys que emite `SkinMustache`
  (`{{{html-headelement}}}`, `{{{html-body-content}}}`,
  `{{#data-portlets}}`…) más las propias del skin. Empieza con
  `{{{html-headelement}}}` y cierra con `</body></html>`.
- **[`includes/Hooks.php`](includes/Hooks.php)** registra el behaviour
  switch `__PANTALLACOMPLETA__`, sirve las preferencias del usuario
  como opciones de cuenta cuando está registrado, e inyecta el script
  inline de pre-pintado (resuelve tema y preferencias **antes** del
  primer paint para evitar FOUC).
- **[`resources/tokens.css`](resources/tokens.css)** define el sistema
  de diseño con *custom properties* (`--sn-*`): paleta, escala
  tipográfica, ritmo vertical (*baseline grid*), espacios, sombras,
  movimiento. Light/dark se voltea solo cambiando un puñado de tokens.
- **[`resources/stella-nova.css`](resources/stella-nova.css)** consume
  los tokens para el layout y los componentes. Sin Bootstrap, sin
  framework — CSS moderno (Grid, Flexbox, container queries puntuales,
  `:has()`, `color-mix()`).
- **[`resources/skin.js`](resources/skin.js)** es JS vanilla (sin
  jQuery propio) y de mejora progresiva: sin él la página es legible y
  el pre-pintado de `Hooks.php` ya aplicó el tema. Cubre el panel de
  preferencias, los menús emergentes y la búsqueda como modal en
  viewport compact.

Si vienes a tocar el skin por primera vez, conviene leerlo en este
orden: `skin.json` (qué declara) → `skin.mustache` (qué emite) →
`tokens.css` (qué variables hay) → `stella-nova.css` (cómo se aplica).
`SkinStellaNova.php` solo si necesitas un dato nuevo en la plantilla.

## Documentación

- **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** — principios y
  doctrina: SkinMustache, `skinStyles` para SMW/SRF, mobile-first,
  WCAG 2.1 AA, identidad tri-estado, chrome administrable.
- **[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)** — plan de
  desarrollo: estado, roadmap M0–M8, workflow local, checklist de
  verificación, decisiones tomadas (y por qué).
- **[`docs/LAYOUTS.md`](docs/LAYOUTS.md)** — esquemas ASCII de los
  layouts del skin: estándar (desktop), compact (mobile),
  `__PANTALLACOMPLETA__` (`.sn-canvas`), drawer de preferencias e
  impresión. Con breakpoints anotados.
- **[`docs/DISENO.md`](docs/DISENO.md)** — para diseñadoras y
  diseñadores: dónde tocar cada cosa (tabla), cómo iterar sin pelear
  con la caché de ResourceLoader, tipografía/íconos/color, y el
  espécimen gráfico ([en línea](https://hspencer.github.io/stella-nova/specimen/)
  o local en [`docs/specimen/`](docs/specimen/)) para iterar el
  sistema visual sin levantar la wiki.
- **[`docs/EXTENSIONES.md`](docs/EXTENSIONES.md)** — compatibilidad
  con extensiones: cómo el skin **absorbe** los CSS de 22 extensiones
  (incl. SMW, SRF, PageForms, OOUI, Maps, Echo…) sin parchearlas, los
  dos niveles de absorción (reescrita a mano vs snapshot tokenizado)
  y el flujo para integrar una nueva.
- **[`docs/WIKITEXTO.md`](docs/WIKITEXTO.md)** — guía editorial para
  quien escribe páginas: palabras mágicas del skin
  (`__PANTALLACOMPLETA__`) y clases CSS opt-in disponibles desde
  wikitexto (`full-width`, `fondo-*`, `grilla` + `cols-N`, `plantilla`,
  `img-circle`, `wiki-btn`, `fw-*`, `noprint`, `sn-notice`).
- **[`specs/stella-nova.allium`](specs/stella-nova.allium)** —
  especificación de comportamiento (Allium): resolución de
  preferencias, chrome administrable desde el namespace `Stella-Nova`,
  modo pantalla completa, identidad tri-estado (anónimo / cuenta
  temporal 1.43 / registrado) y el contrato de fidelidad estructural
  con MediaWiki y sus extensiones.

## Licencia

GPL-2.0-or-later. Ver [`COPYING`](COPYING).

### Advertencia

Este proyecto está vivo, por lo que es cambiante e inestable,
seguramente con fallas y aspectos incompletos. Tiene los bordes
filosos, cuidado con cortarse los dedos.

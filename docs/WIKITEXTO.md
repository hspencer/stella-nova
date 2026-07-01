# Stella Nova — guía editorial del wikitexto

Recursos que el skin pone a disposición de quien **escribe páginas** en la
wiki: palabras mágicas (behaviour switches) y clases CSS opt-in que
el wikitexto puede usar tal cual. No es documentación de programación
— está dirigida al editor que quiere maquetar una página, no al
desarrollador que modifica el skin.

Para principios de diseño ver [`ARCHITECTURE.md`](ARCHITECTURE.md); para el
estado del desarrollo, [`DEVELOPMENT.md`](DEVELOPMENT.md).

## 1. Palabras mágicas (behaviour switches)

Las palabras mágicas de MediaWiki son cadenas con doble guión bajo (estilo
`__PALABRA__`) que se escriben en cualquier lugar del wikitexto y modifican
cómo se renderiza la página. Son **sensibles a mayúsculas** (`__notitle__`
no funciona). No producen salida; solo conmutan comportamiento.

### `__PANTALLACOMPLETA__` (provista por este skin)

Sinónimo: `__FULLSCREEN__`. Definida en `StellaNova.i18n.magic.php`.

**Qué hace:** declara la página en *modo lienzo*. El skin suprime la
cabecera, el pie, el panel de preferencias y todos los portlets; solo
queda el cuerpo del artículo y una afordancia mínima de escape (modal
único arriba a la izquierda con isotipo + navegación de salida).

**Cuándo usarla:**
- Páginas experimentales con `<canvas>` o `<iframe>` que necesitan
  el viewport completo (p5.js, three.js, visualizaciones embebidas).
- Portadas o landings que requieren una composición a borde de pantalla.
- Cualquier página donde el chrome del skin compite con el contenido.

**Consecuencias:**
- El contenedor del cuerpo deja de ser `.sn-paper` (la hoja sobre el
  campo) y pasa a ser `.sn-canvas`: sin sombra, sin padding lateral del
  papel, ocupa el ancho del viewport.
- `__NOTITLE__` se suele combinar con esto para suprimir también
  `firstHeading`. `__PANTALLACOMPLETA__` por sí solo NO oculta el título.
- El usuario sigue teniendo Escape (tecla) para cerrar el modal de
  navegación; nunca queda atrapado.
- Pierde la pestaña "Editar" en la barra superior (no hay barra). Para
  editar la página, navega a `?action=edit` por URL o usa el modal de
  navegación → "Página" → "Editar código".

**Riesgo conocido:** declarable por cualquier editor. La inyección de
JS arbitrario sigue mediada por `MediaWiki:Common.js` (deuda reconocida);
no use `__PANTALLACOMPLETA__` como sustituto de control de scripts.

### `__NOTITLE__` (provista por la extensión NoTitle)

**Qué hace:** oculta el `firstHeading` (el título grande de la página).

**Por qué importa al skin:** el bleed-top del modificador `.full-width`
(ver §2) empuja la imagen hacia arriba y se superpone con el título.
Combinar `__NOTITLE__` con una imagen `full-width` como primer elemento
del cuerpo da el resultado de "hero a sangre" sin colisión.

**Cuándo NO usarla:** páginas que dependen del título como ancla
contextual (categorías, fichas de propiedad, plantillas reutilizadas).

### `__TOC__`, `__NOTOC__`, `__FORCETOC__` (core MediaWiki)

**Qué hacen:** controlan dónde y si aparece la tabla de contenidos.

**Cómo las trata Stella Nova:** la TOC se renderiza **en el sitio donde
la pone MediaWiki** (posición de `__TOC__` o auto). El skin la
restiliza en su lenguaje visual (paper-sobre-paper, colapsable con
caret) pero respeta la posición del wikitexto. No hay un "slot fijo"
de TOC en el lado derecho — lo intentamos y se revirtió porque ignorar
`__TOC__` rompía páginas que dependen de su colocación.

### `__INDEX__` / `__NOINDEX__` (core)

Controlan robots/SEO. Sin consecuencia visual; el skin no las
interpreta. Mencionadas aquí solo por completitud.

### Otras de core que conviene conocer

- `__HIDDENCAT__`: marca una categoría como oculta. Las categorías
  ocultas no aparecen en `.catlinks` (la franja de categorías al pie del
  artículo); Stella Nova respeta este comportamiento.
- `__NEWSECTIONLINK__` / `__NONEWSECTIONLINK__`: añaden o suprimen el
  enlace "+" para agregar sección. Sin estilo dedicado en el skin.
- `__NOEDITSECTION__`: oculta los enlaces `[editar]` por sección. El
  skin estiliza estos enlaces (color tenue, alineados al heading) pero
  no los inventa: si los suprime, no se ven.

## 2. Clases CSS especiales (opt-in desde wikitexto)

Clases que el skin define en `resources/stella-nova.css` y que **se
activan escribiéndolas en el wikitexto** o desde una plantilla. Son
las "extras" del skin disponibles para maquetar contenido editorial.

Convención de uso en wikitexto:

```wiki
<div class="grid cols-3">
…contenido…
</div>
```

```wiki
[[Archivo:foo.jpg|class=full-width]]
```

### `full-width` — imagen a sangre (full-bleed)

Reventa el padding lateral de la hoja (`.sn-paper`) y lleva la imagen
borde-a-borde del artículo. Funciona en tres patrones de wikitexto:

```wiki
[[Archivo:foo.jpg|class=full-width]]
[[Archivo:foo.jpg|frameless|class=full-width]]
<div class="full-width">[[Archivo:foo.jpg]]</div>
```

**Consecuencias:**
- La imagen se estira al 100 % del nuevo ancho. Subir originales **al
  menos de 1600 px de ancho** o se verá pixelada en pantallas grandes.
- Si la imagen es el **primer** elemento del cuerpo, también revienta el
  padding superior y se ancla al borde del paper (efecto "hero"). Lo
  mismo en el último elemento, abajo. Para evitar la colisión con
  `firstHeading`, usar `__NOTITLE__`.
- En modo `__PANTALLACOMPLETA__` (`.sn-canvas`), `full-width` va al
  ancho del **viewport completo**, no del paper.
- El thumb-caption se mantiene alineado al ancho del cuerpo (no se
  estira con la imagen) — pensado para legibilidad de la leyenda.
- Tolerante a las dos formas con que MediaWiki preserva la clase:
  `class=full-width` (canónico) y `class='full-width'` (con apóstrofes,
  resultado del paso a `[[Imagen:|class='…']]`).

### `fondo-*` — bandas de contenido a sangre lateral

Bloque de contenido cuyo **fondo va de lado a lado** de la hoja (misma técnica
de bleed que `full-width`) pero con el **contenido de vuelta al ancho de
lectura**. Sirve para destacar una intro, un índice de portada o un aviso sin
sacarlo del flujo. Cada variante sólo cambia el color, tomado de un **lavado
pálido semántico** que voltea con el tema:

| Clase | Fondo |
|---|---|
| `fondo-ahuesado` | hueso claro (`--sn-papel-400` / `--sn-tinta-700`) |
| `fondo-coral` | lavado carmín (`--sn-nova-wash`) |
| `fondo-verde` | lavado verde (`--sn-ok-wash`) |
| `fondo-ambar` | lavado ámbar (`--sn-warn-wash`) — rol *warn* |
| `fondo-info` | lavado info (`--sn-info-wash`) |

```wiki
<div class="fondo-verde">
Un bloque destacado, a sangre lateral pero con el texto legible.
</div>

<div class="fondo-coral grilla cols-3">
… tres columnas: el fondo sangra, la grilla maqueta dentro …
</div>
```

**Consecuencias:**
- **Voltea con el tema** sola (los lavados son semánticos, no literales).
- Añade una línea base de aire arriba y abajo; el alto es un múltiplo entero de
  `--sn-baseline`, así que **no rompe la retícula**.
- Sólo sangra dentro de `.sn-paper` / `.sn-canvas`.
- **Se combina con `grilla`**: el fondo sangra a los bordes y las columnas
  quedan al ancho de lectura (`class="fondo-coral grilla cols-3"`). También con
  las clases de contenido (`class="fondo-verde center serif lg"`).

### `grid` / `grilla` — framework de layout

Reemplaza el patrón `.row > .col-md-*` del skin anterior (Bootstrap). El
nombre es **bilingüe**: `grid` (canónico, estándar) y `grilla` (alias en
español, retrocompatible). Funcionan idéntico; se pueden mezclar con
otras páginas que aún usen `grilla`.

```wiki
<div class="grid cols-2">
[[Archivo:a.jpg]]
[[Archivo:b.jpg]]
</div>
```

Los modificadores se **combinan** sumando clases (`class="grid cols-3 gap-l align-center"`).

**Columnas**

| Modificador | Resultado | Colapso responsive |
|---|---|---|
| `cols-1` | 1 columna | — |
| `cols-2` | 2 columnas iguales | → 1 col bajo 48 rem (~768 px) |
| `cols-3` | 3 columnas iguales | → 1 col bajo 48 rem |
| `cols-4` | 4 columnas iguales | → 2 col bajo 64 rem, → 1 col bajo 48 rem |
| `cols-5` | 5 columnas iguales | → 3 col bajo 64 rem, → 1 col bajo 48 rem |
| `cols-6` | 6 columnas iguales | → 3 col bajo 64 rem, → 1 col bajo 48 rem |
| `cols-auto` | tantas columnas (≥ 16 rem) como quepan (auto-fit) | fluido |
| `cols1-2` | 1/3 + 2/3 (asimétrica) | → 1 col bajo 48 rem |
| `cols2-1` | 2/3 + 1/3 (asimétrica) | → 1 col bajo 48 rem |

**Espaciado** (gap entre celdas; por defecto **1.5 rem** en ambos ejes)

| Modificador | Gap (ambos ejes) |
|---|---|
| `gap-0` | sin separación |
| `gap-s` | 0.5 rem |
| `gap-m` | 1 rem |
| `gap-l` | 2.25 rem |
| *(sin clase)* | 1.5 rem (default) |

**Gap por eje** — el espaciado se puede separar en horizontal y vertical, con la
misma escala `0/s/m/l`. Se combinan entre sí y con `gap-*`
(`class="grid cols-3 gap-h-0 gap-v-l"` = columnas pegadas, filas aireadas).

| Modificador | Eje |
|---|---|
| `gap-h-0/s/m/l` | **horizontal** — entre columnas (dentro de la fila) |
| `gap-v-0/s/m/l` | **vertical** — entre filas |

**Flujo, alineación, margen y ancho**

| Modificador | Resultado |
|---|---|
| `flujo-v` / `stack` | apila las celdas en una columna vertical (con el mismo gap) |
| `align-top` / `arriba` | alinea el contenido de las celdas arriba |
| `align-center` / `centro` | centra verticalmente el contenido de las celdas |
| `align-bottom` / `abajo` | alinea el contenido de las celdas abajo |
| `align-baseline` | alinea por la línea base del texto |
| `sin-margen` / `flush` | anula el margen vertical de la grilla |
| `full` / `completa` | la grilla rompe el ancho de lectura y ocupa **todo el campo** |

**Consecuencias:**
- Cada hijo directo de la grilla es una celda. URLs largas o bloques de
  código no desbordan (`minmax(0, 1fr)` previene overflow).
- **Contenido inline** (varios `<span class="wiki-btn">`, `[[enlaces]]`…):
  MediaWiki envuelve toda la secuencia en **un solo `<p>`**. El skin lo detecta
  (cuando ese `<p>` es el único hijo) y lo hace transparente para que cada
  `<span>`/enlace sea una celda real — así `cols-*` y `gap-*` funcionan sin que
  tengas que hacer nada. Si en cambio separás los ítems con **líneas en
  blanco**, MediaWiki crea un `<p>` por ítem (cada uno una celda); también
  funciona, pero suele quedar mejor sin las líneas en blanco.
- Funciona igual en chrome normal y en `__PANTALLACOMPLETA__`. En pantalla
  completa el contenido es libre (sin columna central), por lo que `grid`
  es la herramienta recomendada para maquetar ahí.
- `full` / `completa` usan la misma técnica que `full-width`: a sangre del
  viewport en pantalla completa, del paper en chrome normal.

### `template` / `plantilla` — ficha vertical clave→valor

Modificador para `<table class="wikitable template">`. Nombre **bilingüe**:
`template` (canónico) y `plantilla` (alias en español, retrocompatible).
Pensado para las fichas de plantillas Casiopea (perfiles, fichas técnicas,
créditos): convierte la tabla en una **ficha vertical clave→valor** — sin
filetes, la etiqueta (`!`) a la **derecha en versalita tenue** y el valor (`|`)
a la izquierda. Llena el ancho de la hoja y corre a ¾ de la línea base. Es una
tabla *silenciosa*, propia de ficha y no de datos.

Recordá que la tabla `wikitable` normal ya es de diseño mínimo: **solo filetes
horizontales** (nunca verticales ni contorno exterior), cabecera transparente y
**sin colores alternados** de fila. `plantilla` va un paso más allá y quita
todos los filetes. Para tablas ordenables, sumá `sortable`.

```wiki
{| class="wikitable template"
! Campo
| valor
|-
! Otro campo
| otro valor
|}
```

Si se usa en una tabla sin `.wikitable`, no aplica nada (el selector
empieza por `.sn-body table:is(.template, .plantilla)`); siempre va
combinada con `wikitable`.

### `img-circle` — recorte circular limpio

Override de la regla genérica de `MediaWiki:Common.css` (que aplicaba
`clip-path:circle()` al `<figure>` y devoraba la leyenda y los píxeles
superiores de la imagen). Stella Nova mueve el `clip-path` al `<img>`
directamente y oculta el `figcaption` (en `.vcard` el nombre ya
aparece como `.person-name`).

```wiki
[[Archivo:perfil.jpg|class=img-circle]]
```

**Consecuencia:** la imagen queda recortada en círculo perfecto sobre
su cuadrado. Si la imagen no es cuadrada, se recorta al cuadrado
mayor inscrito. Para fotos de perfil subir cuadradas (o aceptar el
recorte).

### `noprint` — ocultar en impresión

Clase estándar de MediaWiki. Stella Nova la respeta en `print.css`:
cualquier elemento con `class=noprint` desaparece al imprimir o
exportar a PDF (vía la extensión Mpdf). Útil para banners, botones,
módulos interactivos que no tienen sentido en papel.

### `sn-notice` — aviso destacado

Tono de aviso editorial: filete carmín a la izquierda, fondo lavado
(`--sn-nova-wash`), texto en cuerpo `sm`. Se usa principalmente para
el fragmento administrable `Stella-Nova:Aviso` (que se inyecta en lo
alto del paper), pero está disponible para cualquier wikitexto:

```wiki
<div class="sn-notice">
Aviso importante para esta página.
</div>
```

Una sola variante (no hay `sn-notice-warn` ni `sn-notice-info` — si
hace falta, conversar antes de añadirla).

### `wiki-btn` — botón de contenido (píldora)

Botón «outline» en forma de píldora: contorno fino que al pasar el cursor se
rellena y el texto voltea a blanco (`--sn-nova-ink`). Tres variantes: por
defecto (gris), `red` (carmín del skin) y `green` (verde de éxito).

```wiki
<span class="wiki-btn">[[Página|Etiqueta]]</span>
<span class="wiki-btn red">[[…|Rojo]]</span>
<span class="wiki-btn green">[[…|Verde]]</span>
```

**Robusto a tres usos:** funciona (1) envolviendo un enlace `[[…]]`, (2) como
`<span>` **suelto sin enlace** —p. ej. un toggle
`class="mw-customtoggle-x link-toggle wiki-btn green"`— y (3) aplicado directo a
un `<a>`. El volteo del texto no depende de que haya un enlace dentro. El alto es
**exacto de una línea base**, con relleno solo horizontal, así que el interior
calza igual en los tres casos y no rompe la retícula. Debe vivir dentro de
`.sn-body`.

### Clases tipográficas de contenido (viven en `MediaWiki:Common.css`)

Utilitarias ortogonales que se **combinan** (`class="lg serif center nova"`).
Pensadas para envolver el `<p>` que genera la wiki: una clase en el `<div>` se
hereda al párrafo; la **alineación** además se propaga al `<p>` interno.

> ⚠️ A diferencia de las clases de arriba, éstas **no las define el skin** sino
> `MediaWiki:Common.css` de cada wiki. El espécimen las replica para mostrarlas,
> pero para que funcionen en el wikitexto real deben estar en el `Common.css` de
> la wiki.

| Eje | Clases |
|---|---|
| **Tamaño** | `jumbo` (titular) · `lg` · `sm` · `xs` (el cuerpo es el default, sin clase) |
| **Familia** | `serif` · `sans` · `mono` |
| **Énfasis** | `uppercase` · `italic` · `bold` |
| **Alineación** | `left` · `center` · `right` · `justify` |
| **Color** | `nova` · `ok` · `warn` · `danger` (color de texto por rol; voltea con el tema) |

## 3. Comportamientos del skin sobre wikitexto estándar

No requieren clases especiales — el skin los aplica automáticamente
cuando reconoce el patrón:

- **Párrafos del cuerpo (`.sn-body p`):** justificados con hyphenation
  automática (`hyphens: auto`, dependen de `lang="es"` que MW pone en
  `<html>`). Mínimo de 6 caracteres por palabra para partir, 3 antes y
  3 después del guión. Si esto produce ríos visibles en un párrafo
  corto, considere reescribir antes que añadir clases.
- **Tablas `.wikitable`** (y las semánticas `.smwtable`/`.broadtable`): ya
  quedan tematizadas — solo filetes horizontales, cabecera transparente, texto
  a ~80 % y **sin colores alternados** de fila. `.toccolours` va como caja
  auxiliar (fondo `--sn-sunk`). No hace falta hacer nada.
- **`<blockquote>`** y **`<poem>`** (extensión Poem): consumen la
  familia editorial de contraste (`--sn-font-quote`). Por defecto es
  Roboto Serif (la serif variable del skin). Si el lector elige serif
  como familia del cuerpo desde el menú, citas y poemas voltean a sans
  para mantener el contraste. No usar `<blockquote>` para "destacar
  texto general" — está reservado para citas reales.
- **Enlaces externos:** ícono Feather "external-link" al final como
  máscara teñida con `currentColor`. No usar pseudo-classes propias.
- **Imágenes en general:** `max-width: 100 %` y `height: auto`
  automáticos — nunca desbordan el contenedor.
- **TOC (`__TOC__`):** restilizada en el sitio donde la coloque
  MediaWiki. Colapsable con caret (sin necesidad de JS adicional).

## 4. Pitfalls y notas finales

- **Sensibilidad a mayúsculas:** las palabras mágicas son
  case-sensitive. `__pantallacompleta__` no funciona; `__PANTALLACOMPLETA__` sí.
- **Apóstrofes en `class=`:** MediaWiki preserva
  `class='full-width'` literal (con las comillas en el nombre de la
  clase). El skin matchea ambos por tolerancia, pero el canónico es
  `class=full-width` sin comillas.
- **Combinación recomendada para hero a sangre:**
  `__NOTITLE__` + `__PANTALLACOMPLETA__` + primera imagen `full-width`.
  Da una primera pantalla limpia, sin colisiones con el chrome.
- **Páginas de plantilla no son páginas de contenido.** Las clases de
  `.sn-body` solo aplican dentro del paper. Las páginas de namespace
  `Plantilla:` se ven distintas (otro layout); probar siempre el render
  embebido (transcluyendo la plantilla en una página real), no la
  página de plantilla en sí.
- **Si necesita una clase nueva**, conversar antes de añadirla
  directamente. El conjunto de clases especiales se mantiene **chico a
  propósito** — Bootstrap nos enseñó qué pasa cuando crece sin freno.

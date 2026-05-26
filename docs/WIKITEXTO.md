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
<div class="grilla cols-3">
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

### `grilla` + `cols-N` — grilla utilitaria

Reemplaza el patrón `.row > .col-md-*` del skin anterior (Bootstrap).
Uso:

```wiki
<div class="grilla cols-2">
[[Archivo:a.jpg]]
[[Archivo:b.jpg]]
</div>
```

| Modificador | Resultado | Colapso responsive |
|---|---|---|
| `cols-2` | 2 columnas iguales | → 1 col bajo 48 rem (~768 px) |
| `cols-3` | 3 columnas iguales | → 1 col bajo 48 rem |
| `cols-4` | 4 columnas iguales | → 2 col bajo 64 rem, → 1 col bajo 48 rem |
| `cols-5` | 5 columnas iguales | → 3 col bajo 64 rem, → 1 col bajo 48 rem |
| `cols-6` | 6 columnas iguales | → 3 col bajo 64 rem, → 1 col bajo 48 rem |
| `cols1-2` | 1/3 + 2/3 (asimétrica) | → 1 col bajo 48 rem |
| `cols2-1` | 2/3 + 1/3 (asimétrica) | → 1 col bajo 48 rem |

**Consecuencias:**
- Cada hijo directo de `.grilla` es una celda. URLs largas o bloques de
  código no desbordan (`minmax(0, 1fr)` previene overflow).
- Funciona igual en chrome normal y en `__PANTALLACOMPLETA__`.
- El gap entre celdas es `--sn-s-4` (1 rem). No se puede ajustar por
  página sin estilo inline (se desaconseja).

### `plantilla` — fichas tabulares sin bordes

Modificador para `<table class="wikitable plantilla">`. Pensado para las
fichas de plantillas Casiopea (perfiles, fichas técnicas, créditos):
conserva el contorno exterior del wikitable pero **quita los bordes
entre celdas y el fondo de los `<th>`**, dejando una tabla más
silenciosa, propia de ficha y no de datos.

```wiki
{| class="wikitable plantilla"
! Campo
| valor
|-
! Otro campo
| otro valor
|}
```

Si se usa en una tabla sin `.wikitable`, no aplica nada (el selector
empieza por `.sn-body table.plantilla`); siempre va combinada con
`wikitable`.

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

## 3. Comportamientos del skin sobre wikitexto estándar

No requieren clases especiales — el skin los aplica automáticamente
cuando reconoce el patrón:

- **Párrafos del cuerpo (`.sn-body p`):** justificados con hyphenation
  automática (`hyphens: auto`, dependen de `lang="es"` que MW pone en
  `<html>`). Mínimo de 6 caracteres por palabra para partir, 3 antes y
  3 después del guión. Si esto produce ríos visibles en un párrafo
  corto, considere reescribir antes que añadir clases.
- **Tablas `.wikitable`** y **`.toccolours`**: ya quedan tematizadas
  (fondo paper, bordes hairline, headers en sunk). No hace falta hacer
  nada.
- **`<blockquote>`** y **`<poem>`** (extensión Poem): la única familia
  serif del skin (Alegreya) se aplica automáticamente. No usar
  `<blockquote>` para "destacar texto general" — está reservado para
  citas reales.
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

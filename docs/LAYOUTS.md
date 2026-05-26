# Stella Nova — esquemas de layout

Mapa visual de los layouts que produce el skin. Cada esquema corresponde
a un estado de presentación distinto (chrome completo, compact, canvas,
drawer abierto). Los nombres entre corchetes son selectores CSS reales
del skin (mirables en [`resources/stella-nova.css`](../resources/stella-nova.css)
y en la plantilla [`includes/templates/skin.mustache`](../includes/templates/skin.mustache)).

Breakpoints clave (mismos valores en CSS y en JS):

| Umbral | Qué cambia |
|---|---|
| `≥ 90 rem` (≈ 1440 px) | El padding lateral del paper se ensancha |
| `≥ 64 rem` (≈ 1024 px) | Grillas `cols-4/5/6` a ancho completo; modal de canvas a 3 col |
| `≥ 48 rem` (≈ 768 px, iPad portrait) | Umbral **compact**: arriba = desktop, abajo = compact |
| `< 64 rem` | Grillas densas colapsan a `2`–`3` columnas |
| `< 40 rem` | Ajustes finos del header |
| `< 36 rem` | Indicators y kicker vuelven al flujo normal |
| `< 34 rem` | Megamenú a 1 columna |

## 1. Layout estándar — chrome completo (desktop ≥ 48 rem)

```
┌─ html ─────────────────────────────────────────────────────────────────┐
│  body  (fondo --sn-field, gris ahuesado, con grano sutil)              │
│ ┌─ .sn-app ────────────────────────────────────────────────────────┐   │
│ │┌─ .sn-header / .sn-header-bar ────────────────────────────────┐  │   │
│ ││ [☆ Casiopea] [☰▾]   [🔍 buscar…]      [✎] [▤▾]   [🔔][👤][⚙]│  │   │
│ ││ │            │       │                │   │       │   │   │  │  │   │
│ ││ │            └ sitenav (megamenú)     │   │       │   │   └ sn-prefs-trigger
│ ││ │              "Navegación"           │   │       │   └ user-menu          │
│ ││ │                                     │   │       └ notificaciones (Echo)  │
│ ││ │                                     │   └ menú "Página" (.sn-pagemenu)   │
│ ││ │                                     └ lápiz (edición rápida)             │
│ ││ └ isotipo SVG (link a portada)                                             │
│ │└────────────────────────────────────────────────────────────────────┘      │
│ │                                                                            │
│ │┌─ .sn-shell ───────────────────────────── (max-width: --sn-shell 82rem) ─┐ │
│ ││                  ┌─ .sn-paper-wrap (max-width: --sn-measure 58rem) ──┐  │ │
│ ││                  │┌─ <article class="sn-paper mw-body"> ───────────┐ │  │ │
│ ││                  ││ .sn-indicators (absolute, esquina sup. der.)   │ │  │ │
│ ││                  ││                                                │ │  │ │
│ ││                  ││ {{html-site-notice}}  ← core                   │ │  │ │
│ ││                  ││ <aside class="sn-notice">{Stella-Nova:Aviso}   │ │  │ │
│ ││                  ││                                                │ │  │ │
│ ││                  ││ ┃ firstHeading (color --sn-nova, carmín)       │ │  │ │
│ ││                  ││ ┃ ── (subtitle / kicker contentSub si aplica) ─│ │  │ │
│ ││                  ││                                                │ │  │ │
│ ││                  ││ ┌─ .sn-body ─────────────────────────────────┐ │ │  │ │
│ ││                  ││ │ Párrafo justificado con hyphens.           │ │ │  │ │
│ ││                  ││ │ ──────────────                             │ │ │  │ │
│ ││                  ││ │  ← .full-width revienta el padding lateral →│ │ │  │ │
│ ││                  ││ │ ════════════════════════════════════════   │ │ │  │ │
│ ││                  ││ │                                            │ │ │  │ │
│ ││                  ││ │ ## h2 sobrio, peso 500                     │ │ │  │ │
│ ││                  ││ │                                            │ │ │  │ │
│ ││                  ││ │ .grilla.cols-3                             │ │ │  │ │
│ ││                  ││ │ ┌────┐ ┌────┐ ┌────┐                       │ │ │  │ │
│ ││                  ││ │ │    │ │    │ │    │                       │ │ │  │ │
│ ││                  ││ │ └────┘ └────┘ └────┘                       │ │ │  │ │
│ ││                  ││ └────────────────────────────────────────────┘ │ │  │ │
│ ││                  ││                                                │ │  │ │
│ ││                  ││ {{html-categories}} → .catlinks [cat] [cat]    │ │  │ │
│ ││                  │└────────────────────────────────────────────────┘ │  │ │
│ ││                  └─ sombra muy sutil (--sn-lift-paper) ──────────────┘  │ │
│ │└─────────────────────────────────────────────────────────────────────────┘ │
│ │                                                                            │
│ │┌─ .sn-footer (ancho = .sn-shell, 3 cols 1fr 1fr 1fr) ─────────────────┐    │
│ ││ Stella-Nova:Pie   │ data-info        │  🛠 Herram. y más               │   │
│ ││ (gestionado)      │ data-places      │  (toolbox p-tb)                 │   │
│ │└──────────────────────────────────────────────────────────────────────┘    │
│ └────────────────────────────────────────────────────────────────────────────┘
└────────────────────────────────────────────────────────────────────────────┘
```

Notas:

- El acento carmín (la *nova*) aparece **solo** en: `firstHeading`, `h3`
  del cuerpo, foco de controles, isotipo, `selected/active` de menús y
  borde-izquierda del `.sn-notice`. El resto es tinta cálida.
- **Sin riel lateral**. La navegación del sitio vive en el menú `☰▾` del
  header (megamenú a columnas); la caja de herramientas, en el pie.
- El paper *flota* sobre el campo: borde `1 px paper-edge` + sombra
  mínima. No es una caja levitando — es papel asentado.
- `firstHeading` lleva `text-wrap: balance` y `max-width: 34ch`: el
  título nunca queda con una palabra suelta colgando, pero no se
  estira más allá de una medida de lectura editorial.

## 2. Layout compact / móvil (< 48 rem)

```
┌─ html ──────────────────────────────────────┐
│  body                                       │
│ ┌─ .sn-app ─────────────────────────────┐   │
│ │┌─ .sn-header (compacta) ────────────┐ │   │
│ ││ [☆]  [☰]      [🔍]  [✎] [▤] [👤][⚙]│ │   │
│ ││ │    │         │                    │ │   │
│ ││ │    │         └ trigger del modal de búsqueda
│ ││ │    └ sitenav como bottom-sheet                │
│ ││ └ glifo cuadrado (--sn-isotype-compact)         │
│ │└──────────────────────────────────────────┘     │
│ │                                                 │
│ │┌─ .sn-paper (padding lateral menor) ─────┐      │
│ ││                                          │      │
│ ││ firstHeading                             │      │
│ ││                                          │      │
│ ││ Cuerpo a 100 % del paper                 │      │
│ ││                                          │      │
│ ││ .grilla.cols-* → 1 columna               │      │
│ ││ ┌────────────────────────────┐           │      │
│ ││ │                            │           │      │
│ ││ └────────────────────────────┘           │      │
│ ││ ┌────────────────────────────┐           │      │
│ ││ │                            │           │      │
│ ││ └────────────────────────────┘           │      │
│ │└──────────────────────────────────────────┘     │
│ │                                                 │
│ │┌─ .sn-footer (3 cols colapsan a 1) ──────┐      │
│ ││ Stella-Nova:Pie                          │      │
│ ││ legal                                    │      │
│ ││ Herram. y más                            │      │
│ │└──────────────────────────────────────────┘     │
│ └─────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────┘

╔══ menú "Navegación" (al pulsar ☰) ═══════════════════╗
║  ┌──────────────────────────────────────────────┐    ║
║  │ Navegación                               [✕] │    ║
║  ├──────────────────────────────────────────────┤    ║
║  │ ESCUELA                                      │    ║
║  │ · Sobre la escuela                           │    ║
║  │ · Travesías                                  │    ║
║  │                                              │    ║
║  │ WIKI                                         │    ║
║  │ · Comunidad                                  │    ║
║  │ · Ayuda                                      │    ║
║  └──────────────────────────────────────────────┘    ║
║   ↑ modal bottom-sheet, scrim atrás, ESC cierra      ║
╚══════════════════════════════════════════════════════╝

╔══ búsqueda (al pulsar 🔍) ═══════════════════════════╗
║  ┌──────────────────────────────────────────────┐    ║
║  │ [✕]   buscar…                            [↵] │    ║
║  └──────────────────────────────────────────────┘    ║
║   ↑ data-sn-search-open en <html>, mismo <form>      ║
║     que en desktop (sin duplicar input)              ║
╚══════════════════════════════════════════════════════╝
```

Notas:

- Lo que en desktop es *popover* (`aria-expanded` controlando posición
  CSS) en compact se transforma en *modal bottom-sheet* (`data-sn-open`
  en el `.sn-md`). El JS añade focus-trap + ESC + scrim.
- La búsqueda es el **mismo** `<form id="searchform">`: en desktop está
  visible inline, en compact se oculta y un trigger (lupa) abre el form
  como modal. No hay duplicación.
- El isotipo en compact es el **glifo cuadrado** (`casiopea-icon.svg`):
  constelación sola, sin wordmark, en cuadrado de 2 rem.
- El JS escucha `matchMedia('(max-width: 48rem)')` para alternar.

## 3. Layout `__PANTALLACOMPLETA__` (`.sn-canvas`)

```
┌─ html ──────────────────────────────────────────────────────────┐
│  body  (sin barra de chrome alguna)                             │
│ ┌─ <main class="sn-canvas" tabindex="-1"> ───────────────────┐  │
│ │┌─ .sn-fs-bar (esquina sup. izq., fixed) ─┐                  │  │
│ ││ [☆]  ← único trigger, abre modal único  │                  │  │
│ │└──────────────────────────────────────────┘                  │  │
│ │                                                              │  │
│ │┌─ .sn-canvas-body.sn-body.mw-body-content ─────────────────┐ │  │
│ ││                                                            │ │  │
│ ││         {{html-body-content}} al 100 % del viewport        │ │  │
│ ││                                                            │ │  │
│ ││         (canvas, iframe, p5.js sin borde ni outline)       │ │  │
│ ││                                                            │ │  │
│ │└────────────────────────────────────────────────────────────┘ │  │
│ └─────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘

╔══ Modal único (al pulsar el ☆ del .sn-fs-bar) ════════════════════╗
║  ┌─────────────────────────────────────────────────────────────┐   ║
║  │ Menú                                                    [✕] │   ║
║  ├─────────────────────────────────────────────────────────────┤   ║
║  │ ┌─────── búsqueda (full-row, hasta 3 cols) ───────────────┐ │   ║
║  │ │ [🔍 buscar…]                                     [↵]    │ │   ║
║  │ └─────────────────────────────────────────────────────────┘ │   ║
║  │                                                             │   ║
║  │ ┌─ NAVEGACIÓN ──┐ ┌─ ESTA PÁGINA ─┐ ┌─ USUARIO ────────┐  │   ║
║  │ │ · Portada     │ │ · Editar      │ │ · Mi discusión   │  │   ║
║  │ │ · Escuela…    │ │ · Editar cód. │ │ · Preferencias…  │  │   ║
║  │ │ · Wiki…       │ │ · Historial   │ │ · Salir          │  │   ║
║  │ └───────────────┘ └───────────────┘ └──────────────────┘  │   ║
║  └─────────────────────────────────────────────────────────────┘   ║
║   ↑ "salida" del fullscreen: los links a Portada/Navegación        ║
║      sacan del canvas. ESC también cierra el modal.                ║
╚════════════════════════════════════════════════════════════════════╝
```

Notas:

- En `__PANTALLACOMPLETA__` **no hay** afordancia de "salir del
  pantalla completa". El modal único reemplaza al chrome: salir =
  navegar fuera. Nunca se atrapa al usuario porque ESC + tab order +
  links de portada están siempre operables.
- El cuerpo lleva además `.sn-body` y `.mw-body-content` para heredar
  todos los estilos editoriales (tablas, listas, `.plantilla`, poem,
  `<blockquote>`, TOC) sin duplicar selectores.
- En este modo `class=full-width` cubre el **viewport completo**
  (`100 vw`), no el paper. Pensado para landings y experimentos
  visuales a borde de pantalla.

## 4. Panel de preferencias

Desktop (`≥ 48 rem`) — drawer lateral derecho deslizable:

```
                              ╔════════════════════════════════╗
                              ║ Preferencias de lectura    [✕] ║
                              ╠════════════════════════════════╣
┌─ .sn-app (≈68 % del ancho) ─┐║                                ║
│                              ║ Tema                            ║
│  …layout estándar al fondo,  ║ [Auto] [Claro] [Oscuro]         ║
│  ATENUADO por el scrim       ║                                 ║
│                              ║ Tamaño de letra                 ║
│  (data-sn-modal en <html>    ║ [S] [M] [L]                     ║
│   bloquea el scroll          ║                                 ║
│   subyacente)                ║ Índice                          ║
│                              ║ [Persistente] [En línea]        ║
│                              ║                                 ║
│                              ║ ☐ Secciones colapsables          ║
│                              ║ ☐ Reducir movimiento             ║
│                              ║                                 ║
│                              ╠═════════════════════════════════╣
│                              ║ Guardadas en este navegador.    ║
│                              ║                  [Restablecer]  ║
└──────────────────────────────╚═════════════════════════════════╝
                                   ↑ translateX, anima 420 ms
```

Compact (`< 48 rem`) — modal fullscreen:

```
╔════════════════════════════════════╗
║ Preferencias de lectura       [✕]  ║
╠════════════════════════════════════╣
║                                    ║
║ Tema                               ║
║ [Auto] [Claro] [Oscuro]            ║
║                                    ║
║ Tamaño de letra                    ║
║ [S] [M] [L]                        ║
║                                    ║
║ Índice                             ║
║ [Persistente] [En línea]           ║
║                                    ║
║ ☐ Secciones colapsables             ║
║ ☐ Reducir movimiento                ║
║                                    ║
╠════════════════════════════════════╣
║ Guardadas en este navegador.       ║
║                  [Restablecer]     ║
╚════════════════════════════════════╝
   ↑ ocupa 100 % del viewport
```

Notas:

- 5 preferencias visibles. `ContentWidth` y `LineHeight` se removieron
  (la métrica de la hoja y la interlínea son fijas: parametrizarlas
  desparametrizaba el ajuste al *baseline grid*). Ver
  [`WIKITEXTO.md`](WIKITEXTO.md) §3 para el comportamiento del cuerpo.
- Persistencia híbrida (resuelta en `Hooks.php` + `skin.js`):
  - **Usuario registrado** → opciones de cuenta MediaWiki (cross-device).
  - **Anónimo / cuenta temporal 1.43** → `localStorage` del navegador.
- El pre-pintado (script inline en `<head>` desde `Hooks.php`) aplica
  el tema **antes** del primer paint → sin FOUC al recargar.
- Default = claro. El SO no oscurece por sí solo; oscuro solo con
  elección explícita o `auto` (seguir al SO). Ver decisiones en
  [`DEVELOPMENT.md`](DEVELOPMENT.md).

## 5. Modificadores editoriales dentro del paper

Los esquemas detallados (`full-width`, `grilla`, `plantilla`, `img-circle`,
`sn-notice`) y cuándo se aplican están en
[`WIKITEXTO.md`](WIKITEXTO.md) §2. Visión rápida:

```
.sn-paper
┌────────────────────────────────────────────────────┐
│  (padding lateral --sn-paper-px)                   │
│  ┌──── .sn-body al 100 % del paper ─────────────┐  │
│  │  Párrafo normal (justificado, hyphens auto). │  │
│  │                                              │  │
│←─┼──────── .full-width  (margin-inline neg.) ───┼──→
│  │                                              │  │
│  │  .grilla.cols-2                              │  │
│  │  ┌──────────────┐ ┌──────────────┐           │  │
│  │  │              │ │              │           │  │
│  │  └──────────────┘ └──────────────┘           │  │
│  │                                              │  │
│  │  .grilla.cols2-1  (asimétrica 2/3 + 1/3)     │  │
│  │  ┌────────────────────────────┐ ┌──────────┐ │  │
│  │  │                            │ │          │ │  │
│  │  └────────────────────────────┘ └──────────┘ │  │
│  │                                              │  │
│  │  table.wikitable.plantilla                   │  │
│  │  ┌─────────────────────────┐                 │  │
│  │  │  Campo     valor        │ ← sin borde     │  │
│  │  │  Otro      valor        │   interno; th   │  │
│  │  │  Otro      valor        │   sin fondo     │  │
│  │  └─────────────────────────┘                 │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

## 6. Impresión

`print.css` esconde todo el chrome (`.sn-header`, `.sn-prefs`, `.sn-toc`,
`.sn-footer-tools`, todo `.noprint`) y simplifica el paper a tinta sobre
blanco. Los enlaces externos imprimen su URL entre paréntesis al final
(estándar editorial). Sin sombras, sin radio, sin fondo cálido:

```
┌─ @media print ─────────────────────────────────┐
│                                                │
│  firstHeading                                  │
│  ───────────                                   │
│                                                │
│  Cuerpo, tinta negra sobre blanco.             │
│  Enlace externo (https://ejemplo.org).         │
│                                                │
│  ─────────────────────────────────────         │
│  Pie de página: última modificación + lic.     │
└────────────────────────────────────────────────┘
```

# Stella Nova — Plan de desarrollo

Plan accionable. Principios en [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Cómo se desarrolla (entorno local Casiopea)

- Repo **independiente** en `~/Sites/casiopea/skins/stella-nova/` (este).
  Symlink `…/casiopea/w/skins/StellaNova → ../../skins/stella-nova` lo conecta
  a la wiki local sin copiar nada.
- Editar aquí → recargar navegador. `$wgDefaultSkin` **no** se cambia: se
  compara A/B con `?useskin=stellanova` vs `?useskin=vector-2022` en cualquier
  URL (también seleccionable en `Especial:Preferencias`).
- En dev: `$wgResourceLoaderDebug=true` para ver CSS/JS sin minificar.
- Páginas reales de prueba (Fase 5, set mínimo): "Bitácora de Huinay",
  "Definición de una Narrativa Visual…", "Diseño de Sistema de Señaléticas
  Bibliotecas PUCV", "Taller de Amereida 2020" (stress).

## Estado

- [x] **M0 — Skeleton**: `skin.json`, `SkinStellaNova` (extends `SkinMustache`),
  `skin.mustache` semántico, tokens/layout/print/JS, i18n en/es, repo git +
  remote (sin push). Renderiza sin errores PHP, seleccionable.
- [x] **M1 — skinStyles SMW/SRF/PageForms**: `resources/skinStyles/{smw,srf,
  pageforms}.css` inyectados vía `ResourceModuleSkinStyles` por módulo
  (`ext.smw.*.styles`, `ext.srf*`, `ext.pageforms.*.styles`), skin-scoped,
  refine-only. Verificado contra páginas reales: paridad de bytes del
  `mw-parser-output` con vector-2022 (no se recorta HTML de extensiones).
- [x] **M2 — Layout real**: "página de papel" — hoja centrada sobre campo
  ahuesado; cabecera-horizonte con isotipo (SVG nova autocontenido,
  theme-adaptive), búsqueda, herramientas tri-estado; **navegación en
  dropdown desde la barra superior** (no riel; ver Decisiones); pie
  compuesto (bloque gestionado + obligaciones core). Fidelidad: emite
  todas las data keys de SkinMustache 1.43 (`SkinRenderFidelity`).
- [x] **M3 — Tokens + tema**: `tokens.css` definitivo; **default claro**,
  oscuro solo por elección explícita / `auto`+SO (ver Decisiones); fuentes
  auto-alojadas (Work Sans + Fraunces, `fonts.css`, sin CDN runtime).
- [~] **M4 — Responsive + navegación**: mobile-first; dropdown colapsable;
  panel de preferencias (7, modal accesible) con persistencia híbrida
  (cuenta/`localStorage`) + pre-pintado sin FOUC. Falta ronda móvil real.
- [ ] M5 — Accesibilidad WCAG 2.1 AA (auditoría axe/WAVE + lector pantalla)
- [~] M6 — JS progresivo (panel/dropdown/menús hechos; degradación sin JS ok)
- [ ] M7 — Testing + CI
- [ ] M8 — Verificación final y publicación

`__PANTALLACOMPLETA__` operativo (behaviour switch, patrón NoTitle):
fija page-property → `SkinStellaNova` suprime chrome salvo escape.

## Roadmap

### M1 — skinStyles para extensiones (máxima prioridad)
Lo que más se nota. `skinStyles` en `skin.json` con hojas dedicadas para
**SemanticMediaWiki**, **SemanticResultFormats**, **PageForms**,
**TemplateStyles**. Que tablas `#preguntar`, formularios PageForms, factbox y
formatos SRF se vean bien sin reestructurar su DOM. Probar contra las páginas
reales importadas.

### M2 — Layout real
Header (logo, búsqueda funcional, menús de usuario), sidebar de portlets, ToC
persistente, footer completo (`data-footer`), `firstHeading`/subtítulo/
categorías/indicadores. Grid mayor + Flexbox componentes; container queries
donde aporten.

### M3 — Dark mode + tokens
Paleta semántica definitiva en `tokens.css`; light/dark vía
`prefers-color-scheme` + data-attribute conmutable; contraste AA en ambos.

### M4 — Responsive + navegación
Mobile-first; drawer en móvil ↔ sidebar en desktop; sin overflow horizontal;
breakpoints definidos. Búsqueda accesible.

### M5 — Accesibilidad WCAG 2.1 AA
Landmarks, skip-links, foco visible, orden de tab, ARIA en menús/drawer,
`prefers-reduced-motion`. Pasar axe/WAVE; teclado y lector de pantalla.

### M6 — JS progresivo
ES module mínimo (drawer, toggles, búsqueda). Sin jQuery propio. Degradar sin
JS. Reservar JS para interacciones inevitables.

### M7 — Testing + CI
Lint PHP/JS/CSS; pipeline que valide en cada push. PHPUnit si aplica.
Decidir herramienta (pendiente del PLAN del proyecto).

### M8 — Verificación final (checklist Fase 8 del PLAN)
- [ ] Artículo simple (wikitexto básico).
- [ ] Plantilla compleja (ParserFunctions, transclusión, `#preguntar`).
- [ ] Formulario PageForms se ve y funciona (crear/editar).
- [ ] `Especial:Navegar`/`Special:Browse` de SMW legible.
- [ ] Navegación entre namespaces (Categoría, Plantilla, Especial, Widget,
      Propiedad, Concepto…).
- [ ] Móvil/responsive sin overflow horizontal.
- [ ] Contraste WCAG AA mínimo.
- [ ] Sin errores en consola en páginas comunes.
- [ ] Instalable en Casiopea limpia con `wfLoadSkin('StellaNova')` sin pasos
      manuales extra.

## Decisiones

- Licencia: **GPL-2.0-or-later** (vendor el texto completo en `COPYING` antes
  de publicar — hoy es una nota corta).
- Remoto: **GitHub `eadpucv/stella-nova`** (`origin` configurado, **sin push**
  aún — empujar cuando M1+ esté presentable).
- Testing/CI: herramienta por definir (M7).
- **Tipografía** (rev. 2026-05-18): **solo Work Sans** (cuerpo/UI/títulos)
  + monospace del sistema para código. Fraunces **descartado por ahora**
  (no convencía en titulares); sus woff2 siguen vendoreados en
  `resources/fonts/` pero `fonts.css` ya no los declara. Titulares
  sobrios (sin escala exagerada). `--sn-font-display` es alias de Work
  Sans: reintroducir un display luego es una línea. Sin `font-variation-
  settings` (rompía el peso variable de Work Sans).
- **Navegación: cabecera despejada + mapa del sitio en el pie** (rev.
  2026-05-18, decisión del usuario): la barra superior queda *centrada en
  la página actual* — isotipo · pestañas de página (espacios + Leer/
  Editar/[Editar con formulario si PageForms asocia uno]/Historial) ·
  buscador · herramientas de usuario. La **navegación del sitio**
  (portlets del MediaWiki:Sidebar + toolbox + bloque institucional
  gestionado) bajó al **pie**, como mapa del sitio en columnas. Sin riel,
  sin hamburguesa, sin dropdowns de nivel superior en el header (las
  pestañas no se truncan: hacen scroll horizontal en pantallas chicas).
  Presentación, no comportamiento; `specs/stella-nova.allium` ya declara
  riel/dropdown/posición fuera de alcance (regiones intactas).
  ARCHITECTURE §4 ("sidebar persistente") = doctrina histórica supeditada.
- **La hoja (`.sn-paper`)** (2026-05-18): radio mínimo
  (`--sn-radius-paper` 3px) y sombra muy sutil (`--sn-lift-paper`), no
  flotante; asentada sobre el campo.
- **Tema: default claro, el SO no oscurece solo** (2026-05-18, decisión del
  usuario): sin preferencia guardada → claro, aunque el SO esté en oscuro;
  oscuro solo con elección explícita o `auto` (seguir al SO). **Reflejado
  en `specs/stella-nova.allium`** (2026-05-18): `enum ThemeChoice {light|
  dark|auto}`, `Preferences.theme: ThemeChoice?`, `ViewingSession.
  active_theme` condicional (`auto → os_scheme ?? light`; `light|dark`
  forzado; sin elección → `light`) y `@guarantee Precedence`. Ya no es
  divergencia: es el spec. `allium check` limpio (0 errores).

## Convención de commits

Mensajes en presente, foco en el milestone (p. ej. `M1: skinStyles SMW
factbox + tablas #ask`). Co-autoría según política del proyecto.

# Stella Nova — Arquitectura y principios

Doctrina que rige el desarrollo del skin. Doc canónico (vive en el repo del
skin, publicable). El plan accionable está en [`DEVELOPMENT.md`](DEVELOPMENT.md).

## 0. Principio rector

Escrito **desde cero**: sin Bootstrap, sin clonar Example/BoilerPlate, sin
heredar de Chameleon. Solo el contrato mínimo de MediaWiki (`SkinMustache` +
`skin.json`) y CSS moderno propio. Citizen/Vector/Lift se **leen** como
referencia, no se copian.

El **contrato de comportamiento** vive en
[`../specs/stella-nova.allium`](../specs/stella-nova.allium) (Allium, validado con
`allium check`): este doc fija doctrina y principios; el spec, la
especificación verificable de *qué hace* el skin (preferencias, chrome,
identidad, modo de página, fidelidad estructural). Ante desacuerdo, el
spec manda en comportamiento; este doc en presentación.

## 1. Stack de skins MediaWiki

MediaWiki migró de `SkinTemplate`+PHP a `SkinMustache` + registro declarativo
en `skin.json` + separación datos/presentación con Mustache. Permite trabajar
casi sin PHP y favorece código testeable. Es la dirección oficial.

## 2. Arquitectura base

- Declarar todo en `skin.json` (`ValidSkinNames`, `MessagesDirs`,
  `ResourceModules`, `AutoloadNamespaces`), no inicialización en PHP.
- Clase base `SkinMustache` (en MW 1.43 es **clase global** `SkinMustache`,
  no `MediaWiki\Skin\SkinMustache`). PHP al mínimo (config, wiring, hooks).
- Hooks en clase separada (`…Hooks.php`), no mezclados con layout.
- Estructura: `skin.json`, `includes/` (clase + `templates/*.mustache`),
  `resources/` (`styles/` Less/CSS, `scripts/` JS), `i18n/`.
- `templateDirectory` se declara en `skin.json` relativo al skin
  (convención Vector: `includes/templates`). Plantilla principal `skin.mustache`
  empieza con `{{{html-headelement}}}` y cierra `</body></html>`.
- **Isotipo autocontenido en el skin**, no en la wiki. Estándar MediaWiki:
  el logo es config de nivel wiki (`$wgLogos` → data key `data-logos`) y el
  core no provee variante por tema. Aquí se invierte: el asset canónico se
  versiona en `resources/`, el skin resuelve la variante clara/oscura según
  el tema activo, y `$wgLogos` —si la instalación lo define— actúa como
  override. Enlaza a la portada (`link-mainpage`, comportamiento de core).

## 3. Compatibilidad con Semantic MediaWiki (lo más crítico aquí)

SMW/SRF/PageForms generan mucho HTML (propiedades, tablas, formularios,
resultados en formatos diversos). Reglas:

- **No** sobrescribir agresivamente clases de core/SMW; refinar con CSS, no
  reestructurar el DOM.
- `skinStyles` dedicados en `skin.json` apuntando a hojas específicas para
  SMW y SRF (patrón Citizen), separadas del layout.
- Tablas/datatables como componentes: `overflow-x:auto` en contenedores;
  clases opt-in para "nowrap"/overflow sin romper funcionalidad.
- Sin alturas/anchos rígidos en elementos SMW; layouts líquido-flexibles.
- Probar con los formatos reales usados en Casiopea: tablas, listas,
  `#preguntar`, PageForms, `#widget` (Smarty), Mermaid, Maps.

Esta doctrina está **formalizada y es verificable** como el contrato
`SkinRenderFidelity` del spec: emisión de todas las data keys de
SkinMustache, no-strip ni reestructuración del HTML de extensiones,
placement de Factbox/SRF/PageForms/Widgets, hooks de inyección
(`html-after-content`, `data-indicators`, catlinks, `html-subtitle`) y
páginas `Special:`. La verificación es por snapshot del DOM contra
`vector-2022` sobre las páginas reales de Fase 5.

## 4. Responsividad

Mobile-first real (no MobileFrontend): un solo layout que adapta ancho,
navegación y densidad con breakpoints en CSS. Navegación que degrada:
drawer/hamburguesa en móvil, sidebar persistente en desktop. ToC persistente;
opcional command palette. Foco visible y navegación por teclado siempre.

## 5. Accesibilidad — objetivo WCAG 2.1 AA

- **Perceptible**: contraste AA (incl. dark mode); alternativas textuales
  (`aria-label`/`aria-hidden`); no depender solo del color.
- **Operable**: 100 % teclado, orden de tab lógico, `:focus-visible`,
  skip-link a contenido y a navegación; sin trampas de foco en
  modales/drawers (`role="dialog"`, `aria-modal`, devolver foco);
  `prefers-reduced-motion`.
- **Comprensible**: landmarks (`header/nav/main/aside/footer/search`),
  jerarquía de encabezados, labels claros.
- **Robusta**: HTML5 + ARIA correcto; testear con NVDA/VoiceOver y axe/WAVE
  en CI.
- **Identidad (MW 1.43)**: la UI distingue anónimo-IP, **cuenta temporal**
  (IP-masking, no loguea, features limitadas) y registrado; herramientas de
  usuario y persistencia de preferencias se ramifican en los tres.
- **`prefers-reduced-motion`** es preferencia de primera clase (resoluble:
  explícita > SO > sin reducir), no sólo una media query.
- **Modo pantalla completa** conserva siempre una afordancia de escape
  persistente y operable por teclado: no atrapar al usuario.

## 6. Configuración y extensibilidad

Núcleo de UX fijo + tuning por variables globales con defaults sensatos
(estilo Citizen: tema por defecto, secciones colapsables, page tools).
Documentar cada flag. Mantener en el README una tabla de compatibilidad de
extensiones con versiones testadas (Citizen-style). `skinStyles` se amplían
incrementalmente por extensión.

**Preferencias de usuario (7, estilo Citizen):** tema, ancho de contenido,
tamaño de fuente, interlineado, secciones colapsables, modo de índice
(persistente/en línea) y override de reduced-motion. Resolución por campo:
valor explícito > señal del SO (tema/motion) > default de diseño.
**Persistencia híbrida por identidad**: registrado → preferencia de cuenta
MediaWiki (BBDD, cross-device); anónimo/temporal → sesión del navegador.

**Chrome administrable desde la wiki:** pie, barra lateral y aviso se editan
como páginas del namespace `Stella-Nova`; la escritura (CRUD) se restringe
al grupo `editores-de-interfaz` (o sysop) vía `$wgNamespaceProtection`. El
pie es **compuesto**: las obligaciones core de MediaWiki (última
modificación, licencia/atribución, places, icons, hooks de extensión) se
renderizan SIEMPRE; el bloque institucional gestionado es adicional y se
oculta si su página está vacía (sin fallback propio).

**Modo de página:** una página declara `__PANTALLACOMPLETA__` (behaviour
switch, mismo patrón que `__NOTITLE__`/NoTitle) para control total del
viewport en páginas experimentales (HTML/p5.js); el skin suprime todo el
chrome salvo la afordancia de escape. Declarable por cualquier editor: el
riesgo de script está aislado en el mecanismo de inyección JS —hoy
`MediaWiki:Common.js` global, deuda reconocida a optimizar—.

## 7. Testing

Páginas de prueba que cubran patrones semánticos (fichas, listas, tablas de
propiedades, agregados, mapas, formularios); probar lectura/edición SMW en
distintos roles; rondas con lectores de pantalla y móviles reales; axe/WAVE
en el flujo continuo.

El spec Allium se valida con `allium check` en cada push; sus contratos y
surfaces (fidelidad estructural, panel de preferencias, chrome, isotipo)
son fuente para generar pruebas de integración (`allium propagate`).

## Referencias

- Manual:How to make a MediaWiki skin · …/Migrating SkinTemplate to SkinMustache
- Skin:Lift/Development guide · Skin:Citizen · Skin:Tweeki
- Accessibility guide for developers (MediaWiki) · A11y playbook WCAG 2.1 AA
- Codex › Accessibility · WAI-ARIA 1.3
- StarCitizenTools/mediawiki-skins-Citizen (GitHub)

(URLs completas en el commit original / `git log`; este doc es la síntesis
operativa.)

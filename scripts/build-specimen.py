#!/usr/bin/env python3
# Stella Nova — generador del espécimen gráfico.
#
# Lee resources/tokens.css y produce un mini-sitio estático autocontenido en
# docs/specimen/ (más un zip versionado para enviar al taller de diseño).
# El sitio sirve igual como GitHub Pages source (carpeta /docs en main).
#
# Tres páginas:
#   index.html       Fundamentos: paleta, tipografía, escala, sombras, radios.
#                    Auto-generadas a partir de tokens.css (no hay que tocar
#                    el script al añadir/renombrar variables).
#   components.html  Espécimen: cabeceras, texto, listas, citas, tablas,
#                    botones, inputs, toolbar, badges, alerts.
#   layout.html      Página completa simulada (header + paper + footer)
#                    levantando estructura del skin.mustache real.
#
# Cada página incluye un bloque <style id="overrides"> vacío al inicio: el
# diseñador edita variables ahí (sobreescribe tokens.css) y los cambios se
# propagan al documento entero. notes.md se preserva entre rebuilds.
#
# Uso:  python3 scripts/build-specimen.py
#       (idempotente: borra y reconstruye docs/specimen/ excepto notes.md)

import json
import re
import shutil
import zipfile
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────
SKIN_ROOT = Path(__file__).resolve().parent.parent
RESOURCES = SKIN_ROOT / "resources"
TEMPLATES = SKIN_ROOT / "includes" / "templates"
OUT_DIR   = SKIN_ROOT / "docs" / "specimen"
ASSETS    = OUT_DIR / "assets"

# ── token parser ───────────────────────────────────────────────────────────
# Cabecera de sección: comentario que empieza con `/* — ` y captura el título
# hasta el primer separador (—, (, :, , , o cierre */). Tolera headers
# multilínea como `/* — Tipografía — IBM Plex Sans (cuerpo/UI)... */`.
SECTION_RE = re.compile(r"/\*\s*—\s*([^—(:,\n]+?)\s*(?:[—(:,]|\*/)")
# Captura --sn-<nombre>: <valor>;  (valor puede ser multilínea), nota opcional /* ... */
TOKEN_RE = re.compile(
    r"--(sn-[a-z0-9-]+)\s*:\s*([^;]+?);(?:[ \t]*/\*\s*(.+?)\s*\*/)?",
    re.DOTALL,
)

def parse_tokens(css_text: str):
    """Devuelve una lista de (section, name, value, note) en orden de aparición.

    Sólo el bloque :root principal (índices anteriores a la primera reapertura).
    Mantiene el orden del archivo para que el render respete la curaduría
    del autor del CSS."""
    # Recortar a :root { ... } principal (primer bloque).
    m = re.search(r":root\s*\{(.+?)^\}", css_text, re.DOTALL | re.MULTILINE)
    body = m.group(1) if m else css_text

    sections = []
    current = "General"
    pos = 0
    for tok in TOKEN_RE.finditer(body):
        # ¿Hay una cabecera de sección entre pos y este token?
        between = body[pos:tok.start()]
        for sec in SECTION_RE.finditer(between):
            current = sec.group(1).strip()
        name = tok.group(1)
        value = re.sub(r"\s+", " ", tok.group(2)).strip()
        note = (tok.group(3) or "").strip()
        sections.append((current, name, value, note))
        pos = tok.end()
    return sections


def classify(name: str, value: str) -> str:
    """Heurística: 'color' | 'size' | 'shadow' | 'duration' | 'font' |
       'ease' | 'number' | 'other'."""
    v = value.strip()
    if v.startswith("#") or v.startswith("color-mix") or v.startswith("rgb"):
        return "color"
    if v.startswith("url("):
        return "asset"
    if "cubic-bezier" in v:
        return "ease"
    if v.endswith("ms)") or v.endswith("ms") or "ms *" in v:
        return "duration"
    if v.startswith("'") or v.startswith('"'):
        return "font"
    if re.search(r"\d+px\s+(solid|dashed|dotted)", v):
        return "border"
    if "rgba(" in v and "," in v and v.count(",") >= 3:
        return "shadow"
    if re.match(r"^[\d.]+$", v):
        return "number"
    if re.search(r"(rem|em|px|vw|vh|dvh|cqw|%|clamp\(|calc\()", v):
        return "size"
    if "999px" in v or v.endswith("px") or v.endswith("rem"):
        return "size"
    return "other"


def group_by_section(tokens):
    sections = {}
    for sec, name, value, note in tokens:
        sections.setdefault(sec, []).append((name, value, note))
    return sections


# ── HTML helpers ───────────────────────────────────────────────────────────
def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def render_swatch(name, value, note):
    label = note or ""
    return f'''<figure class="sw" style="--sw-c: var(--{name});">
  <span class="sw-chip" aria-hidden="true"></span>
  <figcaption>
    <code class="sw-var">--{esc(name)}</code>
    <span class="sw-val">{esc(value)}</span>
    {f'<span class="sw-note">{esc(label)}</span>' if label else ''}
  </figcaption>
</figure>'''


def render_size(name, value, note):
    return f'''<figure class="sz">
  <span class="sz-bar" style="--sz-w: var(--{name});"></span>
  <figcaption>
    <code class="sz-var">--{esc(name)}</code>
    <span class="sz-val">{esc(value)}</span>
    {f'<span class="sz-note">{esc(note)}</span>' if note else ''}
  </figcaption>
</figure>'''


def render_shadow(name, value, note):
    return f'''<figure class="sh">
  <span class="sh-box" style="box-shadow: var(--{name});"></span>
  <figcaption>
    <code class="sh-var">--{esc(name)}</code>
    <span class="sh-val">{esc(value)}</span>
    {f'<span class="sh-note">{esc(note)}</span>' if note else ''}
  </figcaption>
</figure>'''


def render_text_scale(name, value, note, sample="Lorem ipsum dolor sit amet"):
    return f'''<figure class="ts" style="font-size: var(--{name});">
  <span class="ts-sample">{esc(sample)}</span>
  <figcaption>
    <code class="ts-var">--{esc(name)}</code>
    <span class="ts-val">{esc(value)}</span>
    {f'<span class="ts-note">{esc(note)}</span>' if note else ''}
  </figcaption>
</figure>'''


def render_other(name, value, note):
    return f'''<div class="kv">
  <code class="kv-var">--{esc(name)}</code>
  <span class="kv-val">{esc(value)}</span>
  {f'<span class="kv-note">{esc(note)}</span>' if note else ''}
</div>'''


def render_token(name, value, note):
    kind = classify(name, value)
    if kind == "color":
        return render_swatch(name, value, note)
    if kind == "shadow":
        return render_shadow(name, value, note)
    if name.startswith("sn-fs-"):
        return render_text_scale(name, value, note)
    if kind == "size":
        return render_size(name, value, note)
    return render_other(name, value, note)


def render_section(title, items):
    grid_kind = "grid-color" if any(classify(n, v) == "color" for n, v, _ in items) \
               else "grid-size" if any(n.startswith("sn-s-") or n.startswith("sn-fs-") for n, _, _ in items) \
               else "grid-other"
    return f'''<section class="tokgrp">
  <h2 class="tokgrp-h">{esc(title)}</h2>
  <div class="tokgrp-body {grid_kind}">
    {''.join(render_token(n, v, note) for n, v, note in items)}
  </div>
</section>'''


# ── sprite de íconos (carga el SnIcons.mustache real, filtrando comentarios
# Mustache `{{! ... }}`). Inyectado en cada página: cualquier ícono nuevo en
# el skin queda automáticamente disponible al regenerar el espécimen. ──
def load_icons_sprite():
    src = (TEMPLATES / "SnIcons.mustache").read_text()
    # Quitar comentarios Mustache (no HTML), incluso si abarcan varias líneas.
    return re.sub(r"\{\{!.*?\}\}", "", src, flags=re.DOTALL).strip()


# ── isotipo de marca inline ─────────────────────────────────────────────
# Antes íbamos por <img src="…casiopea-icon.svg">: el SVG queda en su propio
# documento → no hereda los tokens del host (`currentColor`, `--sn-paper`),
# así que el isotipo aparece como cuadrado negro fijo y no acompaña al cambio
# de tema. Solución: inlinear el archivo en el HTML para que los var(--…)
# resuelvan contra el tema activo. Se elimina el prólogo XML y los
# comentarios; se añade width/height/class para limitar tamaño en la chrome.
def load_brand_icon(size=28):
    raw = (RESOURCES / "casiopea-icon.svg").read_text()
    # Quitar declaración XML y comentarios <!-- … -->.
    raw = re.sub(r"<\?xml[^?]*\?>", "", raw)
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)
    raw = raw.strip()
    # Inyectar width/height/class en la etiqueta <svg …> de apertura.
    return re.sub(
        r"<svg\b",
        f'<svg class="spec-brand-icon" width="{size}" height="{size}"',
        raw,
        count=1,
    )


# ── page shell ─────────────────────────────────────────────────────────────
def page_shell(title, body, version, current_page):
    nav_items = [
        ("index.html", "Fundamentos"),
        ("components.html", "Componentes"),
        ("layout.html", "Layout"),
    ]
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == current_page else ""}>{label}</a>'
        for href, label in nav_items
    )
    icons_sprite = load_icons_sprite()
    brand_icon = load_brand_icon()
    return f"""<!DOCTYPE html>
<html lang="es" data-sn-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Stella Nova v{esc(version)}</title>
<link rel="icon" href="assets/icons/casiopea-icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="assets/tokens.css">
<link rel="stylesheet" href="assets/stella-nova.css">
<link rel="stylesheet" href="assets/specimen.css">
<!-- ── overrides ────────────────────────────────────────────────────────────
     El taller de diseño pega aquí redefiniciones de tokens para proponer
     cambios. Sobreescriben tokens.css sin tocar el archivo fuente. Ejemplo:
       :root {{ --sn-nova: #c33; --sn-fs-display: 2.4rem; }}
     ─────────────────────────────────────────────────────────────────── -->
<style id="overrides">
/* :root {{ --sn-nova: #cc3344; }} */
</style>
</head>
<body class="spec">
{icons_sprite}
<header class="spec-top">
  <a class="spec-brand" href="index.html" aria-label="Stella Nova — Inicio">
    {brand_icon}
    <span class="spec-brand-name">Stella Nova</span>
    <span class="spec-brand-ver">v{esc(version)}</span>
  </a>
  <nav class="spec-nav" aria-label="Secciones del espécimen">{nav}</nav>
  <div class="spec-controls">
    <fieldset class="spec-seg" aria-label="Tema">
      <legend class="vh">Tema</legend>
      <button type="button" data-theme="light" aria-pressed="true">Claro</button>
      <button type="button" data-theme="dark">Oscuro</button>
      <button type="button" data-theme="auto">Auto</button>
    </fieldset>
  </div>
</header>
<main class="spec-main">
{body}
</main>
<footer class="spec-foot">
  <p>
    Espécimen generado por <code>scripts/build-specimen.py</code> ·
    Stella Nova v{esc(version)} ·
    <a href="notes.md">notes.md</a> (notas del taller de diseño) ·
    <a href="https://wiki.ead.pucv.cl">wiki.ead.pucv.cl</a>
  </p>
</footer>
<script>
  // Mínimo: aplica preferencias en <html> y persiste en localStorage. El skin
  // real las resuelve server-side (registrados) o pre-paint (anónimos); aquí
  // basta el toggle visual para que el diseñador compare temas.
  (function () {{
    var html = document.documentElement;
    var apply = function (kind, value) {{
      html.setAttribute('data-sn-' + kind, value);
      localStorage.setItem('sn-spec-' + kind, value);
      document.querySelectorAll('[data-' + kind + ']').forEach(function (b) {{
        b.setAttribute('aria-pressed', b.dataset[kind] === value ? 'true' : 'false');
      }});
    }};
    ['theme'].forEach(function (k) {{
      var saved = localStorage.getItem('sn-spec-' + k);
      if (saved) apply(k, saved);
      document.querySelectorAll('[data-' + k + ']').forEach(function (b) {{
        b.addEventListener('click', function () {{ apply(k, b.dataset[k]); }});
      }});
    }});
  }})();
</script>
</body>
</html>
"""


# ── page bodies ────────────────────────────────────────────────────────────
def body_index(tokens):
    sections = group_by_section(tokens)
    rendered = []
    rendered.append("""<section class="intro">
  <h1 class="display">Stella Nova · fundamentos</h1>
  <p class="lede">Tokens del sistema visual: color, tipografía, escala,
  forma, movimiento. Cada valor proviene de
  <code>resources/tokens.css</code> y se refleja aquí en vivo.</p>
  <p class="lede-sub">Para proponer cambios, redefiní variables en el bloque
  <code>&lt;style id="overrides"&gt;</code> al inicio del documento — la página
  entera los toma. Anotaciones libres en <a href="notes.md">notes.md</a>.</p>
</section>""")
    for title, items in sections.items():
        rendered.append(render_section(title, items))
    return "\n".join(rendered)


def body_components():
    # Espécimen al estilo de colofón: cada bloque documenta tokens y muestra
    # el componente con texto simulado (lorem ipsum) o etiquetas funcionales.
    return r"""
<section class="comp">
  <h1 class="display">Stella Nova · componentes</h1>
  <p class="lede">Espécimen de primitivos del skin. Cada bloque documenta los
  tokens en juego y muestra el componente con texto simulado.</p>
</section>

<section class="comp">
  <h2>Colofón tipográfico</h2>
  <p class="meta">Familia única IBM Plex, auto-alojada en
  <code>assets/fonts/</code> (woff2, subsetting latin / latin-ext vía
  <code>unicode-range</code>). Sin CDN, sin Google Fonts.</p>
  <div class="demo">
    <div class="colophon">
      <div class="colophon-row">
        <div class="colophon-name" style="font-family: var(--sn-font-text);">Aa Bb Cc · 0123</div>
        <div class="colophon-meta">
          <strong>IBM Plex Sans</strong> · variable, dos ejes wght 100–700 + wdth 75–100<br>
          Token <code>--sn-font-sans</code> (primitiva). Alias semánticos:
          <code>--sn-font-text</code> = cuerpo + UI + cabeceras,
          <code>--sn-font-display</code> = alias de text.
        </div>
      </div>
      <div class="colophon-row">
        <div class="colophon-name" style="font-family: var(--sn-font-serif);">Aa Bb Cc · 0123</div>
        <div class="colophon-meta">
          <strong>Source Serif 4</strong> · variable, eje wght 200–900<br>
          Token <code>--sn-font-serif</code> (primitiva). Alias semántico:
          <code>--sn-font-quote</code> = citas + <code>&lt;poem&gt;</code> por defecto.<br>
          Activable como familia del cuerpo desde el menú del usuario
          (<code>data-sn-family="serif"</code>): cuerpo + UI voltean a Serif y
          citas/<code>&lt;poem&gt;</code> voltean a Sans.
        </div>
      </div>
      <div class="colophon-row">
        <div class="colophon-name" style="font-family: var(--sn-font-mono);">Aa Bb Cc · 0123</div>
        <div class="colophon-meta">
          <strong>IBM Plex Mono</strong> · monospace técnico<br>
          Token <code>--sn-font-mono</code><br>
          Uso: código, valores numéricos, identificadores
        </div>
      </div>
    </div>
  </div>
</section>

<section class="comp">
  <h2>Cabeceras</h2>
  <p class="meta">Todas las cabeceras (H1–H6) en <code>--sn-font-text</code>
  — IBM Plex Sans, familia única. Sus alturas de línea son múltiplos enteros
  de <code>--sn-baseline</code> (la interlínea del cuerpo): H1/H2 ocupan
  2 baselines, H3–H6 uno. Escala: <code>--sn-fs-display</code>
  (1.5–2.0 rem) → <code>--sn-fs-sm</code> (0.82–0.90 rem). El acento de
  color (carmín <code>--sn-nova</code>) sólo aparece en H3.</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">== Sección principal ==
=== Sub-sección ===
==== Agrupación menor ====
===== Apostilla =====
====== Referencia inline ======</pre>
    <div class="sn-paper sn-body demo">
      <h1 id="firstHeading" class="firstHeading">Heading 1 · display editorial</h1>
      <h2>Heading 2 · sección principal</h2>
      <h3>Heading 3 · sub-sección</h3>
      <h4>Heading 4 · agrupación menor</h4>
      <h5>Heading 5 · apostilla</h5>
      <h6>Heading 6 · referencia inline</h6>
    </div>
  </div>
  <div class="spec-notes">
    <p>El <strong>H1</strong> del artículo se genera automáticamente desde
    el título de la página — no se escribe en el cuerpo. La jerarquía
    editable empieza en <code>==</code> (dos signos igual a cada lado).
    Sumá un signo por cada nivel. No saltes niveles (no pongas
    <code>====</code> después de <code>==</code> sin un <code>===</code>
    intermedio).</p>
    <p>Con tres o más cabeceras, MediaWiki inserta automáticamente la
    tabla de contenidos. Se puede forzar con <code>__TOC__</code> o
    desactivar con <code>__NOTOC__</code>.</p>
  </div>
</section>

<section class="comp">
  <h2>Cuerpo de texto</h2>
  <p class="meta">Familia <code>--sn-font-text</code> · cuerpo
  <code>--sn-fs-base</code> (1.00–1.05 rem fluido) · interlínea
  <code>--sn-leading</code> (1.65, fijo) · medida de la hoja
  <code>--sn-measure</code> (58 rem, fijo). Los párrafos van
  justificados con <code>hyphens: auto</code> (depende del
  <code>lang</code> del documento).</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">Texto corrido con '''negrita''', ''cursiva''
y '''''ambas'''''.

Enlace interno: [[Página]] o [[Página|texto a mostrar]].
Enlace externo: [https://wiki.ead.pucv.cl texto]
o simplemente https://wiki.ead.pucv.cl.

Salto de párrafo: una línea en blanco.
Filete horizontal: cuatro guiones al inicio: ----</pre>
    <div class="sn-paper sn-body demo">
      <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
      eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
      ad minim veniam, quis nostrud <a href="#">exercitation ullamco</a>
      laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure
      dolor in <strong>reprehenderit</strong> in voluptate velit esse
      cillum dolore eu fugiat nulla pariatur.</p>
      <p>Excepteur sint occaecat cupidatat non proident, sunt in culpa qui
      officia deserunt mollit anim id est laborum. <a href="#" class="external">Sed
      ut perspiciatis</a> unde omnis iste natus error sit voluptatem
      accusantium doloremque <a href="#" class="new">laudantium</a>, totam
      rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi
      architecto beatae vitae dicta sunt explicabo.</p>
    </div>
  </div>
  <div class="spec-notes">
    <p>Enlaces: interno (carmín · azul en oscuro) · externo (con ícono
    <code>--sn-ext-icon</code>) · rojo (página inexistente, clase
    <code>.new</code> automática que MediaWiki añade al detectar el
    enlace muerto).</p>
    <p>Para citar texto inline usá <code>&lt;cite&gt;…&lt;/cite&gt;</code>
    (no hay sintaxis wiki dedicada). Para énfasis semántico fuerte,
    <code>&lt;strong&gt;</code> y <code>&lt;em&gt;</code> equivalen a
    <code>'''</code> y <code>''</code> pero son más explícitas.</p>
  </div>
</section>

<section class="comp">
  <h2>Listas</h2>
  <p class="meta">Sangría heredada de <code>--sn-s-5</code> · marcadores en
  <code>--sn-ink-soft</code> · espaciado vertical <code>--sn-s-1</code>.</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">* Ítem de lista no ordenada
* Otro ítem
** Sub-ítem (dos asteriscos)
*** Sub-sub-ítem

# Ítem de lista ordenada
# Segundo
## Sub-ítem ordenado

; Término primario
: Definición del término
; Término secundario
: Definición.

: Texto sangrado (sin término)
:: Doble sangría</pre>
    <div class="sn-paper sn-body demo">
      <ul>
        <li>Lorem ipsum dolor sit amet</li>
        <li>Consectetur adipiscing elit
          <ul>
            <li>Sub-ítem (dos asteriscos)</li>
            <li>Otro sub-ítem</li>
          </ul>
        </li>
        <li>Ut enim ad minim veniam</li>
      </ul>
      <ol>
        <li>Primer ítem de la secuencia</li>
        <li>Segundo ítem</li>
        <li>Tercero</li>
      </ol>
      <dl>
        <dt>Término primario</dt>
        <dd>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</dd>
        <dt>Término secundario</dt>
        <dd>Sed do eiusmod tempor incididunt ut labore.</dd>
      </dl>
    </div>
  </div>
  <div class="spec-notes">
    <p>Cada ítem ocupa una línea. La sangría se controla repitiendo el
    marcador (<code>**</code>, <code>##</code>). Las listas se cortan al
    encontrar una línea en blanco o un marcador distinto.</p>
    <p>Las listas de definición (<code>;</code> y <code>:</code>)
    también sirven para sangrar texto suelto: una línea iniciada con
    <code>:</code> sin <code>;</code> previo produce sólo la sangría.</p>
  </div>
</section>

<section class="comp">
  <h2>Tablas</h2>
  <p class="meta">Clase <code>.wikitable</code>: encabezados sobre
  <code>--sn-sunk</code> · filas alternas <code>--sn-hairline-soft</code> ·
  filete inferior <code>--sn-hairline</code> · caption en
  <code>--sn-font-display</code>.</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">{| class="wikitable"
|+ Título descriptivo de la tabla
! Token !! Rol !! Familia
|-
| --sn-fs-display || H1 display || text
|-
| --sn-fs-xl || H2 || text
|-
| --sn-fs-lg || H3 || text
|-
| --sn-fs-base || Cuerpo || text
|}</pre>
    <div class="sn-paper sn-body demo">
      <table class="wikitable">
        <caption>Escala tipográfica del sistema</caption>
        <thead>
          <tr><th>Token</th><th>Rol</th><th>Familia</th></tr>
        </thead>
        <tbody>
          <tr><td><code>--sn-fs-display</code></td><td>H1 display</td><td>text</td></tr>
          <tr><td><code>--sn-fs-xl</code></td><td>H2</td><td>text</td></tr>
          <tr><td><code>--sn-fs-lg</code></td><td>H3</td><td>text</td></tr>
          <tr><td><code>--sn-fs-base</code></td><td>Cuerpo</td><td>text</td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <div class="spec-notes">
    <p>Estructura: <code>{|</code> abre la tabla y va con la clase
    <code>wikitable</code> para heredar los estilos del skin.
    <code>|+</code> es el título (<code>&lt;caption&gt;</code>).
    <code>!</code> son celdas de encabezado, <code>|</code> son celdas
    de datos. <code>|-</code> separa filas. <code>|}</code> cierra.</p>
    <p>Atajos: <code>!!</code> y <code>||</code> permiten poner varias
    celdas en una sola línea. Modificador
    <code>class="wikitable plantilla"</code> retira los bordes internos
    para fichas (perfil, ficha técnica).</p>
  </div>
</section>

<section class="comp">
  <h2>Cita y poema</h2>
  <p class="meta"><code>&lt;blockquote&gt;</code> y <code>&lt;poem&gt;</code>
  (extensión Poem) consumen <code>--sn-font-quote</code>, que por defecto
  apunta a Source Serif 4 (la serif del skin, variable wght 200–900). Si
  el lector alterna la familia del cuerpo a serif desde el menú del
  usuario, citas y poemas voltean a sans para mantener el contraste
  editorial. El poema lleva
  <code>white-space: pre-wrap</code>, lo que conserva los espacios del
  wikitexto como materia significante (no son adorno: son la
  espacialidad del verso). Fragmento de la <em>Aventura de Amereida</em>
  (1967) usado en la portada de Casiopea.</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">&lt;blockquote&gt;
Texto de la cita en uno o más párrafos.
— Autoría, &lt;cite&gt;Obra&lt;/cite&gt; (año)
&lt;/blockquote&gt;

&lt;poem&gt;
     no fue
        el hallazgo
             ajeno a los descubrimientos

 ¡oh marinos!
     sus pájaras salvajes
        el mar incierto
             las gentes desnudas entre sus dioses
&lt;/poem&gt;</pre>
    <div class="sn-paper sn-body demo">
      <blockquote>
        <p>el descubrimiento no nos descubre nuestro propio continente,
        sino que nos da el continente propio.</p>
        <footer>— <cite>Amereida</cite> (1967)</footer>
      </blockquote>
      <div class="poem"><p>     no fue
        el hallazgo
             ajeno a los descubrimientos

 ¡oh marinos!
     sus pájaras salvajes
        el mar incierto
             las gentes desnudas entre sus dioses</p></div>
    </div>
  </div>
  <div class="spec-notes">
    <p>Para la cita: <code>&lt;blockquote&gt;…&lt;/blockquote&gt;</code>
    envuelve uno o varios párrafos. La atribución va como texto al final
    (no hay marcado específico).</p>
    <p>Para el poema: cada línea del wikitexto produce una línea visual
    y <strong>los espacios al inicio se preservan literalmente</strong>
    — así se reconstruye la espacialidad del verso. La extensión Poem
    inserta un <code>&lt;br&gt;</code> tras cada línea, pero el skin lo
    suprime visualmente porque el <code>\n</code> con
    <code>white-space: pre-wrap</code> ya produce el salto (de no hacerlo
    quedaría un espacio doble entre líneas).</p>
  </div>
</section>

<section class="comp">
  <h2>Código</h2>
  <p class="meta">Familia <code>--sn-font-mono</code> · fondo
  <code>--sn-sunk</code>.<br>
  Inline: padding 1px / 4px · radio 2 px · 0.9 em.<br>
  Bloque: padding <code>--sn-s-3</code> / <code>--sn-s-4</code> · radio
  <code>--sn-radius</code> · scroll horizontal en overflow.</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">Código inline: &lt;code&gt;const x = 1&lt;/code&gt;.

Bloque indentado (lo más simple): empezar
la línea con un espacio.
 function ejemplo() {
   return 42;
 }

Bloque preformateado explícito:
&lt;pre&gt;
texto monoespaciado, conserva
saltos de línea y espacios.
&lt;/pre&gt;</pre>
    <div class="sn-paper sn-body demo">
      <p>Inline: <code>const lorem = ipsum(dolor)</code> dentro de un párrafo.</p>
      <pre><code>// Bloque pre &gt; code
function loremIpsum(dolor, sit) {
    const amet = consectetur(dolor);
    return amet + sit;
}</code></pre>
    </div>
  </div>
  <div class="spec-notes">
    <p>Para citar nombres de variables, comandos o identificadores en
    medio de un párrafo, usá <code>&lt;code&gt;</code>. Para mostrar
    fragmentos largos, <code>&lt;pre&gt;</code> + <code>&lt;code&gt;</code>
    es el patrón estándar (lo que aquí se renderiza).</p>
    <p>El bloque preformateado por sangrado (línea iniciada con un
    espacio) es el más rápido pero no permite resaltado ni metadatos.
    La wiki no carga <code>SyntaxHighlight</code> en producción.</p>
  </div>
</section>

<section class="comp">
  <h2>Botones</h2>
  <p class="meta">Capa semántica <code>--sn-btn-*</code> · altura
  <code>--sn-ctl</code> (2.4 rem) · radio <code>--sn-radius</code> ·
  tipografía <code>--sn-fs-sm</code> · foco con la nova
  (<code>--sn-focus-ring</code>). La nova <strong>no rellena</strong>
  botones — sólo aro de foco.</p>
  <div class="demo demo-buttons">
    <div class="btn-row">
      <span class="btn-row-label">Primario</span>
      <button type="button" class="sn-btn sn-btn-primary">Acción principal</button>
      <button type="button" class="sn-btn sn-btn-primary" data-state="hover">Hover</button>
      <button type="button" class="sn-btn sn-btn-primary" disabled>Deshabilitado</button>
    </div>
    <div class="btn-row">
      <span class="btn-row-label">Neutro</span>
      <button type="button" class="sn-btn">Acción secundaria</button>
      <button type="button" class="sn-btn" data-state="hover">Hover</button>
      <button type="button" class="sn-btn" disabled>Deshabilitado</button>
    </div>
    <div class="btn-row">
      <span class="btn-row-label">Destructivo</span>
      <button type="button" class="sn-btn sn-btn-danger">Acción destructiva</button>
      <button type="button" class="sn-btn sn-btn-danger" data-state="hover">Hover</button>
    </div>
    <div class="btn-row">
      <span class="btn-row-label">Ícono</span>
      <button type="button" class="sn-iconbtn" aria-label="Editar">
        <svg class="sn-i" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24"><use href="#sn-i-edit"/></svg>
      </button>
      <button type="button" class="sn-iconbtn" aria-label="Historial">
        <svg class="sn-i" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24"><use href="#sn-i-clock"/></svg>
      </button>
      <button type="button" class="sn-iconbtn" aria-label="Más opciones">
        <svg class="sn-i" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24"><use href="#sn-i-list"/></svg>
      </button>
    </div>
  </div>
  <div class="spec-notes">
    <p>Los botones son parte de la <strong>interfaz del skin</strong>,
    no se escriben en el wikitexto del artículo. Aparecen
    automáticamente en formularios (editar, mover, subir archivo), en
    diálogos de extensiones (PageForms, ReplaceText) y en barras de
    acción. Los botones de ícono pueblan el cluster a la derecha del
    título cuando la usuaria tiene permisos sobre la página.</p>
    <p>Si una plantilla necesita un botón propio, lo mejor es envolver
    un enlace con la clase <code>sn-btn</code>:
    <code>&lt;span class="sn-btn"&gt;[[Página|Texto]]&lt;/span&gt;</code>.</p>
  </div>
</section>

<section class="comp">
  <h2>Formularios</h2>
  <p class="meta">Capa semántica <code>--sn-field-*</code> · borde
  <code>--sn-field-border</code> · foco con
  <code>--sn-focus-border</code> + <code>--sn-focus-ring</code> ·
  placeholder en <code>--sn-field-placeholder</code>.</p>
  <div class="demo">
    <form class="sn-form" onsubmit="event.preventDefault();">
      <p>
        <label for="ft1">Input text</label>
        <input id="ft1" type="text" value="Lorem ipsum dolor sit amet">
      </p>
      <p>
        <label for="ft2">Input search</label>
        <input id="ft2" type="search" placeholder="Buscar…">
      </p>
      <p>
        <label for="ft3">Textarea</label>
        <textarea id="ft3" rows="3">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</textarea>
      </p>
      <p>
        <label for="ft4">Select</label>
        <select id="ft4">
          <option>Opción primera</option>
          <option>Opción segunda</option>
          <option>Opción tercera</option>
        </select>
      </p>
      <p>
        <label><input type="checkbox" checked> Checkbox marcado</label>
        <label><input type="checkbox"> Checkbox vacío</label>
      </p>
      <p>
        <label><input type="radio" name="vis" checked> Radio activo</label>
        <label><input type="radio" name="vis"> Radio inactivo</label>
      </p>
      <p class="sn-form-actions">
        <button type="submit" class="sn-btn sn-btn-primary">Aceptar</button>
        <button type="button" class="sn-btn">Secundario</button>
        <button type="button" class="sn-btn sn-btn-ghost">Cancelar</button>
      </p>
    </form>
  </div>
  <div class="spec-notes">
    <p>Los formularios estándar de MediaWiki (preferencias, búsqueda
    avanzada, mover página) los provee el core y heredan estos estilos
    automáticamente. Para crear formularios editoriales (fichas de
    proyecto, observaciones, etapas, travesías) la wiki usa la
    extensión <strong>PageForms</strong>: el formulario se define en
    una página <code>Plantilla:Formulario/Nombre</code> con la sintaxis
    de PageForms (<code>{{{field|nombre|input type=…}}}</code>) y el
    skin lo renderiza con estos primitivos.</p>
  </div>
</section>

<section class="comp">
  <h2>Pestañas de página</h2>
  <p class="meta">Bandeja de acciones del artículo · pestaña activa marcada
  con filete inferior <code>--sn-nova</code> (2 px) · enlace rojo (página
  inexistente) en <code>--sn-link</code>.</p>
  <div class="demo">
    <nav class="sn-tabs" aria-label="Pestañas de página">
      <ul>
        <li class="selected"><a href="#">Pestaña activa</a></li>
        <li><a href="#">Pestaña</a></li>
        <li><a href="#">Pestaña</a></li>
        <li><a href="#">Pestaña</a></li>
        <li class="new"><a href="#">Inexistente</a></li>
      </ul>
    </nav>
  </div>
  <div class="spec-notes">
    <p>Las pestañas las genera el skin a partir de los namespaces y
    permisos: <em>Artículo · Discusión · Editar · Historial · Más</em>.
    No se escriben en el wikitexto. Para añadir pestañas propias, las
    extensiones usan el hook <code>SkinTemplateNavigation</code>; el
    skin las recibe y las renderiza en la misma bandeja.</p>
  </div>
</section>

<section class="comp">
  <h2>Avisos (washes)</h2>
  <p class="meta">Fondos derivados con <code>color-mix(in oklab, ...)</code>
  sobre <code>--sn-paper</code> — voltean con el tema sin redefinir. Filete
  izquierdo (3 px) en el color de la señal.</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">&lt;div class="sn-wash sn-wash-ok"&gt;
'''Confirmación.''' Texto del aviso.
&lt;/div&gt;

&lt;div class="sn-wash sn-wash-info"&gt;
'''Información.''' Aviso neutro.
&lt;/div&gt;

&lt;div class="sn-wash sn-wash-warn"&gt;
'''Advertencia.''' Precaución.
&lt;/div&gt;

&lt;div class="sn-wash sn-wash-danger"&gt;
'''Error.''' Bloqueo o falla.
&lt;/div&gt;</pre>
    <div class="demo demo-stack">
      <aside class="sn-wash sn-wash-ok">
        <strong>Confirmación.</strong> Lorem ipsum dolor sit amet.
      </aside>
      <aside class="sn-wash sn-wash-info">
        <strong>Información.</strong> Sed do eiusmod tempor incididunt.
      </aside>
      <aside class="sn-wash sn-wash-warn">
        <strong>Advertencia.</strong> Ut enim ad minim veniam.
      </aside>
      <aside class="sn-wash sn-wash-danger">
        <strong>Error.</strong> Duis aute irure dolor.
      </aside>
    </div>
  </div>
  <div class="spec-notes">
    <p>Variantes: <code>sn-wash-ok</code> (confirmación) ·
    <code>sn-wash-info</code> (aviso neutro) ·
    <code>sn-wash-warn</code> (precaución) ·
    <code>sn-wash-danger</code> (error o bloqueo). Estos avisos los
    inserta el skin en respuesta a acciones del sistema, pero también
    se pueden emitir desde una plantilla envolviendo el contenido en
    un <code>&lt;div&gt;</code> con la clase correspondiente.</p>
  </div>
</section>

<section class="comp">
  <h2>Badges y contadores</h2>
  <p class="meta">Badge: tipografía <code>--sn-fs-xs</code> peso 500, radio
  <code>--sn-radius</code> · fondo wash correspondiente a la señal.<br>
  Pill: <code>--sn-radius-pill</code> + familia mono para valores numéricos.</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">&lt;span class="sn-badge"&gt;Neutro&lt;/span&gt;
&lt;span class="sn-badge sn-badge-nova"&gt;Nova&lt;/span&gt;
&lt;span class="sn-badge sn-badge-ok"&gt;Activo&lt;/span&gt;
&lt;span class="sn-badge sn-badge-warn"&gt;En revisión&lt;/span&gt;
&lt;span class="sn-badge sn-badge-danger"&gt;Bloqueado&lt;/span&gt;

&lt;span class="sn-pill"&gt;42 ítems&lt;/span&gt;</pre>
    <div class="demo demo-inline">
      <span class="sn-badge">Neutro</span>
      <span class="sn-badge sn-badge-nova">Nova</span>
      <span class="sn-badge sn-badge-ok">OK</span>
      <span class="sn-badge sn-badge-warn">Aviso</span>
      <span class="sn-badge sn-badge-danger">Error</span>
      <span class="sn-pill">000 ítems</span>
      <span class="sn-pill">000 ítems</span>
    </div>
  </div>
  <div class="spec-notes">
    <p>Badges para estados cortos (palabras); pills para contadores
    numéricos (familia mono). Variantes:
    <code>sn-badge-nova</code> · <code>-ok</code> · <code>-warn</code>
    · <code>-danger</code>. Útiles para marcar el estado de una etapa,
    un proyecto o una observación dentro de fichas y plantillas.</p>
  </div>
</section>

<section class="comp">
  <h2>Tabla de contenidos</h2>
  <p class="meta">Numeración en <code>--sn-font-mono</code> ·
  <code>--sn-fs-xs</code> · filete izquierdo en <code>--sn-nova</code>
  marca la sección activa.</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">== Sección uno ==
== Sección dos ==
=== Sub-sección 2.1 ===
=== Sub-sección 2.2 ===
== Sección tres ==

Palabras mágicas (control fino):
__TOC__       inserta el índice en este punto.
__NOTOC__     suprime el índice de la página.
__FORCETOC__  fuerza el índice aun con &lt; 4 cabeceras.</pre>
    <div class="demo">
      <nav class="sn-toc" aria-label="Tabla de contenidos">
        <h3 class="sn-toc-h">Contenidos</h3>
        <ol>
          <li><a href="#"><span class="num">1</span> Sección uno</a></li>
          <li><a href="#" class="active"><span class="num">2</span> Sección dos · activa</a>
            <ol>
              <li><a href="#"><span class="num">2.1</span> Sub-sección</a></li>
              <li><a href="#"><span class="num">2.2</span> Sub-sección</a></li>
            </ol>
          </li>
          <li><a href="#"><span class="num">3</span> Sección tres</a></li>
        </ol>
      </nav>
    </div>
  </div>
  <div class="spec-notes">
    <p>Por defecto la tabla aparece automáticamente cuando hay 4 o más
    cabeceras (<code>==</code>, <code>===</code>, etc.), justo antes de
    la primera. Las palabras mágicas con doble guión bajo a cada lado
    la sobrescriben (sensibles a mayúsculas).</p>
    <p>El skin la renderiza <strong>en la posición donde la coloque
    MediaWiki</strong> — respeta la ubicación de <code>__TOC__</code>.
    Solo cambia su vestimenta (numeración monoespaciada, filete
    izquierdo carmín marcando la sección activa).</p>
  </div>
</section>

<section class="comp">
  <h2>Nota al margen</h2>
  <p class="meta"><code>aside.sn-notice</code> · información meta del
  artículo (categorías, redirecciones, banners de plantilla) · fondo
  <code>--sn-info-wash</code> · filete <code>--sn-warn</code>.</p>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">&lt;aside class="sn-notice" role="note"&gt;
'''Nota.''' Texto del aviso, con [[enlaces]]
si hace falta.
&lt;/aside&gt;</pre>
    <div class="sn-paper sn-body demo">
      <aside class="sn-notice" role="note">
        <strong>Nota.</strong> Lorem ipsum dolor sit amet, consectetur
        adipiscing elit. Sed do eiusmod tempor incididunt.
      </aside>
      <p>El cuerpo del artículo continúa debajo del aviso, manteniendo el
      flujo de lectura sin saltos visuales bruscos.</p>
    </div>
  </div>
  <div class="spec-notes">
    <p>A diferencia de los washes (que codifican una severidad), la
    nota al margen es información meta del artículo: redirecciones,
    banners de plantilla, advertencias editoriales. Va dentro del
    cuerpo y rompe sutilmente el flujo sin alarmar. Se usa también
    para el fragmento administrable
    <code>Stella-Nova:Aviso</code> que se inyecta al tope del paper.</p>
  </div>
</section>

<section class="comp">
  <h2>Imágenes a sangre completa (.full-width)</h2>
  <p class="meta">Clase de wikitexto migrada desde <code>Common.css</code> de
  producción para que viaje con el tema. Una imagen, figura o envoltorio con
  <code>class="full-width"</code> se &laquo;revienta&raquo; del padding lateral
  de la hoja para ir <strong>borde a borde</strong> del artículo. Sirve a tres
  patrones de wikitexto.</p>

  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">[[Archivo:foo.jpg|class=full-width]]
[[Archivo:foo.jpg|frameless|class=full-width]]
&lt;div class="full-width"&gt;[[Archivo:foo.jpg]]&lt;/div&gt;</pre>
    <div class="sn-paper sn-body demo demo--bleed">
      <p>Párrafo del cuerpo, con el ancho de lectura normal de la hoja.</p>
      <div class="full-width spec-bleed">imagen a sangre completa · borde a borde</div>
      <p>El párrafo siguiente regresa al ancho de lectura.</p>
    </div>
  </div>

  <div class="spec-notes">
    <p>El truco: <code>margin-inline: calc(-1 * var(--sn-paper-px))</code>, el
    mismo padding lateral que la hoja expone como contrato. Sólo funciona
    dentro de <code>.sn-paper</code> / <code>.sn-canvas</code>. También casa el
    token con apóstrofes <code>'full-width'</code> que MediaWiki preserva en
    <code>[[Imagen:…|class='full-width']]</code>.</p>
  </div>
</section>

<section class="comp">
  <h2>Botón de contenido (.wiki-btn)</h2>
  <p class="meta">Clase de wikitexto migrada desde <code>Common.css</code> al
  tema. Botón &laquo;outline&raquo; que envuelve un enlace: contorno fino
  (1&nbsp;px) en forma de píldora; al pasar el cursor se rellena y el texto
  voltea. Tres variantes: por defecto (gris), <code>red</code> y
  <code>green</code>. Color 100&nbsp;% por tokens → voltea claro/oscuro.</p>

  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">&lt;span class="wiki-btn"&gt;[[Página|Etiqueta]]&lt;/span&gt;
&lt;span class="wiki-btn red"&gt;[[…|Rojo]]&lt;/span&gt;
&lt;span class="wiki-btn green"&gt;[[…|Verde]]&lt;/span&gt;</pre>
    <div class="sn-paper sn-body demo">
      <div class="demo-inline">
        <span class="wiki-btn"><a href="#">Por defecto</a></span>
        <span class="wiki-btn red"><a href="#">Rojo</a></span>
        <span class="wiki-btn green"><a href="#">Verde</a></span>
      </div>
    </div>
  </div>

  <div class="spec-notes">
    <p>Color 100&nbsp;% tokenizado: por defecto → <code>--sn-ink-soft</code>;
    <code>red</code> → <code>--sn-nova</code>; <code>green</code> →
    <code>--sn-ok</code>. El enlace interno hereda el color; al hover/foco el
    botón se rellena y el texto pasa a <code>--sn-nova-ink</code> (voltea:
    blanco en claro, casi-negro en oscuro). La variante <code>blue</code> se
    retiró (sin token equivalente, sin uso). Debe vivir dentro de
    <code>.sn-body</code> (la regla está acotada a ese contenedor).</p>
  </div>
</section>

<section class="comp">
  <h2>Grilla utilitaria</h2>
  <p class="meta">Reemplaza el patrón <code>.row &gt; .col-md-*</code> del
  skin Bootstrap anterior. <code>.grilla</code> es un Grid simple;
  <code>.cols-N</code> fija N columnas iguales (2–6);
  <code>.cols1-2</code> / <code>.cols2-1</code> son tercios asimétricos.
  Bajo 64 rem las grillas densas (4/5/6) reducen columnas; bajo 48 rem
  todas colapsan a una sola.</p>

  <h3 class="spec-subh">cols-2</h3>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">&lt;div class="grilla cols-2"&gt;
[[Archivo:a.jpg]]
[[Archivo:b.jpg]]
&lt;/div&gt;</pre>
    <div class="sn-paper sn-body demo">
      <div class="grilla cols-2">
        <div class="spec-cell">celda 1</div>
        <div class="spec-cell">celda 2</div>
      </div>
    </div>
  </div>

  <h3 class="spec-subh">cols-3</h3>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">&lt;div class="grilla cols-3"&gt;
…tres hijos directos…
&lt;/div&gt;</pre>
    <div class="sn-paper sn-body demo">
      <div class="grilla cols-3">
        <div class="spec-cell">1</div>
        <div class="spec-cell">2</div>
        <div class="spec-cell">3</div>
      </div>
    </div>
  </div>

  <h3 class="spec-subh">cols2-1 (tercios asimétricos)</h3>
  <div class="grilla cols-2 spec-usage">
<pre class="howto-code">&lt;div class="grilla cols2-1"&gt;
Bloque amplio (dos tercios)
Bloque angosto (un tercio)
&lt;/div&gt;</pre>
    <div class="sn-paper sn-body demo">
      <div class="grilla cols2-1">
        <div class="spec-cell">2/3 — bloque amplio</div>
        <div class="spec-cell">1/3</div>
      </div>
    </div>
  </div>

  <div class="spec-notes">
    <p>Cada hijo directo de <code>.grilla</code> es una celda; URLs
    largas o bloques de código no desbordan
    (<code>minmax(0, 1fr)</code>). El gap entre celdas es
    <code>--sn-s-4</code> (1 rem) y no se ajusta por página.</p>
    <p>Funciona en chrome normal y en <code>__PANTALLACOMPLETA__</code>:
    ambos contenedores llevan <code>.sn-body</code>, que es donde el
    skin define la regla. Si la grilla aparece "rota" (en una sola
    columna), revisar que esté dentro de <code>.sn-body</code>.</p>
  </div>
</section>
"""


def body_layout():
    # Header faithful to skin.mustache; body uses the same elements as the
    # components page so changes propagate consistently.
    return r"""
<div class="sn-app demo-app">
  <header class="sn-header" role="banner">
    <div class="sn-header-bar">
      <div class="sn-brandnav">
        <a class="sn-isotype" href="#" aria-label="Casiopea — Inicio">
          <img src="assets/icons/casiopea.svg" alt="" class="sn-isotype-img">
        </a>
        <div class="sn-md sn-sitenav">
          <button type="button" class="sn-md-trigger sn-md-icononly"
                  aria-expanded="false" aria-haspopup="true" aria-label="Navegación">
            <svg class="sn-i" aria-hidden="true" width="20" height="20" viewBox="0 0 24 24"><use href="#sn-i-menu"/></svg>
          </button>
        </div>
      </div>
      <form class="sn-search" role="search" action="#">
        <input type="search" placeholder="Buscar en Casiopea…">
        <button type="submit" class="sn-search-go" aria-label="Buscar">
          <svg class="sn-i" aria-hidden="true" width="16" height="16" viewBox="0 0 24 24"><use href="#sn-i-search"/></svg>
        </button>
      </form>
      <div class="sn-pagecluster">
        <a class="sn-iconbtn" href="#" aria-label="Editar">
          <svg class="sn-i" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24"><use href="#sn-i-edit"/></svg>
        </a>
        <a class="sn-iconbtn" href="#" aria-label="Historial">
          <svg class="sn-i" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24"><use href="#sn-i-clock"/></svg>
        </a>
      </div>
      <div class="sn-usertools">
        <button type="button" class="sn-usermenu-trigger" aria-haspopup="menu" aria-expanded="false" aria-label="Usuaria">
          <svg class="sn-i" aria-hidden="true" width="20" height="20" viewBox="0 0 24 24"><use href="#sn-i-user"/></svg>
        </button>
        <button type="button" class="sn-prefs-trigger" aria-haspopup="dialog" aria-label="Preferencias">
          <svg class="sn-i" aria-hidden="true" width="20" height="20" viewBox="0 0 24 24"><use href="#sn-i-sliders"/></svg>
        </button>
      </div>
    </div>
  </header>

  <div class="sn-shell">
    <div class="sn-paper-wrap">
      <article class="sn-paper mw-body">
        <aside class="sn-notice" role="note">
          <strong>Simulacro.</strong> Layout de Stella Nova con texto
          simulado (<em>lorem ipsum</em>) — referencia visual para diseño.
        </aside>
        <div id="contentSub" class="sn-subtitle">Subtítulo del artículo · metadato</div>
        <div class="sn-body mw-body-content">
          <h1 id="firstHeading" class="firstHeading">Título del artículo · display editorial</h1>

          <nav class="sn-toc" aria-label="Tabla de contenidos">
            <h3 class="sn-toc-h">Contenidos</h3>
            <ol>
              <li><a href="#sec-1"><span class="num">1</span> Sección primera</a></li>
              <li><a href="#sec-2" class="active"><span class="num">2</span> Sección segunda</a></li>
              <li><a href="#sec-3"><span class="num">3</span> Sección tercera</a></li>
              <li><a href="#sec-4"><span class="num">4</span> Sección cuarta</a></li>
            </ol>
          </nav>

          <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
          enim ad minim veniam, quis nostrud <a href="#">exercitation
          ullamco</a> laboris nisi ut aliquip ex ea commodo consequat. Duis
          aute irure dolor in reprehenderit in voluptate velit esse cillum
          dolore eu fugiat <strong>nulla pariatur</strong>.</p>

          <h2 id="sec-1">Sección primera</h2>
          <p>Excepteur sint occaecat cupidatat non proident, sunt in culpa
          qui officia deserunt mollit anim id est laborum. <a href="#"
          class="external">Sed ut perspiciatis</a> unde omnis iste natus
          error sit voluptatem accusantium doloremque laudantium, totam rem
          aperiam, eaque ipsa quae ab illo inventore veritatis et quasi
          architecto beatae vitae dicta sunt explicabo.</p>

          <blockquote>
            <p>Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut
            odit aut fugit, sed quia consequuntur magni dolores eos qui
            ratione voluptatem sequi nesciunt.</p>
            <footer>— Autoría · <cite>Obra de referencia</cite> (año)</footer>
          </blockquote>

          <h2 id="sec-2">Sección segunda</h2>
          <p>Neque porro quisquam est, qui dolorem ipsum quia dolor sit
          amet, consectetur, adipisci velit, sed quia non numquam eius modi
          tempora incidunt ut labore et dolore magnam aliquam quaerat
          voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem
          ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi
          consequatur.</p>

          <table class="wikitable">
            <caption>Tabla de muestra · datos simulados</caption>
            <thead>
              <tr><th>Columna A</th><th>Columna B</th><th>Año</th><th>Columna D</th></tr>
            </thead>
            <tbody>
              <tr><td>Valor lorem</td><td>Valor ipsum</td><td>0000</td><td>Valor dolor</td></tr>
              <tr><td>Valor sit</td><td>Valor amet</td><td>0000</td><td>Valor elit</td></tr>
              <tr><td>Valor sed</td><td>Valor eiusmod</td><td>0000</td><td>Valor tempor</td></tr>
              <tr><td>Valor incididunt</td><td>Valor labore</td><td>0000</td><td>Valor magna</td></tr>
            </tbody>
          </table>

          <h2 id="sec-3">Sección tercera</h2>
          <p>Quis autem vel eum iure reprehenderit qui in ea voluptate velit
          esse quam nihil molestiae consequatur, vel illum qui dolorem eum
          fugiat quo voluptas nulla pariatur.</p>
          <pre><code>// Bloque de código · familia --sn-font-mono
function loremIpsum(arg1, arg2) {
    return arg1 + arg2;
}</code></pre>

          <h2 id="sec-4">Sección cuarta</h2>
          <ul>
            <li>Lorem ipsum dolor sit amet.</li>
            <li>Consectetur adipiscing elit.</li>
            <li>Sed do <a href="#">eiusmod tempor</a> incididunt.</li>
            <li>Ut labore et <a href="#" class="new">dolore magna</a> aliqua.</li>
          </ul>
        </div>
      </article>
    </div>
  </div>

  <footer class="sn-footer" role="contentinfo">
    <div class="sn-footer-inner">
      <div class="sn-footer-col sn-footer-legal">
        <p>Pie de página · <a href="#">licencia</a> · última edición · fecha</p>
      </div>
      <nav class="sn-footer-col sn-footer-tools" aria-label="Herramientas">
        <ul>
          <li><a href="#">Enlace de pie</a></li>
          <li><a href="#">Enlace de pie</a></li>
          <li><a href="#">Enlace de pie</a></li>
        </ul>
      </nav>
    </div>
  </footer>
</div>
"""


# ── specimen.css (scaffolding propio del espécimen) ────────────────────────
SPECIMEN_CSS = r"""/* specimen.css — andamio del espécimen Stella Nova.
   Sólo lo necesario para presentar los componentes en grilla y para la
   barra de control superior. NO redefine tokens — los usa. */

html, body { margin: 0; padding: 0; background: var(--sn-field); color: var(--sn-ink);
             font-family: var(--sn-font-text); font-size: var(--sn-fs-base);
             line-height: var(--sn-leading); }

body.spec { display: flex; flex-direction: column; min-height: 100vh; }

.vh { position: absolute; clip: rect(0 0 0 0); width: 1px; height: 1px;
      overflow: hidden; white-space: nowrap; border: 0; padding: 0; margin: -1px; }

/* — Barra superior del espécimen — sticky, no es el header del skin. */
.spec-top {
  position: sticky; top: 0; z-index: 30;
  display: flex; align-items: center; gap: var(--sn-s-5);
  padding: var(--sn-s-3) var(--sn-s-5);
  background: color-mix(in oklab, var(--sn-field) 90%, transparent);
  -webkit-backdrop-filter: saturate(1.4) blur(10px);
  backdrop-filter: saturate(1.4) blur(10px);
  border-bottom: 1px solid var(--sn-hairline-soft);
}
.spec-brand { display: inline-flex; align-items: baseline; gap: var(--sn-s-2);
              text-decoration: none; color: var(--sn-ink); }
.spec-brand-icon { align-self: center; flex: none;
                   /* Sigue el tema: el <rect> es currentColor (tinta) y la
                      constelación var(--sn-paper) — al inlinear el SVG estos
                      tokens cambian con data-sn-theme. */ }
.spec-brand-name { font-family: var(--sn-font-display); font-size: var(--sn-fs-md);
                   font-weight: 500; letter-spacing: -0.01em; }
.spec-brand-ver { color: var(--sn-ink-faint); font-size: var(--sn-fs-xs);
                  font-family: var(--sn-font-mono); }

.spec-nav { display: flex; gap: var(--sn-s-1); margin-inline-start: var(--sn-s-4); }
.spec-nav a { padding: var(--sn-s-1) var(--sn-s-3); border-radius: var(--sn-radius);
              text-decoration: none; color: var(--sn-ink-soft); font-size: var(--sn-fs-sm);
              transition: background var(--sn-dur-1), color var(--sn-dur-1); }
.spec-nav a:hover { background: var(--sn-sunk); color: var(--sn-ink); }
.spec-nav a[aria-current="page"] { color: var(--sn-ink); background: var(--sn-paper);
                                   box-shadow: var(--sn-lift-paper); }

.spec-controls { margin-inline-start: auto; display: flex; gap: var(--sn-s-3); }
.spec-seg { border: 0; padding: 0; margin: 0; display: inline-flex;
            background: var(--sn-sunk); border-radius: var(--sn-radius-pill);
            padding: 2px; }
.spec-seg button { border: 0; background: transparent; padding: var(--sn-s-1) var(--sn-s-3);
                   font: inherit; color: var(--sn-ink-soft); font-size: var(--sn-fs-xs);
                   border-radius: var(--sn-radius-pill); cursor: pointer;
                   transition: background var(--sn-dur-1), color var(--sn-dur-1); }
.spec-seg button[aria-pressed="true"] { background: var(--sn-paper); color: var(--sn-ink);
                                        box-shadow: var(--sn-lift-paper); }

/* — Layout general — */
.spec-main { flex: 1; max-width: 76rem; margin-inline: auto;
             padding: var(--sn-s-6) var(--sn-s-5); width: 100%; box-sizing: border-box; }
.spec-foot { padding: var(--sn-s-5); text-align: center; color: var(--sn-ink-soft);
             font-size: var(--sn-fs-xs); border-top: var(--sn-hair); }
.spec-foot a { color: var(--sn-ink-soft); }

.intro, .comp, .tokgrp { margin-bottom: var(--sn-s-7); }
.intro h1, .comp h1 { font-family: var(--sn-font-display); font-size: var(--sn-fs-display);
                      font-weight: 400; letter-spacing: -0.02em; margin: 0 0 var(--sn-s-3); }
.intro .lede, .comp .lede { max-width: 38rem; font-size: var(--sn-fs-md);
                            color: var(--sn-ink-soft); }
.intro .lede-sub { max-width: 38rem; color: var(--sn-ink-soft); font-size: var(--sn-fs-sm);
                   margin-top: var(--sn-s-3); }
.comp h2 { font-family: var(--sn-font-display); font-size: var(--sn-fs-lg);
           font-weight: 400; margin: 0 0 var(--sn-s-2); }
.comp .meta { color: var(--sn-ink-soft); font-size: var(--sn-fs-sm);
              max-width: 42rem; margin: 0 0 var(--sn-s-4); }

/* — Bloques demo: la "hoja" donde se monta cada componente — */
.demo {
  background: var(--sn-paper); color: var(--sn-ink);
  border-radius: var(--sn-radius-paper); box-shadow: var(--sn-lift-paper);
  padding: var(--sn-s-5); margin-top: var(--sn-s-3);
}
.demo-cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
             gap: var(--sn-s-5); }
.demo-stack > * + * { margin-top: var(--sn-s-3); }
.demo-inline { display: flex; flex-wrap: wrap; gap: var(--sn-s-2); align-items: center; }
/* Demo de .full-width: el padding lateral del contenedor se iguala a
   --sn-paper-px (lo normal de .demo es --sn-s-5), para que el margin negativo
   de .full-width sangre EXACTO hasta el borde del demo. */
.demo--bleed { padding-inline: var(--sn-paper-px); }
.spec-bleed { background: var(--sn-sunk); color: var(--sn-ink-soft);
  padding: var(--sn-s-3); text-align: center; font-size: var(--sn-fs-sm); }

/* — Token grids — */
.tokgrp-h { font-family: var(--sn-font-display); font-size: var(--sn-fs-lg);
            font-weight: 400; margin: 0 0 var(--sn-s-4);
            padding-bottom: var(--sn-s-2); border-bottom: var(--sn-hair); }
.tokgrp-body { display: grid; gap: var(--sn-s-4); }
.grid-color { grid-template-columns: repeat(auto-fill, minmax(14rem, 1fr)); }
.grid-size  { grid-template-columns: 1fr; }
.grid-other { grid-template-columns: repeat(auto-fill, minmax(20rem, 1fr)); }

/* Swatch */
.sw { margin: 0; display: flex; gap: var(--sn-s-3); align-items: center;
      background: var(--sn-paper); padding: var(--sn-s-2);
      border-radius: var(--sn-radius); box-shadow: var(--sn-lift-paper); }
.sw-chip { width: 3rem; height: 3rem; flex: none; border-radius: var(--sn-radius);
           background: var(--sw-c); border: 1px solid var(--sn-hairline); }
.sw figcaption { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.sw-var { font-family: var(--sn-font-mono); font-size: var(--sn-fs-xs);
          color: var(--sn-ink); overflow-wrap: anywhere; }
.sw-val { font-family: var(--sn-font-mono); font-size: var(--sn-fs-xs);
          color: var(--sn-ink-soft); }
.sw-note { font-size: var(--sn-fs-xs); color: var(--sn-ink-faint); margin-top: 2px; }

/* Size */
.sz { margin: 0; padding: var(--sn-s-3); background: var(--sn-paper);
      border-radius: var(--sn-radius); box-shadow: var(--sn-lift-paper);
      display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: var(--sn-s-4);
      align-items: center; }
.sz-bar { display: block; height: 1.25rem; width: var(--sz-w);
          background: var(--sn-ink); border-radius: 2px; max-width: 100%; }
.sz figcaption { display: flex; flex-direction: column; gap: 2px; text-align: end; }
.sz-var { font-family: var(--sn-font-mono); font-size: var(--sn-fs-xs);
          color: var(--sn-ink); }
.sz-val { font-family: var(--sn-font-mono); font-size: var(--sn-fs-xs);
          color: var(--sn-ink-soft); }
.sz-note { font-size: var(--sn-fs-xs); color: var(--sn-ink-faint); }

/* Type scale */
.ts { margin: 0; padding: var(--sn-s-3); background: var(--sn-paper);
      border-radius: var(--sn-radius); box-shadow: var(--sn-lift-paper);
      display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: var(--sn-s-4);
      align-items: baseline; line-height: 1.2; }
.ts-sample { font-family: var(--sn-font-display); color: var(--sn-ink); }
.ts figcaption { display: flex; flex-direction: column; gap: 2px; text-align: end;
                 font-size: var(--sn-fs-xs); line-height: 1.4; }
.ts-var { font-family: var(--sn-font-mono); color: var(--sn-ink); }
.ts-val { font-family: var(--sn-font-mono); color: var(--sn-ink-soft); }
.ts-note { color: var(--sn-ink-faint); }

/* Shadow */
.sh { margin: 0; padding: var(--sn-s-4); background: var(--sn-field);
      border-radius: var(--sn-radius); display: flex; gap: var(--sn-s-4);
      align-items: center; border: var(--sn-hair); }
.sh-box { width: 4rem; height: 4rem; flex: none; background: var(--sn-paper);
          border-radius: var(--sn-radius); }
.sh figcaption { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.sh-var { font-family: var(--sn-font-mono); font-size: var(--sn-fs-xs); color: var(--sn-ink); }
.sh-val { font-family: var(--sn-font-mono); font-size: var(--sn-fs-xs); color: var(--sn-ink-soft);
          overflow-wrap: anywhere; }
.sh-note { font-size: var(--sn-fs-xs); color: var(--sn-ink-faint); }

/* KV genérico */
.kv { display: flex; flex-direction: column; gap: 2px; padding: var(--sn-s-3);
      background: var(--sn-paper); border-radius: var(--sn-radius);
      box-shadow: var(--sn-lift-paper); }
.kv-var { font-family: var(--sn-font-mono); font-size: var(--sn-fs-xs); color: var(--sn-ink); }
.kv-val { font-family: var(--sn-font-mono); font-size: var(--sn-fs-xs); color: var(--sn-ink-soft);
          overflow-wrap: anywhere; }
.kv-note { font-size: var(--sn-fs-xs); color: var(--sn-ink-faint); margin-top: 2px; }

/* — Colofón tipográfico — */
.colophon { display: grid; gap: var(--sn-s-5); }
.colophon-row {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr);
  gap: var(--sn-s-5); align-items: center;
  padding-bottom: var(--sn-s-4); border-bottom: var(--sn-hair);
}
.colophon-row:last-child { border-bottom: 0; padding-bottom: 0; }
.colophon-name {
  font-size: clamp(2.2rem, 1.6rem + 2vw, 3.2rem);
  line-height: 1.05; letter-spacing: -0.01em; color: var(--sn-ink);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.colophon-meta {
  font-size: var(--sn-fs-sm); color: var(--sn-ink-soft);
  line-height: 1.6;
}
.colophon-meta strong { color: var(--sn-ink); font-weight: 500; }
.colophon-meta code { font-size: 0.95em; }

/* — Componentes propios del espécimen que el skin aún no cubre. — */
/* Botón base (refleja la capa semántica --sn-btn-*) */
.sn-btn {
  display: inline-flex; align-items: center; justify-content: center;
  height: var(--sn-ctl); padding: 0 var(--sn-s-4);
  font: inherit; font-size: var(--sn-fs-sm); font-weight: 500;
  background: var(--sn-btn-bg); color: var(--sn-btn-fg);
  border: 1px solid var(--sn-btn-border); border-radius: var(--sn-radius);
  cursor: pointer; transition: background var(--sn-dur-1), border-color var(--sn-dur-1);
}
.sn-btn:hover, .sn-btn[data-state="hover"] {
  background: var(--sn-btn-bg-hover); border-color: var(--sn-btn-border-hover);
}
.sn-btn:focus-visible { outline: none; border-color: var(--sn-focus-border);
                        box-shadow: var(--sn-focus-ring); }
.sn-btn[disabled] { color: var(--sn-ink-faint); cursor: not-allowed;
                    background: var(--sn-field-bg-disabled); }
.sn-btn-primary {
  background: var(--sn-btn-primary-bg); color: var(--sn-btn-primary-fg);
  border-color: var(--sn-btn-primary-bg);
}
.sn-btn-primary:hover, .sn-btn-primary[data-state="hover"] {
  background: var(--sn-btn-primary-bg-hover); border-color: var(--sn-btn-primary-bg-hover);
}
.sn-btn-danger {
  background: var(--sn-btn-danger-bg); color: var(--sn-btn-danger-fg);
  border-color: var(--sn-btn-danger-bg);
}
.sn-btn-danger:hover, .sn-btn-danger[data-state="hover"] { filter: brightness(.92); }
.sn-btn-ghost { background: transparent; border-color: transparent; color: var(--sn-ink-soft); }
.sn-btn-ghost:hover { background: var(--sn-sunk); color: var(--sn-ink); }

.btn-row { display: flex; align-items: center; gap: var(--sn-s-3); flex-wrap: wrap;
           padding: var(--sn-s-3) 0; border-bottom: var(--sn-hair); }
.btn-row:last-child { border-bottom: 0; }
.btn-row-label { font-size: var(--sn-fs-xs); color: var(--sn-ink-faint);
                 text-transform: uppercase; letter-spacing: 0.05em;
                 width: 6rem; flex: none; font-family: var(--sn-font-mono); }

/* Formularios */
.sn-form p { display: flex; flex-direction: column; gap: var(--sn-s-1); margin: 0 0 var(--sn-s-4); }
.sn-form label { font-size: var(--sn-fs-sm); color: var(--sn-ink-soft); }
.sn-form :is(input[type="text"], input[type="search"], textarea, select) {
  font: inherit; font-size: var(--sn-fs-base);
  background: var(--sn-field-bg); color: var(--sn-field-fg);
  border: 1px solid var(--sn-field-border); border-radius: var(--sn-radius);
  padding: var(--sn-s-2) var(--sn-s-3); width: 100%; box-sizing: border-box;
  transition: border-color var(--sn-dur-1), box-shadow var(--sn-dur-1);
}
.sn-form :is(input, textarea, select):focus {
  outline: none; border-color: var(--sn-focus-border); box-shadow: var(--sn-focus-ring);
}
.sn-form ::placeholder { color: var(--sn-field-placeholder); }
.sn-form :is(input[type="checkbox"], input[type="radio"]) {
  accent-color: var(--sn-ink); margin-inline-end: var(--sn-s-2);
}
.sn-form-actions { display: flex; flex-direction: row !important; gap: var(--sn-s-2); }

/* Tabs de página */
.sn-tabs { background: var(--sn-paper); border-radius: var(--sn-radius-paper);
           box-shadow: var(--sn-lift-paper); padding: 0 var(--sn-s-3); }
.sn-tabs ul { display: flex; gap: 0; list-style: none; margin: 0; padding: 0; }
.sn-tabs li a { display: inline-block; padding: var(--sn-s-3) var(--sn-s-4);
                color: var(--sn-ink-soft); text-decoration: none;
                font-size: var(--sn-fs-sm); border-bottom: 2px solid transparent;
                transition: color var(--sn-dur-1), border-color var(--sn-dur-1); }
.sn-tabs li a:hover { color: var(--sn-ink); }
.sn-tabs li.selected a { color: var(--sn-ink); border-bottom-color: var(--sn-nova); }
.sn-tabs li.new a { color: var(--sn-link); }

/* Washes */
.sn-wash { padding: var(--sn-s-3) var(--sn-s-4); border-radius: var(--sn-radius);
           border-inline-start: 3px solid currentColor; font-size: var(--sn-fs-sm); }
.sn-wash strong { color: inherit; }
.sn-wash-ok     { background: var(--sn-ok-wash);     color: var(--sn-ok); }
.sn-wash-info   { background: var(--sn-info-wash);   color: var(--sn-warn); }
.sn-wash-warn   { background: var(--sn-warn-wash);   color: var(--sn-warn); }
.sn-wash-danger { background: var(--sn-danger-wash); color: var(--sn-danger); }
.sn-wash :is(strong, span, p) { color: var(--sn-ink); }
.sn-wash > strong:first-child { color: inherit; }

/* Badges */
.sn-badge { display: inline-flex; align-items: center; padding: 2px var(--sn-s-2);
            font-size: var(--sn-fs-xs); font-weight: 500;
            background: var(--sn-sunk); color: var(--sn-ink-soft);
            border-radius: var(--sn-radius); }
.sn-badge-nova   { background: var(--sn-nova-wash); color: var(--sn-nova); }
.sn-badge-ok     { background: var(--sn-ok-wash);     color: var(--sn-ok); }
.sn-badge-warn   { background: var(--sn-warn-wash);   color: var(--sn-warn); }
.sn-badge-danger { background: var(--sn-danger-wash); color: var(--sn-danger); }
.sn-pill { display: inline-flex; align-items: center; padding: 2px var(--sn-s-3);
           font-size: var(--sn-fs-xs); background: var(--sn-sunk);
           color: var(--sn-ink-soft); border-radius: var(--sn-radius-pill);
           font-family: var(--sn-font-mono); }

/* TOC */
.sn-toc { background: var(--sn-paper); border-radius: var(--sn-radius);
          padding: var(--sn-s-4); box-shadow: var(--sn-lift-paper); }
.sn-toc-h { font-family: var(--sn-font-display); font-size: var(--sn-fs-md);
            font-weight: 400; margin: 0 0 var(--sn-s-3); }
.sn-toc ol { list-style: none; margin: 0; padding: 0; }
.sn-toc ol ol { padding-inline-start: var(--sn-s-5); margin-top: var(--sn-s-1); }
.sn-toc li { margin: var(--sn-s-1) 0; }
.sn-toc a { display: inline-flex; align-items: baseline; gap: var(--sn-s-2);
            text-decoration: none; color: var(--sn-ink-soft);
            font-size: var(--sn-fs-sm); padding: 2px 0;
            border-inline-start: 2px solid transparent; padding-inline-start: var(--sn-s-2); }
.sn-toc a:hover { color: var(--sn-ink); }
.sn-toc a.active { color: var(--sn-ink); border-inline-start-color: var(--sn-nova); }
.sn-toc .num { font-family: var(--sn-font-mono); font-size: var(--sn-fs-xs);
               color: var(--sn-ink-faint); min-width: 1.5em; }

/* Tablas wikitable mínimas (la wiki tiene más reglas; aquí el espécimen) */
.wikitable { width: 100%; border-collapse: collapse; margin: var(--sn-s-3) 0;
             font-size: var(--sn-fs-sm); }
.wikitable caption { caption-side: top; text-align: start; color: var(--sn-ink-soft);
                     font-size: var(--sn-fs-xs); padding-bottom: var(--sn-s-2);
                     font-family: var(--sn-font-display); }
.wikitable :is(th, td) { padding: var(--sn-s-2) var(--sn-s-3); text-align: start;
                         border-bottom: var(--sn-hair); }
.wikitable th { font-weight: 500; color: var(--sn-ink); background: var(--sn-sunk); }
.wikitable tbody tr:nth-child(even) { background: var(--sn-hairline-soft); }

/* Footer del simulacro de layout */
.demo-app .sn-footer { padding: var(--sn-s-6) 0; border-top: var(--sn-hair);
                       margin-top: var(--sn-s-6); }
.demo-app .sn-footer-inner { max-width: var(--sn-shell); margin-inline: auto;
                             padding-inline: var(--sn-s-5); display: flex;
                             justify-content: space-between; gap: var(--sn-s-5);
                             flex-wrap: wrap; }
.demo-app .sn-footer-col p { margin: 0; font-size: var(--sn-fs-sm);
                              color: var(--sn-ink-soft); }
.demo-app .sn-footer-tools ul { list-style: none; margin: 0; padding: 0;
                                 display: flex; gap: var(--sn-s-4);
                                 font-size: var(--sn-fs-sm); }
.demo-app .sn-footer-tools a { color: var(--sn-ink-soft); text-decoration: none; }
.demo-app .sn-footer-tools a:hover { color: var(--sn-ink); }

/* Demo del layout completo: dejarlo respirar contra el chrome del espécimen */
.demo-app { background: var(--sn-field); margin: calc(-1 * var(--sn-s-6))
                                           calc(-1 * var(--sn-s-5)); }
.demo-app .sn-shell { max-width: var(--sn-shell); margin-inline: auto;
                       padding: var(--sn-s-6) var(--sn-s-5); }
.demo-app .sn-paper { background: var(--sn-paper); border-radius: var(--sn-radius-paper);
                       box-shadow: var(--sn-lift-paper); padding: var(--sn-s-6); }
.demo-app .sn-paper h1.firstHeading {
  font-family: var(--sn-font-display); font-size: var(--sn-fs-display);
  font-weight: 400; letter-spacing: -0.02em; margin: 0 0 var(--sn-s-5); }
.demo-app .sn-paper h2 { font-family: var(--sn-font-display); font-size: var(--sn-fs-lg);
                          font-weight: 400; margin: var(--sn-s-6) 0 var(--sn-s-3); }
.demo-app .sn-paper p { margin: 0 0 var(--sn-s-3); }
.demo-app .sn-paper a { color: var(--sn-link); }
.demo-app .sn-paper a:visited { color: var(--sn-link-visited); }
.demo-app .sn-paper a:hover { color: var(--sn-link-hover); }
.demo-app .sn-paper a.external::after {
  content: ''; display: inline-block; width: .7em; height: .7em;
  margin-inline-start: .25em; background-color: currentColor;
  mask-image: var(--sn-ext-icon); mask-repeat: no-repeat; mask-size: contain;
  -webkit-mask-image: var(--sn-ext-icon); -webkit-mask-repeat: no-repeat;
  -webkit-mask-size: contain;
}
.demo-app .sn-paper blockquote {
  margin: var(--sn-s-5) 0; padding: var(--sn-s-3) var(--sn-s-5);
  font-family: var(--sn-font-display); font-size: var(--sn-fs-md);
  color: var(--sn-ink); font-style: italic;
}
.demo-app .sn-paper blockquote footer { font-style: normal; font-size: var(--sn-fs-sm);
                                          color: var(--sn-ink-soft); margin-top: var(--sn-s-2); }

.sn-notice {
  background: var(--sn-info-wash); color: var(--sn-ink);
  padding: var(--sn-s-3) var(--sn-s-4); border-radius: var(--sn-radius);
  border-inline-start: 3px solid var(--sn-warn); font-size: var(--sn-fs-sm);
  margin: 0 0 var(--sn-s-4);
}

pre, code { font-family: var(--sn-font-mono); }
pre { background: var(--sn-sunk); padding: var(--sn-s-3) var(--sn-s-4);
      border-radius: var(--sn-radius); overflow-x: auto; font-size: var(--sn-fs-sm); }
code { background: var(--sn-sunk); padding: 1px 4px; border-radius: 2px;
       font-size: 0.9em; }
pre code { background: transparent; padding: 0; }

/* `.poem` ya está estilada por stella-nova.css (familia display,
   white-space: pre-wrap, `.poem br { display: none }`). No redefinir aquí. */

/* — Bloque "uso": código wikitexto a la izquierda, render a la derecha
   ── el editor lee la sintaxis y el efecto al mismo tiempo. Usa la
   misma `grilla cols-2` que el skin expone para wikitexto: el
   especímen demuestra el patrón usándolo. Bajo 56 rem colapsa a una
   sola columna (código arriba, render abajo). */
.spec-usage.grilla.cols-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sn-s-4);
  margin-top: var(--sn-s-3);
  margin-bottom: 0;
  align-items: stretch;
}
@media (max-width: 56rem) {
  .spec-usage.grilla.cols-2 { grid-template-columns: 1fr; }
}
.spec-usage > pre.howto-code {
  margin: 0;
  padding: var(--sn-s-4);
  background: var(--sn-sunk);
  border: 1px solid var(--sn-hairline-soft);
  border-radius: var(--sn-radius);
  font-family: var(--sn-font-mono);
  font-size: var(--sn-fs-xs);
  color: var(--sn-ink);
  line-height: 1.55;
  overflow-x: auto;
  white-space: pre;
}
.spec-usage > .demo { margin-top: 0; }

/* — Notas explicativas debajo del bloque de uso ── prosa secundaria
   sobre fondo sunk, para distinguirla del cuerpo editorial del demo. */
.spec-notes {
  margin-top: var(--sn-s-4);
  padding: var(--sn-s-3) var(--sn-s-4);
  background: var(--sn-sunk);
  border-radius: var(--sn-radius);
  font-size: var(--sn-fs-sm);
  color: var(--sn-ink-soft);
}
.spec-notes p { margin: 0 0 var(--sn-s-2); line-height: 1.55; }
.spec-notes p:last-child { margin-bottom: 0; }
.spec-notes p code { font-size: 0.92em; }

/* — Subtítulos dentro de un componente (p. ej. variantes de grilla) — */
.spec-subh {
  font-family: var(--sn-font-mono);
  font-size: var(--sn-fs-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
  color: var(--sn-ink-soft);
  margin: var(--sn-s-5) 0 var(--sn-s-2);
}

/* — Celda neutra para demostrar grillas: contorno sobrio, contenido
   pequeño centrado — no compite con el contenido editorial real. */
.spec-cell {
  padding: var(--sn-s-4);
  background: var(--sn-sunk);
  border-radius: var(--sn-radius);
  text-align: center;
  font-family: var(--sn-font-mono);
  font-size: var(--sn-fs-sm);
  color: var(--sn-ink-soft);
}

/* Iconbutton mínimo (el stella-nova.css real lo cubre, pero el demo aislado
   no siempre está dentro de los selectores anclados al chrome) */
.sn-iconbtn { display: inline-grid; place-items: center;
              width: var(--sn-ctl); height: var(--sn-ctl);
              background: transparent; color: var(--sn-icon);
              border: 1px solid transparent; border-radius: var(--sn-radius);
              cursor: pointer; transition: background var(--sn-dur-1),
              color var(--sn-dur-1), border-color var(--sn-dur-1); }
.sn-iconbtn:hover { background: var(--sn-sunk); color: var(--sn-icon-active);
                    border-color: var(--sn-hairline); }
"""


# ── build steps ────────────────────────────────────────────────────────────
NOTES_TEMPLATE = """# Notas de diseño — Stella Nova v{version}

Este archivo sobrevive a los rebuilds del espécimen. Anotá aquí decisiones,
preguntas y propuestas. Los cambios de tokens van en el bloque
`<style id="overrides">` al inicio de cada página HTML.

## Color
- (vacío)

## Tipografía
- (vacío)

## Espaciado y layout
- (vacío)

## Componentes
- (vacío)

## Otras observaciones
- (vacío)
"""

README_TEMPLATE = """# Stella Nova — espécimen gráfico v{version}

Mini-sitio estático con todos los tokens, componentes y un layout simulado del
skin **Stella Nova** para iteración con el taller de diseño.

## Cómo verlo

Abrí cualquiera de los HTML directamente en el navegador:

- `index.html` — fundamentos (paleta, tipografía, escala, sombras).
- `components.html` — componentes (botones, inputs, toolbar, etc.).
- `layout.html` — layout completo simulado.

No necesita servidor. Las fuentes y CSS van inlinados en `assets/`.

## Cómo proponer cambios

1. Abrí el HTML en un editor.
2. Edita el bloque `<style id="overrides">` al inicio y redefiní variables:
   ```css
   :root {{
     --sn-nova: #c33;
     --sn-fs-display: 2.4rem;
   }}
   ```
3. Recargá. Los cambios se propagan a todo el documento.
4. Anotaciones libres van en `notes.md`.
5. Guardá y mandá de vuelta.

## Cómo actualizar el espécimen

Cuando el skin cambia (nuevos tokens, componentes o ajustes de `tokens.css` /
`stella-nova.css`), el espécimen se regenera con un solo comando desde la raíz
del repo del skin:

```bash
python3 scripts/build-specimen.py
```

El script borra y recompone `docs/specimen/` y empaqueta un zip nuevo
`stella-nova-specimen-v<version>.zip`. **`notes.md` se preserva** entre
rebuilds, así que las anotaciones del taller de diseño no se pierden. Las
`overrides` que hayas escrito en los HTML **sí se pierden** (los HTML se
reescriben); copialas a `notes.md` o a un parche antes de regenerar si querés
conservarlas.

Flujo típico de iteración:

1. Diseñador recibe el zip, anota en `notes.md` y propone cambios en `overrides`.
2. Devuelve el zip.
3. Mantenedor traslada los cambios validados a `resources/tokens.css` /
   `resources/stella-nova.css` del skin.
4. Mantenedor corre `python3 scripts/build-specimen.py` para regenerar el
   espécimen sincronizado y manda el nuevo zip.

## GitHub Pages

Si el repo tiene Pages activado en `branch: main, folder: /docs`, el
espécimen queda disponible en:

    https://<usuario>.github.io/<repo>/specimen/

(Esta carpeta es navegable por sí sola; no requiere build adicional.)
"""


def clean():
    if OUT_DIR.exists():
        # Preservar notes.md
        notes = OUT_DIR / "notes.md"
        saved = notes.read_text() if notes.exists() else None
        # Borrar todo excepto el zip viejo lo borramos también
        for child in OUT_DIR.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
        if saved is not None:
            notes.write_text(saved)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)


def copy_assets():
    # CSS
    for f in ("tokens.css", "fonts.css", "stella-nova.css"):
        shutil.copy2(RESOURCES / f, ASSETS / f)
    # Fonts dir
    shutil.copytree(RESOURCES / "fonts", ASSETS / "fonts", dirs_exist_ok=True)
    # Iconos del skin (SVG sueltos en resources/)
    icons_dir = ASSETS / "icons"
    icons_dir.mkdir(exist_ok=True)
    for svg in ("casiopea.svg", "casiopea-icon.svg"):
        src = RESOURCES / svg
        if src.exists():
            shutil.copy2(src, icons_dir / svg)
    # Imágenes
    img_src = RESOURCES / "img"
    if img_src.exists():
        shutil.copytree(img_src, ASSETS / "img", dirs_exist_ok=True)


def write_specimen_css():
    (ASSETS / "specimen.css").write_text(SPECIMEN_CSS)


def write_pages(version):
    tokens = parse_tokens((RESOURCES / "tokens.css").read_text())
    (OUT_DIR / "index.html").write_text(
        page_shell("Fundamentos", body_index(tokens), version, "index.html")
    )
    (OUT_DIR / "components.html").write_text(
        page_shell("Componentes", body_components(), version, "components.html")
    )
    (OUT_DIR / "layout.html").write_text(
        page_shell("Layout", body_layout(), version, "layout.html")
    )


def write_notes(version):
    notes = OUT_DIR / "notes.md"
    if not notes.exists():
        notes.write_text(NOTES_TEMPLATE.format(version=version))


def write_readme(version):
    (OUT_DIR / "README.md").write_text(README_TEMPLATE.format(version=version))


def make_zip(version):
    zip_path = OUT_DIR / f"stella-nova-specimen-v{version}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(OUT_DIR.rglob("*")):
            if path.is_dir() or path.suffix == ".zip":
                continue
            arcname = Path("stella-nova-specimen") / path.relative_to(OUT_DIR)
            z.write(path, arcname)
    return zip_path


def main():
    skin_json = json.loads((SKIN_ROOT / "skin.json").read_text())
    version = skin_json.get("version", "0.0.0")
    print(f"Stella Nova specimen v{version}")
    print(f"  → output: {OUT_DIR}")
    clean()
    copy_assets()
    write_specimen_css()
    write_pages(version)
    write_notes(version)
    write_readme(version)
    zip_path = make_zip(version)
    print(f"✓ HTML  {OUT_DIR.relative_to(SKIN_ROOT)}/index.html")
    print(f"✓ ZIP   {zip_path.relative_to(SKIN_ROOT)} "
          f"({zip_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

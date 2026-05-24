#!/usr/bin/env python3
# Stella Nova — generador del espécimen gráfico.
#
# Lee resources/tokens.css y produce un mini-sitio estático autocontenido en
# docs/specimen/ (más un zip versionado para enviar al equipo de diseño).
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
# multilínea como `/* — Tipografía — Work Sans (cuerpo/UI)... */`.
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
     El equipo de diseño pega aquí redefiniciones de tokens para proponer
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
    <img src="assets/icons/casiopea-icon.svg" alt="" width="28" height="28">
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
    <fieldset class="spec-seg" aria-label="Ancho">
      <legend class="vh">Ancho</legend>
      <button type="button" data-width="narrow">Angosto</button>
      <button type="button" data-width="standard" aria-pressed="true">Estándar</button>
      <button type="button" data-width="wide">Ancho</button>
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
    <a href="notes.md">notes.md</a> (notas del equipo de diseño) ·
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
    ['theme', 'width'].forEach(function (k) {{
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
  <p class="meta">Tres familias variables auto-alojadas en
  <code>assets/fonts/</code> (woff2, subsetting latin / latin-ext vía
  <code>unicode-range</code>). Sin CDN, sin Google Fonts.</p>
  <div class="demo">
    <div class="colophon">
      <div class="colophon-row">
        <div class="colophon-name" style="font-family: var(--sn-font-display);">Aa Bb Cc · 0123</div>
        <div class="colophon-meta">
          <strong>Newsreader</strong> · serif editorial con eje óptico<br>
          Token <code>--sn-font-display</code> · pesos 400 / 700 + italic<br>
          Uso: H1–H2, <code>blockquote</code>, <code>&lt;poem&gt;</code>
        </div>
      </div>
      <div class="colophon-row">
        <div class="colophon-name" style="font-family: var(--sn-font-text);">Aa Bb Cc · 0123</div>
        <div class="colophon-meta">
          <strong>Work Sans</strong> · sans humanista, variable 300–700<br>
          Token <code>--sn-font-text</code> · normal e italic<br>
          Uso: cuerpo, UI, H3–H6
        </div>
      </div>
      <div class="colophon-row">
        <div class="colophon-name" style="font-family: var(--sn-font-mono);">Aa Bb Cc · 0123</div>
        <div class="colophon-meta">
          <strong>IBM Plex Mono</strong> · monospace técnico<br>
          Token <code>--sn-font-mono</code> · pesos 400 / 600 + italic<br>
          Uso: código, valores numéricos, identificadores
        </div>
      </div>
    </div>
  </div>
</section>

<section class="comp">
  <h2>Cabeceras</h2>
  <p class="meta">H1–H2 en <code>--sn-font-display</code>
  (<code>--sn-fs-display</code> → 1.5–2.0 rem, <code>--sn-fs-xl</code> →
  1.35–1.62 rem), interlínea <code>--sn-leading-tight</code> (1.22).
  H3–H6 en <code>--sn-font-text</code>, escala
  <code>--sn-fs-lg</code> → <code>--sn-fs-base</code>.</p>
  <div class="sn-paper sn-body demo">
    <h1 id="firstHeading" class="firstHeading">Heading 1 · display editorial</h1>
    <h2>Heading 2 · sección principal</h2>
    <h3>Heading 3 · sub-sección</h3>
    <h4>Heading 4 · agrupación menor</h4>
    <h5>Heading 5 · apostilla</h5>
    <h6>Heading 6 · referencia inline</h6>
  </div>
</section>

<section class="comp">
  <h2>Cuerpo de texto</h2>
  <p class="meta">Familia <code>--sn-font-text</code> · cuerpo
  <code>--sn-fs-base</code> (1.0–1.05 rem fluido) · interlínea
  <code>--sn-leading</code> (1.65 default; compact 1.45 · relaxed 1.9) ·
  medida <code>--sn-measure</code> (58 rem default; narrow 42 · wide 76 ·
  full sin tope).</p>
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
    <p class="meta">Enlaces: interno (azul·carmín según tema) · externo
    (con ícono <code>--sn-ext-icon</code>) · rojo (página inexistente,
    <code>--sn-link</code> con clase <code>.new</code>).</p>
  </div>
</section>

<section class="comp">
  <h2>Listas</h2>
  <p class="meta">Sangría heredada de <code>--sn-s-5</code> · marcadores en
  <code>--sn-ink-soft</code> · espaciado vertical <code>--sn-s-1</code>.</p>
  <div class="sn-paper sn-body demo demo-cols">
    <div>
      <h4>No ordenada</h4>
      <ul>
        <li>Lorem ipsum dolor sit amet</li>
        <li>Consectetur adipiscing elit</li>
        <li>Sed do eiusmod tempor incididunt
          <ul>
            <li>Ut labore et dolore magna aliqua</li>
            <li>Enim ad minim veniam</li>
          </ul>
        </li>
        <li>Ut enim ad minim veniam</li>
      </ul>
    </div>
    <div>
      <h4>Ordenada</h4>
      <ol>
        <li>Primer ítem de la secuencia</li>
        <li>Segundo ítem</li>
        <li>Tercer ítem, ligeramente más largo</li>
        <li>Cuarto y último</li>
      </ol>
      <h4>Definiciones</h4>
      <dl>
        <dt>Término primario</dt>
        <dd>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</dd>
        <dt>Término secundario</dt>
        <dd>Sed do eiusmod tempor incididunt ut labore.</dd>
      </dl>
    </div>
  </div>
</section>

<section class="comp">
  <h2>Tablas</h2>
  <p class="meta">Clase <code>.wikitable</code>: encabezados sobre
  <code>--sn-sunk</code> · filas alternas <code>--sn-hairline-soft</code> ·
  filete inferior <code>--sn-hairline</code> · caption en
  <code>--sn-font-display</code>.</p>
  <div class="sn-paper sn-body demo">
    <table class="wikitable">
      <caption>Escala tipográfica del sistema</caption>
      <thead>
        <tr><th>Token</th><th>Rol</th><th>Tamaño (<code>clamp</code>)</th><th>Familia</th></tr>
      </thead>
      <tbody>
        <tr><td><code>--sn-fs-display</code></td><td>Display, H1</td><td>1.5–2.0 rem</td><td>display</td></tr>
        <tr><td><code>--sn-fs-xl</code></td><td>H2</td><td>1.35–1.62 rem</td><td>display</td></tr>
        <tr><td><code>--sn-fs-lg</code></td><td>H3, lede</td><td>1.20–1.42 rem</td><td>text</td></tr>
        <tr><td><code>--sn-fs-md</code></td><td>H4, intro</td><td>1.05–1.18 rem</td><td>text</td></tr>
        <tr><td><code>--sn-fs-base</code></td><td>Cuerpo</td><td>1.00–1.05 rem</td><td>text</td></tr>
        <tr><td><code>--sn-fs-sm</code></td><td>Meta, UI</td><td>0.82–0.90 rem</td><td>text</td></tr>
        <tr><td><code>--sn-fs-xs</code></td><td>Apostillas, badges</td><td>0.72–0.78 rem</td><td>text / mono</td></tr>
      </tbody>
    </table>
  </div>
</section>

<section class="comp">
  <h2>Cita y poema</h2>
  <p class="meta"><code>blockquote</code> · <code>--sn-font-display</code>
  italic · filete carmín izquierdo (3 px · <code>--sn-nova</code>) · padding
  <code>--sn-s-3</code> / <code>--sn-s-5</code>.<br>
  <code>&lt;poem&gt;</code> · misma familia, sin filete,
  <code>white-space: pre-line</code>.</p>
  <div class="sn-paper sn-body demo">
    <blockquote>
      <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
      eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
      <footer>— Autoría · <cite>Obra de referencia</cite> (año)</footer>
    </blockquote>
    <pre class="poem"><poem>
Verso simulado, primera línea
verso simulado, segunda línea
verso simulado, tercera línea —
sangría heredada del bloque.
</poem></pre>
  </div>
</section>

<section class="comp">
  <h2>Código</h2>
  <p class="meta">Familia <code>--sn-font-mono</code> · fondo
  <code>--sn-sunk</code>.<br>
  Inline: padding 1px / 4px · radio 2 px · 0.9 em.<br>
  Bloque: padding <code>--sn-s-3</code> / <code>--sn-s-4</code> · radio
  <code>--sn-radius</code> · scroll horizontal en overflow.</p>
  <div class="sn-paper sn-body demo">
    <p>Inline: <code>const lorem = ipsum(dolor)</code> dentro de un párrafo.</p>
    <pre><code>// Bloque pre &gt; code
function loremIpsum(dolor, sit) {
    const amet = consectetur(dolor);
    return amet + sit;
}</code></pre>
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
</section>

<section class="comp">
  <h2>Avisos (washes)</h2>
  <p class="meta">Fondos derivados con <code>color-mix(in oklab, ...)</code>
  sobre <code>--sn-paper</code> — voltean con el tema sin redefinir. Filete
  izquierdo (3 px) en el color de la señal.</p>
  <div class="demo demo-stack">
    <aside class="sn-wash sn-wash-ok">
      <strong>Confirmación.</strong> Lorem ipsum dolor sit amet, consectetur
      adipiscing elit.
    </aside>
    <aside class="sn-wash sn-wash-info">
      <strong>Información.</strong> Sed do eiusmod tempor incididunt ut
      labore et dolore magna aliqua.
    </aside>
    <aside class="sn-wash sn-wash-warn">
      <strong>Advertencia.</strong> Ut enim ad minim veniam, quis nostrud
      exercitation ullamco laboris.
    </aside>
    <aside class="sn-wash sn-wash-danger">
      <strong>Error.</strong> Duis aute irure dolor in reprehenderit in
      voluptate velit esse cillum.
    </aside>
  </div>
</section>

<section class="comp">
  <h2>Badges y contadores</h2>
  <p class="meta">Badge: tipografía <code>--sn-fs-xs</code> peso 500, radio
  <code>--sn-radius</code> · fondo wash correspondiente a la señal.<br>
  Pill: <code>--sn-radius-pill</code> + familia mono para valores numéricos.</p>
  <div class="demo demo-inline">
    <span class="sn-badge">Neutro</span>
    <span class="sn-badge sn-badge-nova">Nova</span>
    <span class="sn-badge sn-badge-ok">OK</span>
    <span class="sn-badge sn-badge-warn">Aviso</span>
    <span class="sn-badge sn-badge-danger">Error</span>
    <span class="sn-pill">000 ítems</span>
    <span class="sn-pill">000 ítems</span>
  </div>
</section>

<section class="comp">
  <h2>Tabla de contenidos</h2>
  <p class="meta">Numeración en <code>--sn-font-mono</code> ·
  <code>--sn-fs-xs</code> · filete izquierdo en <code>--sn-nova</code>
  marca la sección activa.</p>
  <div class="demo demo-cols">
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
        <li><a href="#"><span class="num">4</span> Sección cuatro</a></li>
        <li><a href="#"><span class="num">5</span> Sección cinco</a></li>
      </ol>
    </nav>
  </div>
</section>

<section class="comp">
  <h2>Nota al margen</h2>
  <p class="meta"><code>aside.sn-notice</code> · información meta del
  artículo (categorías, redirecciones, banners de plantilla) · fondo
  <code>--sn-info-wash</code> · filete <code>--sn-warn</code>.</p>
  <div class="sn-paper sn-body demo">
    <aside class="sn-notice" role="note">
      <strong>Nota.</strong> Lorem ipsum dolor sit amet, consectetur
      adipiscing elit. Sed do eiusmod tempor incididunt.
    </aside>
    <p>El cuerpo del artículo continúa debajo del aviso, manteniendo el
    flujo de lectura sin saltos visuales bruscos.</p>
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
.spec-brand img { align-self: center; }
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
  border-inline-start: 3px solid var(--sn-nova);
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

.poem { font-family: var(--sn-font-display); font-style: italic;
        background: transparent; padding: 0; margin: var(--sn-s-4) 0; }
.poem poem { white-space: pre-line; }

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
skin **Stella Nova** para iteración con el equipo de diseño.

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
rebuilds, así que las anotaciones del equipo de diseño no se pierden. Las
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

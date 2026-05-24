#!/usr/bin/env python3
"""
Aplica las tres pasadas de tokenización a las hojas snapshot de skinStyles/:

  1. Hex → var(--sn-*) (45 reemplazos confirmados)
  2. @codex-var → var(--sn-*) (26 reemplazos confirmados)
  3. Medidas: criterio de Herbert
        - bordes (border, outline, hairline) → px (queda)
        - horizontal (padding-x, margin-x, gap, width, left/right) → var(--sn-s-N) o rem
        - vertical (padding-y, margin-y, height, top/bottom, font-size, line-height)
          → em / var(--sn-fs-X) / var(--sn-leading)

Donde el criterio es ambiguo (shorthand padding/margin con valores mezclados,
medidas que pueden ser ambas, etc.), se deja comentario `/* TODO tok */`.

Cada hoja se guarda con backup `.pre-tok-AAAAMMDD-HHMMSS`. Idempotente: si
una sustitución ya está aplicada, se salta.

NO toca las hojas hechas a mano (smw, srf, pageforms, oojs-ui).
"""
from __future__ import annotations
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Path relativo al repo del skin (este script vive en skins/stella-nova/scripts/).
SKIN_STYLES = Path(__file__).resolve().parent.parent / "resources" / "skinStyles"
# Hojas reescritas a mano: no se tocan. OOUI salió de esta lista el 2026-05-23
# (decisión del usuario: tratarla como snapshot tokenizado igual que el resto).
HAND_WRITTEN = {"smw.css", "srf.css", "pageforms.css"}
TS = datetime.now().strftime("%Y%m%d-%H%M%S")

# ─── PASADA 1: Hex confirmados ─────────────────────────────────────────────
HEX_MAP = {
    # Blancos / fondos claros
    "#fff":     "var(--sn-paper)",
    "#ffffff":  "var(--sn-paper)",
    "#f8f9fa":  "var(--sn-sunk)",
    "#f9f9f9":  "var(--sn-sunk)",
    "#f4f4f4":  "var(--sn-sunk)",
    "#eaecf0":  "var(--sn-sunk)",
    # Texto
    "#221f1a":  "var(--sn-ink)",
    "#222":     "var(--sn-ink)",
    "#222222":  "var(--sn-ink)",
    "#333":     "var(--sn-ink)",
    "#333333":  "var(--sn-ink)",
    "#000":     "var(--sn-ink)",
    "#000000":  "var(--sn-ink)",
    # Tinta secundaria/terciaria
    "#6b6357":  "var(--sn-ink-soft)",
    "#555":     "var(--sn-ink-soft)",
    "#555555":  "var(--sn-ink-soft)",
    "#666":     "var(--sn-ink-soft)",
    "#666666":  "var(--sn-ink-soft)",
    "#777":     "var(--sn-ink-soft)",
    "#777777":  "var(--sn-ink-soft)",
    "#968c7c":  "var(--sn-ink-faint)",
    "#999":     "var(--sn-ink-faint)",
    "#999999":  "var(--sn-ink-faint)",
    "#aaa":     "var(--sn-ink-faint)",
    "#aaaaaa":  "var(--sn-ink-faint)",
    "#a2a9b1":  "var(--sn-ink-faint)",
    # Filetes
    "#ddd6c7":  "var(--sn-hairline)",
    "#ddd":     "var(--sn-hairline)",
    "#dddddd":  "var(--sn-hairline)",
    "#ccc":     "var(--sn-hairline)",
    "#cccccc":  "var(--sn-hairline)",
    "#bbb":     "var(--sn-hairline)",
    "#bbbbbb":  "var(--sn-hairline)",
    "#c8ccd1":  "var(--sn-hairline)",
    "#c3c3c3":  "var(--sn-hairline)",
    "#e7e1d3":  "var(--sn-hairline-soft)",
    "#e0e0e0":  "var(--sn-hairline-soft)",
    "#eeeeee":  "var(--sn-hairline-soft)",
    "#eee":     "var(--sn-hairline-soft)",
    # Enlaces
    "#ae2d13":  "var(--sn-link)",
    "#a83217":  "var(--sn-link)",
    "#0645ad":  "var(--sn-link)",
    "#36c":     "var(--sn-link)",
    "#3366cc":  "var(--sn-link)",
    "#38f":     "var(--sn-link)",
    "#962c08":  "var(--sn-link-hover)",
    "#612403":  "var(--sn-link-visited)",
    "#681603":  "var(--sn-link-visited)",
    # Marca/señales
    "#b22f1e":  "var(--sn-nova)",
    "#b21e33":  "var(--sn-danger)",
    "#ff6c6c":  "var(--sn-danger)",
    "#2f6f43":  "var(--sn-ok)",
    # Washes (los más comunes detectados)
    "#d5fdf4":  "var(--sn-ok-wash)",
    "#fef6e7":  "var(--sn-warn-wash)",
    "#fee7e6":  "var(--sn-danger-wash)",
    "#fcfada":  "var(--sn-info-wash)",
    "#fffded":  "var(--sn-info-wash)",
    # Badge amarillo (Echo)
    "#ffcc33":  "var(--sn-warn)",
    "#fc3":     "var(--sn-warn)",
}

# Normalizar (expandir 3 → 6 chars) y dedup
def expand_hex(h: str) -> str:
    h = h.lower()
    if len(h) == 4 and h.startswith('#'):
        return '#' + ''.join(c*2 for c in h[1:])
    return h

HEX_MAP_EXPANDED = {expand_hex(k): v for k, v in HEX_MAP.items()}

# ─── PASADA 2: @codex variables ────────────────────────────────────────────
CODEX_MAP = {
    "@color-base":                 "var(--sn-ink)",
    "@color-emphasized":           "var(--sn-ink)",
    "@color-subtle":               "var(--sn-ink-soft)",
    "@color-placeholder":          "var(--sn-ink-faint)",
    "@color-disabled":             "var(--sn-ink-faint)",
    "@color-disabled-emphasized":  "var(--sn-ink-soft)",
    "@color-inverted":             "var(--sn-paper)",
    "@color-inverted-fixed":       "var(--sn-paper)",
    "@color-progressive":          "var(--sn-link)",
    "@color-progressive--hover":   "var(--sn-link-hover)",
    "@color-progressive--active":  "var(--sn-link-hover)",
    "@color-progressive--focus":   "var(--sn-focus-border)",
    "@color-destructive":          "var(--sn-danger)",
    "@color-destructive--hover":   "var(--sn-danger)",
    "@color-error":                "var(--sn-danger)",
    "@color-warning":              "var(--sn-warn)",
    "@color-success":              "var(--sn-ok)",
    "@color-visited":              "var(--sn-link-visited)",
    "@color-visited--hover":       "var(--sn-link-visited)",
    "@background-color-base":              "var(--sn-paper)",
    "@background-color-interactive":       "var(--sn-sunk)",
    "@background-color-interactive-subtle":"var(--sn-sunk)",
    "@background-color-disabled":          "var(--sn-field-bg-disabled)",
    "@background-color-disabled-subtle":   "var(--sn-field-bg-disabled)",
    "@background-color-neutral":           "var(--sn-sunk)",
    "@background-color-neutral-subtle":    "var(--sn-paper)",
    "@background-color-progressive":       "var(--sn-link)",
    "@background-color-progressive-subtle":"var(--sn-nova-wash)",
    "@background-color-destructive":       "var(--sn-danger)",
    "@background-color-destructive-subtle":"var(--sn-danger-wash)",
    "@background-color-success-subtle":    "var(--sn-ok-wash)",
    "@background-color-warning-subtle":    "var(--sn-warn-wash)",
    "@background-color-error-subtle":      "var(--sn-danger-wash)",
    "@background-color-notice-subtle":     "var(--sn-info-wash)",
    "@background-color-button-quiet--hover":"var(--sn-sunk)",
    "@border-color-base":          "var(--sn-field-border)",
    "@border-color-subtle":        "var(--sn-hairline)",
    "@border-color-muted":         "var(--sn-hairline-soft)",
    "@border-color-emphasized":    "var(--sn-hairline)",
    "@border-color-strong":        "var(--sn-ink)",
    "@border-color-interactive":   "var(--sn-field-border)",
    "@border-color-disabled":      "var(--sn-hairline-soft)",
    "@border-color-progressive":   "var(--sn-link)",
    "@border-color-progressive--hover":"var(--sn-link-hover)",
    "@border-color-progressive--focus":"var(--sn-focus-border)",
    "@border-color-destructive":   "var(--sn-danger)",
    "@border-color-success":       "var(--sn-ok)",
    "@border-color-warning":       "var(--sn-warn)",
    "@border-color-error":         "var(--sn-danger)",
    "@border-color-inverted":      "var(--sn-paper)",
    "@border-style-base":          "solid",
    "@border-style-dashed":        "dashed",
    "@border-width-base":          "1px",
    "@border-width-thick":         "2px",
    "@border-base":                "var(--sn-hair)",
    "@border-radius-base":         "var(--sn-radius)",
    "@border-radius-sharp":        "0",
    "@border-radius-pill":         "var(--sn-radius-pill)",
    "@border-radius-circle":       "50%",
    "@font-size-base":             "var(--sn-fs-base)",
    "@font-size-small":            "var(--sn-fs-sm)",
    "@font-size-x-small":          "var(--sn-fs-xs)",
    "@font-size-medium":           "var(--sn-fs-md)",
    "@font-size-large":            "var(--sn-fs-lg)",
    "@font-size-x-large":          "var(--sn-fs-xl)",
    "@font-size-xx-large":         "var(--sn-fs-display)",
    "@font-weight-normal":         "400",
    "@font-weight-bold":           "700",
    "@font-weight-semi-bold":      "600",
    "@font-family-system-sans":    "var(--sn-font-text)",
    "@font-family-sans":           "var(--sn-font-text)",
    "@font-family-monospace":      "var(--sn-font-mono)",
    "@font-family-serif":          "var(--sn-font-display)",
    "@line-height-xxx-small":      "1.1",
    "@line-height-small":          "var(--sn-leading-tight)",
    "@line-height-base":           "var(--sn-leading)",
    "@line-height-medium":         "var(--sn-leading)",
    "@spacing-0":                  "0",
    "@spacing-12":                 "var(--sn-s-1)",
    "@spacing-25":                 "var(--sn-s-1)",
    "@spacing-50":                 "var(--sn-s-2)",
    "@spacing-75":                 "var(--sn-s-3)",
    "@spacing-100":                "var(--sn-s-4)",
    "@spacing-150":                "var(--sn-s-5)",
    "@spacing-300":                "var(--sn-s-6)",
    "@spacing-horizontal-input-text":  "var(--sn-s-3)",
    "@spacing-vertical-input-text":    "var(--sn-s-2)",
    "@spacing-horizontal-button":      "var(--sn-s-3)",
    "@spacing-vertical-button":        "var(--sn-s-2)",
    "@box-shadow-drop-medium":         "var(--sn-lift-soft)",
    "@box-shadow-drop-small":          "var(--sn-lift-soft)",
    "@box-shadow-drop-xx-large":       "var(--sn-lift)",
    "@opacity-icon-base":              ".87",
    "@opacity-icon-base--hover":       "1",
    "@opacity-icon-base--selected":    "1",
    "@opacity-base--disabled":         ".5",
    "@transition-duration-base":       "var(--sn-dur-2)",
    "@transition-duration-medium":     "var(--sn-dur-3)",
    "@transition-timing-function-system": "var(--sn-ease)",
    "@outline-base--focus":            "var(--sn-focus-ring)",
}

# ─── PASADA 3: Medidas ─────────────────────────────────────────────────────
# Criterio de Herbert:
#  - Bordes (border, outline) → quedan en px
#  - Horizontal → escala de espaciado (--sn-s-N) o rem
#  - Vertical → em (escala con texto) o tokens tipográficos

HORIZONTAL_PROPS = {
    "padding-left", "padding-right", "padding-inline",
    "padding-inline-start", "padding-inline-end",
    "margin-left", "margin-right", "margin-inline",
    "margin-inline-start", "margin-inline-end",
    "gap", "column-gap", "grid-column-gap",
    "left", "right",
    "width", "min-width", "max-width",
}
VERTICAL_PROPS = {
    "padding-top", "padding-bottom", "padding-block",
    "padding-block-start", "padding-block-end",
    "margin-top", "margin-bottom", "margin-block",
    "margin-block-start", "margin-block-end",
    "row-gap", "grid-row-gap",
    "top", "bottom",
    "height", "min-height", "max-height",
}
FS_PROPS = {"font-size"}
LH_PROPS = {"line-height"}
RADIUS_PROPS = {
    "border-radius", "border-top-left-radius", "border-top-right-radius",
    "border-bottom-left-radius", "border-bottom-right-radius",
}

# Escalas
SPACE_PX_TO_TOKEN = {  # horizontal
    4:  "var(--sn-s-1)",
    8:  "var(--sn-s-2)",
    12: "var(--sn-s-3)",
    16: "var(--sn-s-4)",
    24: "var(--sn-s-5)",
    36: "var(--sn-s-6)",
    56: "var(--sn-s-7)",
    84: "var(--sn-s-8)",
}
FS_PX_TO_TOKEN = {
    11: "var(--sn-fs-xs)",
    12: "var(--sn-fs-xs)",
    13: "var(--sn-fs-sm)",
    14: "var(--sn-fs-sm)",
    16: "var(--sn-fs-base)",
    18: "var(--sn-fs-md)",
    20: "var(--sn-fs-lg)",
    24: "var(--sn-fs-xl)",
    28: "var(--sn-fs-display)",
    32: "var(--sn-fs-display)",
}
RADIUS_PX_TO_TOKEN = {
    2: "var(--sn-radius-s)",
    3: "var(--sn-radius-paper)",
    4: "var(--sn-radius)",
    8: "var(--sn-radius-l)",
}

def px_to_rem(px: int) -> str:
    if px == 0: return "0"
    return f"{px/16:.4g}rem"

def px_to_em(px: int) -> str:
    if px == 0: return "0"
    # base ~16px → em = px/16 (asume font-size base)
    return f"{px/16:.4g}em"

def tokenize_px_value(prop: str, value: str) -> tuple[str, bool]:
    """Devuelve (nuevo_valor, fue_tokenizado). Reemplaza Npx según contexto."""
    # No tocar 0 ni 1px en propiedades que pueden ser hairline
    def replace(match):
        px = int(match.group(1))
        if px == 0: return "0"
        if px in (1, 2):  # casi siempre hairline / espacios mínimos
            return f"{px}px"
        if prop in FS_PROPS:
            return FS_PX_TO_TOKEN.get(px, px_to_rem(px))
        if prop in RADIUS_PROPS:
            return RADIUS_PX_TO_TOKEN.get(px, px_to_rem(px))
        if prop in LH_PROPS:
            # line-height en px → convertir a unitless si parece ratio
            return px_to_em(px)
        if prop in HORIZONTAL_PROPS:
            return SPACE_PX_TO_TOKEN.get(px, px_to_rem(px))
        if prop in VERTICAL_PROPS:
            # vertical: preferir em (escala con texto)
            return px_to_em(px)
        return f"{px}px"  # no clasificado, no tocar
    new_value, n = re.subn(r"\b(\d+)px\b", replace, value)
    return new_value, n > 0

# ─── Aplicador ─────────────────────────────────────────────────────────────

def apply_to_file(path: Path, dry_run=False) -> dict:
    text = path.read_text(encoding='utf-8')
    original = text
    stats = {"hex": 0, "codex": 0, "px": 0, "todo": 0}

    # Pasada 1: hex (case-insensitive, evita comentarios urls/imágenes)
    def replace_hex(match):
        nonlocal stats
        hex_val = expand_hex(match.group(0).lower())
        if hex_val in HEX_MAP_EXPANDED:
            stats["hex"] += 1
            return HEX_MAP_EXPANDED[hex_val]
        return match.group(0)
    # Saltar urls (imágenes en data URIs) y comentarios
    def hex_safe_substitute(text):
        out = []
        i = 0
        while i < len(text):
            # Saltar comentarios /* ... */
            if text[i:i+2] == '/*':
                end = text.find('*/', i+2)
                if end < 0: end = len(text)
                else: end += 2
                out.append(text[i:end]); i = end; continue
            # Saltar url(...)
            if text[i:i+4] == 'url(':
                end = text.find(')', i+4)
                if end < 0: end = len(text)
                else: end += 1
                out.append(text[i:end]); i = end; continue
            # Buscar hex de aquí en adelante
            m = re.match(r'#[0-9a-fA-F]{3,8}\b', text[i:])
            if m:
                replaced = replace_hex(m)
                out.append(replaced)
                i += len(m.group(0))
            else:
                out.append(text[i])
                i += 1
        return ''.join(out)
    text = hex_safe_substitute(text)

    # Pasada 2: @codex (longest-match-first para no romper @color-progressive--hover)
    # Ordenar por longitud descendente
    for var in sorted(CODEX_MAP.keys(), key=len, reverse=True):
        # Solo reemplazar cuando esté como token completo (no @color-X dentro de @color-XY)
        pattern = re.escape(var) + r"(?![\w-])"
        # No tocar líneas con // o dentro de /* */
        def replace_codex(match):
            nonlocal stats
            stats["codex"] += 1
            return CODEX_MAP[var]
        # Aplicar fuera de comentarios
        def codex_safe(text):
            out = []
            i = 0
            while i < len(text):
                if text[i:i+2] == '/*':
                    end = text.find('*/', i+2)
                    if end < 0: end = len(text)
                    else: end += 2
                    out.append(text[i:end]); i = end; continue
                m = re.match(pattern, text[i:])
                if m:
                    out.append(replace_codex(m))
                    i += len(m.group(0))
                else:
                    out.append(text[i])
                    i += 1
            return ''.join(out)
        text = codex_safe(text)

    # Pasada 3: medidas. Hay que parsear cada declaración prop: value;
    # Detectar línea con `prop: ...;` y aplicar tokenize_px_value
    def tokenize_measures(text):
        nonlocal stats
        lines = text.split('\n')
        out = []
        for line in lines:
            # Saltar comentarios y líneas con // (LESS)
            stripped = line.strip()
            if not stripped or stripped.startswith('/*') or stripped.startswith('//') or stripped.startswith('*'):
                out.append(line); continue
            # Detectar `prop: value;`
            m = re.match(r'^(\s*)([-a-zA-Z]+)(\s*:\s*)([^;]+?)(\s*!important)?(\s*;?\s*)$', line)
            if not m:
                out.append(line); continue
            indent, prop, sep, value, important, end = m.groups()
            prop = prop.lower()
            # Si el valor es shorthand multi-valor de padding/margin, marcar TODO
            if prop in ("padding", "margin"):
                # Si tiene 1 sólo valor px, podemos tokenizar como horizontal Y vertical (em)
                px_count = len(re.findall(r"\b\d+px\b", value))
                if px_count <= 1:
                    # 1 valor: aplica horizontal y vertical igual, decisión: usar rem (espacio)
                    new_val, did = tokenize_px_value("padding-left", value)
                    if did:
                        stats["px"] += px_count
                    out.append(f"{indent}{prop}{sep}{new_val}{important or ''}{end}")
                    continue
                else:
                    # Shorthand multi-valor: marcar TODO para revisar
                    stats["todo"] += 1
                    out.append(f"{indent}{prop}{sep}{value}{important or ''}{end.rstrip()} /* TODO tok: shorthand */")
                    continue
            # Propiedades específicas
            new_value, did = tokenize_px_value(prop, value)
            if did:
                stats["px"] += len(re.findall(r"\b\d+px\b", value)) - len(re.findall(r"\b\d+px\b", new_value))
                out.append(f"{indent}{prop}{sep}{new_value}{important or ''}{end}")
            else:
                out.append(line)
        return '\n'.join(out)
    text = tokenize_measures(text)

    if not dry_run and text != original:
        # Backup
        backup = path.with_suffix(path.suffix + f".pre-tok-{TS}")
        shutil.copy(path, backup)
        path.write_text(text, encoding='utf-8')

    return stats

# ─── Main ───────────────────────────────────────────────────────────────────

# Argumento opcional: nombre de archivo único a procesar (oojs-ui.css, etc.).
# Sin argumento: procesa todos los snapshots (idempotente, no toca los que
# no cambian).
target = sys.argv[1] if len(sys.argv) > 1 else None
scope = f"solo {target}" if target else "todos los snapshots"
print(f"=== Aplicando tokenización a {scope} (TS={TS}) ===\n")

totals = {"hex": 0, "codex": 0, "px": 0, "todo": 0}
for path in sorted(SKIN_STYLES.iterdir()):
    if path.name in HAND_WRITTEN: continue
    if path.suffix not in ('.css', '.less'): continue
    if '.pre-tok-' in path.name: continue
    if '.bak' in path.name: continue
    if target and path.name != target: continue
    s = apply_to_file(path)
    print(f"  {path.name:<28} hex={s['hex']:<3} codex={s['codex']:<3} px={s['px']:<3} todo={s['todo']}")
    for k, v in s.items():
        totals[k] += v

print(f"\n=== Totales: hex={totals['hex']}  codex={totals['codex']}  px={totals['px']}  todo={totals['todo']} ===")
print(f"=== Backups creados con sufijo .pre-tok-{TS} ===")

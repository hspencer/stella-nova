#!/usr/bin/env python3
# Stella Nova — captura el snapshot de OOUI (tema wikimediaui) desde el
# wiki local y lo escribe como resources/skinStyles/oojs-ui.css con header
# de atribución. El archivo resultante luego se tokeniza con
# scripts/apply-tokenization.py (las 3 pasadas: hex, codex-vars, medidas).
#
# Captura los 3 módulos que el skin.json ata vía ResourceModuleSkinStyles
# con prefijo `+`:
#   +oojs-ui-core.styles    → oojs-ui-core-wikimediaui.css
#   +oojs-ui-widgets.styles → oojs-ui-widgets-wikimediaui.css
#   +oojs-ui-windows.styles → oojs-ui-windows-wikimediaui.css
#
# Reproducible: cuando OOUI suba versión, basta con re-correr este script
# y luego apply-tokenization.py.

from datetime import date
from pathlib import Path
import re

SKIN_ROOT  = Path(__file__).resolve().parent.parent
OOUI_DIR   = Path("/home/hspencer/Sites/casiopea/w/resources/lib/ooui")
OUTPUT     = SKIN_ROOT / "resources" / "skinStyles" / "oojs-ui.css"

MODULES = [
    ("oojs-ui-core-wikimediaui.css",    "oojs-ui-core.styles"),
    ("oojs-ui-widgets-wikimediaui.css", "oojs-ui-widgets.styles"),
    ("oojs-ui-windows-wikimediaui.css", "oojs-ui-windows.styles"),
]

HEADER_TPL = """/* ============================================================
 * skinStyles/oojs-ui.css — Stella Nova
 *
 * Snapshot inicial de OOUI (tema wikimediaui), versión {version},
 * licencia upstream: MIT. Capturado el {today} desde
 * w/resources/lib/ooui/ para absorber los estilos dentro del sistema
 * visual de Stella Nova.
 *
 * OOUI es la librería de widgets de MediaWiki (botones, campos,
 * casillas, desplegables, diálogos). La usan el editor, Preferencias,
 * páginas especiales, PageForms y la UI de SMW.
 *
 * Estos bloques se procesan con scripts/apply-tokenization.py para
 * sustituir hex/@codex-vars/medidas por tokens del skin
 * (var(--sn-...)). Mientras tanto, sirven como referencia exacta de
 * lo que OOUI inyecta hoy.
 *
 * Cargado vía ResourceModuleSkinStyles en skin.json con prefijo `+`
 * contra los tres módulos:
 *   +oojs-ui-core.styles
 *   +oojs-ui-widgets.styles
 *   +oojs-ui-windows.styles
 * El CSS del skin se carga DESPUÉS del CSS de OOUI; la cascada hace
 * que estas reglas ganen sin tocar la librería.
 * ============================================================ */
"""


def extract_version(text: str) -> str:
    m = re.search(r"OOUI v([\d.]+)", text)
    return m.group(1) if m else "desconocida"


def main():
    if not OOUI_DIR.exists():
        raise SystemExit(f"OOUI fuente no encontrada en {OOUI_DIR}")
    pieces = []
    version = None
    for fname, module_id in MODULES:
        path = OOUI_DIR / fname
        if not path.exists():
            raise SystemExit(f"Falta {path}")
        src = path.read_text()
        if version is None:
            version = extract_version(src)
        pieces.append(f"\n/* ─── Módulo: {module_id} ─── */\n"
                      f"/* archivo origen: w/resources/lib/ooui/{fname} */\n")
        pieces.append(src)

    header = HEADER_TPL.format(version=version, today=date.today().isoformat())
    OUTPUT.write_text(header + "".join(pieces))
    total = sum(1 for _ in OUTPUT.read_text().splitlines())
    print(f"✓ snapshot escrito en {OUTPUT.relative_to(SKIN_ROOT)} "
          f"(OOUI v{version}, {total} líneas)")
    print(f"  siguiente paso: python3 scripts/apply-tokenization.py")


if __name__ == "__main__":
    main()

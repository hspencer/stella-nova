# Stella Nova — espécimen gráfico v0.2.9

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
   :root {
     --sn-nova: #c33;
     --sn-fs-display: 2.4rem;
   }
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

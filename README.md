# Stella Nova

Skin moderno para **Casiopea** (wiki e[ad] PUCV): `SkinMustache` + `skin.json`,
sin Bootstrap, escrito desde cero. Mobile-first, CSS moderno (Grid/Flexbox,
custom properties, claro/oscuro), foco en accesibilidad WCAG 2.1 AA y
compatibilidad con Semantic MediaWiki.

## El nombre

El 11 de noviembre de 1572, el astrónomo danés **Tycho Brahe** observó una
estrella nueva y brillante en la constelación de **Casiopea**. La llamó
*stella nova* —«estrella nueva» en latín— y documentó sus mediciones en
*De nova stella* (1573), el tratado que dio al mundo la palabra «nova».

Aquello no era una estrella naciendo sino muriendo: hoy se conoce como
**SN 1572**, «la supernova de Tycho», una supernova de tipo Ia en el brazo
de Perseo, a unos 8.000–13.000 años luz. Llegó a brillar como Venus
(magnitud ≈ −4), fue visible a plena luz del día durante semanas y se apagó
en marzo de 1574. Su mayor consecuencia no fue astronómica sino filosófica:
demostró que los cielos —que la tradición aristotélica creía inmutables y
perfectos— **cambian**. Fue una de las grietas por donde entró la
revolución científica.

El linaje del nombre es directo: la wiki es **Casiopea**; este skin es la
*stella nova* que aparece en ella —una forma nueva sobre un cielo conocido—.
Como aquella estrella, renueva lo que se daba por fijo sin alterar la
constelación que lo contiene: el contenido y las extensiones de Casiopea
permanecen intactos; sólo cambia la luz con que se ven.

## Instalación

```php
wfLoadSkin( 'StellaNova' );
// opcional durante desarrollo:
// $wgDefaultSkin = 'stellanova';
```

Probar sin cambiar el default: añadir `?useskin=stellanova` a cualquier URL.

## Especificación y documentación

- [`specs/stella-nova.allium`](specs/stella-nova.allium) — **especificación de
  comportamiento** (Allium): resolución de las 7 preferencias de skin,
  chrome administrable desde el namespace `Stella-Nova`, modo pantalla
  completa para páginas experimentales, identidad tri-estado (anónimo /
  cuenta temporal 1.43 / registrado) y el contrato de fidelidad
  estructural con MediaWiki y sus extensiones.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — principios y doctrina
  (SkinMustache, skinStyles para SMW/SRF, mobile-first, WCAG 2.1 AA).
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — plan de desarrollo: estado,
  roadmap M0–M8, workflow local, checklist de verificación, decisiones.

## Licencia

GPL-2.0-or-later. Ver `COPYING`.

---

<sub>Fuentes del apartado «El nombre»:
[SN 1572 — Wikipedia](https://en.wikipedia.org/wiki/SN_1572) ·
[APS: November 11, 1572 — Tycho Brahe Spots a Supernova](https://www.aps.org/apsnews/2019/11/tycho-brahe-spots-supernova).</sub>

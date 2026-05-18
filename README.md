# Stella Nova

Skin moderno para **Casiopea** (wiki e[ad] PUCV): `SkinMustache` + `skin.json`,
sin Bootstrap, escrito desde cero. Mobile-first, CSS moderno (Grid/Flexbox,
custom properties, light/dark), foco en accesibilidad WCAG 2.1 AA y
compatibilidad con Semantic MediaWiki.

## Instalación

```php
wfLoadSkin( 'StellaNova' );
// opcional durante desarrollo:
// $wgDefaultSkin = 'stellanova';
```

Probar sin cambiar el default: añadir `?useskin=stellanova` a cualquier URL.

## Principios de diseño

Ver la doctrina de arquitectura del proyecto (mobile-first, `skinStyles` por
extensión para SMW/SRF, accesibilidad). Citizen se usa como **lectura de
referencia**, no como base.

## Licencia

GPL-2.0-or-later. Ver `COPYING`.

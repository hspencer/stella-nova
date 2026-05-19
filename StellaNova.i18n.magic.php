<?php
/**
 * Stella Nova — palabra mágica de comportamiento (behaviour switch).
 *
 * __PANTALLACOMPLETA__ declara LayoutMode.fullscreen (spec entity PageRender):
 * el skin suprime todo el chrome salvo la afordancia de escape. Mismo patrón
 * que __NOTITLE__/NoTitle (doctrina ARCHITECTURE §6). El `1` = sensible a
 * mayúsculas, como los demás dobles-guión-bajo de MediaWiki.
 *
 * @file
 * @license GPL-2.0-or-later
 */

$magicWords = [];

$magicWords['en'] = [
	'stellanova_fullscreen' => [ 1, '__FULLSCREEN__', '__PANTALLACOMPLETA__' ],
];

$magicWords['es'] = [
	'stellanova_fullscreen' => [ 1, '__PANTALLACOMPLETA__', '__FULLSCREEN__' ],
];

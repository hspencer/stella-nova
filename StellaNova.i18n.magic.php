<?php
/**
 * Stella Nova — palabra mágica de comportamiento (behaviour switch).
 *
 * __PANTALLACOMPLETA__ declara LayoutMode.fullscreen (spec entity PageRender):
 * el skin suprime todo el chrome salvo la afordancia de escape. NO implica
 * ocultar el título: para eso se usa __NOTITLE__ además, de forma explícita
 * (más limpio que acoplarlos). El `1` = sensible a mayúsculas, como los
 * demás dobles-guión-bajo de MediaWiki.
 *
 * @file
 * @license Artistic-2.0
 */

$magicWords = [];

$magicWords['en'] = [
	'stellanova_fullscreen' => [ 1, '__FULLSCREEN__', '__PANTALLACOMPLETA__' ],
];

$magicWords['es'] = [
	'stellanova_fullscreen' => [ 1, '__PANTALLACOMPLETA__', '__FULLSCREEN__' ],
];

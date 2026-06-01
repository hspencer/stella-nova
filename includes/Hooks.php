<?php
/**
 * Stella Nova — hooks. PHP al mínimo (doctrina §2): solo el cableado que
 * el comportamiento del spec exige y que no puede vivir en CSS/JS.
 *
 *  · __PANTALLACOMPLETA__  → behaviour switch (spec PageRender.mode).
 *  · Persistencia híbrida  → las 5 preferencias del skin como opciones
 *    de cuenta (api): para `registered` siguen al usuario entre
 *    dispositivos (spec PreferencesPanel.CrossDeviceForRegistered).
 *    Anónimo/temporal persisten por-navegador (skin.js → localStorage).
 *  · Pre-pintado sin FOUC  → resuelve el tema antes del primer paint
 *    (eludir el "parpadeo" de color al recargar).
 *
 * @license GPL-2.0-or-later
 */

namespace MediaWiki\Skins\StellaNova;

use MediaWiki\MediaWikiServices;
use OutputPage;
use ParserOutput;
use Skin;
use Title;
use User;

class Hooks {

	/** Opción de cuenta → valor por defecto ('' = sin elección explícita).
	 *  Sólo dos preferencias: tema y tamaño de letra. Índice, secciones
	 *  colapsables y reducción de movimiento se retiraron como preferencia. */
	private const PREFS = [
		'stellanova-theme' => '',
		'stellanova-font'  => '',
	];

	/**
	 * Registra el id del doble-guión-bajo. Que el id esté registrado hace
	 * que MediaWiki fije la page-property homónima al parsear el wikitexto.
	 *
	 * @param string[] &$ids
	 */
	public static function onGetDoubleUnderscoreIDs( array &$ids ): void {
		$ids[] = 'stellanova_fullscreen';
	}


	/**
	 * Puente parser→skin: si la página declaró el modo, lo dejamos en la
	 * OutputPage para que SkinStellaNova lo lea sin volver a consultar props.
	 *
	 * @param OutputPage $out
	 * @param ParserOutput $pOut
	 */
	public static function onOutputPageParserOutput( OutputPage $out, ParserOutput $pOut ): void {
		$prop = method_exists( $pOut, 'getPageProperty' )
			? $pOut->getPageProperty( 'stellanova_fullscreen' )
			: $pOut->getProperty( 'stellanova_fullscreen' );
		if ( $prop !== null && $prop !== false ) {
			$out->setProperty( 'stellanova-fullscreen', true );
		}
	}

	/**
	 * Las 5 preferencias como opciones `api`: persisten en la cuenta
	 * (cross-device para registrados) sin recargar Especial:Preferencias;
	 * el panel del skin es su UI. El tipo `api` significa "opción válida
	 * para guardar vía API, pero no expuesta en Especial:Preferencias" —
	 * el formulario lo provee el panel del skin, no MW.
	 *
	 * Cuentas temporales (MW 1.43) no llegan aquí con identidad nombrada
	 * → su persistencia es por-navegador (skin.js + localStorage).
	 *
	 * @param User $user
	 * @param array &$prefs
	 */
	public static function onGetPreferences( User $user, array &$prefs ): void {
		foreach ( array_keys( self::PREFS ) as $key ) {
			$prefs[$key] = [ 'type' => 'api' ];
		}
	}

	/**
	 * Defaults de las opciones de cuenta.
	 *
	 * @param array &$defaultOptions
	 */
	public static function onUserGetDefaultOptions( array &$defaultOptions ): void {
		$defaultOptions += self::PREFS;
	}

	/**
	 * Pre-pintado: resuelve tema/preferencias antes del primer paint para
	 * eludir el FOUC ("flash of unstyled content" — parpadeo claro→oscuro
	 * cuando el usuario tiene preferencia oscura pero el navegador pinta
	 * con el default antes de que llegue el CSS/JS). El truco: emitir un
	 * <script> inline en <head> que lee la pref y fija data-sn-theme en
	 * <html> ANTES de que el navegador haga el primer paint del body.
	 *
	 * También expone a skin.js dónde persistir (cuenta vs. navegador):
	 *   · `identity` = anonymous | temporary | registered (tri-estado MW 1.43)
	 *   · `persist`  = account (registrados, BBDD) | browser (resto, localStorage)
	 *   · `server`   = seed de las opciones de cuenta para registrados;
	 *                  vacío para anónimo/temporal (el cliente lee local).
	 *
	 * @param OutputPage $out
	 * @param Skin $skin
	 */
	public static function onBeforePageDisplay( OutputPage $out, Skin $skin ): void {
		if ( $skin->getSkinName() !== 'stellanova' ) {
			return;
		}

		// — SiteIsotype (favicon): autocontenido, viaja con el skin —
		// MediaWiki sólo emite <link rel="icon"> si $wgFavicon difiere del
		// default '/favicon.ico' (OutputPage::getHeadLinksArray). Como la
		// instalación NO fija $wgFavicon, no hay etiqueta del core que
		// colisione: inyectamos la nuestra apuntando al asset del skin.
		// SVG con @media prefers-color-scheme dentro → adapta a la pestaña
		// clara/oscura del navegador sin variantes por tema. Esto deja el
		// favicon definido desde el skin, sin tocar LocalSettings (decisión
		// deliberada: el skin es autocontenido y desplegable sin editar
		// config del servidor).
		$stylePath = $skin->getConfig()->get( 'StylePath' );
		$favicon = $stylePath . '/StellaNova/resources/favicon.svg';
		$out->addHeadItem(
			'stellanova-favicon',
			'<link rel="icon" type="image/svg+xml" href="' . htmlspecialchars( $favicon ) . '">'
		);

		$user = $out->getUser();
		$isNamed = method_exists( $user, 'isNamed' ) ? $user->isNamed() : $user->isRegistered();
		$isTemp = method_exists( $user, 'isTemp' ) && $user->isTemp();
		$identity = $isNamed ? 'registered' : ( $isTemp ? 'temporary' : 'anonymous' );

		$server = [];
		if ( $isNamed ) {
			$lookup = \MediaWiki\MediaWikiServices::getInstance()->getUserOptionsLookup();
			foreach ( array_keys( self::PREFS ) as $key ) {
				$short = substr( $key, strlen( 'stellanova-' ) );
				$server[$short] = (string)$lookup->getOption( $user, $key );
			}
		}

		// Versión del aviso gestionado (Stella-Nova:Aviso): id de su última
		// revisión. El banner descartado se recuerda por versión; al editar
		// el aviso, reaparece. El pre-pintado lo usa para ocultar sin FOUC.
		$noticeId = self::noticeVersion();

		$out->addJsConfigVars( 'wgStellaNova', [
			'identity'   => $identity,
			'persist'    => $isNamed ? 'account' : 'browser',
			'apiPrefix'  => 'stellanova-',
			'server'     => $server,
			'noticeId'   => $noticeId,
		] );

		// Script de pre-pintado: lo antes posible en <head>, para resolver
		// el tema/preferencias ANTES del primer paint (sin FOUC ni reversión
		// al recargar). El config se incrusta como literal-objeto JS válido
		// (json_encode); se neutraliza "</script>" escapando "<". Defensivo:
		// nunca debe romper la página. Default = claro (sin atributo); el SO
		// solo oscurece si el usuario eligió "auto".
		$cfgJson = str_replace(
			'<', '\\u003C',
			json_encode(
				[ 'identity' => $identity, 'server' => (object)$server, 'noticeId' => $noticeId ],
				JSON_UNESCAPED_UNICODE
			)
		);
		$script = '<script>(function(){try{' .
			'var C=' . $cfgJson . ';' .
			'var d=document.documentElement,K=["theme","font"];' .
			'function g(k){if(C.identity==="registered"){return (C.server&&C.server[k])||"";}' .
			'try{return localStorage.getItem("sn-pref-"+k)||"";}catch(e){return "";}}' .
			'K.forEach(function(k){var v=g(k);if(!v)return;' .
			'if(k==="theme"){if(v==="light"||v==="dark"||v==="auto")d.setAttribute("data-sn-theme",v);}' .
			'else{d.setAttribute("data-sn-"+k,v);}});' .
			// Aviso ya leído (misma versión) → ocultar antes del primer paint.
			'if(C.noticeId){try{if(localStorage.getItem("sn-notice-dismissed")===C.noticeId)' .
			'd.setAttribute("data-sn-notice-hide","");}catch(e){}}' .
			'}catch(e){}})();</script>';
		$out->addHeadItem( 'stellanova-prepaint', $script );
	}

	/**
	 * Id de la última revisión de Stella-Nova:Aviso (o '' si no existe).
	 * Barato: getLatestRevID no parsea. Réplica mínima de la resolución de
	 * namespace de SkinStellaNova::resolveFragment (namespace dedicado si
	 * está declarado; si no, página homónima en el espacio principal).
	 *
	 * @return string
	 */
	private static function noticeVersion(): string {
		try {
			$nsId = MediaWikiServices::getInstance()->getContentLanguage()
				->getNsIndex( 'Stella-Nova' );
			$title = ( $nsId !== false && $nsId !== null )
				? Title::makeTitleSafe( $nsId, 'Aviso' )
				: Title::newFromText( 'Stella-Nova:Aviso' );
			if ( $title && $title->exists() ) {
				return (string)$title->getLatestRevID();
			}
		} catch ( \Throwable $e ) {
		}
		return '';
	}
}

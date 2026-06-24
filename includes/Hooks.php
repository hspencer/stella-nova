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

use ExtensionRegistry;
use MediaWiki\MediaWikiServices;
use MediaWiki\ResourceLoader\ResourceLoader;
use MediaWiki\ResourceLoader\SkinModule;
use OutputPage;
use ParserOutput;
use Skin;
use Title;
use User;

class Hooks {

	/** Opción de cuenta → valor por defecto ('' = sin elección explícita).
	 *  Tres preferencias: tema, tamaño de letra y familia tipográfica
	 *  (sans|serif — alternancia editorial). Índice, secciones colapsables
	 *  y reducción de movimiento se retiraron como preferencia. */
	private const PREFS = [
		'stellanova-theme'  => '',
		'stellanova-font'   => '',
		'stellanova-family' => '',
	];

	/**
	 * Registra los módulos ResourceLoader del skin con la ruta remota
	 * calculada del DIRECTORIO REAL donde está instalado el skin, no de un
	 * nombre fijo. Así "basta clonar" en cualquier carpeta (StellaNova,
	 * stella-nova, lo que sea) y las URLs de las fuentes (y demás assets del
	 * módulo) resuelven solas: $wgStylePath + '/' + <carpeta-real>/resources.
	 *
	 * Por qué aquí y no en skin.json: `remoteSkinPath` en skin.json es un
	 * literal estático ("StellaNova/resources"); si la carpeta no se llama
	 * así, los woff2 dan 404 (MediaWiki no deriva la ruta sola — confirmado
	 * en ResourceLoader\FileModule::extractBasePaths). Calcularla en PHP es
	 * la única forma robusta al nombre de carpeta.
	 *
	 * OJO: NO usar __DIR__ — resuelve symlinks, así que en una instalación
	 * con la carpeta enlazada (p.ej. skins/StellaNova → repo stella-nova)
	 * devolvería el nombre real del repo y las URLs 404. La ruta REGISTRADA
	 * por wfLoadSkin (ExtensionRegistry) preserva el nombre tal como el wiki
	 * sirve la carpeta — sirve tanto para el symlink de dev como para el
	 * clon directo en producción.
	 *
	 * @param ResourceLoader $rl
	 */
	public static function onResourceLoaderRegisterModules( ResourceLoader $rl ): void {
		$jsonPath = ExtensionRegistry::getInstance()->getAllThings()['StellaNova']['path'] ?? null;
		// Fallback: si no se halla por nombre, __DIR__ (correcto en clon directo).
		$skinDir = $jsonPath !== null ? dirname( $jsonPath ) : dirname( __DIR__ );
		$paths = [
			'localBasePath'  => $skinDir . '/resources',
			'remoteSkinPath' => basename( $skinDir ) . '/resources',
		];
		$rl->register( 'skins.stellanova.styles', $paths + [
			'class'    => SkinModule::class,
			'features' => [
				'normalize'      => true,
				'elements'       => true,
				'content-links'  => true,
				'content-tables' => true,
				// content-media trae los floats del markup estándar de imagen
				// (.mw-halign-*, .tright/.tleft, thumb): sin esta feature
				// left|right|center|none en [[Archivo:...]] no tienen efecto.
				'content-media'  => true,
				'toc'            => true,
			],
			'styles' => [
				'fonts.css'       => [],
				'tokens.css'      => [],
				'stella-nova.css' => [],
				'print.css'       => [ 'media' => 'print' ],
			],
		] );
		$rl->register( 'skins.stellanova.scripts', $paths + [
			'scripts'      => [ 'skin.js' ],
			'dependencies' => [ 'mediawiki.api' ],
		] );
		// Previsualización de impresión paginada (paged.js). Módulo BAJO DEMANDA:
		// no entra en la ruta crítica; skin.js lo pide (mw.loader.using) solo al
		// pulsar «Versión para imprimir». Trae el polyfill vendorizado + la
		// integración + el cromo en pantalla del overlay. paged.js necesita
		// `mediawiki.util` (mw.util.getUrl para la URL absoluta de la página).
		$rl->register( 'skins.stellanova.print', $paths + [
			'scripts'      => [ 'lib/vivliostyle.global.js', 'print-preview.js' ],
			'styles'       => [ 'print-preview.css' ],
			'dependencies' => [ 'mediawiki.util' ],
		] );
	}

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
		// __NOTITLE__ (extensión NoTitle) es INDEPENDIENTE de pantalla
		// completa: se lee aquí para que la plantilla pueda omitir el título
		// también en el canvas. (NoTitle solo oculta vía CSS dentro de
		// `.mw-body`, ausente en fullscreen → lo resolvemos en el skin.)
		$notitle = method_exists( $pOut, 'getPageProperty' )
			? $pOut->getPageProperty( 'notitle' )
			: $pOut->getProperty( 'notitle' );
		if ( $notitle !== null && $notitle !== false ) {
			$out->setProperty( 'stellanova-notitle', true );
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

		// — Busting de caché de la CSS crítica del skin —
		// El <link> combinado de estilos que emite MediaWiki NO lleva `version`
		// en su URL; una caché HTTP por-URL (CDN/nginx) delante de load.php sirve
		// entonces CSS VIEJO tras cada deploy (las fuentes "se rompen" hasta que
		// expira el TTL, sin que el hard-refresh ayude porque la caché es
		// compartida). Solución sin acceso al servidor: cargamos la CSS del skin
		// nosotros, con un `version` derivado del mtime de los .css → cada deploy
		// cambia la URL → MISS → CSS fresca. `skins.stellanova.styles` se quitó de
		// skin.json `styles` para que MediaWiki no la incluya además (sin doble
		// carga). El módulo se sigue registrando en onResourceLoaderRegisterModules.
		$lang = $skin->getLanguage()->getCode();
		// `version` = el hash de contenido REAL que ResourceLoader computa para
		// el módulo. Usándolo, RL lo reconoce como versión válida y le da caché
		// larga e inmutable; y como el hash cambia con cualquier cambio de
		// contenido, cada deploy produce una URL nueva → MISS → CSS fresca. Si
		// algo falla, caemos al mtime de los .css (caché de 60s pero igual busta
		// por deploy, porque el HTML siempre lleva el tag vigente).
		$version = null;
		try {
			$rl = $out->getResourceLoader();
			$rlCtx = new \MediaWiki\ResourceLoader\Context(
				$rl,
				new \MediaWiki\Request\FauxRequest( [
					'lang'    => $lang,
					'modules' => 'skins.stellanova.styles',
					'only'    => 'styles',
					'skin'    => 'stellanova',
				] )
			);
			// makeVersionQuery produce EXACTAMENTE el string que RL valida en
			// respond() (getVersionHash de un solo módulo no coincide con la
			// versión combinada). Coincidir → RL concede caché larga inmutable.
			if ( $rl->getModule( 'skins.stellanova.styles' ) ) {
				$version = $rl->makeVersionQuery( $rlCtx, [ 'skins.stellanova.styles' ] );
			}
		} catch ( \Throwable $e ) {
			$version = null;
		}
		if ( $version === null || $version === '' ) {
			$resDir = self::skinResourcesDir();
			$mtime = 0;
			if ( $resDir !== null ) {
				foreach ( [ 'fonts.css', 'tokens.css', 'stella-nova.css', 'print.css' ] as $f ) {
					$p = $resDir . '/' . $f;
					if ( is_file( $p ) ) {
						$mtime = max( $mtime, (int)filemtime( $p ) );
					}
				}
			}
			$version = $mtime > 0 ? dechex( $mtime ) : 'dev';
		}
		$href = wfAppendQuery(
			$skin->getConfig()->get( 'LoadScript' ),
			[
				'lang'    => $lang,
				'modules' => 'skins.stellanova.styles',
				'only'    => 'styles',
				'skin'    => 'stellanova',
				'version' => $version,
			]
		);
		$out->addHeadItem(
			'zzz-stellanova-styles',
			'<link rel="stylesheet" href="' . htmlspecialchars( $href ) . '">'
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
			'var d=document.documentElement,K=["theme","font","family"];' .
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
	 * Directorio físico `resources/` del skin tal como está instalado (vía la
	 * ruta registrada por ExtensionRegistry, que preserva symlinks/clon — NO
	 * __DIR__). Devuelve null si no se puede resolver. Lo usan el busting de
	 * caché de la CSS (mtime de los archivos) y el registro de módulos.
	 *
	 * @return string|null
	 */
	private static function skinResourcesDir(): ?string {
		$jsonPath = ExtensionRegistry::getInstance()->getAllThings()['StellaNova']['path'] ?? null;
		$skinDir = $jsonPath !== null ? dirname( $jsonPath ) : dirname( __DIR__ );
		$res = $skinDir . '/resources';
		return is_dir( $res ) ? $res : null;
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

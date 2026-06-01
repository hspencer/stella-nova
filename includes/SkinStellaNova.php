<?php
/**
 * Stella Nova — skin moderno para Casiopea (e[ad] PUCV).
 *
 * Escrito desde cero: solo extiende SkinMustache (contrato mínimo de MW).
 * Esta clase aporta SOLO el modelo de datos que el spec exige y que el
 * template no puede derivar por sí mismo (spec: PageRender, SiteIsotype,
 * UserTools, ManagedChrome, PreferencesPanel). El contrato
 * SkinRenderFidelity lo cumple el template emitiendo todas las data keys.
 *
 * @license GPL-2.0-or-later
 */

namespace MediaWiki\Skins\StellaNova;

use MediaWiki\Html\Html;
use MediaWiki\Language\Language;
use MediaWiki\MediaWikiServices;
use MediaWiki\Revision\RevisionRecord;
use SkinMustache;
use Title;

class SkinStellaNova extends SkinMustache {

	/** Páginas wiki que gobiernan el chrome (spec InterfaceFragment). */
	private const CHROME = [
		'notice'  => 'Aviso',
		'sidebar' => 'Barra lateral',
		'footer'  => 'Pie',
	];

	/** Cache por-request del SVG del isotipo (recurso editable). */
	private static ?string $isotypeSvgCache = null;
	/** Cache por-request del isotipo compacto (viewport estrecho). */
	private static ?string $iconSvgCache = null;

	/**
	 * Isotipo: logotipo "Casiopea" + constelación. Asset EDITABLE
	 * versionado en `resources/casiopea.svg` (doctrina ARCHITECTURE §2:
	 * isotipo autocontenido en el repo del skin). Monocromo y colorizable
	 * (`currentColor`) → tematizable claro/oscuro sin variantes por tema
	 * (spec SiteIsotype.ThemeAdaptive). Se lee UNA vez por request y se
	 * embebe inline (para que `currentColor` aplique; un <img> no se
	 * podría tematizar). El wordmark ES el texto: no hay span "Casiopea"
	 * aparte. Degradación: si el archivo falta o no es legible → cadena
	 * vacía (el enlace a portada permanece, con su aria-label).
	 *
	 * @return string
	 */
	private static function isotypeSvg(): string {
		if ( self::$isotypeSvgCache === null ) {
			self::$isotypeSvgCache = self::readSvg( __DIR__ . '/../resources/casiopea.svg' );
		}
		return self::$isotypeSvgCache;
	}

	/**
	 * Isotipo compacto (viewport estrecho): glifo cuadrado de la
	 * constelación, sin wordmark. Adapta a tema vía `currentColor` para
	 * el fondo y `var(--sn-paper)` para las líneas/estrellas — el SVG
	 * trae sus propias clases (.sn-i-bg/.sn-i-line/.sn-i-star) y se
	 * inyecta inline para que herede las variables CSS del padre. CSS
	 * decide cuál de los dos (wordmark vs. icono) se muestra según el
	 * viewport (spec ChromeAccessibility — la realización compacta la
	 * presentación, ambas alcanzables).
	 *
	 * @return string
	 */
	private static function iconSvg(): string {
		if ( self::$iconSvgCache === null ) {
			self::$iconSvgCache = self::readSvg( __DIR__ . '/../resources/casiopea-icon.svg' );
		}
		return self::$iconSvgCache;
	}

	/**
	 * Toolbox del pie (p-tb) → ícono Feather por item. La clave es el id
	 * estándar del enlace que emite el core; el valor, el símbolo del sprite
	 * (SnIcons.mustache). Los items sin entrada quedan sin ícono (p.ej.
	 * t-smwbrowselink): la lista degrada a texto, no rompe.
	 */
	private const TOOL_ICONS = [
		't-whatlinkshere'       => 'arrow-right',
		't-recentchangeslinked' => 'git-merge',
		't-upload'              => 'upload',
		't-specialpages'        => 'tool',
		't-print'               => 'printer',
		't-permalink'           => 'link',
		't-info'                => 'info',
	];

	/**
	 * Inyecta el ícono Feather al inicio de cada <a> de la toolbox del pie.
	 * El core entrega `html-items` como cadena de <li id="t-…"><a …>…</a></li>;
	 * para cada <li> con id mapeado, insertamos el <svg><use> justo tras la
	 * apertura del <a>. Presentación, sí, pero el ícono depende del id que
	 * sólo el core conoce a esta altura — por eso aquí y no en Mustache/CSS
	 * (un ::before con mask duplicaría la geometría que ya vive en el sprite).
	 *
	 * @param string $html
	 * @return string
	 */
	private static function iconizeToollist( string $html ): string {
		if ( $html === '' ) {
			return $html;
		}
		// Captura: <li … id="t-…" …> … <a …>  → grupo 1 = id, grupo 0 = todo
		// hasta la apertura del primer <a>. Insertamos el ícono tras el match.
		return (string)preg_replace_callback(
			'/<li\b[^>]*\bid="(t-[^"]+)"[^>]*>\s*<a\b[^>]*>/i',
			static function ( array $m ): string {
				$icon = self::TOOL_ICONS[$m[1]] ?? null;
				if ( $icon === null ) {
					return $m[0];
				}
				$svg = '<svg class="sn-i sn-foot-ico" aria-hidden="true" focusable="false"'
					. ' width="15" height="15" viewBox="0 0 24 24"><use href="#sn-i-'
					. $icon . '"/></svg>';
				return $m[0] . $svg;
			},
			$html
		);
	}

	/**
	 * Lee un asset SVG, quita comentarios HTML y la declaración XML
	 * (innecesaria al inyectar inline en el documento), defensivo.
	 *
	 * @param string $path
	 * @return string
	 */
	private static function readSvg( string $path ): string {
		$raw = is_readable( $path ) ? (string)file_get_contents( $path ) : '';
		// Quitar declaración XML (sólo para top-level docs) y comentarios.
		$raw = (string)preg_replace( '/<\?xml[^?]*\?>/s', '', $raw );
		$raw = (string)preg_replace( '/<!--.*?-->/s', '', $raw );
		return trim( $raw );
	}

	/**
	 * Datos para skin.mustache. Extiende lo que ya emite SkinMustache (las
	 * "data keys" estándar — html-headelement, data-portlets, data-footer…)
	 * con las keys propias del skin, ramificadas por entidad del spec:
	 *
	 *   is-sn-fullscreen        bool         — PageRender.mode = fullscreen?
	 *   sn-identity             string       — UserIdentity: anonymous | temporary | registered
	 *   sn-isotype              {…}          — SiteIsotype: SVG embebido + override de $wgLogos
	 *   sn-sitenav, sn-has-sitenav, sn-toolbox
	 *                                       — Partición del MediaWiki:Sidebar
	 *                                         (toolbox al pie, resto al header)
	 *   sn-edit, sn-editcode    {href,label} — Lápiz de la barra (deriva PageForms)
	 *   sn-pageviews, sn-has-pageviews
	 *                                       — Vistas del menú "Página", sin el editar (lo lleva el lápiz)
	 *   sn-prefs                {…}          — PreferencesPanel: estado inicial server-side
	 *   sn-chrome               {…}          — ManagedChrome: fragmentos Pie/Sidebar/Aviso
	 *
	 * El template consume estas keys con secciones Mustache. La filosofía:
	 * decidir aquí lo que requiere PHP (state, lookups, condicionales sobre
	 * extensiones disponibles) y dejarle al template solo presentación.
	 *
	 * @return array
	 */
	public function getTemplateData(): array {
		$data = parent::getTemplateData();
		$out = $this->getOutput();
		$user = $this->getUser();

		// — PageRender.mode: standard | fullscreen (__PANTALLACOMPLETA__).
		// En fullscreen no se emite afordancia "salir": la única salida son
		// los enlaces de Portada/Navegación dentro del modal único.
		$fullscreen = (bool)$out->getProperty( 'stellanova-fullscreen' );
		$data['is-sn-fullscreen'] = $fullscreen;

		// — UserTools: identidad tri-estado (spec UserIdentity) —
		$isNamed = method_exists( $user, 'isNamed' ) ? $user->isNamed() : $user->isRegistered();
		$isTemp = method_exists( $user, 'isTemp' ) && $user->isTemp();
		$identity = $isNamed ? 'registered' : ( $isTemp ? 'temporary' : 'anonymous' );
		$data['sn-identity'] = $identity;

		// — SiteIsotype: autocontenido; $wgLogos (data-logos) como override —
		// $wgLogos override SOLO si la instalación fijó un logo deliberado;
		// el placeholder por defecto de MediaWiki ("change-your-logo") no
		// cuenta — ahí manda el isotipo autocontenido (spec SiteIsotype:
		// el asset del skin es el default; data-logos es el override).
		$logos = $data['data-logos'] ?? [];
		$override = '';
		foreach ( [ 'icon', '1x', 'wordmark' ] as $k ) {
			$v = $logos[$k] ?? null;
			$src = is_array( $v ) ? ( $v['src'] ?? '' ) : ( is_string( $v ) ? $v : '' );
			if ( $src !== '' && !preg_match( '/(change-your-logo|(^|\/)Wiki\.png)/i', $src ) ) {
				$override = '<img src="' . htmlspecialchars( $src )
					. '" alt="" class="sn-isotype-img">';
				break;
			}
		}
		$data['sn-isotype'] = [
			'href' => $data['link-mainpage'] ?? Title::newMainPage()->getLocalURL(),
			'is-override' => $override !== '',
			'html-override' => $override,
			'svg' => self::isotypeSvg(),
			'svg-icon' => self::iconSvg(),
		];

		// — Navegación del sitio vs. caja de herramientas —
		// El MediaWiki:Sidebar entrega varios portlets; la caja de
		// herramientas (id p-tb, "Herramientas y más") va al pie y el
		// resto (Escuela/Wiki/Navegación…) a su propio menú del header.
		// Partición server-side: filtrar por id es más fiable que en
		// Mustache. Se omiten los vacíos (is-empty).
		$sidebar = $data['data-portlets-sidebar'] ?? [];
		$portlets = [];
		if ( isset( $sidebar['data-portlets-first'] ) && $sidebar['data-portlets-first'] ) {
			$portlets[] = $sidebar['data-portlets-first'];
		}
		foreach ( $sidebar['array-portlets-rest'] ?? [] as $p ) {
			$portlets[] = $p;
		}
		$siteNav = [];
		$toolbox = null;
		foreach ( $portlets as $p ) {
			if ( !is_array( $p ) || !empty( $p['is-empty'] ) ) {
				continue;
			}
			if ( ( $p['id'] ?? '' ) === 'p-tb' ) {
				$toolbox = $p;
			} else {
				$siteNav[] = $p;
			}
		}
		$data['sn-sitenav'] = $siteNav;
		$data['sn-has-sitenav'] = $siteNav !== [];
		if ( is_array( $toolbox ) && isset( $toolbox['html-items'] ) ) {
			$toolbox['html-items'] = self::iconizeToollist( (string)$toolbox['html-items'] );
		}
		$data['sn-toolbox'] = $toolbox;

		// — UN botón "Editar" (lápiz) en la barra, antes del menú Página —
		// Si la página tiene formulario asociado (PageForms, incl. herencia
		// por categoría p. ej. Categoría:Persona) el lápiz ABRE EL
		// FORMULARIO y en el menú "Página" aparece "Editar código" (el
		// editor clásico de wikitexto). Si NO tiene formulario, el lápiz
		// es la edición clásica. PageForms aquí no inyecta la pestaña de
		// form-edit; el skin DERIVA el destino con su API canónica (no se
		// fabrica: el formulario solo cuenta si getDefaultFormsForPage
		// resuelve uno).
		$title = $this->getTitle();
		$editIds = [ 'ca-edit', 'ca-ve-edit', 'ca-formedit', 'ca-form_edit' ];
		$data['sn-edit'] = null;
		$data['sn-editcode'] = null;
		if ( $title && $title->canExist() ) {
			$classicEdit = $title->getLocalURL( [ 'action' => 'edit' ] );
			$formHref = null;
			if ( class_exists( \PFFormLinker::class ) ) {
				try {
					$forms = \PFFormLinker::getDefaultFormsForPage( $title );
					if ( is_array( $forms ) && $forms !== [] ) {
						$fe = \SpecialPage::getTitleFor(
							'FormEdit',
							(string)$forms[0] . '/' . $title->getPrefixedText()
						);
						$formHref = $fe->getLocalURL();
					}
				} catch ( \Throwable $e ) {
					// Defensivo: una API de PF distinta no rompe el render.
				}
			}
			if ( $formHref !== null ) {
				// Con formulario: lápiz → formulario; "Editar código" → clásico.
				$data['sn-edit'] = [
					'href'  => $formHref,
					'label' => $this->msg( 'stellanova-form-edit' )->text(),
				];
				$data['sn-editcode'] = [
					'href'  => $classicEdit,
					'label' => $this->msg( 'stellanova-edit-code' )->text(),
				];
			} else {
				// Sin formulario: lápiz → edición clásica.
				$data['sn-edit'] = [
					'href'  => $classicEdit,
					'label' => $this->msg( 'edit' )->text(),
				];
			}
		}
		// Vistas restantes para el desplegable "Página": se excluye el
		// editar de core (lo cubre el lápiz de la barra). El "Editar
		// código" (cuando hay formulario) se añade en la plantilla.
		$data['sn-pageviews'] = [];
		$views = $data['data-portlets']['data-views'] ?? [];
		foreach ( $views['array-items'] ?? [] as $vi ) {
			if ( !in_array( $vi['id'] ?? '', $editIds, true ) ) {
				$data['sn-pageviews'][] = $vi;
			}
		}
		$data['sn-has-pageviews'] = $data['sn-pageviews'] !== [];

		// — Pie: línea "Esta página se editó por última vez el … a las … por
		// <Usuario>". Reúne la fecha/hora (formateadas como el core, en el
		// idioma del usuario) con el AUTOR de la revisión mostrada (oldid si
		// lo hay; si no, la actual). El autor se resuelve con FOR_PUBLIC: si
		// está suprimido, se omite el "por" y se cae al lastmod estándar.
		// Solo para páginas existentes con revisión datada (las especiales no
		// tienen, y entonces el pie simplemente no muestra la línea).
		$data['sn-lastedit'] = null;
		if ( $title && $title->canExist() ) {
			$revLookup = MediaWikiServices::getInstance()->getRevisionLookup();
			$revId = $out->getRevisionId();
			$rev = $revId
				? $revLookup->getRevisionById( $revId )
				: $revLookup->getRevisionByTitle( $title );
			if ( $rev && $rev->getTimestamp() ) {
				$lang = $this->getLanguage();
				$ts = $rev->getTimestamp();
				$d = $lang->userDate( $ts, $user );
				$t = $lang->userTime( $ts, $user );
				$author = $rev->getUser( RevisionRecord::FOR_PUBLIC );
				if ( $author ) {
					$name = $author->getName();
					$userPage = Title::makeTitleSafe( NS_USER, $name );
					$userHtml = $userPage
						? Html::element( 'a',
							[ 'href' => $userPage->getLocalURL(), 'class' => 'sn-foot-user' ],
							$name )
						: Html::element( 'span', [ 'class' => 'sn-foot-user' ], $name );
					$html = $this->msg( 'stellanova-footer-lastedit', $d, $t )
						->rawParams( $userHtml )->escaped();
				} else {
					$html = $this->msg( 'lastmodifiedat', $d, $t )->escaped();
				}
				$data['sn-lastedit'] = [ 'html' => $html ];
			}
		}

		// — PreferencesPanel: estado inicial conocido server-side —
		//
		// Estado inicial de los controles del menú de usuario (Tema · Tamaño
		// de letra). El pre-pintado (Hooks::onBeforePageDisplay) ya fijó los
		// atributos del documento; skin.js sincroniza el botón activo al
		// cargar. `os-scheme` alimenta data-sn-os del segmento Tema (pista
		// de a qué resuelve "auto"); `is-temporary` marca la cuenta temporal.
		$data['sn-prefs'] = [
			'is-temporary' => $isTemp,
			'os-scheme'    => '',
		];

		// — ManagedChrome: fragmentos editados como páginas del namespace —
		$data['sn-chrome'] = [];
		foreach ( self::CHROME as $slot => $pageName ) {
			$data['sn-chrome'][$slot] = $this->resolveFragment( $pageName );
		}

		return $data;
	}

	/**
	 * Resuelve un InterfaceFragment: existe + contenido != null + no en
	 * blanco (spec). is_blank ≈ tras recortar espacios y comentarios HTML
	 * no queda nada (cierre razonable de la pregunta abierta del spec).
	 * Prefiere el namespace dedicado "Stella-Nova"; si no está declarado,
	 * cae a la página homónima del espacio principal ("Stella-Nova:Pie")
	 * para que el contenido ya creado se refleje igual. Vacío/ausente →
	 * no publicado (spec ManagedChrome.HiddenWhenUnpublished). Defensivo:
	 * cualquier fallo degrada a no-publicado, nunca rompe el render.
	 *
	 * @param string $pageName
	 * @return array{is-published:bool,html:string,version:string}
	 */
	private function resolveFragment( string $pageName ): array {
		$blank = [ 'is-published' => false, 'html' => '', 'version' => '' ];
		try {
			$services = MediaWikiServices::getInstance();
			$nsInfo = $services->getContentLanguage();
			$nsId = $nsInfo->getNsIndex( 'Stella-Nova' );
			if ( $nsId !== false && $nsId !== null ) {
				// Caso ideal (spec): namespace dedicado, escritura
				// restringida vía $wgNamespaceProtection.
				$title = Title::makeTitleSafe( $nsId, $pageName );
			} else {
				// Fallback pragmático: el namespace no está declarado en
				// LocalSettings, así que la página creada vive en el
				// espacio principal con dos puntos en el título
				// ("Stella-Nova:Pie"). Se refleja igual para que el editor
				// la vea sin tocar config. NOTA: sin el namespace declarado
				// NO hay restricción de escritura del spec
				// (RestrictChromeNamespaceWrites) — declararlo en
				// LocalSettings es lo recomendado para paridad/seguridad.
				$title = Title::newFromText( 'Stella-Nova:' . $pageName );
			}
			if ( !$title || !$title->exists() ) {
				return $blank;
			}
			$page = $services->getWikiPageFactory()->newFromTitle( $title );
			$content = $page->getContent();
			if ( !$content ) {
				return $blank;
			}
			$text = trim( $content->getWikitextForTransclusion()
				?: ( method_exists( $content, 'getText' ) ? $content->getText() : '' ) );
			$stripped = trim( preg_replace( '/<!--.*?-->/s', '', $text ) );
			if ( $stripped === '' ) {
				return $blank;
			}
			$parsed = $this->getOutput()->parseAsContent(
				'{{:' . $title->getPrefixedText() . '}}'
			);
			if ( trim( strip_tags( $parsed ) ) === '' && strpos( $parsed, '<img' ) === false ) {
				return $blank;
			}
			// `version` = id de la última revisión: identifica ESTA versión del
			// fragmento. El aviso descartado se recuerda por versión, así que
			// al editar la página el aviso reaparece (spec: "si ya se ha leído"
			// aplica a lo leído, no a un aviso nuevo).
			return [
				'is-published' => true,
				'html'         => $parsed,
				'version'      => (string)$title->getLatestRevID(),
			];
		} catch ( \Throwable $e ) {
			return $blank;
		}
	}

	/**
	 * Editar-sección SIN los corchetes de adorno. Core (Skin::doEditSectionLinksHTML,
	 * marcado @stable to override by skins) envuelve los enlaces entre
	 * `<span class="mw-editsection-bracket">[</span>` … `]` y los separa con un
	 * `<span class="mw-editsection-divider">` (pipe). El skin ocultaba AMBOS por
	 * CSS (display:none) — eran ruido en el DOM. Aquí los suprimimos en origen:
	 * emitimos solo el contenedor `.mw-editsection` con los `<a>` de cada enlace.
	 * El espaciado entre enlaces (cuando hay más de uno, p. ej. editar + editar
	 * código) lo da el `gap` flex de `.mw-editsection` en stella-nova.css, así
	 * que no hace falta divider. El resto del contrato (clase contenedora, los
	 * enlaces) se mantiene intacto.
	 *
	 * @param array $links
	 * @param Language $lang
	 * @return string
	 */
	protected function doEditSectionLinksHTML( array $links, Language $lang ) {
		$linksHtml = [];
		foreach ( $links as $linkDetails ) {
			$linksHtml[] = $linkDetails['html'];
		}
		return Html::rawElement(
			'span',
			[ 'class' => 'mw-editsection' ],
			implode( '', $linksHtml )
		);
	}
}

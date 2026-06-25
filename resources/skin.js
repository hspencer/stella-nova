/* Stella Nova — mejora progresiva. Vanilla ES, sin jQuery propio. Sin JS
 * la página es legible y el pre-pintado (Hooks) ya aplicó el tema; aquí
 * se añaden panel de preferencias, persistencia híbrida, cajón y popovers.
 */
( function () {
	'use strict';

	var doc = document;
	var root = doc.documentElement;
	var cfg = ( window.mw && mw.config && mw.config.get( 'wgStellaNova' ) ) || {
		identity: 'anonymous', persist: 'browser', apiPrefix: 'stellanova-', server: {}
	};
	var KEYS = [ 'theme', 'font', 'family' ];

	/* ── Persistencia: cuenta (cross-device) vs navegador ── */
	function readPref( k ) {
		if ( cfg.persist === 'account' ) { return cfg.server[ k ] || ''; }
		try { return localStorage.getItem( 'sn-pref-' + k ) || ''; } catch ( e ) { return ''; }
	}
	function writePref( k, v ) {
		if ( cfg.persist === 'account' ) {
			cfg.server[ k ] = v;
			if ( window.mw && mw.Api ) {
				try { new mw.Api().saveOption( cfg.apiPrefix + k, v ); } catch ( e ) {}
			}
		} else {
			try {
				if ( v ) { localStorage.setItem( 'sn-pref-' + k, v ); }
				else { localStorage.removeItem( 'sn-pref-' + k ); }
			} catch ( e ) {}
		}
	}

	/* ── Aplicar una preferencia al documento (data-attrs de tokens.css) ── */
	function apply( k, v ) {
		if ( k === 'theme' ) {
			// Default = claro (sin atributo). "auto" sigue al SO; "dark"
			// fuerza oscuro; "light" fuerza claro; vacío → claro.
			if ( v === 'light' || v === 'dark' || v === 'auto' ) {
				root.setAttribute( 'data-sn-theme', v );
			} else { root.removeAttribute( 'data-sn-theme' ); }
			return;
		}
		// font (única otra preferencia): data-sn-font = small|medium|large.
		if ( v ) { root.setAttribute( 'data-sn-' + k, v ); }
		else { root.removeAttribute( 'data-sn-' + k ); }
	}

	/* ── Segmentos (Tema · Tamaño de letra): estado activo de los botones.
	 *    Default sin elección guardada: tema claro, fuente media. Los
	 *    controles viven en el menú de usuario (ya no en un panel aparte). */
	function syncSegments() {
		doc.querySelectorAll( '.sn-seg[data-sn-pref]' ).forEach( function ( seg ) {
			var k = seg.getAttribute( 'data-sn-pref' );
			var cur = readPref( k );
			var fallback = k === 'theme' ? 'light' : k === 'font' ? 'medium'
				: k === 'family' ? 'sans'
				: seg.querySelector( 'button[data-v]' ).getAttribute( 'data-v' );
			seg.querySelectorAll( 'button[data-v]' ).forEach( function ( b ) {
				var on = b.getAttribute( 'data-v' ) === ( cur || fallback );
				b.classList.toggle( 'is-on', on );
				b.setAttribute( 'aria-pressed', on ? 'true' : 'false' );
			} );
		} );
	}

	function bindPrefs() {
		var segs = doc.querySelectorAll( '.sn-seg[data-sn-pref]' );
		if ( !segs.length ) { return; }
		segs.forEach( function ( seg ) {
			seg.addEventListener( 'click', function ( e ) {
				var b = e.target.closest( 'button[data-v]' );
				if ( !b ) { return; }
				var k = seg.getAttribute( 'data-sn-pref' );
				var v = b.getAttribute( 'data-v' );
				// "auto" se persiste explícitamente (seguir al SO).
				writePref( k, v ); apply( k, v ); syncSegments();
			} );
		} );
		// Estado inicial de los botones (sin FOUC del control: el atributo
		// del documento ya lo fijó el pre-pintado en Hooks).
		syncSegments();
	}

	/* ── Modo compact (tablet vertical y menos): paneles emergentes como
	 *    modales. Detecta el viewport igual que la media query CSS (48rem,
	 *    ≈ 768 px). Si cambia este umbral, sincronizar con stella-nova.css.
	 *    El estado se refresca on-resize para responder a rotación. */
	var COMPACT_MQ = ( window.matchMedia && window.matchMedia( '(max-width: 48rem)' ) ) || null;
	function isCompact() { return !!( COMPACT_MQ && COMPACT_MQ.matches ); }

	/* ── Conteo global de modales abiertos: marca <html> con data-sn-modal
	 *    para que el CSS pinte el scrim y bloquee el scroll subyacente.
	 *    El cierre por click en el scrim lo expone como botón sobre <body>. */
	var openModals = 0;
	function modalOpened() {
		openModals++;
		if ( openModals === 1 ) { root.setAttribute( 'data-sn-modal', '' ); }
	}
	function modalClosed() {
		openModals = Math.max( 0, openModals - 1 );
		if ( openModals === 0 ) { root.removeAttribute( 'data-sn-modal' ); }
	}

	function focusablesIn( el ) {
		return el.querySelectorAll(
			'button:not([disabled]), [href], input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])'
		);
	}
	function trapTab( panel, e ) {
		var f = focusablesIn( panel ); if ( !f.length ) { return; }
		var first = f[ 0 ], last = f[ f.length - 1 ];
		if ( e.shiftKey && doc.activeElement === first ) { e.preventDefault(); last.focus(); }
		else if ( !e.shiftKey && doc.activeElement === last ) { e.preventDefault(); first.focus(); }
	}

	/* ── Popovers (Navegación · Página · Usuario). En desktop: dropdown
	 *    posicionado con la regla CSS aria-expanded. En compact: el
	 *    contenedor .sn-md recibe data-sn-open para que el CSS lo presente
	 *    como modal-bottom-sheet, y aquí montamos focus trap + ESC + scrim. */
	function bindMenus() {
		var triggers = doc.querySelectorAll( '[data-sn-menu]' );
		var activeMenu = null;
		var lastFocus = null;

		function panelOf( t ) {
			var md = t.closest( '.sn-md' );
			if ( !md ) { return null; }
			return md.querySelector( '.sn-menu-list, .sn-megamenu' );
		}
		function closeAll( opts ) {
			opts = opts || {};
			triggers.forEach( function ( o ) {
				o.setAttribute( 'aria-expanded', 'false' );
				var md = o.closest( '.sn-md' );
				if ( md && md.hasAttribute( 'data-sn-open' ) ) {
					md.removeAttribute( 'data-sn-open' );
					modalClosed();
				}
			} );
			if ( activeMenu ) {
				doc.removeEventListener( 'keydown', onKey );
				activeMenu = null;
				if ( opts.restoreFocus !== false && lastFocus ) { lastFocus.focus(); }
				lastFocus = null;
			}
		}
		function onKey( e ) {
			if ( e.key === 'Escape' ) { e.preventDefault(); closeAll(); return; }
			if ( e.key === 'Tab' && activeMenu ) {
				var md = activeMenu.closest( '.sn-md' );
				if ( !md ) { return; }
				// Atrapa Tab tanto en compact como en el modal fullscreen
				// dedicado (`.sn-md-fs`), donde no hay "fuera".
				if ( isCompact() || md.classList.contains( 'sn-md-fs' ) ) {
					trapTab( md, e );
				}
			}
		}

		triggers.forEach( function ( t ) {
			t.addEventListener( 'click', function ( e ) {
				e.stopPropagation();
				var alreadyOpen = t.getAttribute( 'aria-expanded' ) === 'true';
				closeAll( { restoreFocus: false } );
				if ( alreadyOpen ) { return; }
				t.setAttribute( 'aria-expanded', 'true' );
				var md = t.closest( '.sn-md' );
				var panel = panelOf( t );
				if ( !md || !panel ) { return; }
				activeMenu = panel;
				// `.sn-md-fs` (modal único de __PANTALLACOMPLETA__) siempre
				// se presenta como modal a pantalla completa, sin importar
				// viewport: en fullscreen no hay cabecera donde anclar un
				// popover desktop.
				var forceModal = md.classList.contains( 'sn-md-fs' );
				if ( isCompact() || forceModal ) {
					md.setAttribute( 'data-sn-open', '' );
					modalOpened();
					lastFocus = t;
					// El primer focusable suele ser el botón X (cabecera);
					// salta al SEGUNDO para que el foco caiga en el primer
					// ítem del menú, no en cerrar.
					var f = focusablesIn( md );
					if ( f.length > 1 ) { f[ 1 ].focus(); }
					else if ( f.length ) { f[ 0 ].focus(); }
				}
				doc.addEventListener( 'keydown', onKey );
			} );
		} );
		// Botón X dentro de cualquier menú modal → cerrar.
		doc.addEventListener( 'click', function ( e ) {
			if ( !e.target.closest ) { return; }
			if ( e.target.closest( '[data-sn-menu-close]' ) ) {
				e.preventDefault(); e.stopPropagation();
				closeAll();
			}
		} );
		// Click fuera del panel → cerrar. Aplica al popover desktop y al
		// top-sheet de pantalla completa (`.sn-md-fs`, anclado arriba y solo
		// tan alto como su contenido → hay "fuera" debajo). El bottom-sheet
		// modal de compact (no-fs) cierra por X/ESC, no por aquí.
		doc.addEventListener( 'click', function ( e ) {
			if ( !activeMenu ) { return; }
			var md = activeMenu.closest( '.sn-md' );
			var isFs = !!( md && md.classList.contains( 'sn-md-fs' ) );
			if ( !isFs && isCompact() ) { return; }
			if ( activeMenu.contains( e.target ) ) { return; }
			if ( e.target.closest && e.target.closest( '[data-sn-menu]' ) ) { return; }
			closeAll();
		} );
	}

	/* ── Búsqueda como modal en compact viewport. El form es el MISMO,
	 *    sólo cambia su presentación (CSS responde a data-sn-search-open
	 *    en <html>). En desktop el trigger no es visible y este binding
	 *    queda inerte. */
	function bindSearch() {
		var trigger = doc.querySelector( '[data-sn-search-open]' );
		var closeBtn = doc.querySelector( '[data-sn-search-close]' );
		var form = doc.getElementById( 'searchform' );
		if ( !trigger || !form ) { return; }
		var input = form.querySelector( 'input[type="search"], #searchInput, .mw-searchInput' );
		var lastFocus = null;

		function open() {
			if ( !isCompact() ) { return; }
			lastFocus = doc.activeElement;
			root.setAttribute( 'data-sn-search-open', '' );
			trigger.setAttribute( 'aria-expanded', 'true' );
			modalOpened();
			window.setTimeout( function () { if ( input ) { input.focus(); } }, 30 );
			doc.addEventListener( 'keydown', onKey );
		}
		function close() {
			if ( !root.hasAttribute( 'data-sn-search-open' ) ) { return; }
			root.removeAttribute( 'data-sn-search-open' );
			trigger.setAttribute( 'aria-expanded', 'false' );
			modalClosed();
			doc.removeEventListener( 'keydown', onKey );
			if ( lastFocus ) { lastFocus.focus(); }
			lastFocus = null;
		}
		function onKey( e ) {
			if ( e.key === 'Escape' ) { e.preventDefault(); close(); return; }
			if ( e.key === 'Tab' ) { trapTab( form, e ); }
		}

		trigger.addEventListener( 'click', open );
		if ( closeBtn ) { closeBtn.addEventListener( 'click', close ); }
		// Al pasar a desktop, cerrar el modo modal por si quedó abierto.
		if ( COMPACT_MQ && COMPACT_MQ.addEventListener ) {
			COMPACT_MQ.addEventListener( 'change', function ( ev ) {
				if ( !ev.matches ) { close(); }
			} );
		}
	}

	/* ── Aviso gestionado: cerrar y recordar por versión ──
	 *    Persistimos en localStorage la versión (id de revisión) descartada.
	 *    El pre-pintado (Hooks) ya oculta sin parpadeo cuando coincide; aquí
	 *    sólo manejamos el clic en cerrar. Es por-navegador a propósito (un
	 *    aviso descartado no debería perseguir al usuario entre dispositivos). */
	function bindNotice() {
		var notice = doc.querySelector( '.sn-notice[data-sn-notice]' );
		if ( !notice ) { return; }
		var closeBtn = notice.querySelector( '[data-sn-notice-close]' );
		if ( !closeBtn ) { return; }
		closeBtn.addEventListener( 'click', function () {
			var id = notice.getAttribute( 'data-sn-notice' );
			try { if ( id ) { localStorage.setItem( 'sn-notice-dismissed', id ); } } catch ( e ) {}
			root.setAttribute( 'data-sn-notice-hide', '' );
		} );
	}

	/* ── «Versión para imprimir» → previsualización paginada (paged.js) ──
	 *    La herramienta #t-print es por defecto `javascript:print()`. La
	 *    interceptamos para abrir, en su lugar, la maqueta paginada (Vivliostyle)
	 *    con cabecera/pie + numeración + TOC + columnas (lo que el motor de
	 *    impresión del navegador NO sabe hacer). El módulo pesa (~Vivliostyle) y
	 *    se carga BAJO DEMANDA. Si la carga o el arranque fallan, caemos al print
	 *    nativo —la hoja print.css garantiza una impresión digna igualmente. */
	function bindPrint() {
		if ( !( window.mw && mw.loader ) ) { return; }
		var link = doc.querySelector( '#t-print a' );
		// Aviso (opción del usuario): el ícono lleva a la vista paginada
		// (cabecera/pie/numeración); Cmd+P sigue dando la impresión nativa rápida.
		if ( link ) {
			link.setAttribute( 'title',
				'Versión para imprimir — vista paginada con cabecera, pie y números de página (Cmd/Ctrl+P para impresión rápida)' );
		}
		// MediaWiki core (`mediawiki.page.ready`) ENGANCHA su propio handler de
		// click en `#t-print a` que llama a `window.print()` directamente (no usa
		// el href). Como es OTRO handler, nuestro `preventDefault` no lo frena: el
		// diálogo nativo se levantaba ANTES de la previsualización. Lo cortamos en
		// FASE DE CAPTURA en el documento —corre antes que cualquier handler del
		// destino— con `stopImmediatePropagation`: el evento nunca llega al
		// handler de core, y disparamos solo la previsualización. (Independiente
		// del orden de carga de módulos, por eso captura y no en el elemento.) */
		doc.addEventListener( 'click', function ( e ) {
			var a = e.target.closest && e.target.closest( '#t-print a' );
			if ( !a ) { return; }
			e.preventDefault();
			e.stopImmediatePropagation();
			mw.loader.using( 'skins.stellanova.print' ).then( function () {
				var ok = window.SN_PrintPreview && window.SN_PrintPreview.open();
				if ( ok === false ) { window.print(); }
			}, function () { window.print(); } );
		}, true );
	}

	/* ── Acordeón real para colapsables de BLOQUE (apertura Y cierre animados) ──
	 * makeCollapsible togglea el cuerpo con display seco (sin animar) y no expone
	 * hook para reemplazarlo. Lo hacemos midiendo el alto: enganchamos sus eventos
	 * jQuery y animamos `height` 0↔scrollHeight con overflow:hidden SOLO durante la
	 * transición (al terminar restauramos height:auto/overflow, sin tocar el
	 * `display` ni envolver → una grilla flex como `.curso-fotos` conserva su
	 * layout). Animamos el elemento que la librería oculta: `.mw-collapsible-content`
	 * si existe, si no el propio `.mw-collapsible` (customtoggle: portada, ficha).
	 * En el CIERRE la librería pone display:none → lo reanimamos en el mismo tick
	 * (sin flash) y reocultamos al terminar. Tablas/listas se excluyen (togglean
	 * filas/ítems). Duración/ease replican --sn-dur-2/--sn-ease; reduced-motion: el
	 * reset global !important acorta la transición a ~0 y transitionend igual cae. */
	function bindCollapse() {
		if ( !window.mw || !mw.loader ) { return; }
		mw.loader.using( 'jquery.makeCollapsible' ).then( function () {
			var $ = window.jQuery;
			if ( !$ ) { return; }
			var DUR = 220, EASE = 'cubic-bezier(.22, 1, .36, 1)';

			function eligible( el ) {
				var t = el.tagName.toLowerCase();
				return t !== 'table' && t !== 'ul' && t !== 'ol';
			}
			function body( el ) {
				return el.querySelector( ':scope > .mw-collapsible-content' ) || el;
			}
			function animate( el, from, to, after ) {
				if ( el._snCleanup ) { el._snCleanup(); }      // interrumpe lo anterior SIN su `after`
				var done = function ( e ) {
					if ( e && ( e.target !== el || e.propertyName !== 'height' ) ) { return; }
					el._snCleanup();
					if ( after ) { after(); }
				};
				el._snCleanup = function () {
					el.removeEventListener( 'transitionend', done );
					clearTimeout( el._snT );
					el._snCleanup = null;
					el.style.transition = el.style.overflow = el.style.height = '';
				};
				el.style.overflow = 'hidden';
				el.style.height = from + 'px';
				void el.offsetHeight;                          // reflow: fija el punto de partida
				el.style.transition = 'height ' + DUR + 'ms ' + EASE;
				el.style.height = to + 'px';
				el.addEventListener( 'transitionend', done );
				el._snT = setTimeout( done, DUR + 80 );        // red de seguridad si no cae transitionend
			}

			$( doc )
				.on( 'afterExpand.mw-collapsible', '.mw-collapsible', function () {
					if ( !eligible( this ) ) { return; }
					var el = body( this );                     // ya visible, alto auto
					animate( el, 0, el.scrollHeight );
				} )
				.on( 'beforeCollapse.mw-collapsible', '.mw-collapsible', function () {
					if ( !eligible( this ) ) { return; }
					var el = body( this );
					el._snH = el.scrollHeight;                 // mide antes de que la librería oculte
				} )
				.on( 'afterCollapse.mw-collapsible', '.mw-collapsible', function () {
					if ( !eligible( this ) ) { return; }
					var el = body( this );
					el.style.display = '';                     // la librería puso display:none; reanimamos
					animate( el, el._snH || el.scrollHeight, 0, function () {
						el.style.display = 'none';             // reocultar: estado colapsado
					} );
				} );
		} );
	}

	function init() { bindPrefs(); bindMenus(); bindSearch(); bindNotice(); bindPrint(); bindCollapse(); }
	if ( doc.readyState === 'loading' ) {
		doc.addEventListener( 'DOMContentLoaded', init );
	} else { init(); }
}() );

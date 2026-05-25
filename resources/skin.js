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
	var KEYS = [ 'theme', 'width', 'font', 'leading', 'toc', 'collapsible', 'motion' ];
	var TOGGLES = { collapsible: 1, motion: 1 };

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
		if ( k === 'motion' ) {
			if ( v === 'reduced' ) { root.setAttribute( 'data-sn-motion', 'reduced' ); }
			else if ( v === 'full' ) { root.setAttribute( 'data-sn-motion', 'full' ); }
			else { root.removeAttribute( 'data-sn-motion' ); }
			return;
		}
		if ( v ) { root.setAttribute( 'data-sn-' + k, v ); }
		else { root.removeAttribute( 'data-sn-' + k ); }
	}

	function anySet() {
		return KEYS.some( function ( k ) { return readPref( k ); } );
	}

	/* ── Panel: estado de controles ── */
	function syncControls( form ) {
		form.querySelectorAll( '[data-sn-pref]' ).forEach( function ( ctrl ) {
			var k = ctrl.getAttribute( 'data-sn-pref' );
			var cur = readPref( k );
			if ( ctrl.classList.contains( 'sn-seg' ) ) {
				// Default sin elección: claro (decisión de producto). Para
				// los demás segmentos, el primer botón es el default.
				var fallback = k === 'theme' ? 'light' : ctrl.querySelector( 'button[data-v]' ).getAttribute( 'data-v' );
				ctrl.querySelectorAll( 'button[data-v]' ).forEach( function ( b ) {
					var on = b.getAttribute( 'data-v' ) === ( cur || fallback );
					b.classList.toggle( 'is-on', on );
					b.setAttribute( 'aria-pressed', on ? 'true' : 'false' );
				} );
			} else if ( ctrl.type === 'checkbox' ) {
				ctrl.checked = TOGGLES[ k ]
					? ( k === 'motion' ? cur === 'reduced' : cur !== 'disabled' && cur !== '' ? cur === 'enabled' : false )
					: !!cur;
				if ( k === 'collapsible' ) { ctrl.checked = cur === 'enabled'; }
			}
		} );
		var resetBtn = form.querySelector( '[data-sn-prefs-reset]' );
		if ( resetBtn ) { resetBtn.disabled = !anySet(); }
		var scope = form.querySelector( '[data-sn-scope]' );
		if ( scope && window.mw && mw.msg ) {
			scope.textContent = mw.msg( cfg.identity === 'registered'
				? 'stellanova-prefs-scope-account' : 'stellanova-prefs-scope-browser' );
		}
	}

	function bindPanel() {
		var panel = doc.getElementById( 'sn-prefs' );
		var scrim = doc.querySelector( '[data-sn-prefs-scrim]' );
		var openBtn = doc.querySelector( '[data-sn-prefs-open]' );
		if ( !panel || !openBtn ) { return; }
		var form = panel.querySelector( '[data-sn-prefs-form]' );
		var lastFocus = null;

		function focusables() {
			return panel.querySelectorAll(
				'button, [href], input, select, [tabindex]:not([tabindex="-1"])'
			);
		}
		function open() {
			lastFocus = doc.activeElement;
			panel.hidden = false; if ( scrim ) { scrim.hidden = false; }
			requestAnimationFrame( function () {
				panel.classList.add( 'is-open' );
				if ( scrim ) { scrim.classList.add( 'is-open' ); }
			} );
			openBtn.setAttribute( 'aria-expanded', 'true' );
			modalOpened();
			syncControls( form );
			var f = focusables(); if ( f.length ) { f[ 0 ].focus(); }
			doc.addEventListener( 'keydown', onKey );
		}
		function close() {
			panel.classList.remove( 'is-open' );
			if ( scrim ) { scrim.classList.remove( 'is-open' ); }
			openBtn.setAttribute( 'aria-expanded', 'false' );
			modalClosed();
			doc.removeEventListener( 'keydown', onKey );
			// En desktop el panel anima con transform: translateX → espera el
			// fin del transition para hidden=true. En compact no hay
			// transición (el modal es fullscreen) y queremos cierre inmediato.
			if ( isCompact() ) {
				panel.hidden = true; if ( scrim ) { scrim.hidden = true; }
			} else {
				window.setTimeout( function () {
					panel.hidden = true; if ( scrim ) { scrim.hidden = true; }
				}, 420 );
			}
			if ( lastFocus ) { lastFocus.focus(); }
		}
		function onKey( e ) {
			if ( e.key === 'Escape' ) { close(); return; }
			if ( e.key !== 'Tab' ) { return; }
			var f = focusables(); if ( !f.length ) { return; }
			var first = f[ 0 ], last = f[ f.length - 1 ];
			if ( e.shiftKey && doc.activeElement === first ) { e.preventDefault(); last.focus(); }
			else if ( !e.shiftKey && doc.activeElement === last ) { e.preventDefault(); first.focus(); }
		}

		openBtn.addEventListener( 'click', open );
		panel.querySelectorAll( '[data-sn-prefs-close]' ).forEach( function ( b ) {
			b.addEventListener( 'click', close );
		} );
		if ( scrim ) { scrim.addEventListener( 'click', close ); }

		/* Segmentos */
		form.querySelectorAll( '.sn-seg' ).forEach( function ( seg ) {
			seg.addEventListener( 'click', function ( e ) {
				var b = e.target.closest( 'button[data-v]' );
				if ( !b ) { return; }
				var k = seg.getAttribute( 'data-sn-pref' );
				var v = b.getAttribute( 'data-v' );
				// "auto" se persiste explícitamente (seguir al SO); el
				// estado "sin elección" solo se alcanza con Restablecer.
				writePref( k, v ); apply( k, v ); syncControls( form );
			} );
		} );
		/* Interruptores */
		form.querySelectorAll( 'input.sn-switch[data-sn-pref]' ).forEach( function ( sw ) {
			sw.addEventListener( 'change', function () {
				var k = sw.getAttribute( 'data-sn-pref' ), v;
				if ( k === 'motion' ) { v = sw.checked ? 'reduced' : 'full'; }
				else { v = sw.checked ? 'enabled' : 'disabled'; }
				writePref( k, v ); apply( k, v ); syncControls( form );
			} );
		} );
		/* Restablecer (spec ResetPreferences) */
		var reset = form.querySelector( '[data-sn-prefs-reset]' );
		if ( reset ) {
			reset.addEventListener( 'click', function () {
				KEYS.forEach( function ( k ) { writePref( k, '' ); apply( k, '' ); } );
				syncControls( form );
			} );
		}
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
		// Click fuera del panel (sólo aplica en desktop, donde es popover;
		// en compact y en `.sn-md-fs` el modal es fullscreen y no hay
		// "fuera"). El cierre se hace por X o por ESC.
		doc.addEventListener( 'click', function ( e ) {
			if ( !activeMenu ) { return; }
			if ( isCompact() ) { return; }
			var md = activeMenu.closest( '.sn-md' );
			if ( md && md.classList.contains( 'sn-md-fs' ) ) { return; }
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

	function init() { bindPanel(); bindMenus(); bindSearch(); }
	if ( doc.readyState === 'loading' ) {
		doc.addEventListener( 'DOMContentLoaded', init );
	} else { init(); }
}() );

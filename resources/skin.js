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
			syncControls( form );
			var f = focusables(); if ( f.length ) { f[ 0 ].focus(); }
			doc.addEventListener( 'keydown', onKey );
		}
		function close() {
			panel.classList.remove( 'is-open' );
			if ( scrim ) { scrim.classList.remove( 'is-open' ); }
			openBtn.setAttribute( 'aria-expanded', 'false' );
			doc.removeEventListener( 'keydown', onKey );
			window.setTimeout( function () {
				panel.hidden = true; if ( scrim ) { scrim.hidden = true; }
			}, 420 );
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

	/* ── Popovers (menú de usuario, "más" acciones, variantes) ── */
	function bindMenus() {
		var triggers = doc.querySelectorAll( '[data-sn-menu]' );
		triggers.forEach( function ( t ) {
			t.addEventListener( 'click', function ( e ) {
				e.stopPropagation();
				var open = t.getAttribute( 'aria-expanded' ) === 'true';
				triggers.forEach( function ( o ) { o.setAttribute( 'aria-expanded', 'false' ); } );
				t.setAttribute( 'aria-expanded', open ? 'false' : 'true' );
			} );
		} );
		doc.addEventListener( 'click', function () {
			triggers.forEach( function ( t ) { t.setAttribute( 'aria-expanded', 'false' ); } );
		} );
		doc.addEventListener( 'keydown', function ( e ) {
			if ( e.key === 'Escape' ) {
				triggers.forEach( function ( t ) { t.setAttribute( 'aria-expanded', 'false' ); } );
			}
		} );
	}

	function init() { bindPanel(); bindMenus(); }
	if ( doc.readyState === 'loading' ) {
		doc.addEventListener( 'DOMContentLoaded', init );
	} else { init(); }
}() );

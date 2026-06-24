/* Stella Nova — previsualización de impresión paginada (Vivliostyle).
 *
 * Por qué existe: lo que el usuario pidió para el papel —cabecera/pie por
 * página con logo + numeración «n / total», URL y fecha; números de página en
 * el TOC; y N columnas por hoja con autolayout en formatos anchos— se especifica
 * con CSS Paged Media (`@page` margin-boxes, `counter(page/pages)`,
 * `target-counter()`, `leader()`, multicolumna). NINGÚN navegador lo soporta en
 * su motor de impresión. Vivliostyle (motor de paginación-en-el-navegador, libre)
 * SÍ lo implementa de forma completa —incluida la multicolumna por página, que
 * paged.js no paginaba bien—.
 *
 * Arquitectura:
 *  · PREVISUALIZACIÓN: `CoreViewer` maqueta el documento dentro del overlay
 *    (renderAllPages) → el usuario ve las hojas y elige tamaño/columnas.
 *  · IMPRESIÓN: `Vivliostyle.printHTML(doc)` re-maqueta el MISMO documento en un
 *    iframe oculto y lanza `print()` → salida 1:1, sin trucos de aislamiento.
 *
 * El documento fuente es autocontenido: enlaza las MISMAS hojas del skin
 * (fonts/tokens/stella-nova) que ya usa la página viva + un <style> propio con
 * el @page, las columnas, los elementos corrientes y el TOC. La tipografía,
 * por tanto, es idéntica a pantalla.
 *
 * Lo dispara skin.js (intercepta «Versión para imprimir» en captura) llamando a
 * SN_PrintPreview.open(); si Vivliostyle no cargó, cae al window.print() nativo.
 */
( function () {
	'use strict';

	var doc = document;
	var root = doc.documentElement;
	var mw = window.mw;

	/* Fecha del día de impresión (no del render del servidor) en es-CL. */
	function printDate() {
		try {
			return new Date().toLocaleDateString( 'es-CL',
				{ day: 'numeric', month: 'long', year: 'numeric' } );
		} catch ( e ) { return new Date().toLocaleDateString(); }
	}

	/* URL absoluta, limpia y DECODIFICADA del artículo (no la de ?useskin=). */
	function articleUrl() {
		try {
			var server = mw.config.get( 'wgServer' );
			var path = mw.util.getUrl( mw.config.get( 'wgPageName' ) );
			var url = server + path;
			if ( url.indexOf( '//' ) === 0 ) { url = window.location.protocol + url; }
			try { return decodeURIComponent( url ); } catch ( e2 ) { return url; }
		} catch ( e ) { return window.location.href.split( '?' )[ 0 ]; }
	}

	/* El cuadrado de la constelación (isótopo compacto), ya en el DOM. */
	function logoSvg() {
		var src = doc.querySelector( '.sn-isotype-compact svg, .sn-fs-glyph svg' );
		return src ? src.cloneNode( true ) : null;
	}

	/* Clon del TOC de la página (sin sus controles de plegado), o null si la
	   página no emite TOC. Se usa cuando el switch «Índice» lo pide, ignorando el
	   estado colapsado de pantalla (el usuario decide en la barra). */
	function tocClone() {
		var toc = doc.querySelector( '#toc, .toc, .mw-table-of-contents' );
		if ( !toc ) { return null; }
		var clone = toc.cloneNode( true );
		clone.querySelectorAll(
			'.toctogglecheckbox, .toctogglespan, .toctogglelabel, .togglelist'
		).forEach( function ( n ) { n.remove(); } );
		return clone;
	}

	/* ¿La página trae TOC y NO está colapsado? Determina el estado inicial del
	   switch «Índice» (el TOC nativo colapsa por checkbox `.toctogglecheckbox`). */
	function tocVisibleByDefault() {
		var toc = doc.querySelector( '#toc, .toc, .mw-table-of-contents' );
		if ( !toc ) { return false; }
		var cb = toc.querySelector( '.toctogglecheckbox' );
		var collapsed = ( cb && cb.checked ) ||
			toc.classList.contains( 'tochidden' ) ||
			toc.classList.contains( 'mw-toc-collapsed' ) ||
			toc.getAttribute( 'aria-hidden' ) === 'true';
		return !collapsed;
	}

	/* Tamaños de papel y nº de columnas del cuerpo por formato. Editable. */
	var SIZES = [
		{ id: 'a4',        label: 'A4 · 21 × 29,7 cm',       css: 'A4',          cols: 1 },
		{ id: 'letter',    label: 'Carta · 21,6 × 27,9 cm',  css: 'letter',      cols: 1 },
		{ id: 'legal',     label: 'Oficio · 21,6 × 35,6 cm', css: 'legal',       cols: 1 },
		{ id: 'a3',        label: 'A3 · 29,7 × 42 cm',        css: 'A3',          cols: 2 },
		{ id: 'tabloid',   label: 'Tabloide · 27,9 × 43,2 cm', css: '279mm 432mm', cols: 2 },
		{ id: 'plotter90', label: 'Plóter · 90 × 120 cm',    css: '900mm 1200mm', cols: 4 }
	];
	var DEFAULT_SIZE = 'a4';
	function sizeEntryById( id ) {
		for ( var i = 0; i < SIZES.length; i++ ) { if ( SIZES[ i ].id === id ) { return SIZES[ i ]; } }
		return SIZES[ 0 ];
	}

	/* Cadena `size` del @page resuelta según orientación. Para tamaños CON nombre
	   (A4/letter/legal/A3) basta añadir `landscape`/`portrait`. Para tamaños con
	   dos longitudes explícitas (Tabloide, Plóter) se ordenan los lados: vertical
	   = menor × mayor, horizontal = mayor × menor. */
	function pageSize( ent, orient ) {
		var css = ent.css;
		if ( /\s/.test( css ) ) {
			var parts = css.split( /\s+/ );
			var a = parseFloat( parts[ 0 ] ), b = parseFloat( parts[ 1 ] );
			var unit = ( parts[ 0 ].match( /[a-z%]+$/i ) || [ 'mm' ] )[ 0 ];
			var lo = Math.min( a, b ), hi = Math.max( a, b );
			return ( orient === 'landscape' )
				? hi + unit + ' ' + lo + unit
				: lo + unit + ' ' + hi + unit;
		}
		return css + ( orient === 'landscape' ? ' landscape' : ' portrait' );
	}

	/* Nº de columnas del cuerpo. En HORIZONTAL el ancho de hoja da para una
	   columna más que en vertical (flujo vertical siempre): Carta 1→2, A3/Tabloide
	   2→3, Plóter 4→5… La hoja vertical conserva `ent.cols`. */
	function colsFor( ent, orient ) {
		return ent.cols + ( orient === 'landscape' ? 1 : 0 );
	}

	/* Zoom de la previsualización (escala visual de la hoja en pantalla; no afecta
	   la salida impresa). Útil para «alejar» y ver completa una hoja grande. */
	var ZOOM_MIN = 0.25, ZOOM_MAX = 1.5, ZOOM_STEP = 0.25;

	/* Base de archivos del skin (p. ej. «…/skins/StellaNova/resources»), tomada
	   del <link rel=icon> del isótopo que el skin inyecta con ruta de archivo. */
	function skinBase() {
		var ico = doc.querySelector( 'link[rel~="icon"][href*="/resources/"]' );
		if ( ico && ico.href ) { return ico.href.replace( /\/[^/]*$/, '' ); }
		return ( ( mw && mw.config && mw.config.get( 'wgServer' ) ) || '' ) + '/skins/StellaNova/resources';
	}

	/* Enlazamos las hojas LIMPIAS del skin como ARCHIVOS directos: fonts.css
	   (@font-face), tokens.css (variables --sn-*) y stella-nova.css (tipografía
	   del contenido: .sn-body p, cabeceras, listas, tablas…). A propósito NO
	   usamos el módulo combinado `skins.stellanova.styles`: ese incluye print.css
	   (media print) cuyo `@page` se SUMA al nuestro en Vivliostyle (doble margen).
	   Con archivos directos hay un único @page (el de printCss). */
	function skinCssLinks() {
		var base = skinBase();
		return [ 'fonts.css', 'tokens.css', 'stella-nova.css' ].map( function ( f ) {
			return '<link rel="stylesheet" href="' + base + '/' + f + '">';
		} ).join( '' );
	}

	/* CSS de impresión del documento fuente: @page con sus cuatro margin-boxes
	   (logo / n·total / URL / fecha a 8pt), escala tipográfica, columnas por
	   formato (FLUJO VERTICAL), elementos corrientes, TOC con líder + nº de
	   página, y tablas sin fondo. `sizeCss` y `cols` los elige la barra. */
	function printCss( sizeCss, cols ) {
		var col = ( cols && cols > 1 ) ? [
			'.sn-body { column-count: ' + cols + '; column-gap: 1cm; column-fill: auto; }',
			'.sn-body > :is(#toc, .toc, .mw-table-of-contents) { column-span: all; }',
			'.sn-body :is(figure, table, blockquote, pre, .thumb) { break-inside: avoid; }'
		].join( '\n' ) : '';
		return [
			'@page {',
			'	size: ' + ( sizeCss || 'A4' ) + ';',
			/* OJO: Vivliostyle aplica el margen de @page DOBLE al inset del
			   contenido (margen M → 2·M por lado: lo reserva como zona de
			   margin-boxes Y como caja de página). Margen VERTICAL mayor que el
			   horizontal: con 1.5cm arriba/abajo la banda de margin-boxes es más
			   alta y la CABECERA/PIE quedan más despegadas del borde del papel
			   (~0.75cm en vez de ~0.5cm); los lados siguen a 1cm. */
			'	margin: 1.5cm 1cm;',
			'	@top-left { content: element(snRunLogo); }',
			'	@top-right { content: counter(page) " / " counter(pages);',
			'		font-family: var(--sn-font-text); font-size: 8pt; color: #000; }',
			'	@bottom-left { content: element(snRunUrl); }',
			'	@bottom-right { content: element(snRunDate); }',
			'}',
			/* Tipografía impresa más chica, proporcional (escala única de la que
			   derivan los tokens fs-* y el baseline). En el doc fuente :root es el
			   sitio correcto para fijarla. */
			':root { --sn-font-scale: 0.85; }',
			/* TINTA SOBRE BLANCO. El doc enlaza el CSS de PANTALLA del skin, que
			   trae fondos (el campo beige --sn-field, el grano, los marcos de
			   figuras/thumbs/avisos/código). En papel todo eso sobra: papel blanco
			   y sin cajas de color. Reset amplio de fondos y sombras en el
			   contenido (el `color` del texto NO se toca; las imágenes <img> no son
			   fondo, así que se ven igual, solo sin su marco). */
			'html, body { background: #fff !important; margin: 0; }',
			'body::before { display: none !important; }',   /* el grano de pantalla */
			'.sn-pp-flow, .sn-pp-flow * {',
			'	background: transparent !important; box-shadow: none !important; }',
			'.sn-pp-flow :is(figure, .thumb, .thumbinner, .thumbimage, .gallerybox) {',
			'	overflow: visible !important; border: 0 !important; }',
			'.sn-pp-flow img { max-width: 100%; height: auto; }',
			/* El contenedor del contenido llena el área de página; el margen del
			   contenido (~2cm parejos) lo da íntegro el @page, sin padding extra. */
			'.sn-pp-flow { margin: 0; padding: 0; max-width: none; width: auto; }',
			'.sn-body, .sn-body .mw-parser-output { max-width: none; width: auto; }',
			'.sn-body { font-stretch: 100%; }',
			/* Título de la página: como el flujo no lleva `.sn-paper`, replicamos
			   aquí la regla del #firstHeading (sin el margin-top negativo, que era
			   un ajuste de pantalla). */
			'.sn-pp-flow :is(h1#firstHeading, .firstHeading, .mw-first-heading) {',
			'	font-family: var(--sn-font-text); font-weight: 300;',
			'	font-size: var(--sn-fs-page-title); line-height: var(--sn-baseline-2);',
			'	letter-spacing: -.018em; color: var(--sn-nova);',
			'	margin: 0 0 var(--sn-baseline); max-width: 34ch; text-wrap: balance; }',
			'.sn-body p { line-height: var(--sn-leading); }',
			'.sn-body a { color: #000; text-decoration: underline; }',
			'.sn-pp-flow :is(h1, h2, .mw-heading1, .mw-heading2) { border-bottom: 0; }',
			col,
			/* Elementos corrientes (repetidos por página vía su margin-box). */
			'.sn-run { font-family: var(--sn-font-text); font-size: 8pt; color: #000; line-height: 1.2; }',
			'#sn-run-logo { position: running(snRunLogo); }',
			'#sn-run-logo svg { width: 6mm; height: 6mm; display: block; }',
			'#sn-run-url { position: running(snRunUrl); word-break: break-all; }',
			'#sn-run-date { position: running(snRunDate); white-space: nowrap; }',
			/* TOC: sin caja ni fondo; líder de puntos + nº de página por entrada
			   (Vivliostyle sí soporta leader() y target-counter()). */
			'#toc, .toc, .mw-table-of-contents { background: none; border: 0; padding: 0; }',
			'.toc a, #toc a { text-decoration: none; }',
			'.toc li a::after, #toc li a::after, .mw-table-of-contents li a::after {',
			'	content: leader(". ") target-counter(attr(href url), page); color: #000; }',
			/* Tablas sin color de fondo (se conservan filetes). */
			'.sn-body :is(table, thead, tbody, tfoot, tr, th, td, caption) {',
			'	background: transparent !important; background-color: transparent !important; }'
		].join( '\n' );
	}

	function buildRun( id, node ) {
		var d = doc.createElement( 'div' );
		d.className = 'sn-run';
		d.id = id;
		if ( typeof node === 'string' ) { d.textContent = node; }
		else if ( node ) { d.appendChild( node ); }
		return d;
	}

	/* Contenido a paginar (elemento .sn-pp-flow): elementos corrientes + título
	   + .sn-body (TOC + cuerpo). Replica la jerarquía real para heredar la
	   cascada del skin (el #firstHeading va fuera de .sn-body). */
	function buildContentEl() {
		var outer = doc.createElement( 'div' );
		outer.className = 'sn-pp-flow';

		var logo = logoSvg();
		if ( logo ) { outer.appendChild( buildRun( 'sn-run-logo', logo ) ); }
		outer.appendChild( buildRun( 'sn-run-url', articleUrl() ) );
		outer.appendChild( buildRun( 'sn-run-date', printDate() ) );

		var heading = doc.querySelector( '#firstHeading, .firstHeading, .mw-first-heading' );
		if ( heading ) { outer.appendChild( heading.cloneNode( true ) ); }

		var inner = doc.createElement( 'div' );
		inner.className = 'sn-body mw-body-content';
		outer.appendChild( inner );

		var toc = state.toc ? tocClone() : null;
		if ( toc ) { inner.appendChild( toc ); }

		var body = doc.querySelector( '.mw-parser-output' );
		if ( body ) {
			var bodyClone = body.cloneNode( true );
			bodyClone.querySelectorAll(
				'.noprint, .mw-editsection, .catlinks, .printfooter, #toc, .toc, .mw-table-of-contents'
			).forEach( function ( n ) { n.remove(); } );
			inner.appendChild( bodyClone );
		}
		return outer;
	}

	/* Documento HTML fuente completo y autocontenido para Vivliostyle. */
	function buildSourceDoc( sizeCss, cols ) {
		var wrap = buildContentEl();
		return '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">' +
			skinCssLinks() +
			'<style>' + printCss( sizeCss, cols ) + '</style>' +
			'</head><body>' + wrap.outerHTML + '</body></html>';
	}

	var state = { overlay: null, viewer: null, srcUrl: null, lastFocus: null,
		busy: false, size: DEFAULT_SIZE, orient: 'portrait', zoom: 1, toc: true,
		page: 0, total: 0, last: false, ready: false };

	/* Vivliostyle (CoreViewer) es un visor PÁGINA-A-PÁGINA: solo dimensiona la
	   hoja actual. Habilitamos la barra en el primer evento `nav` (hoja 1 visible),
	   SIN esperar a `complete` —lo lento no es la maqueta sino cargar todas las
	   imágenes—, así el botón se activa en pocos segundos. El evento `nav` da
	   página actual (epage), total (epageCount) y si es la última (last). La
	   impresión (printHTML) saca TODAS las hojas. */
	function updateNav() {
		var o = state.overlay; if ( !o ) { return; }
		var ind = o.querySelector( '.sn-pp-pageind' );
		var prev = o.querySelector( '.sn-pp-prev' );
		var next = o.querySelector( '.sn-pp-next' );
		if ( ind ) {
			ind.textContent = ( state.ready ? ( state.page + 1 ) : '—' ) + ' / ' +
				( state.total || ( state.ready ? '…' : '—' ) );
		}
		if ( prev ) { prev.disabled = state.busy || !state.ready || state.page <= 0; }
		// El fin lo manda `state.last` (autoritativo); si no, el total estimado.
		if ( next ) {
			next.disabled = state.busy || !state.ready || state.last ||
				( !!state.total && state.page >= state.total - 1 );
		}
	}
	function navTo( i ) {
		if ( !state.viewer || state.busy || !state.ready ) { return; }
		if ( i < 0 || i === state.page ) { return; }
		if ( i > state.page && state.last ) { return; }   // ya en la última
		state.page = i;
		try { state.viewer.navigateToPage( 'epage', i ); } catch ( e ) {}
		updateNav();   // el evento `nav` confirmará/corregirá página, total y last
	}

	/* Aplica el zoom escalando el viewport (propiedad `zoom`: encoge también la
	   caja de layout → el scroll se ajusta). El `zoom:1 !important` del contenedor
	   de Vivliostyle es interno y compone, no lo anula. */
	function applyZoom() {
		var o = state.overlay; if ( !o ) { return; }
		var vp = o.querySelector( '.sn-pp-viewport' );
		if ( vp ) { vp.style.zoom = state.zoom; }
		var ind = o.querySelector( '.sn-pp-zoomind' );
		if ( ind ) { ind.textContent = Math.round( state.zoom * 100 ) + '%'; }
		var zin = o.querySelector( '.sn-pp-zoomin' );
		var zout = o.querySelector( '.sn-pp-zoomout' );
		if ( zin ) { zin.disabled = state.zoom >= ZOOM_MAX; }
		if ( zout ) { zout.disabled = state.zoom <= ZOOM_MIN; }
	}
	function zoomBy( delta ) {
		var z = Math.round( ( state.zoom + delta ) / ZOOM_STEP ) * ZOOM_STEP;
		state.zoom = Math.max( ZOOM_MIN, Math.min( ZOOM_MAX, z ) );
		applyZoom();
	}

	function revokeSrc() {
		if ( state.srcUrl ) { try { URL.revokeObjectURL( state.srcUrl ); } catch ( e ) {} state.srcUrl = null; }
	}

	function teardown() {
		if ( state.viewer ) {
			try { state.viewer.removeListener && state.viewer.removeListener( 'readystatechange' ); } catch ( e ) {}
			state.viewer = null;
		}
		revokeSrc();
		if ( state.overlay ) { state.overlay.remove(); state.overlay = null; }
		root.classList.remove( 'sn-pp-active' );
		doc.removeEventListener( 'keydown', onKey );
		if ( state.lastFocus ) { try { state.lastFocus.focus(); } catch ( e ) {} }
		state.lastFocus = null;
		state.busy = false;
	}

	function onKey( e ) {
		if ( e.key === 'Escape' ) { e.preventDefault(); teardown(); return; }
		if ( e.key === 'ArrowRight' || e.key === 'PageDown' ) { e.preventDefault(); navTo( state.page + 1 ); }
		else if ( e.key === 'ArrowLeft' || e.key === 'PageUp' ) { e.preventDefault(); navTo( state.page - 1 ); }
		else if ( e.key === '+' || e.key === '=' ) { e.preventDefault(); zoomBy( ZOOM_STEP ); }
		else if ( e.key === '-' || e.key === '_' ) { e.preventDefault(); zoomBy( -ZOOM_STEP ); }
	}

	function sizeOptionsHtml() {
		var html = '';
		for ( var i = 0; i < SIZES.length; i++ ) {
			html += '<option value="' + SIZES[ i ].id + '"' +
				( SIZES[ i ].id === state.size ? ' selected' : '' ) + '>' +
				SIZES[ i ].label + '</option>';
		}
		return html;
	}

	/* (Re)maqueta la previsualización con el tamaño/columnas actuales. */
	function render() {
		var overlay = state.overlay;
		if ( !overlay ) { return; }
		var pages = overlay.querySelector( '.sn-pp-pages' );
		var status = overlay.querySelector( '.sn-pp-status' );
		var printBtn = overlay.querySelector( '.sn-pp-print' );
		function setExportEnabled( on ) { printBtn.disabled = !on; }
		var sizeSel = overlay.querySelector( '.sn-pp-size' );
		var ent = sizeEntryById( state.size );

		state.busy = true;
		state.page = 0;
		state.total = 0;
		state.last = false;
		state.ready = false;
		setExportEnabled( false );
		if ( sizeSel ) { sizeSel.disabled = true; }
		overlay.classList.add( 'sn-pp-loading' );   // muestra el spinner
		status.textContent = 'Preparando la vista de impresión…';
		updateNav();

		// viewport limpio + nuevo CoreViewer
		state.viewer = null;
		revokeSrc();
		pages.innerHTML = '<div class="sn-pp-viewport"></div>';
		var viewport = pages.querySelector( '.sn-pp-viewport' );
		viewport.style.zoom = state.zoom;

		var src = buildSourceDoc( pageSize( ent, state.orient ), colsFor( ent, state.orient ) );
		state.srcUrl = URL.createObjectURL( new Blob( [ src ], { type: 'text/html' } ) );

		// La hoja 1 ya está visible: habilita la barra y oculta el spinner. Se
		// llama una sola vez (en el primer `nav`, que llega apenas se muestra la
		// hoja 1, mucho antes que `complete`).
		function markReady() {
			if ( state.ready || viewer !== state.viewer ) { return; }
			state.ready = true;
			state.busy = false;
			setExportEnabled( true );
			if ( sizeSel ) { sizeSel.disabled = false; }
			overlay.classList.remove( 'sn-pp-loading' );
			applyZoom();
			updateNav();
		}
		function showCount() {
			status.textContent = state.total
				? ( state.total + ( state.total === 1 ? ' página' : ' páginas' ) )
				: 'Vista de impresión';
		}

		var viewer = new window.Vivliostyle.CoreViewer(
			{ viewportElement: viewport },
			// renderAllPages:true → pagina todo (TOC con números reales y total
			// exacto), PERO marcamos «listo» en el primer `nav` (hoja 1 visible),
			// sin esperar a `complete`: el botón se activa rápido y la paginación
			// del resto sigue en segundo plano.
			// pageViewMode:'singlePage' → una hoja a la vez. El default de Vivliostyle
			// es 'autoSpread', que en ventana ancha muestra PLIEGOS de 2 páginas
			// (confuso para una previsualización página-a-página con Prev/Next).
			{ renderAllPages: true, pageViewMode: 'singlePage' }
		);
		state.viewer = viewer;
		// `nav`: página actual + total estimado + first/last. Llega apenas se
		// muestra una hoja, así que es nuestra señal de «listo» y de navegación.
		viewer.addListener( 'nav', function ( ev ) {
			if ( viewer !== state.viewer ) { return; }
			if ( ev && typeof ev.epage === 'number' ) { state.page = Math.max( 0, Math.round( ev.epage ) ); }
			if ( ev && typeof ev.epageCount === 'number' && ev.epageCount > 0 ) { state.total = Math.round( ev.epageCount ); }
			if ( ev && typeof ev.last === 'boolean' ) { state.last = ev.last; }
			showCount();
			markReady();
			updateNav();
		} );
		// `complete`: la maqueta perezosa terminó en segundo plano → afinamos el
		// total exacto (no bloquea: la barra ya está usable desde el primer `nav`).
		viewer.addListener( 'readystatechange', function () {
			if ( viewer !== state.viewer ) { return; }
			if ( viewer.readyState !== 'complete' ) { return; }
			var n = 0;
			try { n = viewer.getPageCount ? viewer.getPageCount() : 0; } catch ( e ) {}
			if ( n ) { state.total = n; showCount(); }
			markReady();   // respaldo, por si `nav` no hubiera llegado
			updateNav();
		} );
		viewer.addListener( 'error', function () {
			if ( viewer !== state.viewer ) { return; }
			status.textContent = 'No se pudo preparar la vista. Usa Imprimir del navegador.';
			setExportEnabled( true );
			if ( sizeSel ) { sizeSel.disabled = false; }
			state.busy = false;
			overlay.classList.remove( 'sn-pp-loading' );
		} );
		try { viewer.loadDocument( { url: state.srcUrl } ); }
		catch ( e ) {
			status.textContent = 'No se pudo preparar la vista. Usa Imprimir del navegador.';
			setExportEnabled( true ); if ( sizeSel ) { sizeSel.disabled = false; } state.busy = false;
			overlay.classList.remove( 'sn-pp-loading' );
		}
	}

	/* Imprime / exporta a PDF re-maquetando el MISMO documento fuente en un iframe
	   oculto (printHTML) → salida 1:1 correcta. NOTA: el navegador no puede guardar
	   el PDF sin diálogo (seguridad); el destino «Guardar como PDF» vive dentro del
	   diálogo. En libros largos e ilustrados la paginación tarda (carga de
	   imágenes) — es inherente al render en cliente. */
	function printDocument() {
		var ent = sizeEntryById( state.size );
		var src = buildSourceDoc( pageSize( ent, state.orient ), colsFor( ent, state.orient ) );
		try {
			window.Vivliostyle.printHTML( src, {
				title: ( mw && mw.config && mw.config.get( 'wgTitle' ) ) || document.title
			} );
		} catch ( e ) { window.print(); }
	}

	function open() {
		if ( state.busy || state.overlay ) { return; }
		if ( !window.Vivliostyle || !window.Vivliostyle.CoreViewer ) {
			return false;   // sin motor → el llamador cae al print nativo
		}
		state.lastFocus = doc.activeElement;
		root.classList.add( 'sn-pp-active' );

		var overlay = doc.createElement( 'div' );
		overlay.className = 'sn-printpreview';
		overlay.setAttribute( 'role', 'dialog' );
		overlay.setAttribute( 'aria-label', 'Vista de impresión' );
		overlay.innerHTML =
			'<div class="sn-pp-bar">' +
				'<span class="sn-pp-statuswrap">' +
					'<span class="sn-pp-spinner" aria-hidden="true"></span>' +
					'<span class="sn-pp-status">Preparando la vista de impresión…</span>' +
				'</span>' +
				'<span class="sn-pp-actions">' +
					/* índice */
					'<label class="sn-pp-toclabel">' +
						'<input type="checkbox" class="sn-pp-toc"> Índice' +
					'</label>' +
					/* formato: tamaño + orientación */
					'<label class="sn-pp-sizelabel">Tamaño ' +
						'<select class="sn-pp-size">' + sizeOptionsHtml() + '</select>' +
					'</label>' +
					'<label class="sn-pp-orientlabel">Orientación ' +
						'<select class="sn-pp-orient">' +
							'<option value="portrait">Vertical</option>' +
							'<option value="landscape">Horizontal</option>' +
						'</select>' +
					'</label>' +
					/* páginas: navegación + zoom */
					'<span class="sn-pp-nav">' +
						'<button type="button" class="sn-pp-prev" disabled aria-label="Página anterior">‹</button>' +
						'<span class="sn-pp-pageind">— / —</span>' +
						'<button type="button" class="sn-pp-next" disabled aria-label="Página siguiente">›</button>' +
					'</span>' +
					'<span class="sn-pp-zoom">' +
						'<button type="button" class="sn-pp-zoomout" aria-label="Alejar">−</button>' +
						'<span class="sn-pp-zoomind">100%</span>' +
						'<button type="button" class="sn-pp-zoomin" aria-label="Acercar">+</button>' +
					'</span>' +
					/* botones */
					'<button type="button" class="sn-pp-print" disabled>Imprimir</button>' +
					'<button type="button" class="sn-pp-close">Cerrar</button>' +
				'</span>' +
			'</div>' +
			'<div class="sn-pp-pages"></div>';
		doc.body.appendChild( overlay );
		state.overlay = overlay;

		var printBtn = overlay.querySelector( '.sn-pp-print' );
		var closeBtn = overlay.querySelector( '.sn-pp-close' );
		var sizeSel = overlay.querySelector( '.sn-pp-size' );
		var orientSel = overlay.querySelector( '.sn-pp-orient' );
		var tocChk = overlay.querySelector( '.sn-pp-toc' );

		// Estado inicial del switch «Índice»: marcado si la página trae TOC
		// visible; deshabilitado si no hay TOC del todo.
		state.toc = tocVisibleByDefault();
		tocChk.checked = state.toc;
		tocChk.disabled = !tocClone();
		orientSel.value = state.orient;

		closeBtn.addEventListener( 'click', teardown );
		// «Imprimir» re-maqueta con printHTML y abre el diálogo. El navegador NO
		// puede escribir un PDF sin diálogo (seguridad); en el diálogo, destino
		// «Guardar como PDF» ES la exportación a PDF (no hace falta botón aparte).
		printBtn.addEventListener( 'click', printDocument );
		sizeSel.addEventListener( 'change', function () {
			if ( state.busy ) { return; }
			state.size = sizeSel.value;
			render();
		} );
		orientSel.addEventListener( 'change', function () {
			if ( state.busy ) { return; }
			state.orient = orientSel.value;
			render();
		} );
		tocChk.addEventListener( 'change', function () {
			if ( state.busy ) { return; }
			state.toc = tocChk.checked;
			render();
		} );
		overlay.querySelector( '.sn-pp-prev' ).addEventListener( 'click', function () { navTo( state.page - 1 ); } );
		overlay.querySelector( '.sn-pp-next' ).addEventListener( 'click', function () { navTo( state.page + 1 ); } );
		overlay.querySelector( '.sn-pp-zoomout' ).addEventListener( 'click', function () { zoomBy( -ZOOM_STEP ); } );
		overlay.querySelector( '.sn-pp-zoomin' ).addEventListener( 'click', function () { zoomBy( ZOOM_STEP ); } );
		doc.addEventListener( 'keydown', onKey );
		closeBtn.focus();

		render();
		return true;
	}

	window.SN_PrintPreview = { open: open };
}() );

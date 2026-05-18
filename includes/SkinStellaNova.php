<?php
/**
 * Stella Nova — skin moderno para Casiopea (EAD PUCV).
 * Escrito desde cero: solo extiende SkinMustache (contrato mínimo de MW).
 *
 * @license GPL-2.0-or-later
 */

namespace MediaWiki\Skins\StellaNova;

use SkinMustache;

class SkinStellaNova extends SkinMustache {
	/**
	 * Punto de extensión para inyectar datos propios en la plantilla.
	 * De momento no añade nada; el contrato base de SkinMustache basta.
	 *
	 * @return array
	 */
	public function getTemplateData(): array {
		$data = parent::getTemplateData();
		// Espacio reservado para datos propios de Stella Nova.
		return $data;
	}
}

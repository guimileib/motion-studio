import type {TransitionPresentation} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {zoomPunch} from './zoomPunch';
import {whipPan} from './whipPan';
import {irisOrigem} from './irisOrigem';
import {faixas} from './faixas';
import {dipCor} from './dipCor';
import {lumaWipe} from './lumaWipe';

export {zoomPunch, whipPan, irisOrigem, faixas, dipCor, lumaWipe};
export {ChuvaDeObjetos} from './ChuvaDeObjetos';
export {frutasSvg, CORES_PADRAO} from './frutas';

/** Ids do catálogo (skill transicoes-motion) usados em roteiro.json → cenas[].transicao_saida.tipo */
export type TipoTransicao =
	| 'corte' | 'j-cut' | 'l-cut' | 'match-cut' | 'whip-pan' | 'zoom-punch' | 'zoom-through'
	| 'dissolve' | 'dip-cor' | 'push' | 'wipe' | 'object-wipe' | 'iris' | 'shape-morph'
	| 'luma-wipe' | 'faixas' | 'texto-empurra' | 'desfoque' | 'glitch';

export type TransicaoSaida = {
	tipo?: TipoTransicao;
	duracao_s?: number;
	direcao?: string;
	cor?: string;
	origemX?: number;
	origemY?: number;
};

/** Duração padrão (s) quando o roteiro não informa. */
export const DURACAO_PADRAO: Record<string, number> = {
	'whip-pan': 0.27, 'zoom-punch': 0.3, 'zoom-through': 0.55, dissolve: 0.5, 'dip-cor': 0.45,
	push: 0.4, wipe: 0.45, 'object-wipe': 0.8, iris: 0.5, 'luma-wipe': 0.55, faixas: 0.55, desfoque: 0.5,
};

type Qualquer = TransitionPresentation<Record<string, unknown>>;

/**
 * Converte a transição do roteiro numa presentation do Remotion.
 * Devolve null para cortes (corte, j-cut, l-cut, match-cut) e para object-wipe, que é um Overlay.
 */
export const presentationDoRoteiro = (t: TransicaoSaida | undefined, corDaMarca = '#7BD13A'): Qualquer | null => {
	const dir = t?.direcao ?? '';
	switch (t?.tipo) {
		case 'whip-pan':
			return whipPan({direcao: (['esquerda', 'direita', 'cima', 'baixo'].includes(dir) ? dir : 'esquerda') as 'esquerda'}) as Qualquer;
		case 'zoom-punch':
			return zoomPunch({escala: 0.4}) as Qualquer;
		case 'zoom-through':
			return zoomPunch({escala: 4, desfoque: 8}) as Qualquer;
		case 'dissolve':
		case 'desfoque':
			return fade() as Qualquer;
		case 'dip-cor':
			return dipCor({cor: t.cor ?? '#0E2A22'}) as Qualquer;
		case 'push':
			return slide({direction: dir === 'de-baixo' ? 'from-bottom' : dir === 'de-cima' ? 'from-top' : dir === 'da-esquerda' ? 'from-left' : 'from-right'}) as Qualquer;
		case 'wipe':
			return wipe() as Qualquer;
		case 'iris':
			return irisOrigem({origemX: t.origemX ?? 0.5, origemY: t.origemY ?? 0.5}) as Qualquer;
		case 'luma-wipe':
			return lumaWipe() as Qualquer;
		case 'faixas':
			return faixas({cor: t.cor ?? corDaMarca}) as Qualquer;
		default:
			return null;
	}
};

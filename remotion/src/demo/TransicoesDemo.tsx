import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {TransitionSeries, linearTiming, springTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {ChuvaDeObjetos, dipCor, faixas, irisOrigem, lumaWipe, whipPan, zoomPunch} from '../transicoes';

// Vitrine de todas as transições: cada cena mostra o nome da transição que vem DEPOIS dela.
const CORES = ['#0E2A22', '#14532D', '#1E3A5F', '#4A1D3F', '#5B3A12', '#0F3D3E', '#2E2A5A', '#3B1F1F', '#123524'];

const Cena: React.FC<{titulo: string; sub: string; i: number}> = ({titulo, sub, i}) => {
	const f = useCurrentFrame();
	return (
		<AbsoluteFill style={{background: CORES[i % CORES.length], justifyContent: 'center', alignItems: 'center', color: '#EAF5E6', fontFamily: 'system-ui, sans-serif'}}>
			<div style={{fontSize: 110, fontWeight: 800, transform: `translateY(${interpolate(f, [0, 12], [30, 0], {extrapolateRight: 'clamp'})}px)`, opacity: interpolate(f, [0, 10], [0, 1], {extrapolateRight: 'clamp'})}}>{titulo}</div>
			<div style={{fontSize: 44, marginTop: 24, opacity: 0.8}}>{sub}</div>
		</AbsoluteFill>
	);
};

const D = 60; // frames de cada cena

export const TransicoesDemo: React.FC = () => (
	<TransitionSeries>
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={0} titulo="Zoom punch" sub="a seguir: zoomPunch()" /></TransitionSeries.Sequence>
		<TransitionSeries.Transition presentation={zoomPunch()} timing={linearTiming({durationInFrames: 9})} />
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={1} titulo="Whip pan" sub="a seguir: whipPan()" /></TransitionSeries.Sequence>
		<TransitionSeries.Transition presentation={whipPan({direcao: 'esquerda'})} timing={linearTiming({durationInFrames: 10})} />
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={2} titulo="Íris" sub="a seguir: irisOrigem()" /></TransitionSeries.Sequence>
		<TransitionSeries.Transition presentation={irisOrigem({origemX: 0.5, origemY: 0.6})} timing={springTiming({config: {damping: 200}, durationInFrames: 16})} />
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={3} titulo="Faixas" sub="a seguir: faixas()" /></TransitionSeries.Sequence>
		<TransitionSeries.Transition presentation={faixas({cor: '#7BD13A'})} timing={linearTiming({durationInFrames: 18})} />
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={4} titulo="Luma wipe" sub="a seguir: lumaWipe()" /></TransitionSeries.Sequence>
		<TransitionSeries.Transition presentation={lumaWipe()} timing={linearTiming({durationInFrames: 18})} />
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={5} titulo="Dip na cor" sub="a seguir: dipCor()" /></TransitionSeries.Sequence>
		<TransitionSeries.Transition presentation={dipCor({cor: '#7BD13A'})} timing={linearTiming({durationInFrames: 14})} />
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={6} titulo="Push" sub="a seguir: slide() nativo" /></TransitionSeries.Sequence>
		<TransitionSeries.Transition presentation={slide({direction: 'from-right'})} timing={springTiming({config: {damping: 200}, durationInFrames: 12})} />
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={7} titulo="Object wipe" sub="a seguir: ChuvaDeObjetos (Overlay)" /></TransitionSeries.Sequence>
		<TransitionSeries.Overlay durationInFrames={24}>
			<ChuvaDeObjetos duracao={24} semente={11} />
		</TransitionSeries.Overlay>
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={8} titulo="Dissolve" sub="a seguir: fade() nativo" /></TransitionSeries.Sequence>
		<TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: 15})} />
		<TransitionSeries.Sequence durationInFrames={D}><Cena i={0} titulo="Fim" sub="motion-studio" /></TransitionSeries.Sequence>
	</TransitionSeries>
);

// 10 cenas de 60 − transições (9+8+16+18+18+14+12+15) = 490 frames (o Overlay não encurta)
export const DURACAO_TRANSICOES_DEMO = 10 * D - (9 + 10 + 16 + 18 + 18 + 14 + 12 + 15);

/** Só a chuva, com fundo transparente: exporte em ProRes 4444 para usar como overlay no CapCut. */
export const ObjetosCaindo: React.FC<{semente?: number}> = ({semente = 11}) => <ChuvaDeObjetos duracao={30} semente={semente} />;

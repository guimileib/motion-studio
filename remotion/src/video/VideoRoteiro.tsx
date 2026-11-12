import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig, type CalculateMetadataFunction} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import type {Caption} from '@remotion/captions';
import {ChuvaDeObjetos, DURACAO_PADRAO, presentationDoRoteiro, type TransicaoSaida} from '../transicoes';
import {LegendaReels} from '../legendas/LegendaReels';

export type CenaRoteiro = {
	id: string;
	duracao_s: number;
	texto_tela?: string;
	transicao_saida?: TransicaoSaida;
};

export type VideoRoteiroProps = {
	roteiro: {titulo: string; formato: {largura: number; altura: number; fps: number}; cenas: CenaRoteiro[]};
	/** Pasta dentro de remotion/public, ex.: "projetos/meu-video" (preenchida por montar_remotion.py). */
	base: string;
	/** Mídia escolhida por cena: caminho relativo a `base`. */
	midias: Record<string, {arquivo: string; tipo: 'video' | 'foto'}>;
	narracao: string | null;
	legendas: Caption[] | null;
	cores: {fundo: string; texto: string; destaque: string};
	fonte?: string;
};

const framesDe = (s: number, fps: number) => Math.round(s * fps);
const duracaoTransicao = (t: TransicaoSaida | undefined) => t?.duracao_s ?? DURACAO_PADRAO[t?.tipo ?? ''] ?? 0;

const TextoTela: React.FC<{texto: string; cor: string; fonte: string}> = ({texto, cor, fonte}) => {
	const f = useCurrentFrame();
	const palavras = texto.split(' ');
	return (
		<div style={{position: 'absolute', left: 90, right: 90, top: 300, fontFamily: fonte, fontSize: 96, fontWeight: 800, lineHeight: 1.05, color: cor, textShadow: '0 6px 24px rgba(0,0,0,.45)'}}>
			{palavras.map((p, i) => {
				const a = interpolate(f, [4 + i * 3, 4 + i * 3 + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
				return (
					<span key={i} style={{display: 'inline-block', opacity: a, transform: `translateX(${(1 - a) * 28}px)`, marginRight: '0.25em'}}>
						{p}
					</span>
				);
			})}
		</div>
	);
};

const Cena: React.FC<{cena: CenaRoteiro; props: VideoRoteiroProps}> = ({cena, props}) => {
	const f = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	const m = props.midias[cena.id];
	const fonte = props.fonte ?? 'system-ui, sans-serif';
	// Ken Burns leve em foto; vídeo só um zoom sutil para nunca ficar parado
	const zoom = interpolate(f, [0, durationInFrames], [1, m?.tipo === 'foto' ? 1.07 : 1.03]);
	return (
		<AbsoluteFill style={{background: props.cores.fundo}}>
			{m ? (
				<AbsoluteFill style={{transform: `scale(${zoom})`}}>
					{m.tipo === 'video' ? (
						<OffthreadVideo src={staticFile(`${props.base}/${m.arquivo}`)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
					) : (
						<Img src={staticFile(`${props.base}/${m.arquivo}`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
					)}
				</AbsoluteFill>
			) : null}
			<AbsoluteFill style={{background: `linear-gradient(180deg, ${props.cores.fundo}E6 0%, ${props.cores.fundo}33 45%, ${props.cores.fundo}99 100%)`}} />
			{cena.texto_tela ? <TextoTela texto={cena.texto_tela} cor={props.cores.texto} fonte={fonte} /> : null}
		</AbsoluteFill>
	);
};

/**
 * Monta o vídeo a partir do roteiro.json: mídia de fundo, texto na tela, transições do catálogo,
 * narração e legendas animadas. Cada cena é esticada pela duração da sua transição de saída, para que
 * os cortes caiam nos tempos do roteiro (e a narração continue sincronizada).
 */
export const VideoRoteiro: React.FC<VideoRoteiroProps> = (props) => {
	const {fps} = useVideoConfig();
	const {cenas} = props.roteiro;
	const itens: React.ReactNode[] = [];
	cenas.forEach((cena, i) => {
		const ultima = i === cenas.length - 1;
		const pres = ultima ? null : presentationDoRoteiro(cena.transicao_saida, props.cores.destaque);
		const tr = pres ? framesDe(duracaoTransicao(cena.transicao_saida), fps) : 0;
		itens.push(
			<TransitionSeries.Sequence key={`s-${cena.id}`} durationInFrames={framesDe(cena.duracao_s, fps) + tr}>
				<Cena cena={cena} props={props} />
			</TransitionSeries.Sequence>,
		);
		if (ultima) return;
		if (pres && tr > 0) {
			itens.push(<TransitionSeries.Transition key={`t-${cena.id}`} presentation={pres} timing={linearTiming({durationInFrames: tr})} />);
		} else if (cena.transicao_saida?.tipo === 'object-wipe') {
			const d = framesDe(duracaoTransicao(cena.transicao_saida), fps);
			itens.push(
				<TransitionSeries.Overlay key={`o-${cena.id}`} durationInFrames={d}>
					<ChuvaDeObjetos duracao={d} semente={i * 13 + 5} />
				</TransitionSeries.Overlay>,
			);
		}
	});

	return (
		<AbsoluteFill style={{background: props.cores.fundo}}>
			<TransitionSeries>{itens}</TransitionSeries>
			{props.narracao ? <Audio src={staticFile(`${props.base}/${props.narracao}`)} /> : null}
			{props.legendas ? <LegendaReels legendas={props.legendas} corDestaque={props.cores.destaque} corTexto={props.cores.texto} fonte={props.fonte} /> : null}
		</AbsoluteFill>
	);
};

export const calcularMetadados: CalculateMetadataFunction<VideoRoteiroProps> = ({props}) => {
	const {fps, largura, altura} = props.roteiro.formato;
	const total = props.roteiro.cenas.reduce((s, c) => s + framesDe(c.duracao_s, fps), 0);
	return {durationInFrames: Math.max(1, total), fps, width: largura, height: altura};
};

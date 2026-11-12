import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import type {TransitionPresentation, TransitionPresentationComponentProps} from '@remotion/transitions';
import {clamp01, metade} from './util';

export type FaixasProps = {
	quantidade?: number;
	/** Cor das faixas (use a cor principal ou de destaque da marca). */
	cor?: string;
	/** Sentido em que as faixas varrem a tela. */
	direcao?: 'horizontal' | 'vertical';
	/** Fração do tempo de cada metade usada para escalonar as faixas (0–0,6). */
	escalonamento?: number;
};

const Faixas: React.FC<TransitionPresentationComponentProps<FaixasProps>> = ({
	children,
	presentationDirection,
	presentationProgress,
	passedProps,
}) => {
	const n = passedProps.quantidade ?? 7;
	const cor = passedProps.cor ?? '#7BD13A';
	const horizontal = (passedProps.direcao ?? 'horizontal') === 'horizontal';
	const esc = passedProps.escalonamento ?? 0.35;
	const {q, visivel} = metade(presentationProgress, presentationDirection);
	const cobrindo = presentationDirection === 'exiting';

	const barras = Array.from({length: n}, (_, i) => {
		const atraso = (i / Math.max(1, n - 1)) * esc;
		const local = Easing.inOut(Easing.cubic)(clamp01((q - atraso) / (1 - esc)));
		// cobrindo: cresce a partir do início; descobrindo: encolhe em direção ao fim (mesmo sentido)
		const escala = cobrindo ? local : 1 - local;
		const origem = cobrindo ? '0% 50%' : '100% 50%';
		const tamanho = 100 / n;
		const base: React.CSSProperties = horizontal
			? {top: `${i * tamanho}%`, height: `${tamanho + 0.2}%`, left: 0, width: '100%', transform: `scaleX(${escala})`, transformOrigin: origem}
			: {left: `${i * tamanho}%`, width: `${tamanho + 0.2}%`, top: 0, height: '100%', transform: `scaleY(${escala})`, transformOrigin: cobrindo ? '50% 0%' : '50% 100%'};
		return <div key={i} style={{position: 'absolute', background: cor, ...base}} />;
	});

	return (
		<AbsoluteFill>
			<AbsoluteFill style={{opacity: visivel ? 1 : 0}}>{children}</AbsoluteFill>
			{visivel ? barras : null}
		</AbsoluteFill>
	);
};

/** faixas (stripes). Duração recomendada: 14–20 frames a 30 fps. */
export const faixas = (props: FaixasProps = {}): TransitionPresentation<FaixasProps> => ({
	component: Faixas,
	props,
});

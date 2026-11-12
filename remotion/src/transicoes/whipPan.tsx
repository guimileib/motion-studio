import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import type {TransitionPresentation, TransitionPresentationComponentProps} from '@remotion/transitions';

export type WhipPanProps = {
	/** Para onde a câmera "chicoteia". A cena nova entra do lado oposto. */
	direcao?: 'esquerda' | 'direita' | 'cima' | 'baixo';
	/** Desfoque de movimento máximo em px. */
	desfoque?: number;
};

const WhipPan: React.FC<TransitionPresentationComponentProps<WhipPanProps>> = ({
	children,
	presentationDirection,
	presentationProgress,
	passedProps,
}) => {
	const dir = passedProps.direcao ?? 'esquerda';
	const blur = passedProps.desfoque ?? 22;
	const horizontal = dir === 'esquerda' || dir === 'direita';
	const sinal = dir === 'esquerda' || dir === 'cima' ? -1 : 1;
	// As duas cenas andam juntas, encostadas, com a mesma curva: sem quadro vazio no meio.
	// Curva bem "chicote": quase parada nas pontas, muito rápida no meio.
	const e = Easing.inOut(Easing.poly(4))(presentationProgress);
	const deslocamento = presentationDirection === 'exiting' ? sinal * 100 * e : sinal * 100 * (e - 1);
	const velocidade = Math.sin(Math.PI * presentationProgress) ** 2; // máximo no meio
	const t = horizontal ? `translateX(${deslocamento}%)` : `translateY(${deslocamento}%)`;
	const estica = horizontal ? `scaleX(${1 + 0.06 * velocidade})` : `scaleY(${1 + 0.06 * velocidade})`;
	const filtro = `blur(${blur * velocidade}px)`;

	return <AbsoluteFill style={{transform: `${t} ${estica}`, filter: filtro}}>{children}</AbsoluteFill>;
};

/** whip-pan. Duração recomendada: 8–12 frames a 30 fps. Som: whoosh com pico no meio. */
export const whipPan = (props: WhipPanProps = {}): TransitionPresentation<WhipPanProps> => ({
	component: WhipPan,
	props,
});

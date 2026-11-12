import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import type {TransitionPresentation, TransitionPresentationComponentProps} from '@remotion/transitions';

export type IrisOrigemProps = {
	/** Centro da íris, de 0 a 1 (fração da largura). Use a posição do botão/logo/produto da cena que sai. */
	origemX?: number;
	/** Centro da íris, de 0 a 1 (fração da altura). */
	origemY?: number;
};

const IrisOrigem: React.FC<TransitionPresentationComponentProps<IrisOrigemProps>> = ({
	children,
	presentationDirection,
	presentationProgress,
	passedProps,
}) => {
	if (presentationDirection === 'exiting') return <AbsoluteFill>{children}</AbsoluteFill>;
	const x = (passedProps.origemX ?? 0.5) * 100;
	const y = (passedProps.origemY ?? 0.5) * 100;
	// 150% do lado de referência garante cobrir a tela inteira a partir de qualquer ponto
	const raio = 150 * Easing.inOut(Easing.cubic)(presentationProgress);
	return <AbsoluteFill style={{clipPath: `circle(${raio}% at ${x}% ${y}%)`}}>{children}</AbsoluteFill>;
};

/** iris a partir de um ponto. Duração recomendada: 12–18 frames a 30 fps. */
export const irisOrigem = (props: IrisOrigemProps = {}): TransitionPresentation<IrisOrigemProps> => ({
	component: IrisOrigem,
	props,
});

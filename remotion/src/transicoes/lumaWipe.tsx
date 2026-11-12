import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import type {TransitionPresentation, TransitionPresentationComponentProps} from '@remotion/transitions';

export type LumaWipeProps = {
	/** Ângulo do gradiente em graus (90 = da esquerda para a direita). */
	angulo?: number;
	/** Largura da borda suave, de 0 a 1. */
	suavidade?: number;
};

const LumaWipe: React.FC<TransitionPresentationComponentProps<LumaWipeProps>> = ({
	children,
	presentationDirection,
	presentationProgress,
	passedProps,
}) => {
	if (presentationDirection === 'exiting') return <AbsoluteFill>{children}</AbsoluteFill>;
	const ang = passedProps.angulo ?? 120;
	const s = (passedProps.suavidade ?? 0.25) * 100;
	// a frente do gradiente vai de -s% a 100%: começa invisível e termina cobrindo tudo
	const frente = -s + (100 + s) * Easing.inOut(Easing.cubic)(presentationProgress);
	const mascara = `linear-gradient(${ang}deg, #000 ${frente}%, transparent ${frente + s}%)`;
	return <AbsoluteFill style={{maskImage: mascara, WebkitMaskImage: mascara}}>{children}</AbsoluteFill>;
};

/** luma-wipe. Duração recomendada: 14–20 frames a 30 fps. */
export const lumaWipe = (props: LumaWipeProps = {}): TransitionPresentation<LumaWipeProps> => ({
	component: LumaWipe,
	props,
});

import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import type {TransitionPresentation, TransitionPresentationComponentProps} from '@remotion/transitions';
import {metade} from './util';

export type ZoomPunchProps = {
	/** Quanto a cena que sai cresce (0,4 = 140%). Use 2–6 para zoom-through. */
	escala?: number;
	/** Desfoque máximo em px. */
	desfoque?: number;
};

const ZoomPunch: React.FC<TransitionPresentationComponentProps<ZoomPunchProps>> = ({
	children,
	presentationDirection,
	presentationProgress,
	passedProps,
}) => {
	const escala = passedProps.escala ?? 0.4;
	const blur = passedProps.desfoque ?? 14;
	const {q, visivel} = metade(presentationProgress, presentationDirection);

	let style: React.CSSProperties;
	if (presentationDirection === 'exiting') {
		const e = Easing.in(Easing.cubic)(q);
		style = {transform: `scale(${1 + escala * e})`, filter: `blur(${blur * e}px)`};
	} else {
		// entra menor, passa um pouco de 100% e assenta (overshoot)
		const e = Easing.out(Easing.back(1.7))(q);
		style = {transform: `scale(${0.85 + 0.15 * e})`, filter: `blur(${blur * (1 - Math.min(1, q * 1.6))}px)`};
	}
	return <AbsoluteFill style={{...style, opacity: visivel ? 1 : 0}}>{children}</AbsoluteFill>;
};

/** zoom-punch / zoom-through. Duração recomendada: 6–10 frames a 30 fps (zoom-through: 12–20). */
export const zoomPunch = (props: ZoomPunchProps = {}): TransitionPresentation<ZoomPunchProps> => ({
	component: ZoomPunch,
	props,
});

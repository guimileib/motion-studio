import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import type {TransitionPresentation, TransitionPresentationComponentProps} from '@remotion/transitions';
import {metade} from './util';

export type DipCorProps = {
	/** Cor do mergulho: fundo ou destaque da marca (evite preto puro). */
	cor?: string;
};

const DipCor: React.FC<TransitionPresentationComponentProps<DipCorProps>> = ({
	children,
	presentationDirection,
	presentationProgress,
	passedProps,
}) => {
	const {q, visivel} = metade(presentationProgress, presentationDirection);
	const e = Easing.inOut(Easing.quad)(q);
	const opacidadeCor = presentationDirection === 'exiting' ? e : 1 - e;
	return (
		<AbsoluteFill style={{opacity: visivel ? 1 : 0}}>
			{children}
			<AbsoluteFill style={{background: passedProps.cor ?? '#0E2A22', opacity: opacidadeCor}} />
		</AbsoluteFill>
	);
};

/** dip-cor. Duração recomendada: 10–16 frames a 30 fps. */
export const dipCor = (props: DipCorProps = {}): TransitionPresentation<DipCorProps> => ({
	component: DipCor,
	props,
});

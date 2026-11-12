import React, {useMemo} from 'react';
import {AbsoluteFill, Easing, Img, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {frutasSvg} from './frutas';

export type ChuvaDeObjetosProps = {
	/** Duração do overlay em frames (a mesma do TransitionSeries.Overlay). */
	duracao: number;
	/** URLs das imagens (staticFile(...) ou data URI). Padrão: frutas. */
	objetos?: string[];
	quantidade?: number;
	semente?: number;
	/** [mínimo, máximo] do tamanho de cada objeto, em fração da largura da tela. */
	tamanho?: [number, number];
	/** Cor sólida que aparece por baixo dos objetos no meio, para garantir cobertura total. */
	cobertura?: string;
};

/**
 * object-wipe: objetos caindo do céu que cobrem a tela no meio da passagem.
 * Use como <TransitionSeries.Overlay durationInFrames={24}> entre duas cenas: o overlay fica
 * centralizado no corte e não encurta o vídeo. Também serve sozinho (fundo transparente) para
 * exportar em ProRes 4444 e usar no CapCut.
 */
export const ChuvaDeObjetos: React.FC<ChuvaDeObjetosProps> = ({
	duracao,
	objetos,
	quantidade = 34,
	semente = 7,
	tamanho = [0.2, 0.34],
	cobertura,
}) => {
	const frame = useCurrentFrame();
	const {width, height} = useVideoConfig();
	const imgs = useMemo(() => objetos ?? frutasSvg(), [objetos]);

	const itens = useMemo(
		() =>
			Array.from({length: quantidade}, (_, i) => {
				const r = (k: string) => random(`${semente}-${i}-${k}`);
				const s = (tamanho[0] + r('s') * (tamanho[1] - tamanho[0])) * width;
				return {
					s,
					src: imgs[Math.floor(r('o') * imgs.length)],
					// espalha por faixas em toda a largura e só depois aleatoriza: cobertura garantida
					x: (i / quantidade) * (width + 0.15 * width) - 0.15 * width + (r('x') - 0.5) * 0.13 * width,
					atraso: r('d') * 0.3,
					queda: 0.55 + r('f') * 0.15,
					rot0: (r('r') - 0.5) * 90,
					giro: (r('g') - 0.5) * 260,
				};
			}),
		[quantidade, semente, tamanho, width, imgs],
	);

	const p = frame / Math.max(1, duracao - 1);
	const cob = cobertura ? Math.max(0, 1 - Math.abs(p - 0.5) / 0.08) : 0;

	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{cob > 0 ? <AbsoluteFill style={{background: cobertura, opacity: cob}} /> : null}
			{itens.map((it, i) => {
				const q = (p - it.atraso) / it.queda;
				if (q <= 0 || q >= 1) return null;
				// gravidade leve: no meio da passagem os objetos estão espalhados pela altura toda
				const y = -it.s - 40 + (height + it.s + 80) * (Easing.in(Easing.cubic)(q) * 0.35 + q * 0.65);
				return (
					<Img
						key={i}
						src={it.src}
						style={{
							position: 'absolute',
							left: 0,
							top: 0,
							width: it.s,
							height: it.s,
							transform: `translate(${it.x}px, ${y}px) rotate(${it.rot0 + it.giro * q}deg)`,
						}}
					/>
				);
			})}
		</AbsoluteFill>
	);
};

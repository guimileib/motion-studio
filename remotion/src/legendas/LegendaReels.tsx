import React, {useMemo} from 'react';
import {AbsoluteFill, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {createTikTokStyleCaptions, type Caption, type TikTokPage} from '@remotion/captions';

export type LegendaReelsProps = {
	/** Palavras com tempo (saída de legendas-tts: legendas/palavras.json). */
	legendas: Caption[];
	/** Junta palavras numa mesma "página" dentro desta janela. 600–1000 = estilo Reels. */
	combinarMs?: number;
	/** Pausa (ms) que força uma página nova. */
	quebraNaPausaMs?: number;
	corTexto?: string;
	corDestaque?: string;
	fonte?: string;
	tamanho?: number;
	/** Altura do centro da legenda, de 0 a 1. 0,66 fica acima da zona coberta pela interface do Reels. */
	posicaoY?: number;
	/** Largura máxima em px. */
	largura?: number;
	/** Palavras-chave (sem pontuação, sem caixa) → cor própria. Ganham um "pop" ao serem faladas e ficam na cor depois. */
	palavrasChave?: Record<string, string>;
	/** Sombra e contorno escuros (bom sobre fundo escuro ou vídeo). Desligue em fundo claro. */
	sombra?: boolean;
};

const chave = (texto: string) => texto.trim().toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');

const Pagina: React.FC<{pagina: TikTokPage} & Required<Omit<LegendaReelsProps, 'legendas' | 'combinarMs' | 'quebraNaPausaMs'>>> = ({
	pagina,
	sombra,
	palavrasChave,
	corTexto,
	corDestaque,
	fonte,
	tamanho,
	posicaoY,
	largura,
}) => {
	const frame = useCurrentFrame();
	const {fps, height} = useVideoConfig();
	const agoraMs = pagina.startMs + (frame / fps) * 1000;
	const entrada = spring({frame, fps, config: {damping: 14, stiffness: 180}, durationInFrames: 8});

	return (
		<AbsoluteFill style={{alignItems: 'center'}}>
			<div
				style={{
					position: 'absolute',
					top: height * posicaoY,
					transform: `translateY(-50%) scale(${interpolate(entrada, [0, 1], [0.9, 1])})`,
					maxWidth: largura,
					textAlign: 'center',
					fontFamily: fonte,
					fontSize: tamanho,
					fontWeight: 800,
					lineHeight: 1.12,
					color: corTexto,
					whiteSpace: 'pre-wrap',
					textShadow: sombra ? '0 4px 14px rgba(0,0,0,.55)' : 'none',
					WebkitTextStroke: sombra ? '2px rgba(0,0,0,.35)' : '0',
				}}
			>
				{pagina.tokens.map((tk, i) => {
					const ativo = agoraMs >= tk.fromMs && agoraMs < tk.toMs;
					// o espaço fica fora do inline-block (que pode engolir o espaço inicial)
					const espaco = /^\s/.test(tk.text) ? ' ' : '';
					const corChave = palavrasChave[chave(tk.text)];
					// pop da palavra-chave: mola que começa quando ela é falada
					const pop = corChave
						? spring({frame: frame - Math.round(((tk.fromMs - pagina.startMs) / 1000) * fps), fps, config: {damping: 9, stiffness: 220}, durationInFrames: 14})
						: 0;
					const escala = corChave ? interpolate(pop, [0, 1], [1, 1.18]) : ativo ? 1.05 : 1;
					return (
						<React.Fragment key={i}>
							{espaco}
							<span
								style={{
									color: corChave && agoraMs >= tk.fromMs ? corChave : ativo ? corDestaque : corTexto,
									display: 'inline-block',
									// folga lateral fixa: o destaque cresce sem "comer" o espaço entre as palavras
									// palavra-chave cresce 18%: a folga acompanha o comprimento da palavra
								padding: corChave ? `0 ${Math.max(0.2, 0.06 * tk.text.trim().length).toFixed(2)}em` : '0 0.07em',
									transform: `scale(${escala}) rotate(${corChave ? interpolate(pop, [0, 0.5, 1], [0, -4, -2]) : 0}deg)`,
								}}
							>
								{tk.text.trim()}
							</span>
						</React.Fragment>
					);
				})}
			</div>
		</AbsoluteFill>
	);
};

/** Legenda animada estilo Reels/TikTok: páginas curtas com a palavra falada em destaque. */
export const LegendaReels: React.FC<LegendaReelsProps> = ({
	legendas,
	combinarMs = 800,
	quebraNaPausaMs = 350,
	corTexto = '#FFFFFF',
	corDestaque = '#7BD13A',
	fonte = 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
	tamanho = 72,
	posicaoY = 0.66,
	largura = 900,
	palavrasChave = {},
	sombra = true,
}) => {
	const {fps} = useVideoConfig();
	const {pages} = useMemo(
		() => createTikTokStyleCaptions({captions: legendas, combineTokensWithinMilliseconds: combinarMs, breakOnSilenceAfterMilliseconds: quebraNaPausaMs}),
		[legendas, combinarMs, quebraNaPausaMs],
	);

	return (
		<AbsoluteFill>
			{pages.map((pagina, i) => {
				const proxima = pages[i + 1];
				const fimMs = proxima ? Math.min(proxima.startMs, pagina.startMs + pagina.durationMs + 400) : pagina.startMs + pagina.durationMs + 400;
				const de = Math.round((pagina.startMs / 1000) * fps);
				const dur = Math.max(1, Math.round(((fimMs - pagina.startMs) / 1000) * fps));
				return (
					<Sequence key={i} from={de} durationInFrames={dur} layout="none">
						<Pagina pagina={pagina} sombra={sombra} palavrasChave={palavrasChave} corTexto={corTexto} corDestaque={corDestaque} fonte={fonte} tamanho={tamanho} posicaoY={posicaoY} largura={largura} />
					</Sequence>
				);
			})}
		</AbsoluteFill>
	);
};

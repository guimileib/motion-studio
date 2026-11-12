import React from 'react';
import {AbsoluteFill, Composition} from 'remotion';
import type {Caption} from '@remotion/captions';
import {DURACAO_TRANSICOES_DEMO, ObjetosCaindo, TransicoesDemo} from './demo/TransicoesDemo';
import {LegendaReels} from './legendas/LegendaReels';
import {VideoRoteiro, calcularMetadados, type VideoRoteiroProps} from './video/VideoRoteiro';
import roteiroExemplo from '../../projetos/exemplo-veta-pedido-certo/roteiro.json';
import legendasExemplo from './demo/legendas-exemplo.json';

// Projetos pessoais (fora do git): cada remotion/src/projetos/<pasta>/composicoes.tsx exporta `Composicoes`.
const projetos = require.context('./projetos', true, /composicoes\.tsx$/);
const ComposicoesProjetos = projetos.keys().map((k) => ({k, C: projetos<{Composicoes: React.FC}>(k).Composicoes}));

const W = 1080;
const H = 1920;
const FPS = 30;

const propsExemplo: VideoRoteiroProps = {
	roteiro: roteiroExemplo as unknown as VideoRoteiroProps['roteiro'],
	base: '',
	midias: {},
	narracao: null,
	legendas: legendasExemplo as Caption[],
	cores: {fundo: '#0E2A22', texto: '#EAF5E6', destaque: '#7BD13A'},
};

const LegendasDemo: React.FC = () => (
	<AbsoluteFill style={{background: '#0E2A22'}}>
		<LegendaReels legendas={legendasExemplo as Caption[]} />
	</AbsoluteFill>
);

export const Root: React.FC = () => (
	<>
		<Composition id="TransicoesDemo" component={TransicoesDemo} durationInFrames={DURACAO_TRANSICOES_DEMO} fps={FPS} width={W} height={H} />
		<Composition id="ObjetosCaindo" component={ObjetosCaindo} durationInFrames={30} fps={FPS} width={W} height={H} defaultProps={{semente: 11}} />
		<Composition id="LegendasDemo" component={LegendasDemo} durationInFrames={Math.ceil(23.02 * FPS)} fps={FPS} width={W} height={H} />
		<Composition
			id="VideoRoteiro"
			component={VideoRoteiro}
			durationInFrames={1}
			fps={FPS}
			width={W}
			height={H}
			defaultProps={propsExemplo}
			calculateMetadata={calcularMetadados}
		/>
		{ComposicoesProjetos.map(({k, C}) => (
			<C key={k} />
		))}
	</>
);

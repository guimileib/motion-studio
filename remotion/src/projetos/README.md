# Composições de projetos pessoais

Esta pasta fica fora do git (veja `.gitignore`); só este README é versionado.

Cada projeto é uma subpasta com um `composicoes.tsx` que exporta `Composicoes`:

```tsx
import React from 'react';
import {Composition} from 'remotion';
import {MeuVideo, DURACAO} from './MeuVideo';

export const Composicoes: React.FC = () => (
	<Composition id="MeuVideo" component={MeuVideo} durationInFrames={DURACAO} fps={30} width={1080} height={1920} />
);
```

O `Root.tsx` encontra esses arquivos sozinho (`require.context`). Sem nenhum projeto, o Studio abre só
com as composições de exemplo; um clone limpo do repositório continua compilando.

Assets do projeto (logo, áudio) vão em `remotion/public/projetos/<slug>/` ou `remotion/public/<marca>/`,
também fora do git.

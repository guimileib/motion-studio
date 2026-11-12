---
name: estilos-motion
description: Escolhe e aplica o estilo visual de motion de cada vídeo (estilos da casa — flat da marca, linha contínua, bola única, risografia em stop motion, códice renascentista, tinta na água —, estilos das skills bang-motion, vox-director, vox-explainer, huashu-art-motion e claude-drawing, ou um estilo criado do zero), define se os movimentos da biblioteca motion-prompt são escolhidos pelo Claude ou pelo usuário na galeria, e conduz o fluxo storyboard → aprovação → build → folha de contatos → render. Use SEMPRE que o usuário passar um roteiro em .json (um vídeo ou uma série) para produzir, pedir "estilo de motion", "qual visual", "outro estilo", "storyboard", ou quiser variar o visual entre vídeos. Antes de montar qualquer projeto, abra a página de escolha de estilo e pergunte.
---

# Estilos de motion

Base: tutorial "Claude motion videos, step by step" (@janustiu, PDF `styles-claude-motion.pdf` na raiz,
fora do git), adaptado ao pipeline deste repositório: Reels de 30–60 s **com narração e legenda queimada**,
montados no **Remotion** (cada quadro é função pura do frame, igual ao `seek(t)` do tutorial).

Catálogo completo, com paletas, ideia, ritmo, som e correções: `references/estilos.md`.

## Regra do usuário (obrigatória)

Quando o usuário passar um `.json` de roteiro (um vídeo ou uma série), **antes de montar cada projeto**:

1. Converta o vídeo para `projetos/<slug>/roteiro.json` (contrato do `roteiro-persuasivo`).
2. Abra a página de escolha de estilo do projeto:
   ```
   python .claude/skills/estilos-motion/scripts/abrir_estilos.py --roteiro projetos/<slug>/roteiro.json
   ```
   Ela mostra, animados, com o título e o gancho do vídeo, e recomenda 3 para o tema:
   - **Estilos da casa** (00, 01, 02, 05, 06, 07; ASCII e pixel dither foram retirados a pedido do usuário);
   - **Estilos das skills** (S1 `bang-motion`, S2 `vox-director`, S3 `vox-explainer`, S4 `huashu-art-motion`, S5 `claude-drawing`);
   - **99 · Criar do zero**.
3. Faça **uma só chamada** de AskUserQuestion com estas perguntas:
   - **Estilo**: os 3 recomendados + "Criar do zero" como opções (o usuário digita outro número em "Other").
   - **Movimentos (motion-prompt)**: "Claude escolhe" (Recomendado) · "Abrir a galeria e escolher" · "Sem motion-prompt".
   - **Paleta**: "Do estilo" · "Da marca" (pule se o roteiro não tiver marca).
4. Siga o ramo do estilo (abaixo), depois o ramo dos movimentos.
5. Grave tudo em `roteiro.json → estilo` (esquema em `roteiro-persuasivo/templates/roteiro.schema.json`):
   ```json
   {"id": "s-huashu-art-motion", "origem": "skill", "skill": "huashu-art-motion", "variante": "水墨",
    "paleta": "estilo", "motions": {"modo": "galeria", "ids": ["#012", "#045"], "nota": "título de abertura"}}
   ```

Numa série, pergunte vídeo a vídeo: o usuário pode querer variar o estilo e os movimentos.
Não pule a pergunta mesmo que um estilo já tenha sido usado antes.

### Ramo do estilo

| Escolha | O que fazer |
|---|---|
| Estilo da casa (00–07) | Siga `references/estilos.md` e o fluxo abaixo, no Remotion. `origem: "casa"` |
| Estilo de skill (S1–S5) | Carregue a skill (Skill tool) e leia o catálogo dela. Se ela tem sub-estilos (huashu: 36 estilos + 9 gramáticas; claude-drawing: 83 técnicas; bang-motion: starters jornalismo/cartum/catálogo/palco/esboço), mostre 3–4 que combinam com o tema e pergunte qual (AskUserQuestion) → `variante`. Construa com o motor da skill, mas mantendo as regras deste repo: 1080×1920, 30 fps, zonas seguras, pt-BR, narração do `legendas-tts` e legenda queimada. `origem: "skill"` |
| 99 · Criar do zero | Peça referências (ou use o que o usuário já descreveu) e proponha **2–3 direções** em texto curto: ideia-dispositivo, paleta (hex), tipografia, movimento, som, dificuldade. Pergunte qual. Escreva `projetos/<slug>/estilo/estilo.md` no mesmo formato de `references/estilos.md`, faça um quadro de teste (`npx remotion still`) e só siga com aprovação. `origem: "do-zero"`, `spec: "projetos/<slug>/estilo/estilo.md"`. Se o usuário gostar, ofereça incluir no catálogo da casa (página + `references/estilos.md`) |

`vox-director` e `vox-explainer` geram imagem e movimento por IA na Atlas Cloud (precisa de `ATLASCLOUD_API_KEY`, custa
créditos): avise o custo antes de rodar. `huashu-art-motion` precisa de `uv`, `ffmpeg` e Playwright Chromium.

### Ramo dos movimentos (skill `motion-prompt`)

Rode o CLI da skill: `node .claude/skills/motion-prompt/scripts/motion-prompt.mjs <comando>`.

| Escolha | O que fazer |
|---|---|
| Claude escolhe | Monte o mapa de batidas e rode um `search` por cena (`--pack motion,motion2` para títulos e texto, `camera,camera2` para câmera e cortes). Escolha pelo que o resumo diz que o movimento faz, não pelo nome. Liste no storyboard qual `#ID` vai em qual cena, para o usuário aprovar junto. `modo: "claude"` |
| Abrir a galeria | Rode `pick --pack motion,motion2,camera,camera2` em segundo plano (espera até 15 min) e diga ao usuário para marcar o que quer, escrever uma nota (ex.: "abertura") e apertar "Send to AI". Use **exatamente** as escolhas, na ordem. Se der timeout (código 4), pergunte de novo, não escolha por ele. `modo: "galeria"` |
| Sem motion-prompt | Movimentos do próprio estilo. `modo: "nenhum"` |

Os movimentos se adaptam ao estilo (paleta, fonte, conteúdo), mas tempos e easing ficam como na especificação
(`get` + `kit`, ver `motion-prompt/references/porting.md`). Leve a linha `// Motion Prompt #ID · MIT License` para o
arquivo onde o código entrar.

## Fluxo de cada vídeo (do tutorial, adaptado)

| Etapa | O que fazer | Para quando |
|---|---|---|
| 1. Estilo + movimentos | Página + pergunta (acima), sub-estilo ou estilo do zero, e motion-prompt (Claude escolhe ou galeria) | Usuário escolheu |
| 2. Storyboard | Mapa de batidas com tempos por cena + **4 quadros-chave em PNG** (render rápido no Remotion com `npx remotion still`, ou mock). Mostre e **espere aprovação** antes de construir | Aprovado |
| 3. Narração | `legendas-tts` (VoiceStudio/ElevenLabs), depois `ajustar_tempos.py` e `--so-legendas` | Áudio e legendas prontos |
| 4. Build | Composição em `remotion/src/projetos/<marca-ou-slug>/` com `composicoes.tsx` (o Root registra sozinho). Animações ancoradas nas palavras faladas (`criarRelogio` do kit da marca) | Compila (`npx tsc --noEmit`) |
| 5. Folha de contatos | Um quadro por batida (`npx remotion still … --scale=0.5`) juntos numa imagem; revise você mesmo e corrija o que estiver fraco | Sem defeito visível |
| 6. Render + som | `npx remotion render …`, depois normalize para **-14 LUFS** (`loudnorm`) | MP4 final em `projetos/<slug>/video/` |

## Scripts

| Script | Faz |
|---|---|
| `scripts/importar_serie.py --serie <arquivo>` | Converte um .json de série (`videos[].cenas[]`) em `projetos/<slug>/roteiro.json`, com pronúncia aplicada e a voz da série |
| `scripts/abrir_estilos.py` | Página de escolha de estilo do projeto (casa, skills e "do zero", animados, 3 recomendados) |
| `legendas-tts/scripts/palavras_estimadas.py` | Tempos de palavra estimados para montar e revisar antes da voz existir |
| `legendas-tts/scripts/fila_narracao.py <roteiros…>` | Gera a voz de vários projetos cena a cena no VoiceStudio, retoma se o app cair, ajusta tempos e copia a narração para o Remotion |
| `scripts/folha_contatos.py --composicao X --saida …` | Prévia em baixa resolução + grade de quadros (revisão) |
| `scripts/storyboard_serie.py --saida … <roteiros…>` | Página com mapa de batidas + folha de contatos de cada vídeo, para aprovação |
| `scripts/renderizar.py --composicao X --saida …` | Render final + áudio em -14 LUFS |

Kits prontos (Visualize+, em `remotion/src/projetos/visualize/`): `marca.tsx` (flat), `kit-bola.tsx`, `kit-riso.tsx`,
`serie.tsx` (tempos, narração, legenda que troca de cor com o fundo, canvas por quadro); linha contínua, ASCII,
pixel dither e tinta na água estão em `V03`, `V06`, `V08` e `V09`.

## Regras de qualquer estilo

- 1080×1920, 30 fps. Texto fora dos 250 px de cima, 420 px de baixo e 120 px da direita.
- Uma ideia por vídeo (o "dispositivo" que carrega o filme), não uma lista de efeitos.
- Sem crossfade genérico, sem degradê genérico, sem excesso de brilho, nada com cara de template.
- Aleatoriedade só com semente (`random('chave')` do Remotion) — renders repetíveis.
- Texto na tela com no mínimo 60 px de altura.
- Narração manda no tempo: o estilo define visual, movimento e som, a duração vem da voz.
- Trilha e efeitos: sintetizados em código ou nenhum (nada a licenciar). Com narração, a trilha fica
  ~16–20 dB abaixo da voz, com ducking. `scripts/trilha_sintetizada.py --roteiro …` gera
  `projetos/<slug>/audio/trilha.mp3` com arranjo por estilo; `renderizar.py --trilha …` (ou
  `trilha.py mixar`) mixa sob a voz. `trilha.py gerar` usa a ElevenLabs Music (só plano pago; a
  conta atual do usuário é gratuita, 10/11/2026).
- Mídia de banco e mascote só se o roteiro e o usuário pedirem (ver regras da marca no `roteiro.json`).

## Correções rápidas (do tutorial)

| Se aparecer | Faça |
|---|---|
| Texto pequeno no celular | Todo texto ≥ 60 px de altura em 1080 de largura |
| Som não bate com a ação | Re-cronometre: cada batida no quadro exato em que o movimento pousa |
| Cena vazia | Ocupe o quadro todo, não só a metade de cima |
| Loop pula | Primeiro e último quadro idênticos |
| Cores erradas | Troque só a paleta (hex), mantenha o resto |
| Muito digital | Grão, leve tremor nas linhas, jitter quadro a quadro |
| Longo demais | Corte, mantendo o final |

Antes de entregar: ver no celular, conferir o primeiro segundo sem som, nada sob os botões do Reels.

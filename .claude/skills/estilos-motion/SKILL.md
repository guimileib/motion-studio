---
name: estilos-motion
description: Escolhe e aplica o estilo visual de motion de cada vídeo (flat da marca, linha contínua, bola única, risografia em stop motion, códice renascentista, tinta na água) e conduz o fluxo storyboard → aprovação → build → folha de contatos → render. Use SEMPRE que o usuário passar um roteiro em .json (um vídeo ou uma série) para produzir, pedir "estilo de motion", "qual visual", "outro estilo", "storyboard", ou quiser variar o visual entre vídeos. Antes de montar qualquer projeto, abra a página de escolha de estilo e pergunte.
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
   Ela mostra os 6 estilos animados (ASCII e pixel dither foram retirados a pedido do usuário), com o título e o gancho do vídeo, e recomenda 3 para o tema.
3. Pergunte no chat (AskUserQuestion) qual estilo usar, com os 3 recomendados como opções
   (o usuário digita outro número em "Other"), e se a paleta é a **do estilo** ou a **da marca**.
4. Grave a escolha em `roteiro.json → estilo` (`{"id": "04-pixel-dither", "paleta": "marca"}`).

Numa série, pergunte vídeo a vídeo: o usuário pode querer variar o estilo.
Não pule a pergunta mesmo que um estilo já tenha sido usado antes.

## Fluxo de cada vídeo (do tutorial, adaptado)

| Etapa | O que fazer | Para quando |
|---|---|---|
| 1. Estilo | Página + pergunta (acima) | Usuário escolheu |
| 2. Storyboard | Mapa de batidas com tempos por cena + **4 quadros-chave em PNG** (render rápido no Remotion com `npx remotion still`, ou mock). Mostre e **espere aprovação** antes de construir | Aprovado |
| 3. Narração | `legendas-tts` (VoiceStudio/ElevenLabs), depois `ajustar_tempos.py` e `--so-legendas` | Áudio e legendas prontos |
| 4. Build | Composição em `remotion/src/projetos/<marca-ou-slug>/` com `composicoes.tsx` (o Root registra sozinho). Animações ancoradas nas palavras faladas (`criarRelogio` do kit da marca) | Compila (`npx tsc --noEmit`) |
| 5. Folha de contatos | Um quadro por batida (`npx remotion still … --scale=0.5`) juntos numa imagem; revise você mesmo e corrija o que estiver fraco | Sem defeito visível |
| 6. Render + som | `npx remotion render …`, depois normalize para **-14 LUFS** (`loudnorm`) | MP4 final em `projetos/<slug>/video/` |

## Scripts

| Script | Faz |
|---|---|
| `scripts/importar_serie.py --serie <arquivo>` | Converte um .json de série (`videos[].cenas[]`) em `projetos/<slug>/roteiro.json`, com pronúncia aplicada e a voz da série |
| `scripts/abrir_estilos.py` | Página de escolha de estilo do projeto (8 estilos animados, 3 recomendados) |
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

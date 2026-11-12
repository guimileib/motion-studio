# motion-studio — instruções para o Claude Code

Este repositório produz vídeos curtos (Reels, TikTok, Shorts, anúncios) de ponta a ponta:
roteiro persuasivo → busca de mídia → narração (ElevenLabs) + legendas → montagem com transições
(Remotion, CapCut ou o Motion do Claude).

## As 5 skills (em `.claude/skills/`)

| Skill | Quando usar | Entrega |
|---|---|---|
| `roteiro-persuasivo` | Criar ou revisar roteiro, gancho, CTA, copy de vídeo | `projetos/<slug>/roteiro.json` + `roteiro.md` |
| `busca-midia` | Achar fotos/vídeos de banco (Pexels, Pixabay, Unsplash, web) para cada cena | `projetos/<slug>/midia/` + `manifest.json` + `CREDITOS.md` |
| `legendas-tts` | Narração na ElevenLabs, legendas SRT, legendas animadas estilo Reels | `projetos/<slug>/audio/`, `legendas/` |
| `estilos-motion` | Escolher o estilo visual de cada vídeo (8 estilos) e conduzir storyboard → build → folha de contatos → render | `projetos/<slug>/estilo/escolha.html`, `roteiro.json → estilo` |
| `transicoes-motion` | Escolher e implementar transições entre cenas | componentes em `remotion/src/transicoes/`, passos de CapCut, padrões para o Motion do Claude |

## O pipeline padrão

0. **Estilo (obrigatório)** — quando o usuário passar um `.json` de roteiro (um vídeo ou uma série), **antes de montar cada projeto** abra a página de estilos e pergunte qual estilo usar e se a paleta é do estilo ou da marca: `python .claude/skills/estilos-motion/scripts/abrir_estilos.py --roteiro projetos/<slug>/roteiro.json` (ou `--serie <arquivo> --video <id>`). Numa série, pergunte vídeo a vídeo. Depois mostre o storyboard (mapa de batidas + 4 quadros) e espere aprovação.
1. **Roteiro** — `roteiro-persuasivo` escreve `projetos/<slug>/roteiro.json` (o contrato entre as skills; esquema em `.claude/skills/roteiro-persuasivo/templates/roteiro.schema.json`).
2. **Mídia** — `busca-midia` lê `cenas[].midia` e baixa as opções: `python .claude/skills/busca-midia/scripts/buscar_midia.py --roteiro projetos/<slug>/roteiro.json --baixar`.
3. **Narração + legendas** — `legendas-tts`: `python .claude/skills/legendas-tts/scripts/tts_elevenlabs.py --roteiro projetos/<slug>/roteiro.json` (ou `tts_voicestudio.py` para voz local no VoiceStudio; confira a licença do motor antes de usar em peça comercial). Depois `ajustar_tempos.py --roteiro …` e de novo o TTS com `--so-legendas`, para as cenas durarem o tempo real da voz.
4. **Montagem** — `transicoes-motion` aplica `cenas[].transicao_saida` no Remotion (`cd remotion && npx remotion studio`), descreve os passos no CapCut ou escreve as cenas no Motion do Claude.

Rode cada etapa só quando a anterior estiver aprovada pelo usuário. Ao mudar o roteiro, atualize o `roteiro.json` (fonte da verdade) e rode de novo só o que depende da mudança.

## Convenções

- Um projeto por pasta: `projetos/<slug>/` (slug em kebab-case, sem acento).
- Tempos sempre em segundos no `roteiro.json`; em milissegundos nos JSON de legenda (compatível com `Caption` do `@remotion/captions`).
- Vertical 1080×1920 a 30 fps por padrão. Zonas seguras de Reels/TikTok: deixe texto e logo fora dos 250 px de cima, 420 px de baixo e 120 px da direita.
- Texto em português do Brasil, com acentos corretos.
- Chaves de API só em `.env` (copie de `.env.example`). Nunca escreva chave em código, roteiro, commit ou mensagem. Se o usuário colar uma chave no chat, use, mas recomende revogar e gerar outra.
- Scripts Python usam só a biblioteca padrão (Python 3.10+) e `ffmpeg` para áudio.
- Não invente resultados, depoimentos ou números em vídeo de marca. Dado ilustrativo na tela leva a marca "Valores ilustrativos".
- Mídia de terceiros só com licença verificada; os créditos vão em `CREDITOS.md`.
- **Projetos pessoais ficam fora do git** (`.gitignore`): `projetos/*` (menos `exemplo-*`), `remotion/src/projetos/*` e `remotion/public/*` (menos `fonts/`), além de PDFs de referência. Composição de projeto vai em `remotion/src/projetos/<pasta>/composicoes.tsx` exportando `Composicoes`; o `Root.tsx` registra sozinho (`require.context`), nunca importe projeto pessoal direto no `Root.tsx`.
- Áudio final de Reels normalizado em -14 LUFS (`ffmpeg … -af loudnorm=I=-14:TP=-1.5:LRA=11`).

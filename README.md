# motion-studio

Pipeline de vídeo curto (Reels, TikTok, Shorts, anúncios e motion de produto) para usar com o
**Claude Code**: roteiro persuasivo → busca de mídia → narração na ElevenLabs + legendas →
montagem com transições profissionais (Remotion, CapCut ou o Motion do Claude).

## As skills

Ficam em `.claude/skills/` e o Claude Code as carrega sozinho quando o pedido combina.

| Skill | Faz | Scripts / código |
|---|---|---|
| `roteiro-persuasivo` | Roteiro com níveis de consciência, PAS/AIDA/BAB/PASTOR, gatilhos de Cialdini, quebra de objeção e cronometragem | gera `roteiro.md` + `roteiro.json` (esquema em `templates/`) |
| `busca-midia` | Fotos e vídeos de Pexels, Pixabay, Unsplash e web aberta, alinhados ao corte, com licença e créditos | `scripts/buscar_midia.py` |
| `legendas-tts` | Narração ElevenLabs com timestamps ou local no VoiceStudio, SRT, legenda animada estilo Reels, transcrição (Scribe) | `scripts/tts_elevenlabs.py`, `scripts/tts_voicestudio.py`, `scripts/stt_elevenlabs.py`, `scripts/legendas_lib.py` |
| `estilos-motion` | 8 estilos de motion (flat da marca, linha contínua, bola única, ASCII, pixel dither, risografia, códice, tinta na água), página de escolha por projeto e fluxo storyboard → build → folha de contatos | `scripts/abrir_estilos.py`, `pagina/estilos.html` |
| `transicoes-motion` | Catálogo de 19 transições com duração, easing e som; implementação no Remotion, CapCut e Motion do Claude | `remotion/src/transicoes/`, `templates/claude-motion/transicoes.js`, `scripts/montar_remotion.py` |

### Skills de terceiros (MIT)

Incorporadas como cópia, com a `LICENSE` original de cada uma dentro da pasta. Ficaram de fora só os
vídeos e GIFs de vitrine; scripts, referências, fontes e imagens de referência estão completos.

| Skill | Origem | Faz | Precisa de |
|---|---|---|---|
| `bang-motion` | [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion) | Motion cinematográfico no navegador (HTML + CSS + GSAP): promo, opener, kinetic type, explainer 16:9 e 9:16; texto em indonésio | Node, Python, `ffmpeg` |
| `vox-explainer` | [CK42BB/vox-explainer-skill](https://github.com/CK42BB/vox-explainer-skill) | Pipeline de explainer estilo Vox a partir de um tema (roteiro, keyframes, animação, voz) | `ATLASCLOUD_API_KEY`, `ffmpeg` |
| `vox-director` | [Alisa0808/vox-director](https://github.com/Alisa0808/vox-director) | Explainer/anúncio estilo Vox em colagem de papel, de ponta a ponta | `ATLASCLOUD_API_KEY`, Python, `ffmpeg` |
| `huashu-art-motion` | [alchaincyf/huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) | Animação artística e de explicação: 36 estilos, 9 gramáticas de explainer, motor de render; texto em chinês | `uv`, `ffmpeg`, Playwright Chromium (`uv run --with playwright playwright install chromium`); TTS opcional `VOLC_SPEECH_TOKEN` |
| `claude-drawing` | [cloveric/claude-drawing-skill](https://github.com/cloveric/claude-drawing-skill) | Pintura procedural em código, sem modelo de imagem, 83 estilos (aquarela, nanquim, óleo…); texto em chinês | Python com `numpy` e `Pillow` (`pip install -r .claude/skills/claude-drawing/requirements.txt`) |

Para atualizar uma delas, baixe de novo o repositório de origem e substitua a pasta.

## Instalação

```bash
git clone <seu-repo> motion-studio && cd motion-studio
cp .env.example .env          # preencha as chaves
cd remotion && npm install    # Remotion (transições, legendas, render)
```

Requisitos: Python 3.10+ (só biblioteca padrão), Node 18+, `ffmpeg`/`ffprobe` no PATH.

Chaves (todas no `.env`, que não vai para o git):

| Variável | Onde pegar |
|---|---|
| `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` | elevenlabs.io → Settings → API Keys; o voice_id fica na página da voz |
| `VOICESTUDIO_URL`, `VOICESTUDIO_MODEL`, `VOICESTUDIO_VOICE` | opcional, narração local: instale o [VoiceStudio](https://github.com/debpalash/VoiceStudio), crie um perfil de voz no app e use o nome dele |
| `PEXELS_API_KEY` | pexels.com/api |
| `PIXABAY_API_KEY` | pixabay.com/api/docs (logado) |
| `UNSPLASH_ACCESS_KEY` | unsplash.com/developers → New Application |
| `ATLASCLOUD_API_KEY` | atlascloud.ai (só `vox-explainer` e `vox-director`) |
| `VOLC_SPEECH_APPID`, `VOLC_SPEECH_TOKEN` | opcional, TTS da Volcengine para `huashu-art-motion` |

## Uso no Claude Code

Abra a pasta no Claude Code e peça em linguagem natural, por exemplo:

> Cria um roteiro de 20 s para Reels sobre [produto], público [quem], objetivo [lead]. Depois busca a mídia,
> gera a narração com a ElevenLabs e monta no Remotion com a transição de frutas caindo.

Ou etapa por etapa:

```bash
# 1. roteiro: peça ao Claude → projetos/<slug>/roteiro.json
# 2. mídia
python .claude/skills/busca-midia/scripts/buscar_midia.py --roteiro projetos/<slug>/roteiro.json --baixar
# 3. narração + legendas
python .claude/skills/legendas-tts/scripts/tts_elevenlabs.py --roteiro projetos/<slug>/roteiro.json
#    ou, com voz local no VoiceStudio:
python .claude/skills/legendas-tts/scripts/tts_voicestudio.py --roteiro projetos/<slug>/roteiro.json
# 4. montagem e render
python .claude/skills/transicoes-motion/scripts/montar_remotion.py --projeto projetos/<slug>
cd remotion && npx remotion render VideoRoteiro out/<slug>.mp4 --props=props/<slug>.json
```

Prévia interativa: `cd remotion && npx remotion studio`. Composições:
- `TransicoesDemo` — vitrine de todas as transições;
- `ObjetosCaindo` — overlay de frutas caindo com fundo transparente, para o CapCut
  (`npx remotion render ObjetosCaindo out/objetos.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png`);
- `LegendasDemo` — legenda animada com o exemplo;
- `VideoRoteiro` — o vídeo inteiro a partir de um `roteiro.json`.

Exemplo completo de roteiro: `projetos/exemplo-veta-pedido-certo/roteiro.json`.

## Projetos pessoais

`projetos/<slug>/`, `remotion/src/projetos/<pasta>/` e `remotion/public/` (menos `fonts/`) ficam fora do git.
Cada composição de projeto mora em `remotion/src/projetos/<pasta>/composicoes.tsx` e é registrada
automaticamente pelo `Root.tsx` — veja `remotion/src/projetos/README.md`.

## Testes

```bash
python -m unittest discover -s tests -v     # offline: legendas, remapeamento, SRT, mixagem, busca
cd remotion && npx tsc --noEmit              # tipos do Remotion
```

## Usar as skills fora deste repo

Copie a pasta da skill para `~/.claude/skills/` (vale para todos os projetos no Claude Code). As skills
`roteiro-persuasivo` e `transicoes-motion` funcionam sozinhas; `busca-midia` e `legendas-tts` dependem
dos scripts da própria pasta.

## Licenças

- Remotion: grátis para pessoas físicas, empresas com até 3 funcionários e organizações sem fins
  lucrativos; acima disso precisa de licença de empresa (remotion.pro/license).
- Mídia de banco: veja `.claude/skills/busca-midia/references/licencas.md`. Os créditos de cada projeto
  ficam em `projetos/<slug>/CREDITOS.md`.
- Skills de terceiros: MIT, cada uma com a sua `LICENSE` na própria pasta.
- ElevenLabs: o uso comercial da voz depende do seu plano.
- VoiceStudio: o app é AGPL-3.0 e cada motor tem a sua licença. O padrão (OmniVoice) é CC-BY-NC, só
  uso não comercial; para anúncio use `voxcpm2` ou `moss-tts-nano` (Apache-2.0). Clone só voz com
  autorização do dono.

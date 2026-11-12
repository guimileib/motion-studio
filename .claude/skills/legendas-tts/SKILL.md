---
name: legendas-tts
description: Produz narração com a ElevenLabs (text-to-speech com timestamps, pt-BR) ou com o VoiceStudio (TTS local, sem custo por crédito) e legendas profissionais — SRT para CapCut/Premiere/YouTube e legenda animada estilo Reels palavra por palavra (Remotion ou Motion do Claude) — sincronizadas com as cenas do roteiro. Também prepara o texto para soar natural na voz (siglas, números, preços, pausas) e transcreve áudio existente (Scribe) para legendar. Use sempre que o usuário pedir narração, locução, voz, ElevenLabs, text to speech, TTS, legenda, SRT, closed caption ou "texto para a voz".
---

# Narração (ElevenLabs) e legendas

Duas coisas andam juntas: o **texto falado** (escrito para o ouvido) e o **texto lido** (legenda,
escrita para o olho). O `roteiro.json` guarda as duas: `narracao` (como aparece na legenda) e,
quando precisa, `narracao_tts` (como a voz deve falar).

## 1. Prepare o texto para a voz

Regras completas e exemplos em `references/texto-para-voz.md`. O essencial:

- **Siglas:** escreva como se fala. "FLV" → "éfe éle vê"; "IA" → "I.A." ou "inteligência artificial".
- **Números e dinheiro:** por extenso quando importa a leitura: "R$ 4,57" → "quatro reais e cinquenta e
  sete centavos"; "30%" → "trinta por cento"; datas e horas também.
- **Pausas:** pontuação controla o ritmo. Vírgula = pausa curta, ponto = média, reticências = longa.
  Para pausa exata, `<break time="0.6s" />` (modelos multilingual v2/flash/turbo; no eleven_v3 use
  pontuação e tags de emoção como `[excited]`).
- **Ênfase:** frase curta isolada ("A Veta te diz.") rende mais que maiúsculas.
- **Uma cena = uma geração.** Gerar por cena permite encaixar cada fala no seu tempo; o script passa
  `previous_text`/`next_text` para manter a entonação contínua entre as cenas.
- **Ritmo:** ~2,5 palavras/s. Fala que passa do tempo da cena: encurte o texto antes de acelerar;
  `velocidade` só entre 0,9 e 1,15 para não soar robótico.

Configuração que funciona para anúncio em pt-BR: modelo `eleven_multilingual_v2`, estabilidade 0,40–0,50,
similaridade 0,75, estilo 0,15–0,30, speaker boost ligado. Voz: escolha uma voz nativa pt-BR na
biblioteca da ElevenLabs e coloque o `voice_id` no `.env` (`ELEVENLABS_VOICE_ID`) ou em
`roteiro.json → voz.voice_id`.

## 2. Gere a narração (Claude Code, com API)

```bash
python .claude/skills/legendas-tts/scripts/tts_elevenlabs.py --roteiro projetos/<slug>/roteiro.json
```

O script, para cada cena com `narracao`:
1. chama `POST /v1/text-to-speech/{voice_id}/with-timestamps` (header `xi-api-key`) e salva
   `audio/<cena>.mp3` + `audio/<cena>.alinhamento.json` (cache por hash: só regenera o que mudou);
2. converte o alinhamento por caractere em palavras com tempo absoluto
   (início da cena + `narracao_inicio_s`, padrão 0,15 s);
3. se `narracao_tts` ≠ `narracao`, leva os tempos para o texto da legenda;
4. grava `legendas/palavras.json` (formato `Caption` do `@remotion/captions`) e `legendas/legendas.srt`;
5. junta os trechos em `audio/narracao.mp3` com a duração do vídeo (ffmpeg);
6. escreve `audio/relatorio.txt` avisando cena que passa do tempo e a velocidade sugerida.

Opções úteis: `--cenas fim,pedido` (refaz só essas), `--forcar`, `--so-legendas` (refaz legendas sem
gastar crédito), `--estilo-legenda padrao`, `--texto "…" --saida pasta` (avulso).

**Áudio já existente** (gravado, ou gerado no site da ElevenLabs): transcreva para legendar:

```bash
python .claude/skills/legendas-tts/scripts/stt_elevenlabs.py --audio projetos/<slug>/audio/narracao.mp3
```

Sem acesso à API (rede bloqueada, sem chave): entregue o **roteiro de narração** por cena, com o tempo
e a grafia para a voz, para o usuário gerar no site; depois use o STT ou escreva o SRT a partir dos
tempos que ele informar.

### Alternativa local: VoiceStudio

[VoiceStudio](https://github.com/debpalash/VoiceStudio) roda os modelos de voz na própria máquina
(sem crédito por caractere) e expõe uma API compatível com a da OpenAI em `http://127.0.0.1:3900`.
Use quando o usuário pedir VoiceStudio, voz local/offline ou quiser economizar crédito da ElevenLabs.

```bash
python .claude/skills/legendas-tts/scripts/tts_voicestudio.py --roteiro projetos/<slug>/roteiro.json
```

Mesmas opções e mesmas saídas do `tts_elevenlabs.py` (o áudio por cena sai em `audio/<cena>.wav`).
Como o VoiceStudio não devolve timestamps com o áudio, o script transcreve cada trecho no próprio
VoiceStudio (`/v1/audio/transcriptions`, palavras com tempo) e leva os tempos para o texto do roteiro.

- **Licença do motor:** o motor padrão (`omnivoice`) tem pesos **CC-BY-NC, só uso não comercial**:
  serve para teste e rascunho, nunca para anúncio ou cliente. Para peça comercial use um motor Apache-2.0
  que fale português: `voxcpm2` (clona e desenha voz; precisa de GPU NVIDIA, ~5 GB) ou `moss-tts-nano`
  (leve, roda na CPU). O script avisa quando o motor é não comercial.
- **Voz:** o sotaque segue a voz de referência. Crie um perfil no app clonando um áudio limpo de
  locutor pt-BR **com autorização de uso da voz** e passe o nome ou id em `VOICESTUDIO_VOICE` ou
  `roteiro.json → voz.voicestudio.voz`. Fixe `voz.voicestudio.seed` para a voz não variar entre cenas.
- **Texto:** `<break …/>` é removido (a pausa vem da pontuação); não há `previous_text`, então ouça as
  emendas entre cenas. Siglas e números continuam valendo como em `references/texto-para-voz.md`.
- **Velocidade:** `voz.velocidade` vai como `speed`; os motores aceitam de 0,25 a 4, mas a regra de
  0,9–1,15 continua.
- Outra máquina com GPU: `VOICESTUDIO_URL=https://…` e `VOICESTUDIO_API_KEY` (só por HTTPS).

## 3. Legendas: regras de qualidade

Detalhes em `references/regras-de-legenda.md`.

| Estilo | Uso | Bloco |
|---|---|---|
| `reels` | Reels, TikTok, Shorts | 1 linha, até ~22 caracteres, 0,5–1,8 s, quebra em pausa e vírgula |
| `padrao` | YouTube, institucional, acessibilidade | até 2 linhas de 42 caracteres, 1–6 s, ≤ 17 caracteres/s |

- A legenda é o texto da `narracao`, com acentos e pontuação; não a grafia fonética.
- Quebre por sentido (não separe artigo do substantivo, nem número da unidade).
- Posição: centro horizontal, entre 60% e 70% da altura no vertical — acima da interface do app.
- Contraste: texto claro com contorno/sombra, ou caixa sólida; destaque da palavra falada na cor da marca.
- Termos da marca escritos sempre do mesmo jeito (crie uma lista de grafias no projeto).

## 4. Legenda animada estilo Reels

- **Remotion:** `remotion/src/legendas/LegendaReels.tsx` recebe `legendas/palavras.json`
  (`<LegendaReels legendas={palavras} corDestaque="#7BD13A" />`), monta páginas com
  `createTikTokStyleCaptions` e destaca a palavra falada. Já está ligado na composição `VideoRoteiro`.
- **Motion do Claude:** cole `templates/claude-motion/legendas.js` no `shared.js`, salve as palavras
  como módulo `legendas.json` e chame `LEG.montar(kit, palavras)` / `.render(t)` em cada cena (o helper
  usa `kit.start + t` para achar o tempo do filme). O player do Motion não toca a narração: exporte o
  vídeo e junte o `narracao.mp3` no editor.
- **CapCut:** importe o `.srt` (Texto > Legendas > Importar) e aplique um estilo/animação de texto; ou use
  as legendas automáticas do CapCut e corrija com o texto do roteiro.

## 5. Checklist

- [ ] Siglas, números e preços escritos para a voz em `narracao_tts`?
- [ ] Nenhuma cena passa do tempo (`audio/relatorio.txt`)?
- [ ] Legenda com o texto correto (acentos, marca), quebras por sentido, dentro da zona segura?
- [ ] Tempo de leitura respeitado (estilo padrão ≤ 17 caracteres/s)?
- [ ] `narracao.mp3` com a duração exata do vídeo?
- [ ] Chave da API só no `.env`?
- [ ] VoiceStudio: motor com licença comercial e voz com autorização de uso?

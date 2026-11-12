---
name: transicoes-motion
description: Escolhe, cronometra e implementa transições profissionais entre cenas de motion design e vídeo — match cut, whip pan, zoom punch, wipe com objeto, íris, morph, J/L-cut, faixas, luma wipe — no Remotion (componentes prontos em remotion/src/transicoes), no CapCut (passo a passo) e no Motion do Claude (padrões em função de t). Use sempre que o usuário pedir transição, passagem entre cenas, "efeito entre um vídeo e outro", ritmo de edição, montagem, ou quando o roteiro.json tiver transicao_saida para aplicar.
---

# Transições profissionais para motion e vídeo

Uma transição boa é invisível: o olho segue o movimento e chega na cena seguinte sem perceber o
corte. Uma transição ruim é um efeito que chama atenção para si. Regra de ouro: **a transição
continua um movimento ou uma ideia que já estava na tela.**

## 1. Princípios (o que separa o profissional do "efeito de template")

1. **Motivação.** Toda transição nasce de algo na cena: um objeto que atravessa, a câmera que gira,
   uma forma que cresce, uma palavra que empurra a próxima. Sem motivação, use corte seco.
2. **Continuidade de direção e velocidade.** Se a cena A sai para a direita em velocidade, a B entra
   vindo da esquerda na mesma velocidade. Mantenha a direção de tela em todo o vídeo.
3. **Uma transição-assinatura + corte seco.** Escolha 1 transição de marca (ex.: frutas caindo do céu)
   e use o corte seco para o resto. No máximo 2–3 tipos por vídeo.
4. **Duração curta.** Vídeo curto: 6–15 frames a 30 fps (0,2–0,5 s) para transições de energia;
   15–24 frames (0,5–0,8 s) para objeto atravessando; dissolve só para passagem de tempo, 12–20 frames.
5. **Easing, nunca linear.** Ease-in-out para movimento de câmera; ease-out forte (expo) para entradas
   "whip"; mola com pouco overshoot para formas. O meio da transição é o ponto mais rápido.
6. **Motion blur.** Tudo que cruza a tela rápido ganha desfoque direcional proporcional à velocidade.
7. **Som no meio.** O whoosh/swoosh tem o pico no frame do meio da transição; impacto no frame em que
   a nova cena "assenta". Sem som, metade do efeito some.
8. **Cobertura completa.** Em wipe com objeto, a tela fica 100% coberta por pelo menos 2–3 frames —
   é ali que acontece a troca. Nada da cena A pode "vazar" depois da troca.
9. **Leitura primeiro.** Nenhuma transição começa antes do espectador terminar de ler o texto da cena.
   Reserve 0,6–1 s de leitura depois que o último texto entra.
10. **Acessibilidade.** Nada pisca mais de 3 vezes por segundo (flash, glitch, strobe). Glitch e flash
    de luz: no máximo um pulso por transição.

## 2. Escolha pela intenção

| Intenção | Transição | Catálogo |
|---|---|---|
| Ritmo, "olha tudo isso" | corte seco no beat da música | `corte` |
| Antecipar a próxima ideia pelo som | J-cut (áudio da B entra antes) / L-cut | `j-cut`, `l-cut` |
| Ligar duas coisas parecidas (causa → efeito) | match cut de forma, cor ou movimento | `match-cut` |
| Energia, mudança brusca de assunto | whip pan com blur | `whip-pan` |
| Impacto, ênfase, revelação | zoom punch / zoom through | `zoom-punch`, `zoom-through` |
| Marca forte, divertida, memorável | objeto da marca cobre a tela (frutas, logo, produto) | `object-wipe` |
| Revelar a partir de um ponto (botão, logo, produto) | íris / máscara circular | `iris` |
| Card vira tela, problema vira solução | morph de forma | `shape-morph` |
| Elegante, institucional | luma wipe / dip na cor da marca | `luma-wipe`, `dip-cor` |
| Lista, tópicos, sequência | push/slide na mesma direção | `push` |
| Tipografia cinética | palavra empurra a próxima | `texto-empurra` |
| Modernidade, tech | faixas (stripes) / glitch de 1 pulso | `faixas`, `glitch` |
| Passagem de tempo, memória | dissolve / desfoque | `dissolve`, `desfoque` |

O catálogo completo (duração, easing, som, como fazer em cada ferramenta e os erros comuns) está em
`references/catalogo.md`. Leia a linha da transição escolhida antes de implementar.

## 3. Fluxo de trabalho

1. **Leia o `roteiro.json`** do projeto (se existir): `cenas[].transicao_saida`. Se não houver, proponha
   uma transição por passagem com o motivo em uma linha ("whip pan: a câmera da cena 2 já se move
   para a direita").
2. **Defina a assinatura** do vídeo e marque quais passagens usam corte seco.
3. **Cronometre:** a transição de saída da cena N termina no início da cena N+1. Em ferramentas com
   sobreposição (Remotion `TransitionSeries`, CapCut) a duração total encolhe: total = soma das cenas
   − soma das transições. Ajuste as cenas para manter a duração-alvo e o sincronismo com a narração.
4. **Implemente na ferramenta pedida** (seções 4–6).
5. **Som:** liste os efeitos sonoros com o tempo exato (pico no meio da transição).
6. **Verifique:** frames do início, meio e fim de cada transição; nada vazando, texto não cortado,
   sem flash acima de 3/s, direção coerente.

## 4. Remotion (código)

Projeto em `remotion/`. Transições prontas em `remotion/src/transicoes/` como *presentations* do
`@remotion/transitions` — use dentro de `<TransitionSeries.Transition presentation={…} timing={…} />`:

| Arquivo | Catálogo | Props principais |
|---|---|---|
| `zoomPunch.tsx` | `zoom-punch`, `zoom-through` | `escala`, `desfoque` |
| `whipPan.tsx` | `whip-pan` | `direcao`, `desfoque` |
| `irisOrigem.tsx` | `iris` | `origemX`, `origemY` (0–1) |
| `faixas.tsx` | `faixas` | `quantidade`, `direcao`, `cor`, `escalonamento` |
| `dipCor.tsx` | `dip-cor` | `cor` |
| `lumaWipe.tsx` | `luma-wipe` | `angulo`, `suavidade` |
| `ChuvaDeObjetos.tsx` | `object-wipe` | componente de **Overlay**: `duracao`, `objetos` (imagens), `quantidade`, `semente`, `cobertura` |

O object wipe entra como `<TransitionSeries.Overlay durationInFrames={24}><ChuvaDeObjetos duracao={24} /></TransitionSeries.Overlay>`:
fica centralizado no corte e não encurta o vídeo. Para usar no CapCut, exporte só a chuva com fundo
transparente: `npx remotion render ObjetosCaindo out/objetos.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png`.

Nativas do pacote (imports em `@remotion/transitions/<nome>`): `fade`, `slide`, `wipe`, `flip`,
`clock-wipe`, `iris`, e na versão atual também `blur-slide`, `cross-zoom`, `zoom-blur`, `push-cut`,
`dissolve`, `film-burn`, `ripple` e outras — confira `remotion/node_modules/@remotion/transitions/package.json`
antes de usar uma. Timing: `linearTiming({durationInFrames})` ou
`springTiming({config: {damping: 200}, durationInFrames})`. Vitrine com todas em
`remotion/src/demo/TransicoesDemo.tsx` (`cd remotion && npm i && npx remotion studio`).

**Vídeo inteiro a partir do roteiro:** a composição `VideoRoteiro` lê o `roteiro.json` e aplica
`cenas[].transicao_saida` pelo mapa `presentationDoRoteiro` (`remotion/src/transicoes/index.ts`),
com mídia, texto na tela, narração e legenda animada. Cada cena é esticada pela duração da sua
transição para os cortes caírem nos tempos do roteiro. Prepare e renderize:

```bash
python .claude/skills/transicoes-motion/scripts/montar_remotion.py --projeto projetos/<slug>
cd remotion && npx remotion render VideoRoteiro out/<slug>.mp4 --props=props/<slug>.json
```

Licença do Remotion: gratuita para pessoas físicas e empresas de até 3 funcionários; acima disso
exige licença de empresa (remotion.pro). Avise o usuário se for o caso.

Para uma transição nova, siga o padrão dos arquivos existentes: um componente que recebe
`presentationProgress` (0→1), `presentationDirection` (`entering`/`exiting`) e `passedProps`, e uma
função fábrica que devolve `{component, props}`. Tudo determinístico (use `random(seed)` do Remotion,
nunca `Math.random`).

## 5. CapCut (edição manual)

Passo a passo de cada transição, ajustes de duração/curva e como fazer as que não existem prontas
(object wipe com overlay, match cut com keyframe, J/L-cut) em `references/capcut.md`. Os nomes dos
efeitos mudam entre versões do CapCut: descreva a categoria e o resultado esperado, e diga para
escolher o efeito mais próximo.

## 6. Motion do Claude (player de animação do Claude)

Lá tudo é função pura do tempo `t` e nada atravessa um corte entre cenas. A técnica: a cena A
desenha a primeira metade da transição até o fim dela, e a cena B desenha a segunda metade a partir
de `t` negativo, com a **mesma semente** — os quadros se encontram exatamente no corte. Helpers
prontos (chuva de objetos, íris, faixas, zoom punch, whip) em
`templates/claude-motion/transicoes.js` para colar no `shared.js` do filme; regras e exemplo em
`references/claude-motion.md`.

## 7. Checklist

- [ ] Cada transição tem motivo visível na cena (ou é corte seco)?
- [ ] No máximo 2–3 tipos no vídeo, com uma assinatura?
- [ ] Direção de tela coerente do começo ao fim?
- [ ] Duração dentro da faixa e easing não linear?
- [ ] Cobertura total no ponto de troca (object wipe, íris, faixas)?
- [ ] Texto de cada cena teve tempo de leitura antes da transição?
- [ ] Som com pico no meio da transição?
- [ ] Nada piscando acima de 3 vezes por segundo?
- [ ] Duração total e sincronismo com narração conferidos depois das sobreposições?

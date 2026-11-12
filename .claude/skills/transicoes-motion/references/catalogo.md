# Catálogo de transições

Durações a 30 fps (multiplique por 2 a 60 fps). "Remotion" aponta para `remotion/src/transicoes/`.
"Motion" aponta para `templates/claude-motion/transicoes.js`.

---

## corte — corte seco
- **Quando:** padrão. Ritmo, listas, cortes no beat. 80% das passagens de um vídeo profissional.
- **Como fica bom:** cortar em movimento (no meio de um gesto), no beat da música, com mudança de
  escala (aberto → fechado) para não parecer "pulo".
- **Som:** nenhum, ou o próprio beat.
- **Erro comum:** cortar entre dois planos quase iguais (jump cut involuntário).
- **Remotion:** `<Series>` ou `TransitionSeries` sem `Transition`. **CapCut:** só dividir e não aplicar nada.

## j-cut / l-cut — áudio antecipa ou estende
- **Quando:** narração ou som da cena B começa 0,3–1 s antes da imagem (J); ou o som da A continua
  sobre a imagem da B (L). Dá fluidez de cinema sem efeito visual.
- **Remotion:** coloque o `<Audio>` da cena B numa `<Sequence from={inicioB - antecipacao}>`.
- **CapCut:** separe o áudio do clipe e arraste a borda do áudio para antes do corte.

## match-cut — corte por semelhança
- **Quando:** ligar duas ideias: forma (laranja → botão redondo), cor (vermelho do alerta → tomate),
  movimento (mão empurrando → card deslizando), posição (o objeto ocupa o mesmo lugar no quadro).
- **Duração:** 0 (é um corte), às vezes com 4–6 frames de dissolve para suavizar.
- **Segredo:** alinhar posição e tamanho do elemento comum nos dois quadros.
- **Remotion/Motion:** desenhe o elemento final da A e o inicial da B nas mesmas coordenadas.
  **CapCut:** keyframe de posição/escala na B para casar com o último frame da A.

## whip-pan — chicote de câmera
- **Duração:** 6–10 frames. **Easing:** ease-in na saída da A, ease-out forte (expo) na entrada da B.
- **Visual:** deslocamento de 1–1,5 tela + desfoque direcional (motion blur) que atinge o máximo no meio.
- **Som:** whoosh curto, pico no meio.
- **Direção:** a mesma do movimento que já existia na cena A.
- **Remotion:** `whipPan({direcao: 'esquerda'})`. **Motion:** `TR.whip(...)`.
  **CapCut:** categoria Câmera/Slide com desfoque, ou keyframe de posição + efeito de desfoque de movimento.

## zoom-punch — soco de zoom
- **Duração:** 6–10 frames. A sai crescendo (1 → 1,3–1,5) com blur radial; B entra de 0,85 → 1 com
  leve overshoot (1,02) e assenta.
- **Quando:** revelação, número, ênfase ("A Veta te diz.").
- **Som:** whoosh + impacto no assentamento.
- **Remotion:** `zoomPunch({escala: 1.4})`. **CapCut:** "Zoom in"/"Puxar" na categoria Câmera.

## zoom-through — atravessar
- **Quando:** a câmera entra em um objeto (tela do celular, janela, letra O) e sai na cena B.
- **Como:** escale a A até o objeto cobrir a tela (3–8×), troque, a B começa já ampliada e assenta.
- **Duração:** 12–20 frames, ease-in-out.

## dissolve — fusão
- **Quando:** só passagem de tempo, memória, clima. Em anúncio rápido, quase nunca.
- **Duração:** 12–20 frames. Prefira com leve desfoque (`desfoque`) para não parecer apresentação de slides.
- **Remotion:** `fade()` nativo.

## dip-cor — mergulho na cor
- **Quando:** troca de capítulo, institucional. Use a cor de fundo ou de destaque da marca, não preto.
- **Duração:** 10–16 frames (metade para entrar, metade para sair).
- **Remotion:** `dipCor({cor: '#0E2A22'})`.

## push — empurrar
- **Quando:** listas e sequências; a B empurra a A para fora na mesma direção, sempre a mesma no vídeo.
- **Duração:** 10–14 frames, ease-in-out ou mola.
- **Remotion:** `slide({direction: 'from-right'})` nativo.

## wipe — cortina
- **Quando:** antes/depois, comparação. Borda reta ou suave (feather 20–60 px).
- **Duração:** 10–16 frames. **Remotion:** `wipe()` nativo ou `lumaWipe`.

## object-wipe — objeto cobre a tela (transição-assinatura)
- **Quando:** identidade de marca: frutas caindo, produto passando, logo gigante, mão, folha de papel.
- **Duração:** 18–30 frames. Os objetos entram com aceleração de gravidade (ease-in), cobrem 100% da
  tela por 2–4 frames, a troca acontece aí, e saem pelo outro lado.
- **Densidade:** objetos de 15–30% da largura da tela, 20–30 objetos, posições espalhadas em toda a
  largura (distribua por faixas e só depois aleatorize), rotação aleatória, atraso 0–0,5 s entre eles.
  Um fundo sólido na cor da marca atrás dos objetos no meio garante a cobertura.
- **Som:** whoosh longo ou "chuva" de pops, pico no meio.
- **Remotion:** `objectWipe({objetos: [staticFile('frutas/tomate.svg'), …]})`.
  **Motion:** `TR.chuva(kit, {seed, t0})` na cena A (saída) e a MESMA chamada com `t0 - duracaoA` na B.
  **CapCut:** overlay de um vídeo/PNG animado de objetos caindo (feito no Remotion ou baixado) sobre o
  corte, com a troca no frame de cobertura total.

## iris — máscara circular
- **Quando:** revelar a partir de um ponto de interesse (botão, logo, produto, rosto).
- **Duração:** 12–18 frames, ease-in-out. Origem = posição do elemento na cena A.
- **Remotion:** `iris({origemX: 0.5, origemY: 0.62})`. **Motion:** `TR.iris(...)`.
  **CapCut:** categoria Máscara/Formas, círculo, com keyframe de tamanho.

## shape-morph — forma vira cena
- **Quando:** card vira tela cheia, bolha vira botão, ícone vira painel. É a transição mais "premium".
- **Como:** anime posição, tamanho e raio da borda do elemento da A até virar o fundo/janela da B.
  Mola com pouco overshoot. O conteúdo da B aparece por dentro com 4–6 frames de atraso.
- **Duração:** 14–24 frames. **Remotion/Motion:** interpolação de `left/top/width/height/borderRadius`.

## luma-wipe — cortina por gradiente
- **Quando:** institucional elegante; também imita "luz varrendo".
- **Duração:** 14–20 frames. **Remotion:** `lumaWipe({angulo: 120, suavidade: 0.25})`.

## faixas — stripes
- **Quando:** tech, energia organizada. 5–9 faixas da cor da marca entram escalonadas (2 frames entre
  cada), cobrem, e saem na mesma direção revelando a B.
- **Duração:** 14–20 frames. **Remotion:** `faixas({quantidade: 7, cor: '#7BD13A'})`. **Motion:** `TR.faixas(...)`.

## texto-empurra — tipografia cinética
- **Quando:** a palavra-chave da cena A sai e "empurra" a da B, ou cresce até virar o fundo.
- **Como:** a palavra final da A escala/desliza na direção da leitura; a da B entra do mesmo lado.
- **Duração:** 8–14 frames.

## desfoque — blur dissolve
- **Quando:** sonho, memória, foco que muda. Blur de 0 → 20–40 px na A, troca, B de 30 → 0.
- **Duração:** 12–18 frames.

## glitch — falha digital
- **Quando:** tech, erro, "algo está errado" (ex.: divergência de estoque). UM pulso só.
- **Duração:** 4–8 frames. Deslocamento RGB + fatias horizontais. **Nunca** mais de 3 pulsos por
  segundo (risco para fotossensíveis).

---

## Mapa de som

| Transição | Som | Onde |
|---|---|---|
| whip-pan, push, object-wipe | whoosh | pico no meio |
| zoom-punch | whoosh curto + impacto | impacto no assentamento |
| iris, shape-morph | swoosh suave / pop | no fim |
| faixas | sequência de clicks/ticks | um por faixa |
| glitch | ruído digital curto | no pulso |
| dissolve, dip-cor | nenhum ou "swell" | sobe até o meio |

## Duração total com sobreposição

`total = Σ duração das cenas − Σ duração das transições` (Remotion `TransitionSeries` e CapCut).
Para manter cada cena começando no tempo do roteiro, some a duração da transição de entrada à cena.

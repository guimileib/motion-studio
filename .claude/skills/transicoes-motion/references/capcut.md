# Transições no CapCut (desktop e celular)

Os nomes e as categorias dos efeitos mudam entre versões e idiomas do CapCut. Ao instruir o usuário,
descreva a categoria e o resultado ("um zoom que entra na próxima cena"), e diga para escolher o efeito
mais parecido. Abaixo, o caminho geral e os ajustes que tornam o resultado profissional.

## Aplicar uma transição pronta

1. Na linha do tempo, toque no pequeno ícone entre dois clipes (ou aba **Transições** no desktop).
2. Escolha a categoria (Básico, Câmera, Desfoque, Slide, Máscara, Luz, Glitch…) e o efeito.
3. Ajuste a **duração**: 0,2–0,4 s para energia; 0,5–0,8 s para objeto atravessando.
4. Não use "Aplicar a todos", a não ser que seja o corte com a mesma transição-assinatura.
5. Ouça: adicione o whoosh na aba Áudio > Efeitos sonoros, com o pico no meio da transição.

## Receitas que não existem prontas

### Whip pan com motion blur
1. Nos últimos 4 frames da cena A, keyframe de posição X: 0 → −1,2× a largura.
2. Nos primeiros 6 frames da cena B, keyframe X: +1,2× → 0, curva de velocidade "ease out".
3. Efeito de **Desfoque de movimento**/"Motion blur" nos dois trechos.
4. Whoosh com pico no corte.

### Zoom punch
1. Últimos 5 frames da A: escala 100% → 140% (keyframes), curva "ease in".
2. Primeiros 6 frames da B: escala 85% → 102% → 100% (três keyframes).
3. Desfoque de zoom/radial curto na A.

### Object wipe (ex.: frutas caindo do céu)
1. Renderize o overlay no Remotion: `npx remotion render ObjetosCaindo out/objetos.mov --codec=prores --prores-profile=4444`
   (vídeo com transparência), ou use um PNG/vídeo com fundo verde.
2. Coloque o overlay numa faixa acima, centralizado sobre o corte entre A e B.
3. Ajuste para que o frame de cobertura total coincida com o corte.
4. Se for fundo verde: ferramenta **Remover fundo > Chroma key**.

### Match cut
1. Ache o último frame da A com o elemento comum (forma, cor ou posição).
2. Na B, com keyframes de posição/escala, alinhe o elemento comum à mesma posição e tamanho.
3. Corte seco; opcional: 3–4 frames de "Dissolver".

### J-cut e L-cut
1. Toque no clipe > **Extrair áudio** (ou separar).
2. J-cut: arraste o início do áudio da B 0,3–1 s para antes do corte.
3. L-cut: arraste o fim do áudio da A para depois do corte.

### Íris a partir de um ponto
1. Duplique a cena B numa faixa acima, começando antes do corte.
2. Aplique **Máscara > Círculo** na B, posicione no ponto de interesse.
3. Keyframe do tamanho da máscara: 0 → maior que a tela em 0,4–0,6 s, ease in-out.
4. Desfoque da borda da máscara 5–10%.

## Ajustes finais
- Curvas de velocidade: prefira "ease in/out" ao padrão linear.
- Exporte a 1080×1920, 30 fps (ou 60 se o motion tiver muito movimento), taxa de bits "Recomendada" ou maior.
- Confira as zonas seguras do Reels antes de exportar (legenda e logo longe das bordas de baixo e da direita).

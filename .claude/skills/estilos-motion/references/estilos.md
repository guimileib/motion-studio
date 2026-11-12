# Catálogo de estilos

Estilos 01–07: adaptados do tutorial "Claude motion videos, step by step" (@janustiu). O original é
para vídeos de até 10 s, sem narração, com a palavra "MOTION" no fim. Aqui cada estilo vira uma
**linguagem visual** aplicada a um Reels narrado: o mesmo dispositivo atravessa todas as cenas, e o
fechamento escreve a ideia-chave ou o CTA do roteiro, não "MOTION".

Anatomia de um pedido de estilo (use ao escrever o storyboard):
**abertura** (o que é, duração, formato) · **ideia** (um dispositivo só) · **batidas** (uma linha por
intervalo de tempo: o que está na tela, o que se move, as palavras) · **visual** (fundo, paleta em hex,
tipo, textura) · **movimento** (onde é rápido, onde segura, como as cenas passam) · **som** (andamento,
instrumentos, um som por ação).

---

## 00 · Flat da marca
- **Ideia:** cartões, ícones e objetos desenhados em flat que entram em bloco, ancorados nas palavras faladas.
- **Visual:** paleta e fontes da marca do projeto (ex.: Visualize+ `#1D2744` / `#34D5EF`, League Gothic + Poppins), partículas suaves, sem foto.
- **Movimento:** entradas com a curva da marca (0,22, 1, 0,36, 1), 600 ms, deslocamento de 24 px; molas curtas nos destaques.
- **Som:** só narração, ou trilha leve sintetizada.
- **Dificuldade:** fácil. Referência pronta: v01 Visualize+ (`remotion/src/projetos/visualize/`).
- **Bom para:** qualquer tema; o padrão seguro de marca.

## 01 · Linha contínua
- **Ideia:** uma única linha que nunca levanta desenha tudo: começa como gráfico, se desfaz e vira cada objeto do roteiro (o esquilo, a cadeira, o celular…) e escreve a frase final em letra cursiva.
- **Visual:** papel quadriculado `#F4F1EA`, grade `#DAD5CA` 1 px, linha azul elétrico `#2F5BFF` 6 px com ponta redonda e leve tremor de tinta, ponto brilhante na ponta da caneta. Sem preenchimentos.
- **Movimento:** ponta da caneta em velocidade constante de desenho, acelera em retas longas; cada forma nasce da anterior se desfazendo, nunca por corte; câmera segue a ponta.
- **Som:** marimba e baixo pinçado ~110 BPM, risco de caneta que acompanha a velocidade, "tic" em cada marca, pluck quando a forma fecha.
- **Dificuldade:** média. **Se der errado:** "A linha é um caminho único, sem quebra. Confira todos os quadros."
- **Bom para:** dados, crescimento, raciocínio passo a passo (v03 geleias, v07 números do site).

## 02 · Bola única (showreel)
- **Ideia:** uma bola vermelha está em todos os planos; cada cena é uma técnica de motion agindo sobre ela (quique com squash, inundação de cor, órbita, grade de losangos, túnel, estilhaço que vira o ponto final da frase).
- **Visual:** quase-preto `#111116`, creme `#EFEBE4`, vermelho `#FF3319`, cobalto `#2A42FF`. Formas chapadas, grotesca extra-negrito + rótulos em mono; cantoneiras, contador "01 / 05" e timecode dentro da zona segura.
- **Movimento:** estalos de 2–4 quadros contra pausas legíveis, peso real nos quiques, cortes secos na batida.
- **Som:** eletrônico 128 BPM, thud de madeira no quique, clique por letra, lâmina no corte, riser no túnel, silêncio, estilhaço + grave no fechamento.
- **Dificuldade:** fácil. **Se der errado:** mantenha a bola em todo plano — é o que faz parecer reel e não lista de efeitos.
- **Bom para:** "o diferente", destaque, um elemento só (v01, v02 rebanho).

## 03 · Terminal ASCII — RETIRADO (o usuário não gostou, 10/11/2026; não oferecer)
- **Ideia:** tudo é desenhado só com caracteres monoespaçados, como um demo 3D rodando num terminal; o cursor digita os títulos.
- **Técnica:** geometria 3D própria, brilho amostrado numa grade de ~90–120 colunas e mapeado em `" .:-=+*#%@"`; nada fora da grade.
- **Visual:** preto `#000000`, verde fósforo `#33FF66` com brilho leve, curvatura CRT, scanlines e flicker; uma fonte mono.
- **Movimento:** rotação 3D suave dentro da grade rígida; digitação linear; glitches de 2–3 quadros.
- **Som:** techno mínimo ~124 BPM, teclado mecânico, zumbido de CRT, chirps no glitch, cascata de ticks.
- **Dificuldade:** média. **Se der errado:** cabeça borrada → grade mais densa (~120 colunas).
- **Bom para:** IA, GEO, SEO, automação (v06 IA responde antes do clique).

## 04 · Pixel dither — RETIRADO (o usuário não gostou, 10/11/2026; não oferecer)
- **Ideia:** um objeto liso colapsa em pixels e o resto do vídeo é pixel art de Game Boy; a resolução é o efeito.
- **Técnica:** cenas em 135×240 ampliadas para 1080×1920 sem suavização (nearest-neighbour), dithering Bayer ordenado, 4 cores estritas.
- **Visual:** `#0F380F`, `#306230`, `#8BAC0F`, `#9BBC0F` (ou 4 tons da marca), scanlines leves, grade de LCD.
- **Movimento:** em degraus, animado "em dois" (sensação de 12 fps dentro dos 30 fps); estalos instantâneos.
- **Som:** chiptune ~140 BPM (onda quadrada, triangular, ruído), blip a cada degrau, boing no quique, moeda no fim.
- **Dificuldade:** fácil — o melhor primeiro teste. Pixel art esconde pequenas falhas.
- **Bom para:** velocidade, carregamento, jogo de atenção (v07 3·10·20, v08 Instagram).

## 05 · Risografia em stop motion
- **Ideia:** recortes de papel em duas tintas de riso deslizam, viram e se empilham sobre uma mesa, como curta artesanal — imperfeito de propósito.
- **Visual:** papel `#F3EFE6` com fibras, rosa fluor `#FF48B0` e verde-azulado `#00838A` + sobreposição, retícula visível, grão, desregistro de 3 px, sombras curtas.
- **Movimento:** "em três" (~8 fps) com tremor quadro a quadro em cada forma; squash ao pousar.
- **Som:** lo-fi com piano de brinquedo, contrabaixo e vassourinha ~100 BPM; papel deslizando, thump de cartão, carimbo no fim.
- **Dificuldade:** média. **Se der errado:** muito limpo/digital → mais desregistro e mais jitter.
- **Bom para:** pequeno negócio, festa, cotidiano, tom humano (v05 momentos, v09 rosto).

## 06 · Códice renascentista
- **Ideia:** uma pena desenha num caderno de inventor (original, não cópia de Da Vinci): geometria em giz vermelho, contorno em sépia, hachura, anotações espelhadas; o desenho ganha vida e sai voando da página.
- **Visual:** pergaminho `#E9D9B5` com manchas e vinheta, sépia `#5A3A1E` com peso de linha variado e borrões, giz vermelho `#A4452C` só na construção; hachura para toda sombra; sem degradê digital.
- **Movimento:** ritmo de mão (traços rápidos, pausas pequenas); o voo é o único momento rápido; virada de página com curvatura real.
- **Som:** alaúde ou cravo lento, pena arranhando a cada traço, rangidos de engrenagem, farfalhar na virada.
- **Dificuldade:** difícil (2–3 rodadas na hachura). Lembre a ordem: construção → contorno → hachura.
- **Bom para:** estudos, história, autoridade (v01 1933, v06 Hopkins 1923, v09 estudos de Princeton/Harvard).

## 07 · Tinta na água
- **Ideia:** milhares de partículas se comportam como tinta caindo na água — caem, curvam, florescem em câmera lenta — e um campo de fluxo as condensa na palavra-chave, que depois se dissolve.
- **Técnica:** ruído curl para turbulência, gravidade e arrasto leves; na fase das letras, cada partícula puxa para um ponto amostrado da palavra; mistura aditiva em baixa opacidade.
- **Visual:** água branca `#FAFAFA` com cáusticas sutis, índigo `#1B1F6B`, magenta `#C2185B` e o violeta da mistura; macro sedoso, sem contornos.
- **Movimento:** câmera lenta o tempo todo, orgânico, nunca linear; formação das letras gradual.
- **Som:** ambiente com piano lento e reverb longo, sem bateria, plunk grave em cada gota.
- **Dificuldade:** difícil e o render mais pesado. **Se der errado:** palavra ilegível → mais partículas assentam nas letras.
- **Bom para:** memória, percepção, emoção (v01 memória, v05 lembrança, v09 primeira impressão).

---

## Paleta: do estilo ou da marca

Cada estilo funciona com a paleta original (mais fiel ao look) ou trocando só os hex pelos da marca
(mais reconhecível no feed). Pergunte sempre. Com a marca Visualize+: fundo `#1D2744`, ciano `#34D5EF`,
azul-céu `#46A1CD`, royal `#0A248B`, aço `#4481B5`; títulos League Gothic, textos Poppins.

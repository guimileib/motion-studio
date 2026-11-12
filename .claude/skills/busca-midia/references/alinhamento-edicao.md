# Alinhando a mídia com a edição

## Transição → o que procurar no clipe

| Transição (catálogo) | Fim da cena A | Começo da cena B | Termos úteis |
|---|---|---|---|
| whip-pan | câmera se movendo rápido para o lado X | movimento vindo do mesmo lado | `fast pan`, `whip pan`, `tracking shot` |
| zoom-punch / zoom-through | objeto central, câmera se aproximando | plano centralizado | `push in`, `dolly in`, `close up` |
| match-cut | forma/cor marcante numa posição | forma/cor parecida na mesma posição | descreva a forma: `round`, `circle`, `red` |
| object-wipe | qualquer; o objeto cobre | qualquer | — (o objeto vem do motion) |
| iris | ponto de interesse claro (produto, botão) | — | `product close up`, `isolated` |
| push | movimento na direção do push, ou plano estático | idem | `static shot`, `tracking` |
| dissolve | planos de clima, pouca informação | idem | `ambient`, `slow motion`, `bokeh` |

## Ritmo

- Corte a cada 1,5–3 s em anúncio; o clipe precisa de 0,5 s de folga em cada ponta para transição.
- Slow motion (60/120 fps) dá margem para acelerar ou desacelerar no editor.
- Prefira clipes que já começam em movimento: o primeiro frame do clipe é o primeiro frame da cena.

## Escala e composição

- Sequência clássica: plano aberto (onde estamos) → médio (o que acontece) → fechado (o detalhe que importa).
- No vertical, o assunto no centro ou no terço inferior, deixando o terço de cima para o título.
- Vídeo horizontal pode virar vertical com recorte (crop 9:16) só se o assunto estiver no centro e a
  resolução permitir (lado menor ≥ 1080 depois do recorte → original 4K).

## Cor

- Escolha clipes com a temperatura parecida (todos quentes ou todos frios).
- Aplique um tratamento único no editor (LUT ou ajuste leve) para unificar fontes diferentes.
- A cor da marca entra nos elementos de motion (textos, cards, objetos), não precisa estar no clipe.

## Checagem rápida de um clipe baixado

```bash
ffprobe -v error -show_entries stream=width,height,r_frame_rate -show_entries format=duration -of compact clipe.mp4
ffmpeg -ss 0.5 -i clipe.mp4 -frames:v 1 -y /tmp/inicio.jpg   # veja o começo
ffmpeg -sseof -0.5 -i clipe.mp4 -frames:v 1 -y /tmp/fim.jpg  # e o fim
```

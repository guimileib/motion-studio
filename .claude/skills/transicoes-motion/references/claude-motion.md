# Transições no Motion do Claude

O Motion do Claude (artifact de animação no claude.ai) roda cada cena como módulo próprio; tudo na
tela é função pura de `t` (segundos desde o início da cena) e **nada passa de uma cena para a
outra**. Por isso, transição lá é feita em duas metades que se encontram no corte.

## A técnica das duas metades

1. Escolha a duração `D` da transição e o instante em que ela começa na cena A: `t0A = durA − D/2`
   (a troca acontece no meio, exatamente no corte).
2. Na cena A, desenhe a transição com `t0 = t0A`.
3. Na cena B, desenhe a MESMA transição, com a MESMA semente, com `t0 = t0A − durA` (negativo).
   Em `t = 0` da B, o quadro é idêntico ao último da A.
4. O conteúdo da A some por baixo da cobertura (opacidade 1 → 0 nos últimos 0,3–0,4 s) e o da B
   só entra quando a cobertura passa.

Exemplo com a chuva de objetos (cena A de 4 s, transição de ~1,6 s):

```js
// shared.js: cole templates/claude-motion/transicoes.js e defina os objetos da marca
// cena A
init(kit) { this.out = TR.chuva(kit, { seed: 11, t0: 3.2, objetos: FRUTAS }); },
render(t) { /* conteúdo… */ this.out.render(t); },
// cena B (mesma semente; t0 = 3.2 − 4 = −0.8)
init(kit) { this.inn = TR.chuva(kit, { seed: 11, t0: -0.8, objetos: FRUTAS }); },
render(t) { this.inn.render(t); },
```

Use uma semente diferente para cada passagem, para a chuva não se repetir igual.

## Helpers prontos (`templates/claude-motion/transicoes.js`)

| Helper | Catálogo | Uso |
|---|---|---|
| `TR.chuva(kit, {seed, t0, n, objetos, tamanho})` | object-wipe | devolve `{render(t)}`; mesma chamada nas duas cenas |
| `TR.faixas(kit, {t0, dur, n, cor})` | faixas | idem |
| `TR.iris(style, t, {t0, dur, x, y, modo})` | iris | `modo: 'fecha'` no fim da A, `'abre'` no começo da B |
| `TR.zoomPunch(style, t, {t0, dur, lado, escala})` | zoom-punch | `lado: 'saida'` na A, `'entrada'` na B |
| `TR.whip(style, t, {t0, dur, direcao, lado})` | whip-pan | idem; mesma direção nas duas |

## Regras do player que afetam transições

- Sem transições/animações CSS nem timers: tudo sai de `t` no `render`.
- Aleatoriedade só com `kit.rng(seed)`.
- Nada pisca mais de 3 vezes por segundo.
- Som: no `score.js`, `S.fx('whoosh', T.<cenaA> + t0A, {dur: D})` com o pico no corte.
- Marcação de strings: markup em aspas simples, `style="…"` em aspas duplas, sem aspas dentro do style.

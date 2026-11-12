---
name: busca-midia
description: Busca, escolhe e baixa imagens e vídeos de banco (Pexels, Pixabay, Unsplash) e da web aberta com licença verificada, alinhados à edição — cada cena do roteiro recebe clipes com a orientação, duração, movimento, cor e enquadramento que combinam com a transição e o ritmo — e registra créditos. Use sempre que o usuário pedir b-roll, imagem de fundo, vídeo de banco, stock footage, "acha um vídeo de…", referências visuais, ou quando o roteiro.json tiver cenas com midia.busca.
---

# Busca de mídia alinhada à edição

Mídia de banco boa não é "a mais bonita": é a que **encaixa no corte** — orientação certa, duração
suficiente, movimento na direção da transição, cor da paleta, escala que progride. E só entra com
licença verificada.

## 1. Do roteiro para a lista de planos (shot list)

Para cada cena do `roteiro.json` (ou do pedido), defina antes de buscar:

| Campo | Pergunta | Exemplo |
|---|---|---|
| Assunto | O que precisa estar no quadro? | caixas de laranja na banca |
| Escala | aberto, médio, fechado, detalhe? | detalhe (mão pegando a fruta) |
| Movimento | câmera parada, travelling, slow motion, timelapse? Para que lado? | travelling para a direita |
| Cor/luz | combina com a paleta? dia/noite? | tons verdes, luz natural |
| Duração | ≥ duração da cena + 0,5 s (folga para a transição) | ≥ 5 s |
| Orientação | vertical 9:16 para Reels; horizontal se for recortar | vertical |
| Espaço para texto | onde o título vai ficar? Precisa de área "limpa" | terço de cima limpo |

Regras de alinhamento com a edição (detalhes em `references/alinhamento-edicao.md`):
- **Transição dita o movimento:** whip pan para a esquerda → clipe com movimento para a esquerda no
  fim da cena A e no começo da B. Match cut → forma/cor parecida nos dois lados.
- **Progressão de escala:** aberto → médio → fechado ao longo do vídeo; evite dois planos iguais seguidos.
- **Consistência:** mesma temperatura de cor, mesma estética (não misture foto de banco "clichê"
  com motion chapado sem tratar).
- **Evite:** marca d'água, logos de terceiros, rostos olhando para a câmera em anúncio (parece
  depoimento), texto embutido, imagem que contradiz o roteiro.

## 2. Termos de busca

Escreva 3–5 termos por cena em `cenas[].midia.busca`, **inglês primeiro** (os acervos são maiores em
inglês) e depois português. Do concreto ao amplo:
`"hand picking orange supermarket close up"`, `"oranges produce section"`, `"fresh fruit market"`,
`"hortifruti supermercado"`. Inclua o movimento quando importa (`slow motion`, `top view`,
`tracking shot`, `timelapse`).

## 3. Rode a busca (Claude Code)

```bash
# lista candidatos de todas as cenas e baixa o 1º de cada
python .claude/skills/busca-midia/scripts/buscar_midia.py --roteiro projetos/<slug>/roteiro.json --baixar

# busca avulsa
python .claude/skills/busca-midia/scripts/buscar_midia.py --q "fresh oranges falling slow motion" --tipo video --orientacao vertical
```

O script consulta Pexels, Pixabay e Unsplash (só fotos), filtra orientação e duração mínima, escolhe
o arquivo de vídeo mais próximo de 1080 p, guarda cache de 24 h (exigência da Pixabay), faz o "ping"
de download do Unsplash e grava `midia/manifest.json` (todos os candidatos + `escolhido` por cena) e
`CREDITOS.md`. Chaves no `.env`: `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `UNSPLASH_ACCESS_KEY`
(gratuitas nos sites de desenvolvedor de cada banco). Sem uma chave, a fonte é pulada com aviso.

## 4. Escolha com critério

Apresente ao usuário 3 candidatos por cena (link da página, resolução, duração, por que encaixa) e
recomende um. Para trocar, mude `escolhido` no `manifest.json` e rode de novo com `--baixar`.
Verifique cada escolhido: abra a prévia (Read numa imagem baixada ou num frame extraído com
`ffmpeg -ss 1 -i clipe.mp4 -frames:v 1 frame.jpg`) e confira o checklist.

## 5. Busca na web aberta

Quando os bancos não têm o assunto (produto específico, local real, evento): use a busca web
restringindo a fontes com licença clara — Wikimedia Commons (CC0/CC BY/CC BY-SA, com crédito),
Mixkit, Coverr, NASA (domínio público), sites oficiais de imprensa da própria marca. Abra a página e
confirme a licença antes de baixar. **Nunca** use imagem de Google Imagens, Instagram, TikTok, YouTube,
Pinterest ou site de notícias sem licença explícita. Licenças e o que cada uma permite:
`references/licencas.md`.

## 6. Checklist

- [ ] Cada cena tem mídia com orientação certa e duração ≥ cena + 0,5 s?
- [ ] O movimento do clipe combina com a transição de entrada/saída?
- [ ] Escala varia entre cenas seguidas? Cor consistente com a paleta?
- [ ] Área limpa para o texto na tela, sem marca d'água, logo de terceiro ou texto embutido?
- [ ] Pessoas identificáveis não aparecem endossando o produto (licenças de banco proíbem isso)?
- [ ] Licença confirmada e crédito registrado em `CREDITOS.md`?

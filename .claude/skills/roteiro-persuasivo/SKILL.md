---
name: roteiro-persuasivo
description: Escreve roteiros profissionais de vídeo (Reels, TikTok, Shorts, anúncios, VSL, motion de produto) baseados em persuasão e padrões de marketing — níveis de consciência, AIDA, PAS, BAB, PASTOR, gatilhos de Cialdini, quebra de objeção — e entrega o roteiro cronometrado em roteiro.md e roteiro.json para as skills de mídia, narração, legenda e transição. Use sempre que o usuário pedir roteiro, script, copy de vídeo, gancho, CTA, anúncio, VSL, "vídeo que venda", "vídeo que convença", mesmo sem citar marketing.
---

# Roteiro persuasivo

Você é um copywriter de resposta direta que também sabe editar vídeo. Um roteiro bom faz uma pessoa
específica sentir uma dor específica, enxergar uma saída crível e dar UM próximo passo. Cada segundo
tem um trabalho; o que não trabalha, sai.

## 1. Diagnóstico antes de escrever (2 minutos que salvam o roteiro)

Extraia do pedido, de arquivos ou do site do cliente; pergunte só o que for decisivo (no máximo uma
pergunta) e declare o que assumiu.

1. **Quem compra** — cargo/situação concreta ("gerente de FLV de supermercado de bairro"), não demografia.
2. **Dor, desejo, objeção** — nas palavras do cliente. A objeção principal é o que ele diria para não agir.
3. **Nível de consciência** (Eugene Schwartz) — decide por onde o roteiro começa:

| Nível | A pessoa… | O roteiro começa por… |
|---|---|---|
| Inconsciente | não sabe que tem o problema | uma cena/estatística que revela o problema |
| Consciente do problema | sente a dor, não conhece soluções | a dor, nomeada com precisão |
| Consciente da solução | sabe que existe solução, não conhece você | o mecanismo: por que o seu jeito funciona |
| Consciente do produto | conhece você, não decidiu | prova, comparação, quebra de objeção |
| Totalmente consciente | só espera o motivo | oferta + CTA direto |

4. **Mecanismo único** — o "como" que torna a promessa crível (ex.: "calcula o pedido pela venda real").
5. **Prova disponível** — números reais, cases, demonstração, depoimento real. Sem prova real, use
   demonstração do produto, nunca invente.
6. **Um objetivo e um CTA** — alcance, lead, venda ou agendamento. Um vídeo, uma ação.
7. **Formato** — plataforma, duração, proporção, se tem narração, rosto ou só motion.

## 2. Escolha a estrutura

Detalhes e exemplos de cada uma em `references/frameworks.md`.

| Estrutura | Melhor para | Esqueleto |
|---|---|---|
| **PAS** | consciente do problema, anúncio curto | Problema → Agitação → Solução |
| **AIDA** | topo/meio de funil, motion de produto | Atenção → Interesse → Desejo → Ação |
| **BAB** | transformação visual (antes/depois) | Antes → Depois → Ponte |
| **PASTOR** | VSL e vídeos de 60 s+ | Problema → Amplificar → Solução/Story → Transformação → Oferta → Resposta |
| **Gancho-Retenção-Recompensa** | conteúdo orgânico | Gancho → loop aberto → entrega → payoff + CTA |
| **Mito × Verdade** | autoridade | "Todo mundo diz X" → "Na prática Y" → prova → CTA |
| **Demonstração** | produto visual/SaaS | resultado primeiro → como → resultado de novo |

Regra: para 15–30 s, PAS ou AIDA comprimida; para 45–90 s, PASTOR ou storytelling.

## 3. Escreva nesta ordem

1. **Promessa em uma frase.** Se não cabe, a ideia não está clara.
2. **Gancho (0–3 s)** — fala + texto na tela + ação visual dizendo a mesma coisa. Escreva 3 opções de
   tipos diferentes (banco em `references/ganchos.md`): pergunta de dor, erro comum, número
   específico, contrarian, identificação, cena inesperada.
3. **Corpo** — a estrutura escolhida, uma ideia por cena, cada cena de 2 a 6 s.
4. **Prova** — o elemento mais forte disponível, o mais cedo possível depois do problema.
5. **Objeção principal quebrada** — dentro do corpo, sem nomeá-la como objeção.
6. **CTA** — verbo + benefício + facilidade ("Chama no WhatsApp e veja o pedido da sua loja").
   Se não houver CTA explícito pedido, feche com a marca + promessa.

## 4. Regras de copy que mais pesam

- **Específico vence genérico:** "perda de 4,7% na banca" > "perdas". Use só números com fonte; cite
  a fonte na legenda do post ou na tela quando for estatística de mercado.
- **Linguagem do cliente**, não do fornecedor: "banana que estraga na banca" > "deterioração de perecíveis".
- **Benefício antes de recurso:** recurso = o que faz; benefício = o que muda na vida dele.
- **"Você" mais que "nós".** A marca entra como guia, o cliente é o herói.
- **Frases para falar:** curtas, voz ativa, uma ideia por frase. Leia em voz alta cronometrando.
- **Texto na tela ≠ narração inteira:** na tela vai a palavra-chave da cena (3–7 palavras).
- **Ritmo de narração em pt-BR:** ~2,5 palavras/s em anúncio animado (2,2 calmo, 2,8 acelerado).
  Calcule: `palavras ≈ duração_da_cena × 2,5`. Roteiro que não cabe no tempo é o erro mais comum.

## 5. Gatilhos de persuasão (use com verdade)

Os 7 princípios de Cialdini — reciprocidade, compromisso/coerência, prova social, autoridade,
afinidade, escassez e unidade — e como aplicar cada um em vídeo estão em
`references/gatilhos-e-etica.md`. Use 1 a 3 por vídeo, nunca todos. Escassez e urgência só quando
forem reais (prazo, vagas, lote). Prova social só com dado ou depoimento real e autorizado.

## 6. Entrega

Sempre dois arquivos em `projetos/<slug>/` (crie a pasta):

1. **`roteiro.md`** — para o humano aprovar, no modelo de `templates/roteiro.md`: promessa, público,
   nível de consciência, estrutura, 3 ganchos, tabela cena a cena (tempo, narração, texto na tela,
   visual, mídia, transição), CTA, legenda do post, notas de edição.
2. **`roteiro.json`** — o contrato com as outras skills, no esquema
   `templates/roteiro.schema.json`. Campos que as outras skills leem:
   - `cenas[].narracao` (legenda) e `cenas[].narracao_tts` (opcional, grafia para a voz: siglas,
     números e preços escritos como se falam) → `legendas-tts`;
   - `cenas[].midia.busca` (3–5 termos, em inglês primeiro, depois português) → `busca-midia`;
   - `cenas[].transicao_saida` (`tipo` do catálogo da skill `transicoes-motion`, `duracao_s`, `som`)
     → `transicoes-motion`.

Valide o JSON depois de escrever: `python -c "import json;json.load(open('projetos/<slug>/roteiro.json'))"`
e confira que a soma de `duracao_s` bate com `duracao_alvo_s`.

Se o usuário só quiser o texto no chat, entregue a tabela do `roteiro.md` na resposta e ofereça
gerar os arquivos.

## 7. Checklist antes de entregar

- [ ] A promessa cabe em uma frase e o gancho a anuncia nos primeiros 3 s?
- [ ] O começo bate com o nível de consciência do público?
- [ ] Cada cena tem uma ideia, e a narração cabe no tempo (≈2,5 palavras/s)?
- [ ] Existe prova real ou demonstração — e nenhum número inventado?
- [ ] A objeção principal foi respondida?
- [ ] Um único CTA, coerente com o objetivo?
- [ ] O texto na tela funciona sem som?
- [ ] Gatilhos usados com verdade (sem escassez falsa, sem depoimento inventado)?
- [ ] Publicidade de parceiro identificada como tal (CONAR)? Promessas de saúde/finanças sem garantia?
- [ ] `roteiro.json` válido e somando a duração-alvo?

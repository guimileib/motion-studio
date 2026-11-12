# Escrevendo texto para a voz (ElevenLabs, pt-BR)

## Siglas, marcas e termos técnicos

| Legenda (`narracao`) | Voz (`narracao_tts`) |
|---|---|
| FLV | éfe éle vê (ou "frutas, legumes e verduras" na 1ª vez) |
| IA | I.A. / inteligência artificial |
| ERP | é érre pê |
| WhatsApp | uótsap (só se a voz errar) |
| veta.ia.br | veta ponto i a ponto bê érre |
| KPI | cá pê i |

Teste a pronúncia de nomes de marca em uma geração curta antes do roteiro inteiro. Se a voz insistir no
erro, mude a grafia fonética ou crie um dicionário de pronúncia na ElevenLabs.

## Números

| Escrito | Para a voz |
|---|---|
| R$ 4,57/kg | quatro reais e cinquenta e sete centavos o quilo |
| 30% | trinta por cento |
| 4,7% | quatro vírgula sete por cento |
| +350 | mais de trezentos e cinquenta |
| 1º | primeiro |
| 24/7 | vinte e quatro horas, sete dias por semana |
| 2026 | dois mil e vinte e seis |

A normalização automática (`apply_text_normalization: auto`) acerta muitos casos, mas preço,
porcentagem com vírgula e unidade são os que mais erram — escreva por extenso.

## Ritmo e pausas

- Frases de 5 a 12 palavras. Uma ideia por frase.
- Ponto final entre ideias dá respiro; vírgula para listas; reticências para suspense.
- Pergunta retórica com "?" sobe a entonação no fim — ótima para gancho.
- Pausa exata: `<break time="0.5s" />` (até ~3 s) nos modelos multilingual v2, flash e turbo.
  Pausas demais deixam a fala instável; use poucas.
- `eleven_v3`: aceita tags de emoção/entrega entre colchetes (`[excited]`, `[whispers]`, `[laughs]`)
  e não usa `<break>`. Gere algumas versões e escolha a melhor.

## Entonação de anúncio

- Gancho: pergunta curta, sem "Olá, tudo bem?".
- Benefício: verbo no presente, frase afirmativa curta.
- Assinatura: nome da marca isolado, com ponto ("Veta I.A.").
- Evite MAIÚSCULAS para ênfase; reescreva a frase para a palavra importante ficar no fim.

## Duração

Palavras ≈ segundos × 2,5. Se a fala passar do tempo da cena:
1. corte palavras (artigos, "que", "você sabe…");
2. só depois, velocidade 1,05–1,15;
3. último caso: estique a cena no `roteiro.json` (e avise a skill de transições).

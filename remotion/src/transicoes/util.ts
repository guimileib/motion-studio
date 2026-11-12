// Utilidades compartilhadas pelas transições.
// Convenção: a cena que sai usa a 1ª metade do progresso (0 → 0,5) e a que entra usa a 2ª (0,5 → 1).
// Assim a troca acontece exatamente no meio, coberta pelo efeito.

export const clamp01 = (x: number) => (x < 0 ? 0 : x > 1 ? 1 : x);

/** Progresso local da metade que cabe a esta cena (0 → 1) e se ela está visível. */
export const metade = (p: number, direcao: 'entering' | 'exiting') =>
	direcao === 'exiting'
		? {q: clamp01(p / 0.5), visivel: p < 0.5}
		: {q: clamp01((p - 0.5) / 0.5), visivel: p >= 0.5};

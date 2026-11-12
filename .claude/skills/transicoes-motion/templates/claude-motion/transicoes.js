// Helpers de transição para o Motion do Claude (cole no modules/shared.js do filme).
// Tudo é função pura de t. Nada atravessa o corte: a cena A desenha a 1ª metade, a cena B a 2ª,
// com a MESMA semente e o mesmo t0 relativo (t0 na B = t0 na A − duração da A).
// Os helpers recebem o `kit` da cena como parâmetro (nunca o kit do shared.js).

window.TR = (function () {
  // ---------- chuva de objetos (object-wipe) ----------
  // objetos: lista de strings de markup (<svg>…</svg>) ou de URLs de imagem (kit.assets.url('x.webp')).
  function chuva(kit, opt) {
    const r = kit.rng(opt.seed || 3), W = kit.W, H = kit.H, n = opt.n || 26, t0 = opt.t0;
    const [mn, mx] = opt.tamanho || [170, 320];
    const objs = opt.objetos || [];
    const layer = kit.h('<div style="position:absolute;inset:0;z-index:' + (opt.z || 8) + ';pointer-events:none"></div>');
    kit.stage.append(layer);
    const items = [];
    for (let i = 0; i < n; i++) {
      const s = mn + r() * (mx - mn), src = objs[Math.floor(r() * objs.length)] || '';
      const inner = src.trim().charAt(0) === '<' ? src : '<img src="' + src + '" style="width:100%;height:100%;object-fit:contain;display:block">';
      const el = kit.h('<div style="position:absolute;left:0;top:0;width:' + s + 'px;height:' + s + 'px">' + inner + '</div>');
      layer.append(el);
      // posições por faixas em toda a largura, depois um pouco de aleatoriedade: cobertura garantida
      items.push({ st: el.style, s, x: (i / n) * (W + 160) - 160 + (r() - 0.5) * 140, d: r() * 0.55, fall: 0.95 + r() * 0.35, r0: (r() - 0.5) * 90, spin: (r() - 0.5) * 260 });
    }
    return { mid: t0 + 0.8, end: t0 + 1.9, render(t) {
      for (const it of items) {
        const p = (t - t0 - it.d) / it.fall;
        if (p <= 0 || p >= 1) { it.st.opacity = 0; continue; }
        const y = kit.lerp(-it.s - 40, H + 40, kit.ei(p) * 0.7 + p * 0.3); // gravidade + velocidade inicial
        it.st.opacity = 1;
        it.st.transform = 'translate(' + it.x.toFixed(1) + 'px,' + y.toFixed(1) + 'px) rotate(' + (it.r0 + it.spin * p).toFixed(1) + 'deg)';
      }
    } };
  }

  // ---------- íris ----------
  // Aplica clip-path circular no estilo de um elemento. modo 'fecha' (fim da cena A) ou 'abre' (início da B).
  function iris(style, t, o) {
    const p = kit_clamp((t - o.t0) / o.dur), e = p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
    const raio = o.modo === 'fecha' ? 150 * (1 - e) : 150 * e; // % do lado maior: 150 cobre a tela toda
    style.clipPath = 'circle(' + raio.toFixed(2) + '% at ' + ((o.x ?? 0.5) * 100) + '% ' + ((o.y ?? 0.5) * 100) + '%)';
  }

  // ---------- faixas (stripes) ----------
  // Mesma chamada nas duas cenas. 1ª metade: faixas cobrem; 2ª metade: descobrem na mesma direção.
  function faixas(kit, o) {
    const n = o.n || 7, cor = o.cor || 'var(--main)', H = kit.H, W = kit.W, h = H / n;
    const layer = kit.h('<div style="position:absolute;inset:0;z-index:' + (o.z || 9) + ';pointer-events:none"></div>');
    kit.stage.append(layer);
    const bars = [];
    for (let i = 0; i < n; i++) {
      const b = kit.h('<div style="position:absolute;left:0;width:' + W + 'px;top:' + (i * h - 1) + 'px;height:' + (h + 2) + 'px;background:' + cor + '"></div>');
      layer.append(b); bars.push(b.style);
    }
    const stag = o.escalonamento || 0.035, dur = o.dur || 0.6;
    return { render(t) {
      bars.forEach((s, i) => {
        const p = kit_clamp((t - o.t0 - i * stag) / (dur - stag * (n - 1)));
        const a = p < 0.5 ? kit.eio(p * 2) : 1, b = p < 0.5 ? 0 : kit.eio((p - 0.5) * 2);
        // cobre da esquerda para a direita e descobre para a direita
        s.transformOrigin = p < 0.5 ? '0 50%' : '100% 50%';
        s.transform = 'scaleX(' + (p < 0.5 ? a : 1 - b).toFixed(4) + ')';
        s.opacity = p <= 0 || p >= 1 ? 0 : 1;
      });
    } };
  }

  // ---------- zoom punch ----------
  // lado 'saida': A cresce e desfoca no fim. lado 'entrada': B começa menor e assenta com overshoot.
  function zoomPunch(style, t, o) {
    const p = kit_clamp((t - o.t0) / o.dur);
    if (o.lado === 'saida') {
      const e = p * p * p;
      style.transform = 'scale(' + (1 + (o.escala || 0.4) * e).toFixed(4) + ')';
      style.filter = 'blur(' + (12 * e).toFixed(2) + 'px)';
    } else {
      const c1 = 1.7, c3 = c1 + 1, e = 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2);
      style.transform = 'scale(' + (0.85 + 0.15 * e).toFixed(4) + ')';
      style.filter = 'blur(' + (10 * (1 - Math.min(1, p * 1.6))).toFixed(2) + 'px)';
    }
  }

  // ---------- whip pan ----------
  function whip(style, t, o) {
    const p = kit_clamp((t - o.t0) / o.dur), W = o.largura || 1080, s = o.direcao === 'direita' ? 1 : -1;
    const x = o.lado === 'saida' ? s * 1.2 * W * p * p * p : -s * 1.2 * W * Math.pow(1 - p, 3);
    const vel = o.lado === 'saida' ? 3 * p * p : 3 * Math.pow(1 - p, 2);
    style.transform = 'translateX(' + x.toFixed(1) + 'px) scaleX(' + (1 + 0.08 * vel).toFixed(4) + ')';
    style.filter = 'blur(' + (18 * vel).toFixed(2) + 'px)';
  }

  function kit_clamp(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  return { chuva, iris, faixas, zoomPunch, whip };
})();

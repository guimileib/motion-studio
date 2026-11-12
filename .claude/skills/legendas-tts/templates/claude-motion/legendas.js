// Legenda estilo Reels para o Motion do Claude (cole no modules/shared.js do filme).
// As palavras vêm de legendas/palavras.json (formato Caption do Remotion, tempos em ms do FILME).
// Salve esse JSON como módulo do filme: modules/legendas.json (kind json).
// Em cada cena:
//   init(kit)  { this.leg = LEG.montar(kit, kit.json('legendas.json'), { cor: 'var(--accent)' }); }
//   render(t)  { this.leg.render(t); }
// O helper converte o tempo da cena em tempo do filme com kit.start + t.

window.LEG = (function () {
  function paginas(caps, janelaMs) {
    const out = [];
    let atual = null;
    for (const c of caps) {
      const txt = c.text;
      if (!atual || c.startMs - atual.ini > janelaMs || /[.!?]$/.test(atual.toks[atual.toks.length - 1].text.trim())) {
        atual = { ini: c.startMs, fim: c.endMs, toks: [] };
        out.push(atual);
      }
      atual.toks.push({ text: txt, de: c.startMs, ate: c.endMs });
      atual.fim = c.endMs;
    }
    out.forEach((p, i) => { const prox = out[i + 1]; p.fim = prox ? Math.min(prox.ini, p.fim + 400) : p.fim + 400; });
    return out;
  }

  function montar(kit, caps, o) {
    o = o || {};
    const pags = paginas(caps || [], o.janelaMs || 800);
    const caixa = kit.h('<div style="position:absolute;left:90px;right:90px;top:' + Math.round(kit.H * (o.y || 0.66)) +
      'px;transform:translateY(-50%);text-align:center;white-space:pre-wrap;font-family:var(--display, var(--sans, system-ui, sans-serif));font-weight:800;font-size:' +
      (o.tamanho || 72) + 'px;line-height:1.12;z-index:' + (o.z || 7) + ';text-shadow:0 4px 14px rgba(0,0,0,.55)"></div>');
    kit.stage.append(caixa);
    let atualIdx = -1, spans = [];
    return { render(t) {
      const ms = (kit.start + t) * 1000;
      let idx = -1;
      for (let i = 0; i < pags.length; i++) if (ms >= pags[i].ini && ms < pags[i].fim) { idx = i; break; }
      if (idx !== atualIdx) {
        atualIdx = idx;
        caixa.textContent = '';
        spans = [];
        if (idx >= 0) for (const tk of pags[idx].toks) {
          if (/^\s/.test(tk.text)) caixa.append(' ');
          const s = kit.el('span', { text: tk.text.trim(), style: 'display:inline-block;padding:0 0.07em' });
          caixa.append(s); spans.push(s);
        }
      }
      if (idx < 0) { caixa.style.opacity = 0; return; }
      const p = pags[idx], e = Math.min(1, (ms - p.ini) / 120);
      caixa.style.opacity = 1;
      caixa.style.transform = 'translateY(-50%) scale(' + (0.9 + 0.1 * e).toFixed(3) + ')';
      p.toks.forEach((tk, i) => {
        const ativo = ms >= tk.de && ms < tk.ate;
        spans[i].style.color = ativo ? (o.cor || 'var(--accent)') : (o.corTexto || 'var(--second)');
        spans[i].style.transform = 'scale(' + (ativo ? 1.05 : 1) + ')';
      });
    } };
  }
  return { montar };
})();

#!/usr/bin/env python3
"""Página de storyboard de vários projetos: estilo, mapa de batidas (cenas com tempos) e folha de contatos.

Uso:
  python storyboard_serie.py --saida projetos/_series/storyboard.html projetos/a/roteiro.json projetos/b/roteiro.json …
  (abre no navegador; --nao-abrir para só gerar)
"""
from __future__ import annotations

import argparse
import html
import json
import os
import webbrowser
from pathlib import Path

NOMES = {
    "00-flat-marca": "00 · Flat da marca", "01-linha-continua": "01 · Linha contínua", "02-bola-unica": "02 · Bola única",
    "03-terminal-ascii": "03 · Terminal ASCII", "04-pixel-dither": "04 · Pixel dither", "05-riso-stop-motion": "05 · Risografia stop motion",
    "06-codice": "06 · Códice renascentista", "07-tinta-na-agua": "07 · Tinta na água",
}

CSS = """
:root{--bg:#0f1220;--card:#181c2e;--linha:#2a3050;--texto:#eef1fb;--suave:#9aa3c7;--acento:#34D5EF}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--texto);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header,main{max-width:1280px;margin:0 auto;padding:24px}h1{font-size:26px;margin:0 0 4px}.sub{color:var(--suave);margin:0}
nav{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}nav a{color:var(--texto);background:var(--card);border:1px solid var(--linha);border-radius:99px;padding:4px 12px;text-decoration:none;font-size:13px}
section{background:var(--card);border:1px solid var(--linha);border-radius:16px;padding:18px 20px;margin-bottom:22px}
h2{margin:0;font-size:21px}.estilo{display:inline-block;margin:6px 0 12px;background:var(--acento);color:#0f1220;font-weight:700;font-size:13px;border-radius:99px;padding:2px 10px}
.meta{color:var(--suave);font-size:13px;margin-left:8px}
table{width:100%;border-collapse:collapse;font-size:14px;margin:6px 0 14px}td,th{border-top:1px solid var(--linha);padding:6px 8px;vertical-align:top;text-align:left}
th{color:var(--suave);font-weight:600}td.tempo{white-space:nowrap;color:var(--acento);font-variant-numeric:tabular-nums}td.tela{font-weight:600}
img{width:100%;border-radius:10px;display:block}
@media(max-width:700px){header,main{padding:16px}td.narr{display:none}}
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roteiros", nargs="+", type=Path)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--titulo", default="Storyboard da série")
    ap.add_argument("--nao-abrir", action="store_true")
    a = ap.parse_args()
    saida = a.saida.resolve()
    secoes, links = [], []
    for p in a.roteiros:
        rot = json.loads(p.read_text(encoding="utf-8"))
        slug = rot.get("slug") or p.parent.name
        est = (rot.get("estilo") or {}).get("id", "")
        voz = "voz real" if not (p.parent / "legendas" / ".estimado").exists() else "tempos estimados (voz ainda na fila)"
        linhas, t = [], 0.0
        for c in rot["cenas"]:
            ini = float(c.get("inicio_s", t))
            t = ini + float(c["duracao_s"])
            linhas.append(f"<tr><td class='tempo'>{ini:.1f}–{t:.1f}s</td><td class='tela'>{html.escape(c.get('texto_tela',''))}</td>"
                          f"<td>{html.escape(c.get('visual',''))}</td><td class='narr'>{html.escape(c.get('narracao',''))}</td></tr>")
        folha = p.parent / "previa" / "folha.jpg"
        img = f"<img src='{html.escape(Path(os.path.relpath(folha, saida.parent)).as_posix())}' alt='Folha de contatos de {html.escape(rot['titulo'])}'>" if folha.exists() else "<p>(sem folha de contatos)</p>"
        ident = rot.get("id") or slug
        links.append(f"<a href='#{slug}'>{html.escape(ident)}</a>")
        secoes.append(
            f"<section id='{slug}'><h2>{html.escape(ident)} · {html.escape(rot['titulo'])}</h2>"
            f"<span class='estilo'>{html.escape(NOMES.get(est, est or 'sem estilo'))} · paleta {html.escape((rot.get('estilo') or {}).get('paleta',''))}</span>"
            f"<span class='meta'>{t:.0f} s · {voz}</span>"
            f"<table><tr><th>Tempo</th><th>Texto na tela</th><th>Visual</th><th class='narr'>Narração</th></tr>{''.join(linhas)}</table>{img}</section>")
    doc = (f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
           f"<title>{html.escape(a.titulo)}</title><style>{CSS}</style></head><body><header><h1>{html.escape(a.titulo)}</h1>"
           f"<p class='sub'>Mapa de batidas e quadros de cada vídeo. Diga no chat o que mudar (vídeo + tempo) ou aprove.</p>"
           f"<nav>{''.join(links)}</nav></header><main>{''.join(secoes)}</main></body></html>")
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(doc, encoding="utf-8")
    print(f"Storyboard: {saida}")
    if not a.nao_abrir:
        webbrowser.open(saida.as_uri())


if __name__ == "__main__":
    main()

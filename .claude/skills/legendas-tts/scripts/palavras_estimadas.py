#!/usr/bin/env python3
"""Gera legendas/palavras.json ESTIMADO (sem voz), espalhando as palavras de cada cena pelo tempo dela.

Serve para montar e revisar o vídeo (storyboard, quadros-chave) antes da narração existir.
Não sobrescreve um palavras.json real; quando o TTS rodar, ele substitui este arquivo.

Uso:
  python palavras_estimadas.py --roteiro projetos/<slug>/roteiro.json [--forcar]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from legendas_lib import _distribuir, palavras_para_captions  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roteiro", type=Path, required=True)
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    rot = json.loads(a.roteiro.read_text(encoding="utf-8"))
    destino = a.roteiro.parent / "legendas" / "palavras.json"
    marca = a.roteiro.parent / "legendas" / ".estimado"
    if destino.exists() and not marca.exists() and not a.forcar:
        sys.exit(f"{destino} já tem tempos reais da voz; use --forcar para sobrescrever")
    t, palavras = 0.0, []
    for c in rot["cenas"]:
        ini = float(c.get("inicio_s", t))
        t = ini + float(c["duracao_s"])
        texto = (c.get("narracao") or "").split()
        if texto:
            palavras += _distribuir(texto, ini + 0.15, t - 0.3)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(palavras_para_captions(palavras), ensure_ascii=False, indent=1), encoding="utf-8")
    marca.write_text("palavras.json estimado (sem voz)\n", encoding="utf-8")
    print(f"{destino}: {len(palavras)} palavras estimadas em {t:.1f}s")


if __name__ == "__main__":
    main()

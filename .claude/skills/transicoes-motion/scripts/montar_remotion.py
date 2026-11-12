#!/usr/bin/env python3
"""Prepara um projeto para renderizar no Remotion (composição VideoRoteiro).

Copia a mídia escolhida (midia/manifest.json), a narração (audio/narracao.mp3) e as legendas
(legendas/palavras.json) para remotion/public/projetos/<slug>/ e grava remotion/props/<slug>.json.

  python .claude/skills/transicoes-motion/scripts/montar_remotion.py --projeto projetos/meu-video
  cd remotion && npx remotion render VideoRoteiro out/meu-video.mp4 --props=props/meu-video.json
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]  # .claude/skills/transicoes-motion/scripts → raiz do repo


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", type=Path, required=True)
    ap.add_argument("--sem-legenda", action="store_true")
    ap.add_argument("--sem-narracao", action="store_true")
    a = ap.parse_args()

    proj = a.projeto.resolve()
    rot = json.loads((proj / "roteiro.json").read_text("utf-8"))
    slug = rot.get("slug") or proj.name
    base = f"projetos/{slug}"
    destino = RAIZ / "remotion" / "public" / base
    destino.mkdir(parents=True, exist_ok=True)

    midias = {}
    man = proj / "midia" / "manifest.json"
    if man.exists():
        for cena, info in json.loads(man.read_text("utf-8")).get("cenas", {}).items():
            esc = info.get("escolhido")
            if esc is None or not info.get("candidatos"):
                continue
            it = info["candidatos"][esc]
            local = it.get("local")
            if not local or not (proj / local).exists():
                print(f"! {cena}: escolhido ainda não baixado (rode buscar_midia.py --baixar)")
                continue
            alvo = destino / local
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(proj / local, alvo)
            midias[cena] = {"arquivo": local, "tipo": it["tipo"]}

    narracao = None
    if not a.sem_narracao and (proj / "audio" / "narracao.mp3").exists():
        (destino / "audio").mkdir(exist_ok=True)
        shutil.copy2(proj / "audio" / "narracao.mp3", destino / "audio" / "narracao.mp3")
        narracao = "audio/narracao.mp3"

    legendas = None
    if not a.sem_legenda and (proj / "legendas" / "palavras.json").exists():
        legendas = json.loads((proj / "legendas" / "palavras.json").read_text("utf-8"))

    cores = rot.get("cores") or {"fundo": "#0E2A22", "texto": "#EAF5E6", "destaque": "#7BD13A"}
    props = {"roteiro": rot, "base": base, "midias": midias, "narracao": narracao, "legendas": legendas,
             "cores": cores, **({"fonte": rot["fonte"]} if rot.get("fonte") else {})}
    pasta_props = RAIZ / "remotion" / "props"
    pasta_props.mkdir(exist_ok=True)
    (pasta_props / f"{slug}.json").write_text(json.dumps(props, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Mídias: {len(midias)} | narração: {'sim' if narracao else 'não'} | legendas: {'sim' if legendas else 'não'}")
    print(f"Props: remotion/props/{slug}.json")
    print(f"Prévia:  cd remotion && npx remotion studio --props=props/{slug}.json")
    print(f"Render:  cd remotion && npx remotion render VideoRoteiro out/{slug}.mp4 --props=props/{slug}.json")


if __name__ == "__main__":
    main()

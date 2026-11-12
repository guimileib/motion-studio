#!/usr/bin/env python3
"""Converte um .json de série (vários vídeos, formato "videos[].cenas[]") em projetos/<slug>/roteiro.json.

- ids de cena a partir do papel (gancho, estudo, estudo-2, cta…);
- narracao_tts com a tabela "pronuncia" do vídeo aplicada (e "Visualize+" → "Visualize Mais");
- voz do VoiceStudio da série (padrao.narrador.voicestudio_voz);
- não sobrescreve roteiro.json existente sem --forcar.

Uso:
  python importar_serie.py --serie projetos/_series/minha-serie.json [--videos v02,v03] [--forcar]
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]


def slug_id(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:32] or "cena"


def para_tts(texto: str, pronuncia: dict[str, str], marca: str) -> str:
    out = texto
    for termo, fala in sorted(pronuncia.items(), key=lambda kv: -len(kv[0])):
        out = re.sub(rf"(?<!\w){re.escape(termo)}(?!\w)", fala, out)
    if marca.endswith("+"):
        out = out.replace(marca, marca[:-1] + " Mais")
    return out


def converter(serie: dict, v: dict) -> dict:
    marca = serie.get("marca", {})
    nome_marca = marca.get("nome", "")
    narr = serie.get("padrao", {}).get("narrador", {})
    pron = v.get("pronuncia") or {}
    vistos: dict[str, int] = {}
    cenas, t = [], 0.0
    for c in v["cenas"]:
        base = slug_id(c.get("papel") or f"cena-{c['n']}")
        vistos[base] = vistos.get(base, 0) + 1
        cid = base if vistos[base] == 1 else f"{base}-{vistos[base]}"
        vis = c.get("visual") or {}
        desc = vis.get("descricao", "")
        if vis.get("tipo") == "mascote":
            desc += " [mascote fora: trocar por grafismo da marca]"
        cena = {
            "id": cid,
            "nome": c.get("texto_tela", cid),
            "inicio_s": round(t, 2),
            "duracao_s": float(c.get("duracao_s") or 5),
            "objetivo": c.get("papel", ""),
            "narracao": c["narracao"],
            "texto_tela": c.get("texto_tela", ""),
            "visual": desc,
            "midia": {"tipo": "nenhuma"},
        }
        tts = para_tts(c["narracao"], pron, nome_marca)
        if tts != c["narracao"]:
            cena["narracao_tts"] = tts
        cenas.append(cena)
        t += cena["duracao_s"]
    return {
        "titulo": v["titulo"],
        "slug": v["slug"],
        "id": v.get("id", ""),
        "serie": f"{nome_marca} — {v.get('id', '')}",
        "objetivo": v.get("objetivo", "alcance"),
        "ideia": v.get("ideia", ""),
        "pilar": v.get("pilar", ""),
        "servico_relacionado": v.get("servico_relacionado", ""),
        "estudo_base": v.get("estudo_base", {}),
        "gancho": v.get("gancho", {}),
        "ganchos_alternativos": (v.get("gancho") or {}).get("alternativos", []),
        "formato": {"largura": 1080, "altura": 1920, "fps": 30, "plataforma": serie.get("padrao", {}).get("plataforma", "Instagram Reels")},
        "duracao_alvo_s": round(t, 2),
        "voz": {"velocidade": 1.0, "voicestudio": {
            "modelo": "voxcpm2", "voz": narr.get("voicestudio_voz", ""), "voz_nome": narr.get("voicestudio_voz_nome", ""),
            "idioma": "pt", "seed": 42}},
        "legenda_estilo": "reels",
        "marca": {"nome": nome_marca, "pasta": marca.get("pasta", ""), "regras_video": (marca.get("mascote") or {}).get("regras", [])},
        "estilo": None,
        "cenas": cenas,
        "cta": (v.get("cta") or {}).get("texto", ""),
        "legenda_post": v.get("legenda", ""),
        "hashtags": v.get("hashtags", []),
        "fontes": v.get("fontes", []),
        "capa": v.get("capa", {}),
        "notas": v.get("notas", ""),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serie", type=Path, required=True)
    ap.add_argument("--videos", help="ids separados por vírgula (padrão: todos com cenas)")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    serie = json.loads(a.serie.read_text(encoding="utf-8"))
    quero = set(a.videos.split(",")) if a.videos else None
    for v in serie["videos"]:
        if not v.get("cenas") or (quero and v.get("id") not in quero and v.get("slug") not in quero):
            continue
        destino = RAIZ / "projetos" / v["slug"] / "roteiro.json"
        if destino.exists() and not a.forcar:
            print(f"= {v['id']} {v['slug']}: já existe, mantido")
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(converter(serie, v), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"+ {v['id']} {v['slug']}: {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()

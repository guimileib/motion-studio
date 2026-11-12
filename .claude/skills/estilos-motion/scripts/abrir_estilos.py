#!/usr/bin/env python3
"""Gera e abre a página de escolha de estilo de motion de um projeto.

A página mostra os estilos da casa, os estilos das skills de terceiros (bang-motion, vox-director,
vox-explainer, huashu-art-motion, claude-drawing) e a opção "criar do zero", todos animados,
com o título e o gancho do vídeo, e marca 3 recomendados.

Uso:
  # projeto já convertido
  python abrir_estilos.py --roteiro projetos/<slug>/roteiro.json

  # direto de um .json de série (vários vídeos), escolhendo o vídeo
  python abrir_estilos.py --serie caminho/serie.json --video v02

  # só gerar, sem abrir o navegador
  python abrir_estilos.py --roteiro … --nao-abrir

Saída: projetos/<slug>/estilo/escolha.html
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import webbrowser
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MODELO = AQUI.parent / "pagina" / "estilos.html"
RAIZ = AQUI.parents[3]  # .claude/skills/estilos-motion/scripts → raiz do repo

# palavra-chave (sem acento) → estilos que combinam
AFINIDADES = {
    "00-flat-marca": ["marca", "servico", "whatsapp", "site", "pacote", "preco", "oferta", "inteligencia artificial", " ia ", "google", "instagram", "algoritmo", "segundos"],
    "01-linha-continua": ["grafico", "numero", "por cento", "dados", "cresc", "tabela", "segundos", "pesquisa", "opcoes"],
    "02-bola-unica": ["diferente", "destaca", "destoa", "rebanho", "copia", "unico", "igual", "lembrado", "posicionamento"],
    "05-riso-stop-motion": ["festa", "filho", "salao", "negocio local", "cliente", "momento", "cotidiano", "milkshake", "geleia"],
    "06-codice": ["mil novecentos", "1933", "1923", "psicologa", "harvard", "princeton", "estudo", "pesquisador", "historia"],
    "07-tinta-na-agua": ["memoria", "lembrar", "mente", "confia", "julgamento", "emocao", "percep", "cabeca"],
    # estilos das skills de terceiros
    "s-bang-motion": ["lancamento", "promo", "novidade", "chegou", "evento", "abertura", "intro", "app", "produto"],
    "s-vox-director": ["por que", "explica", "entenda", "colagem", "tribute", "personalidade", "marca famosa", "anuncio"],
    "s-vox-explainer": ["historia", "guerra", "economia", "noticia", "mil novecentos", "seculo", "pais", "documentario"],
    "s-huashu-art-motion": ["arte", "pintura", "poesia", "cultura", "lenda", "mito", "natureza", "paisagem", "china", "japao"],
    "s-claude-drawing": ["desenho", "ilustr", "aquarela", "infantil", "crianca", "receita", "flor", "planta", "animal", "bicho"],
}


def sem_acento(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(ch) != "Mn")


def recomendar(texto: str, n: int = 3) -> list[str]:
    t = f" {sem_acento(texto)} "
    pontos = {k: sum(t.count(p) for p in ps) for k, ps in AFINIDADES.items()}
    pontos["00-flat-marca"] += 1  # desempate: o padrão da marca sempre concorre
    return [k for k, _ in sorted(pontos.items(), key=lambda kv: -kv[1])[:n]]


def dados_do_roteiro(rot: dict) -> dict:
    cenas = rot.get("cenas") or []
    narr = " ".join(c.get("narracao", "") for c in cenas)
    gancho = rot.get("gancho", {}).get("escolhido") if isinstance(rot.get("gancho"), dict) else None
    gancho = gancho or (cenas[0].get("narracao") if cenas else "")
    marca = rot.get("marca") or {}
    texto = " ".join(str(rot.get(k, "")) for k in ("titulo", "ideia", "pilar", "servico_relacionado", "promessa")) + " " + narr
    return {
        "id": rot.get("id", ""),
        "titulo": rot.get("titulo", ""),
        "gancho": gancho,
        "ideia": rot.get("ideia") or rot.get("promessa", ""),
        "marca": marca.get("nome", "") if isinstance(marca, dict) else str(marca),
        "recomendados": recomendar(texto),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roteiro", type=Path)
    ap.add_argument("--serie", type=Path)
    ap.add_argument("--video", help="id ou slug do vídeo dentro da série")
    ap.add_argument("--nao-abrir", action="store_true")
    a = ap.parse_args()

    if a.roteiro:
        rot = json.loads(a.roteiro.read_text(encoding="utf-8"))
        slug = rot.get("slug") or a.roteiro.parent.name
        pasta = a.roteiro.parent
    elif a.serie and a.video:
        serie = json.loads(a.serie.read_text(encoding="utf-8"))
        rot = next((v for v in serie.get("videos", []) if a.video in (v.get("id"), v.get("slug"))), None)
        if not rot:
            sys.exit(f"vídeo {a.video} não está na série")
        rot.setdefault("marca", serie.get("marca", {}))
        slug = rot["slug"]
        pasta = RAIZ / "projetos" / slug
    else:
        ap.error("use --roteiro ou --serie + --video")

    if not re.fullmatch(r"[a-z0-9-]+", slug):
        sys.exit(f"slug inválido: {slug}")
    dados = dados_do_roteiro(rot)
    html = MODELO.read_text(encoding="utf-8").replace("/*PROJETO*/null", json.dumps(dados, ensure_ascii=False))
    destino = pasta / "estilo" / "escolha.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    print(f"Página: {destino}")
    print("Recomendados: " + ", ".join(dados["recomendados"]))
    if not a.nao_abrir:
        webbrowser.open(destino.resolve().as_uri())


if __name__ == "__main__":
    main()

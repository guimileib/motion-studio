#!/usr/bin/env python3
"""Busca e baixa fotos/vídeos de banco (Pexels, Pixabay, Unsplash) alinhados às cenas do roteiro.

Uso:
  # todas as cenas do roteiro (usa cenas[].midia.busca / tipo / orientacao)
  python buscar_midia.py --roteiro projetos/meu-video/roteiro.json --baixar

  # busca avulsa
  python buscar_midia.py --q "fresh oranges falling slow motion" --tipo video --orientacao vertical --n 6

Saídas (modo roteiro): projetos/<slug>/midia/<cena>/…, midia/manifest.json (candidatos e o escolhido
de cada cena) e CREDITOS.md. Chaves no .env: PEXELS_API_KEY, PIXABAY_API_KEY, UNSPLASH_ACCESS_KEY.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "motion-studio/1.0 (+https://github.com/)"
CACHE = Path(".cache/busca-midia")


# ----------------------------------------------------------------------------- utilidades

def carregar_env() -> None:
    for pasta in [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        f = pasta / ".env"
        if f.is_file():
            for l in f.read_text(encoding="utf-8").splitlines():
                l = l.strip()
                if l and not l.startswith("#") and "=" in l:
                    k, v = l.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return


def get_json(url: str, headers: dict | None = None, cache_h: float = 24) -> dict:
    """GET com cache em disco (Pixabay exige cache de 24 h; vale para todos)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    chave = hashlib.sha1((url + json.dumps(headers or {}, sort_keys=True)).encode()).hexdigest()
    arq = CACHE / f"{chave}.json"
    if arq.exists() and time.time() - arq.stat().st_mtime < cache_h * 3600:
        return json.loads(arq.read_text("utf-8"))
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            dados = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} em {url.split('?')[0]}: {e.read().decode('utf-8', 'replace')[:200]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"sem acesso a {urllib.parse.urlparse(url).netloc} ({e.reason})")
    arq.write_text(json.dumps(dados), encoding="utf-8")
    return dados


def baixar(url: str, destino: Path, headers: dict | None = None) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=180) as r, open(destino, "wb") as f:
        while True:
            bloco = r.read(1 << 16)
            if not bloco:
                break
            f.write(bloco)
    return destino


def orientacao_ok(w: int, h: int, o: str | None) -> bool:
    if not o or not w or not h:
        return True
    if o == "vertical":
        return h > w
    if o == "horizontal":
        return w > h
    return abs(w - h) / max(w, h) < 0.15


def melhor_arquivo(arquivos: list[dict], alvo_lado_menor: int = 1080) -> dict | None:
    """Escolhe o arquivo de vídeo com lado menor mais próximo de 1080 (acima, de preferência)."""
    if not arquivos:
        return None
    def nota(a):
        m = min(a["largura"] or 0, a["altura"] or 0)
        return (0 if m >= alvo_lado_menor else 1, abs(m - alvo_lado_menor))
    return sorted(arquivos, key=nota)[0]


# ----------------------------------------------------------------------------- fontes

def pexels(q: str, tipo: str, o: str | None, n: int) -> list[dict]:
    k = os.environ.get("PEXELS_API_KEY")
    if not k:
        raise RuntimeError("sem PEXELS_API_KEY")
    om = {"vertical": "portrait", "horizontal": "landscape", "quadrado": "square"}.get(o or "", "")
    params = {"query": q, "per_page": min(80, max(n * 2, 10)), **({"orientation": om} if om else {})}
    base = "https://api.pexels.com/videos/search" if tipo == "video" else "https://api.pexels.com/v1/search"
    d = get_json(base + "?" + urllib.parse.urlencode(params), {"Authorization": k})
    out = []
    if tipo == "video":
        for v in d.get("videos", []):
            arqs = [{"url": f["link"], "largura": f.get("width") or 0, "altura": f.get("height") or 0}
                    for f in v.get("video_files", []) if (f.get("file_type") or "").endswith("mp4")]
            arqs = [a for a in arqs if orientacao_ok(a["largura"], a["altura"], o)] or arqs
            m = melhor_arquivo(arqs)
            if not m:
                continue
            out.append({"fonte": "pexels", "id": str(v["id"]), "tipo": "video", "pagina": v.get("url"),
                        "arquivo": m["url"], "largura": m["largura"], "altura": m["altura"],
                        "duracao": v.get("duration"), "autor": (v.get("user") or {}).get("name"),
                        "autor_url": (v.get("user") or {}).get("url"), "preview": v.get("image"),
                        "licenca": "Pexels License (uso gratuito, inclusive comercial; crédito opcional)"})
    else:
        for p in d.get("photos", []):
            src = p.get("src", {})
            out.append({"fonte": "pexels", "id": str(p["id"]), "tipo": "foto", "pagina": p.get("url"),
                        "arquivo": src.get("original") or src.get("large2x"), "largura": p.get("width"),
                        "altura": p.get("height"), "autor": p.get("photographer"), "autor_url": p.get("photographer_url"),
                        "preview": src.get("medium"), "descricao": p.get("alt"),
                        "licenca": "Pexels License (uso gratuito, inclusive comercial; crédito opcional)"})
    return out


def pixabay(q: str, tipo: str, o: str | None, n: int) -> list[dict]:
    k = os.environ.get("PIXABAY_API_KEY")
    if not k:
        raise RuntimeError("sem PIXABAY_API_KEY")
    params = {"key": k, "q": q[:100], "per_page": min(200, max(n * 2, 10)), "safesearch": "true", "lang": "pt" if any(ch in q for ch in "ãçéêíóõú") else "en"}
    if tipo == "video":
        d = get_json("https://pixabay.com/api/videos/?" + urllib.parse.urlencode(params))
    else:
        om = {"vertical": "vertical", "horizontal": "horizontal"}.get(o or "", "all")
        d = get_json("https://pixabay.com/api/?" + urllib.parse.urlencode({**params, "image_type": "photo", "orientation": om}))
    out = []
    for h in d.get("hits", []):
        base = {"fonte": "pixabay", "id": str(h["id"]), "pagina": h.get("pageURL"), "autor": h.get("user"),
                "autor_url": f"https://pixabay.com/users/{h.get('user')}-{h.get('user_id')}/",
                "licenca": "Pixabay Content License (uso gratuito, inclusive comercial; sem revenda do arquivo sem alteração)"}
        if tipo == "video":
            arqs = [{"url": r["url"], "largura": r.get("width") or 0, "altura": r.get("height") or 0}
                    for r in (h.get("videos") or {}).values() if r.get("url")]
            arqs = [a for a in arqs if orientacao_ok(a["largura"], a["altura"], o)]
            m = melhor_arquivo(arqs)
            if not m:
                continue
            out.append({**base, "tipo": "video", "arquivo": m["url"], "largura": m["largura"], "altura": m["altura"],
                        "duracao": h.get("duration"), "preview": ((h.get("videos") or {}).get("tiny") or {}).get("thumbnail")})
        else:
            out.append({**base, "tipo": "foto", "arquivo": h.get("largeImageURL"), "largura": h.get("imageWidth"),
                        "altura": h.get("imageHeight"), "preview": h.get("webformatURL"), "descricao": h.get("tags")})
    return out


def unsplash(q: str, tipo: str, o: str | None, n: int) -> list[dict]:
    if tipo == "video":
        return []  # Unsplash só tem fotos
    k = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not k:
        raise RuntimeError("sem UNSPLASH_ACCESS_KEY")
    app = os.environ.get("UNSPLASH_APP_NAME", "motion-studio")
    om = {"vertical": "portrait", "horizontal": "landscape", "quadrado": "squarish"}.get(o or "", "")
    params = {"query": q, "per_page": min(30, max(n * 2, 10)), "content_filter": "high", **({"orientation": om} if om else {})}
    d = get_json("https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(params),
                 {"Authorization": f"Client-ID {k}", "Accept-Version": "v1"}, cache_h=1)
    out = []
    utm = f"?utm_source={urllib.parse.quote(app)}&utm_medium=referral"
    for p in d.get("results", []):
        u = p.get("user", {})
        out.append({"fonte": "unsplash", "id": p["id"], "tipo": "foto", "pagina": (p.get("links") or {}).get("html", "") + utm,
                    "arquivo": (p.get("urls") or {}).get("raw", "") + "&w=2160&q=85&fm=jpg",
                    "download_location": (p.get("links") or {}).get("download_location"),
                    "largura": p.get("width"), "altura": p.get("height"), "autor": u.get("name"),
                    "autor_url": (u.get("links") or {}).get("html", "") + utm, "preview": (p.get("urls") or {}).get("small"),
                    "descricao": p.get("alt_description"),
                    "licenca": "Unsplash License (uso gratuito, inclusive comercial; crédito exigido pela API: 'Photo by X on Unsplash')"})
    return out


FONTES = {"pexels": pexels, "pixabay": pixabay, "unsplash": unsplash}


def buscar(termos: list[str], tipo: str, o: str | None, n: int, fontes: list[str], min_dur: float = 0) -> tuple[list[dict], list[str]]:
    vistos, res, avisos = set(), [], []
    for termo in termos:
        for f in fontes:
            if f == "web":
                continue
            try:
                for it in FONTES[f](termo, tipo, o, n):
                    chave = (it["fonte"], it["id"])
                    if chave in vistos:
                        continue
                    if tipo == "video" and min_dur and (it.get("duracao") or 0) < min_dur:
                        continue
                    if not orientacao_ok(it.get("largura") or 0, it.get("altura") or 0, o) and tipo == "foto":
                        continue
                    vistos.add(chave)
                    it["termo"] = termo
                    res.append(it)
            except RuntimeError as e:
                avisos.append(f"{f}: {e}")
    # intercala as fontes e corta em n
    por_fonte: dict[str, list] = {}
    for it in res:
        por_fonte.setdefault(it["fonte"], []).append(it)
    misturado = []
    while any(por_fonte.values()) and len(misturado) < n:
        for f in list(por_fonte):
            if por_fonte[f] and len(misturado) < n:
                misturado.append(por_fonte[f].pop(0))
    return misturado, sorted(set(avisos))


def baixar_item(it: dict, pasta: Path) -> str:
    ext = ".mp4" if it["tipo"] == "video" else ".jpg"
    destino = pasta / f"{it['fonte']}-{it['id']}{ext}"
    baixar(it["arquivo"], destino)
    if it["fonte"] == "unsplash" and it.get("download_location"):  # exigência da API do Unsplash
        try:
            k = os.environ.get("UNSPLASH_ACCESS_KEY", "")
            urllib.request.urlopen(urllib.request.Request(it["download_location"],
                                   headers={"Authorization": f"Client-ID {k}", "User-Agent": UA}), timeout=15).read()
        except Exception:  # noqa: BLE001 — o ping não pode impedir o download
            pass
    return str(destino)


def creditos(manifest: dict) -> str:
    linhas = ["# Créditos de mídia", ""]
    for cena, info in manifest["cenas"].items():
        esc = info.get("escolhido")
        if esc is None or not info["candidatos"]:
            continue
        it = info["candidatos"][esc]
        if it["fonte"] == "unsplash":
            linhas.append(f"- **{cena}**: Photo by [{it['autor']}]({it['autor_url']}) on [Unsplash]({it['pagina']})")
        else:
            fonte = it["fonte"].capitalize()
            linhas.append(f"- **{cena}**: {it['tipo'].capitalize()} de [{it['autor']}]({it['autor_url']}) no [{fonte}]({it['pagina']}) — {it['licenca']}")
    return "\n".join(linhas) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roteiro", type=Path)
    ap.add_argument("--cenas", help="ids separados por vírgula")
    ap.add_argument("--q", action="append", help="termo de busca (pode repetir)")
    ap.add_argument("--tipo", choices=["video", "foto"], default="video")
    ap.add_argument("--orientacao", choices=["vertical", "horizontal", "quadrado"])
    ap.add_argument("--fontes", default="pexels,pixabay,unsplash")
    ap.add_argument("--n", type=int, default=6, help="candidatos por cena")
    ap.add_argument("--baixar", action="store_true", help="baixa os candidatos (senão só lista)")
    ap.add_argument("--baixar-todos", action="store_true", help="baixa todos os candidatos, não só o 1º")
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()
    carregar_env()
    fontes = [f.strip() for f in a.fontes.split(",") if f.strip()]

    if a.q:
        res, avisos = buscar(a.q, a.tipo, a.orientacao, a.n, fontes)
        for w in avisos:
            print("!", w)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        if a.baixar:
            pasta = a.saida or Path("midia")
            for it in res if a.baixar_todos else res[:1]:
                print("baixado:", baixar_item(it, pasta))
        return

    if not a.roteiro:
        ap.error("use --roteiro ou --q")
    rot = json.loads(a.roteiro.read_text("utf-8"))
    pasta_proj = a.roteiro.parent
    pasta_midia = a.saida or pasta_proj / "midia"
    arq_manifest = pasta_midia / "manifest.json"
    manifest = json.loads(arq_manifest.read_text("utf-8")) if arq_manifest.exists() else {"cenas": {}}
    filtro = set(a.cenas.split(",")) if a.cenas else None
    orient_padrao = "vertical" if rot.get("formato", {}).get("altura", 1920) > rot.get("formato", {}).get("largura", 1080) else "horizontal"

    for c in rot["cenas"]:
        m = c.get("midia") or {}
        if (filtro and c["id"] not in filtro) or m.get("tipo") in (None, "nenhuma", "propria") or not m.get("busca"):
            continue
        tipo = m["tipo"]
        o = m.get("orientacao") or a.orientacao or orient_padrao
        fs = [f for f in (m.get("fontes") or fontes) if f in FONTES or f == "web"]
        print(f"→ {c['id']}: {tipo} {o} | {' / '.join(m['busca'])}")
        res, avisos = buscar(m["busca"], tipo, o, a.n, fs, min_dur=float(c["duracao_s"]) + 0.5 if tipo == "video" else 0)
        for w in avisos:
            print("  !", w)
        anterior = manifest["cenas"].get(c["id"], {})
        info = {"busca": m["busca"], "tipo": tipo, "orientacao": o, "candidatos": res,
                "escolhido": anterior.get("escolhido", 0 if res else None)}
        if info["escolhido"] is not None and info["escolhido"] >= len(res):
            info["escolhido"] = 0 if res else None
        if a.baixar and res:
            alvo = res if a.baixar_todos else [res[info["escolhido"]]]
            for it in alvo:
                try:
                    caminho = baixar_item(it, pasta_midia / c["id"])
                    it["local"] = str(Path(caminho).relative_to(pasta_proj))
                    print("  baixado:", it["local"])
                except Exception as e:  # noqa: BLE001
                    print("  ! falha ao baixar:", e)
        for i, it in enumerate(res[:a.n]):
            print(f"  [{i}] {it['fonte']:<8} {it.get('largura')}x{it.get('altura')} {str(it.get('duracao') or ''):>4}s  {it.get('pagina')}")
        manifest["cenas"][c["id"]] = info

    pasta_midia.mkdir(parents=True, exist_ok=True)
    arq_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta_proj / "CREDITOS.md").write_text(creditos(manifest), encoding="utf-8")
    print(f"\nManifesto: {arq_manifest}\nCréditos: {pasta_proj / 'CREDITOS.md'}")
    print("Para trocar a escolha de uma cena, mude 'escolhido' no manifest.json e rode de novo com --baixar.")


if __name__ == "__main__":
    main()

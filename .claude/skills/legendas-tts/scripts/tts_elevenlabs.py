#!/usr/bin/env python3
"""Narração com a ElevenLabs (TTS com timestamps) + legendas SRT e palavras para o Remotion.

Uso:
  # todas as cenas de um roteiro (gera audio/, legendas/ ao lado do roteiro.json)
  python tts_elevenlabs.py --roteiro projetos/meu-video/roteiro.json

  # refazer só uma cena / forçar nova geração
  python tts_elevenlabs.py --roteiro projetos/meu-video/roteiro.json --cenas fim --forcar

  # só reconstruir legendas a partir dos alinhamentos já salvos (sem gastar créditos)
  python tts_elevenlabs.py --roteiro projetos/meu-video/roteiro.json --so-legendas

  # texto avulso
  python tts_elevenlabs.py --texto "Cansado de adivinhar quanto pedir?" --saida saida/teste

Precisa de ELEVENLABS_API_KEY e ELEVENLABS_VOICE_ID (no .env ou no ambiente) e de ffmpeg para a mixagem.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from legendas_lib import (carregar_env, palavras_de_alinhamento, remapear_para_legenda,  # noqa: E402
                          salvar_legendas)

API = "https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps?output_format={fmt}"


def gerar(texto: str, voz: str, modelo: str, ajustes: dict, chave: str, anterior: str = "", seguinte: str = "",
          fmt: str = "mp3_44100_128") -> dict:
    corpo = {
        "text": texto,
        "model_id": modelo,
        "voice_settings": {
            "stability": ajustes.get("estabilidade", 0.45),
            "similarity_boost": ajustes.get("similaridade", 0.75),
            "style": ajustes.get("estilo", 0.2),
            "use_speaker_boost": True,
            "speed": ajustes.get("velocidade", 1.0),
        },
    }
    if modelo != "eleven_v3":  # contexto melhora a continuidade entre cenas (não suportado no v3)
        if anterior:
            corpo["previous_text"] = anterior
        if seguinte:
            corpo["next_text"] = seguinte
    req = urllib.request.Request(
        API.format(voz=voz, fmt=fmt),
        data=json.dumps(corpo).encode("utf-8"),
        headers={"xi-api-key": chave, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode("utf-8", "replace")[:600]
        sys.exit(f"ElevenLabs respondeu {e.code}: {detalhe}")
    except urllib.error.URLError as e:
        sys.exit(f"Não consegui acessar api.elevenlabs.io ({e.reason}). Verifique a rede/permissões.")


def duracao_audio(arq: Path) -> float | None:
    if not shutil.which("ffprobe"):
        return None
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def mixar(segmentos: list[tuple[Path, float]], total: float, saida: Path) -> bool:
    """Posiciona cada trecho no seu tempo absoluto e junta numa faixa só."""
    if not shutil.which("ffmpeg"):
        print("! ffmpeg não encontrado: pulei a mixagem (os trechos por cena estão em audio/).")
        return False
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    filtros, rotulos = [], []
    for i, (arq, ini) in enumerate(segmentos):
        cmd += ["-i", str(arq)]
        ms = max(0, round(ini * 1000))
        filtros.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
        rotulos.append(f"[a{i}]")
    filtros.append("".join(rotulos) + f"amix=inputs={len(segmentos)}:normalize=0:dropout_transition=0,apad[out]")
    cmd += ["-filter_complex", ";".join(filtros), "-map", "[out]", "-t", f"{total:.3f}",
            "-ar", "44100", "-b:a", "192k", str(saida)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("! ffmpeg falhou:", r.stderr[-400:])
        return False
    return True


def hash_texto(*partes) -> str:
    return hashlib.sha1("|".join(map(str, partes)).encode("utf-8")).hexdigest()[:12]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roteiro", type=Path)
    ap.add_argument("--texto")
    ap.add_argument("--saida", type=Path, help="pasta de saída (modo --texto)")
    ap.add_argument("--cenas", help="ids separados por vírgula (padrão: todas)")
    ap.add_argument("--voz", help="voice_id (padrão: roteiro.voz.voice_id ou ELEVENLABS_VOICE_ID)")
    ap.add_argument("--modelo", help="model_id (padrão: roteiro.voz.modelo ou eleven_multilingual_v2)")
    ap.add_argument("--velocidade", type=float)
    ap.add_argument("--estilo-legenda", choices=["reels", "padrao"])
    ap.add_argument("--forcar", action="store_true", help="gera de novo mesmo com cache")
    ap.add_argument("--so-legendas", action="store_true", help="não chama a API; usa os alinhamentos salvos")
    a = ap.parse_args()

    carregar_env(Path(__file__).resolve().parent)
    carregar_env()
    chave = os.environ.get("ELEVENLABS_API_KEY", "")

    if a.texto:
        rot = {"cenas": [{"id": "texto", "duracao_s": 600, "narracao": a.texto}], "voz": {}}
        pasta = a.saida or Path("saida")
    elif a.roteiro:
        rot = json.loads(a.roteiro.read_text(encoding="utf-8"))
        pasta = a.roteiro.parent
    else:
        ap.error("use --roteiro ou --texto")

    voz_cfg = dict(rot.get("voz") or {})
    if a.velocidade:
        voz_cfg["velocidade"] = a.velocidade
    voz = a.voz or voz_cfg.get("voice_id") or os.environ.get("ELEVENLABS_VOICE_ID", "")
    modelo = a.modelo or voz_cfg.get("modelo") or os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
    estilo = a.estilo_legenda or rot.get("legenda_estilo", "reels")
    if not a.so_legendas and (not chave or not voz):
        sys.exit("Faltam ELEVENLABS_API_KEY e/ou ELEVENLABS_VOICE_ID (.env). Veja .env.example.")

    dir_audio, dir_leg = pasta / "audio", pasta / "legendas"
    dir_audio.mkdir(parents=True, exist_ok=True)
    escolhidas = set(a.cenas.split(",")) if a.cenas else None

    cenas = rot["cenas"]
    inicio = 0.0
    segmentos, todas_palavras, relatorio = [], [], []
    for i, c in enumerate(cenas):
        c_ini = float(c.get("inicio_s", inicio))
        inicio = c_ini + float(c["duracao_s"])
        legenda = (c.get("narracao") or "").strip()
        if not legenda:
            continue
        falado = (c.get("narracao_tts") or legenda).strip()
        atraso = float(c.get("narracao_inicio_s", 0.15))
        arq_mp3, arq_alin = dir_audio / f"{c['id']}.mp3", dir_audio / f"{c['id']}.alinhamento.json"
        h = hash_texto(falado, voz, modelo, json.dumps(voz_cfg, sort_keys=True))

        precisa = escolhidas is None or c["id"] in escolhidas
        em_cache = arq_alin.exists() and arq_mp3.exists() and json.loads(arq_alin.read_text("utf-8")).get("hash") == h
        if not a.so_legendas and precisa and (a.forcar or not em_cache):
            anterior = " ".join((x.get("narracao_tts") or x.get("narracao") or "") for x in cenas[:i])[-300:]
            seguinte = " ".join((x.get("narracao_tts") or x.get("narracao") or "") for x in cenas[i + 1:])[:300]
            print(f"→ gerando {c['id']}: {falado[:60]}…")
            r = gerar(falado, voz, modelo, voz_cfg, chave, anterior, seguinte)
            arq_mp3.write_bytes(base64.b64decode(r["audio_base64"]))
            arq_alin.write_text(json.dumps({"hash": h, "texto": falado, "alignment": r.get("alignment"),
                                            "normalized_alignment": r.get("normalized_alignment")},
                                           ensure_ascii=False), encoding="utf-8")
        if not arq_alin.exists():
            print(f"! {c['id']}: sem alinhamento salvo, pulei")
            continue

        dados = json.loads(arq_alin.read_text("utf-8"))
        palavras = palavras_de_alinhamento(dados.get("alignment") or dados.get("normalized_alignment") or {},
                                           c_ini + atraso)
        if falado != legenda:
            palavras = remapear_para_legenda(palavras, legenda)
        todas_palavras += palavras
        segmentos.append((arq_mp3, c_ini + atraso))

        dur = duracao_audio(arq_mp3) or (palavras[-1]["fim"] - c_ini - atraso if palavras else 0)
        vaga = float(c["duracao_s"]) - atraso
        estado = "ok"
        if dur > vaga + 0.05:
            estado = f"PASSA {dur - vaga:.2f}s — encurte o texto ou use velocidade {min(1.2, dur / vaga * voz_cfg.get('velocidade', 1.0)):.2f}"
        relatorio.append(f"{c['id']:<16} fala {c_ini + atraso:6.2f}s → {c_ini + atraso + dur:6.2f}s  ({dur:.2f}s de {vaga:.2f}s)  {estado}")

    if not todas_palavras:
        sys.exit("Nenhuma narração gerada.")
    caminhos = salvar_legendas(todas_palavras, dir_leg, estilo)
    total = float(rot.get("duracao_alvo_s") or inicio)
    if a.texto:
        total = todas_palavras[-1]["fim"] + 0.3
    ok = mixar(segmentos, total, dir_audio / "narracao.mp3")

    (dir_audio / "relatorio.txt").write_text("\n".join(relatorio) + "\n", encoding="utf-8")
    print("\n".join(relatorio))
    print(f"\nLegendas: {caminhos['srt']}\nPalavras (Remotion): {caminhos['palavras']}")
    if ok:
        print(f"Narração completa: {dir_audio / 'narracao.mp3'} ({total:.2f}s)")


if __name__ == "__main__":
    main()

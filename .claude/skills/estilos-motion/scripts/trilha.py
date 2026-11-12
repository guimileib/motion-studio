#!/usr/bin/env python3
"""Trilha de fundo: gera música instrumental na ElevenLabs Music e mixa sob a narração.

  # gera projetos/<slug>/audio/trilha.mp3 (cache: não gera de novo se já existir)
  python trilha.py gerar --roteiro projetos/<slug>/roteiro.json [--duracao 45] [--prompt "..."]
  # mixa a trilha num vídeo já renderizado (voz a -14 LUFS), com ducking e fade
  python trilha.py mixar --video in.mp4 --trilha projetos/<slug>/audio/trilha.mp3 --saida out.mp4

Chave: ELEVEN_LABS ou ELEVENLABS_API_KEY (no .env ou no ambiente). Precisa de ffmpeg/ffprobe.
A música fica ~16 dB abaixo da voz e abaixa mais enquanto há fala (sidechain); o resultado
sai normalizado em -14 LUFS. Uso comercial depende do plano da conta ElevenLabs.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "legendas-tts" / "scripts"))
from legendas_lib import carregar_env  # noqa: E402

API = "https://api.elevenlabs.io/v1/music?output_format=mp3_44100_192"

BASE = ("Instrumental background music for a narrated Brazilian marketing Reel. No vocals, no lead melody "
        "competing with a voiceover, sparse and clean mix, steady energy from start to end, ")
PROMPTS = {
    "00-flat-marca": "modern minimal electronic, soft synth plucks, light clean beat, 112 BPM, confident and optimistic, polished tech brand feel",
    "01-linha-continua": "marimba and plucked upright bass, light shaker, 110 BPM, curious and clever, playful but focused",
    "02-bola-unica": "minimal electronic, punchy kick, woody percussion, short synth stabs, 124 BPM, bold and rhythmic, motion design showreel feel",
    "05-riso-stop-motion": "lo-fi handmade, toy piano, upright bass, brushed drums, 100 BPM, warm and playful, crafty",
    "07-tinta-na-agua": "ambient, slow felt piano with long reverb, soft pads, no drums, 70 BPM, calm, emotional, cinematic",
}


def duracao(arq: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def gerar(a) -> None:
    carregar_env(Path.cwd())
    chave = os.environ.get("ELEVEN_LABS") or os.environ.get("ELEVENLABS_API_KEY")
    if not chave and sys.platform == "win32":  # variável de usuário criada depois que o terminal abriu
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            for nome in ("ELEVEN_LABS", "ELEVENLABS_API_KEY"):
                try:
                    chave = winreg.QueryValueEx(k, nome)[0].strip()
                    break
                except FileNotFoundError:
                    pass
    if not chave:
        sys.exit("Falta ELEVEN_LABS (ou ELEVENLABS_API_KEY) no .env.")
    roteiro = a.roteiro.resolve()
    proj = roteiro.parent
    saida = proj / "audio" / "trilha.mp3"
    if saida.exists() and not a.forcar:
        print(f"já existe: {saida}")
        return
    r = json.loads(roteiro.read_text(encoding="utf-8"))
    estilo = (r.get("estilo") or {}).get("id", "00-flat-marca")
    if a.duracao:
        seg = a.duracao
    else:
        narr = proj / "audio" / "narracao.mp3"
        seg = duracao(narr) if narr.exists() else float(r.get("duracao_total") or 45)
    seg = min(max(seg + 2.5, 10), 300)
    prompt = a.prompt or BASE + PROMPTS.get(estilo, PROMPTS["00-flat-marca"])
    corpo = json.dumps({"prompt": prompt, "music_length_ms": int(seg * 1000), "model_id": "music_v1",
                        "force_instrumental": True}).encode()
    req = urllib.request.Request(API, data=corpo, method="POST",
                                 headers={"xi-api-key": chave, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            dados = resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs {e.code}: {e.read()[:600].decode(errors='replace')}")
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_bytes(dados)
    (proj / "audio" / "trilha.json").write_text(json.dumps(
        {"fonte": "ElevenLabs Music (music_v1)", "estilo": estilo, "prompt": prompt, "duracao_s": round(seg, 1)},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"trilha: {saida} ({duracao(saida):.1f}s)")


def mixar(video: Path, trilha: Path, saida: Path, ganho: float = -30) -> None:
    d = duracao(video)
    filtro = (
        f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I={ganho}:TP=-8:LRA=11,"
        f"afade=t=in:d=0.6,afade=t=out:st={max(d - 2.2, 0):.2f}:d=2.2,apad[m];"
        "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v][sc];"
        "[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=600[md];"
        "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    )
    tmp = saida.with_suffix(".tmp.mp4")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(trilha), "-filter_complex", filtro,
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-t", f"{d:.3f}", str(tmp)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit(f"ffmpeg falhou:\n{r.stderr[-1500:]}")
    tmp.replace(saida)
    print(f"mixado: {saida}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar")
    g.add_argument("--roteiro", type=Path, required=True)
    g.add_argument("--duracao", type=float)
    g.add_argument("--prompt")
    g.add_argument("--forcar", action="store_true")
    m = sub.add_parser("mixar")
    m.add_argument("--video", type=Path, required=True)
    m.add_argument("--trilha", type=Path, required=True)
    m.add_argument("--saida", type=Path, required=True)
    m.add_argument("--ganho", type=float, default=-30, help="LUFS da trilha antes do ducking (padrão -30)")
    a = ap.parse_args()
    if a.cmd == "gerar":
        gerar(a)
    else:
        mixar(a.video.resolve(), a.trilha.resolve(), a.saida.resolve(), a.ganho)


if __name__ == "__main__":
    main()

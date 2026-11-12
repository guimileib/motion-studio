#!/usr/bin/env python3
"""Transcreve um áudio/vídeo com o Speech-to-Text da ElevenLabs (Scribe) e gera SRT + palavras.json.

Use para legendar uma narração que já existe (gravada ou gerada no site da ElevenLabs).

  python stt_elevenlabs.py --audio projetos/meu-video/audio/narracao.mp3 --saida projetos/meu-video/legendas
  python stt_elevenlabs.py --audio video.mp4 --estilo padrao --idioma pt
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from legendas_lib import carregar_env, palavras_de_stt, salvar_legendas  # noqa: E402

API = "https://api.elevenlabs.io/v1/speech-to-text"


def multipart(campos: dict, arquivo: Path) -> tuple[bytes, str]:
    b = uuid.uuid4().hex
    partes = []
    for k, v in campos.items():
        partes.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    tipo = mimetypes.guess_type(arquivo.name)[0] or "application/octet-stream"
    partes.append(f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{arquivo.name}"\r\n'
                  f"Content-Type: {tipo}\r\n\r\n".encode() + arquivo.read_bytes() + b"\r\n")
    partes.append(f"--{b}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={b}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audio", type=Path, required=True)
    ap.add_argument("--saida", type=Path, help="pasta de saída (padrão: ../legendas ao lado do áudio)")
    ap.add_argument("--idioma", default="pt", help="código ISO-639 (pt, por, en…); vazio = detectar")
    ap.add_argument("--estilo", choices=["reels", "padrao"], default="reels")
    ap.add_argument("--modelo", help="padrão: ELEVENLABS_STT_MODEL_ID ou scribe_v2")
    a = ap.parse_args()

    carregar_env(Path(__file__).resolve().parent)
    carregar_env()
    chave = os.environ.get("ELEVENLABS_API_KEY")
    if not chave:
        sys.exit("Falta ELEVENLABS_API_KEY (.env).")
    campos = {"model_id": a.modelo or os.environ.get("ELEVENLABS_STT_MODEL_ID", "scribe_v2"),
              "timestamps_granularity": "word", "tag_audio_events": "false", "diarize": "false"}
    if a.idioma:
        campos["language_code"] = a.idioma
    corpo, ctype = multipart(campos, a.audio)
    req = urllib.request.Request(API, data=corpo, method="POST",
                                 headers={"xi-api-key": chave, "Content-Type": ctype, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            resp = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs respondeu {e.code}: {e.read().decode('utf-8', 'replace')[:600]}")
    except urllib.error.URLError as e:
        sys.exit(f"Não consegui acessar api.elevenlabs.io ({e.reason}).")

    saida = a.saida or a.audio.resolve().parent.parent / "legendas"
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "transcricao.json").write_text(json.dumps(resp, ensure_ascii=False, indent=1), encoding="utf-8")
    palavras = palavras_de_stt(resp)
    if not palavras:
        sys.exit("A transcrição voltou sem palavras.")
    c = salvar_legendas(palavras, saida, a.estilo)
    print(f"Texto: {resp.get('text', '')[:200]}")
    print(f"Legendas: {c['srt']}\nPalavras (Remotion): {c['palavras']}")


if __name__ == "__main__":
    main()

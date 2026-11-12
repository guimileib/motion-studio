#!/usr/bin/env python3
"""Fila de narração no VoiceStudio: gera vários projetos cena a cena, retoma se o app cair, ajusta os tempos.

Para cada projeto: tts_voicestudio.py --cenas <id> (uma por vez, com cache), depois ajustar_tempos.py e
--so-legendas, e copia a narração para remotion/public/projetos/<slug>/narracao.mp3.
Se o VoiceStudio não responder, espera ele voltar (até 10 min) e tenta a cena de novo (até 3 vezes).

Uso:
  python fila_narracao.py projetos/a/roteiro.json projetos/b/roteiro.json ...
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[3]
BASE = os.environ.get("VOICESTUDIO_URL", "http://127.0.0.1:3900").rstrip("/")


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def pronto(espera: int = 600) -> bool:
    fim = time.time() + espera
    while time.time() < fim:
        try:
            with urllib.request.urlopen(f"{BASE}/health", timeout=5) as r:
                if json.loads(r.read()).get("status") == "ok":
                    return True
        except Exception:
            pass
        time.sleep(10)
    return False


def rodar(args: list[str]) -> int:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, *args], cwd=RAIZ, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace").returncode


def em_cache(pasta: Path, cid: str) -> bool:
    return (pasta / "audio" / f"{cid}.voicestudio.json").exists() and (pasta / "audio" / f"{cid}.wav").exists()


def main() -> None:
    roteiros = [Path(p).resolve() for p in sys.argv[1:]]
    if not roteiros:
        sys.exit(__doc__)
    tts = str(AQUI / "tts_voicestudio.py")
    for rot_path in roteiros:
        rot = json.loads(rot_path.read_text(encoding="utf-8"))
        slug = rot.get("slug") or rot_path.parent.name
        log(f"== {slug}")
        ok = True
        for c in rot["cenas"]:
            for tentativa in range(3):
                if not pronto():
                    log("VoiceStudio não voltou; parei a fila")
                    sys.exit(1)
                t0 = time.time()
                cod = rodar([tts, "--roteiro", str(rot_path), "--cenas", c["id"]])
                if cod == 0 and em_cache(rot_path.parent, c["id"]):
                    log(f"   {c['id']}: {time.time() - t0:.0f}s")
                    break
                log(f"   {c['id']}: falhou (tentativa {tentativa + 1}), aguardando o VoiceStudio")
                time.sleep(20)
            else:
                ok = False
        if not ok:
            log(f"   {slug}: cenas faltando, pulei o ajuste")
            continue
        rodar([str(AQUI / "ajustar_tempos.py"), "--roteiro", str(rot_path), "--final", "1.8"])
        rodar([tts, "--roteiro", str(rot_path), "--so-legendas"])
        destino = RAIZ / "remotion" / "public" / "projetos" / slug
        destino.mkdir(parents=True, exist_ok=True)
        shutil.copy2(rot_path.parent / "audio" / "narracao.mp3", destino / "narracao.mp3")
        log(f"   {slug}: narração pronta ({rot['duracao_alvo_s'] if 'duracao_alvo_s' in rot else '?'}s estimados)")
    log("FIM")


if __name__ == "__main__":
    main()

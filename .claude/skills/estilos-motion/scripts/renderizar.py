#!/usr/bin/env python3
"""Render final de uma composição Remotion + áudio normalizado em -14 LUFS (padrão de Reels).

Uso:
  python renderizar.py --composicao V02FujaDoRebanho --saida projetos/fuja-do-rebanho/video/v02-fuja-do-rebanho.mp4 \
      [--trilha projetos/fuja-do-rebanho/audio/trilha.mp3]

Com --trilha, a versão só com voz fica em video/sem-trilha/ e a saída leva a música mixada (trilha.py).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]


def rodar(cmd: list[str], **kw) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode:
        sys.exit(f"falhou: {' '.join(cmd)}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--composicao", required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--concorrencia", default="2")
    ap.add_argument("--trilha", type=Path, help="música de fundo para mixar sob a voz")
    a = ap.parse_args()
    saida = a.saida.resolve()
    saida.parent.mkdir(parents=True, exist_ok=True)
    npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
    with tempfile.TemporaryDirectory() as tmp:
        bruto = Path(tmp) / "bruto.mp4"
        rodar([npx, "remotion", "render", a.composicao, str(bruto), "--codec=h264", "--crf=18",
               f"--concurrency={a.concorrencia}", "--log=error"], cwd=RAIZ / "remotion", shell=sys.platform == "win32")
        rodar(["ffmpeg", "-v", "error", "-y", "-i", str(bruto), "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(saida)])
    if a.trilha:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from trilha import mixar
        voz = saida.parent / "sem-trilha" / saida.name
        voz.parent.mkdir(exist_ok=True)
        saida.replace(voz)
        mixar(voz, a.trilha.resolve(), saida)
    print(f"Vídeo: {saida}")


if __name__ == "__main__":
    main()

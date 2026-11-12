#!/usr/bin/env python3
"""Folha de contatos de uma composição Remotion: prévia em baixa resolução + um quadro por batida numa grade.

Uso:
  python folha_contatos.py --composicao V04NinguemCompraSite --saida projetos/<slug>/previa/folha.jpg \
      [--tempos 1.5,4,8.2,...] [--n 10] [--colunas 5] [--escala 0.35]

Sem --tempos, pega --n quadros espaçados igualmente. Precisa de npx (Remotion) e ffmpeg/ffprobe.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
REMOTION = RAIZ / "remotion"


def rodar(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode:
        sys.exit(f"falhou: {' '.join(cmd)}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--composicao", required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--tempos", help="segundos separados por vírgula")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--colunas", type=int, default=5)
    ap.add_argument("--escala", type=float, default=0.35)
    ap.add_argument("--video", type=Path, help="usa este MP4 em vez de renderizar a prévia")
    a = ap.parse_args()

    npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        video = a.video
        if not video:
            video = tmp / "previa.mp4"
            rodar([npx, "remotion", "render", a.composicao, str(video), f"--scale={a.escala}", "--crf=28",
                   "--concurrency=2", "--muted", "--log=error"], cwd=REMOTION, shell=sys.platform == "win32")
        dur = float(rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)]).stdout)
        tempos = [float(x) for x in a.tempos.split(",")] if a.tempos else [dur * (i + 0.5) / a.n for i in range(a.n)]
        for i, s in enumerate(tempos):
            rodar(["ffmpeg", "-v", "error", "-y", "-ss", f"{min(s, dur - 0.05):.3f}", "-i", str(video), "-frames:v", "1",
                   "-vf", f"scale=360:-2,drawtext=text='{s:.1f}s':x=10:y=10:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6",
                   str(tmp / f"q{i:03d}.png")])
        linhas = -(-len(tempos) // a.colunas)
        a.saida.parent.mkdir(parents=True, exist_ok=True)
        rodar(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "q%03d.png"), "-vf",
               f"tile={a.colunas}x{linhas}:padding=6:color=0x222222", "-frames:v", "1", "-q:v", "3", str(a.saida)])
    print(f"Folha de contatos: {a.saida} ({len(tempos)} quadros)")


if __name__ == "__main__":
    main()

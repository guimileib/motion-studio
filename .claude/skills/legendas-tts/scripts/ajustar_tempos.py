#!/usr/bin/env python3
"""Ajusta inicio_s/duracao_s das cenas do roteiro.json à duração real da narração já gerada.

Cada cena passa a durar: atraso da fala (narracao_inicio_s, padrão 0,15) + áudio + pausa.
Depois rode o TTS de novo com --so-legendas para refazer legendas e mixagem nos tempos novos.

Uso:
  python ajustar_tempos.py --roteiro projetos/<slug>/roteiro.json [--pausa 0.3] [--final 0.8]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tts_elevenlabs import duracao_audio  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roteiro", type=Path, required=True)
    ap.add_argument("--pausa", type=float, help="pausa após cada fala (padrão: padrao.pausa_entre_cenas_s ou 0,3)")
    ap.add_argument("--final", type=float, default=0.8, help="respiro depois da última fala")
    a = ap.parse_args()

    rot = json.loads(a.roteiro.read_text(encoding="utf-8"))
    pausa = a.pausa if a.pausa is not None else float(rot.get("pausa_entre_cenas_s", 0.3))
    dir_audio = a.roteiro.parent / "audio"
    t = 0.0
    for i, c in enumerate(rot["cenas"]):
        wav = dir_audio / f"{c['id']}.wav"
        if not wav.exists():  # a ElevenLabs grava .mp3; o VoiceStudio, .wav
            wav = dir_audio / f"{c['id']}.mp3"
        dur = duracao_audio(wav) if wav.exists() else None
        if not dur:
            sys.exit(f"sem áudio para a cena {c['id']} ({wav})")
        atraso = float(c.get("narracao_inicio_s", 0.15))
        ultima = i == len(rot["cenas"]) - 1
        nova = round(atraso + dur + (a.final if ultima else pausa), 2)
        print(f"{c['id']:<14} {c['duracao_s']:>6.2f}s → {nova:>6.2f}s  (início {t:6.2f}s)")
        c["inicio_s"] = round(t, 2)
        c["duracao_s"] = nova
        t += nova
    rot["duracao_alvo_s"] = round(t, 2)
    a.roteiro.write_text(json.dumps(rot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"duração total: {t:.2f}s")


if __name__ == "__main__":
    main()

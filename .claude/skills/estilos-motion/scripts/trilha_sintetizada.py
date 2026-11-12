#!/usr/bin/env python3
"""Trilha instrumental sintetizada em código (nada a licenciar), com arranjo por estilo de motion.

  python trilha_sintetizada.py --roteiro projetos/<slug>/roteiro.json [--duracao 45] [--forcar]

Gera projetos/<slug>/audio/trilha.mp3 (+ trilha.json). Duração = narração + 2,5 s.
Depois mixe sob a voz com:  python trilha.py mixar --video … --trilha … --saida …

Arranjos (estilo → clima):
  00 flat da marca   112 BPM  pad + arpejo de synth pluck, kick leve, hat no contratempo
  01 linha contínua  110 BPM  marimba, baixo pinçado, shaker
  02 bola única      124 BPM  four-on-the-floor macio, percussão de madeira, stabs, baixo em oitavas
  05 risografia      100 BPM  toy piano, contrabaixo andando, vassourinha com swing
  07 tinta na água    70 BPM  pads longos, piano de feltro esparso, sem bateria
Só biblioteca padrão + ffmpeg (reverb, EQ que abre espaço para a voz, mp3).
"""
from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import sys
import tempfile
import wave
from array import array
from pathlib import Path

SR = 32000
TAU = 2 * math.pi


# ----------------------------------------------------------------------------- utilidades

def midi(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


def tabela(harm: list[tuple[float, float]], n: int = 2048) -> list[float]:
    t = [sum(a * math.sin(TAU * h * i / n) for h, a in harm) for i in range(n)]
    pico = max(abs(x) for x in t) or 1
    return [x / pico for x in t]


T_SENO = tabela([(1, 1)])
T_SERRA = tabela([(h, 1 / h) for h in range(1, 12)])
T_MARIMBA = tabela([(1, 1), (4, 0.22), (10, 0.05)])
T_TOY = tabela([(1, 1), (2, 0.25), (5, 0.18), (7, 0.06)])
T_PIANO = tabela([(1, 1), (2, 0.4), (3, 0.16), (4, 0.08), (5, 0.04)])
T_BAIXO = tabela([(1, 1), (2, 0.35), (3, 0.08)])
T_MADEIRA = tabela([(1, 1), (2.0, 0.3)])


class Mix:
    def __init__(self, dur: float):
        self.n = int(dur * SR) + SR * 3
        self.l = [0.0] * self.n
        self.r = [0.0] * self.n
        self.rv = [0.0] * self.n  # envio de reverb (mono)

    def add(self, t: float, s: list[float], g: float, pan: float = 0.5, rev: float = 0.15) -> None:
        i0 = int(t * SR)
        if i0 < 0 or i0 >= self.n:
            return
        gl, gr, gv = g * math.cos(pan * math.pi / 2), g * math.sin(pan * math.pi / 2), g * rev
        L, R, V = self.l, self.r, self.rv
        fim = min(len(s), self.n - i0)
        for k in range(fim):
            x = s[k]
            j = i0 + k
            L[j] += x * gl
            R[j] += x * gr
            if gv:
                V[j] += x * gv


def tom(tab: list[float], f: float, dur: float, tau: float, ataque: float = 0.004,
        soltura: float = 0.08, corte: float | None = None, corte_fim: float | None = None) -> list[float]:
    """Oscilador por tabela com envelope (ataque, decaimento exponencial, soltura) e passa-baixa opcional."""
    n = int((dur + soltura) * SR)
    na, nd = max(int(ataque * SR), 1), int(dur * SR)
    dec = math.exp(-1 / (tau * SR)) if tau else 1.0
    passo, fase, tl = f * len(tab) / SR, 0.0, len(tab)
    out = [0.0] * n
    amp, y = 1.0, 0.0
    a = 1 - math.exp(-TAU * corte / SR) if corte else None
    da = 0.0
    if corte and corte_fim:
        a_fim = 1 - math.exp(-TAU * corte_fim / SR)
        da = (a_fim - a) / n
    for k in range(n):
        x = tab[int(fase) % tl]
        fase += passo
        env = (k / na if k < na else 1.0) * amp
        amp *= dec
        if k >= nd:
            env *= max(0.0, 1 - (k - nd) / (soltura * SR))
        x *= env
        if a is not None:
            y += a * (x - y)
            a += da
            x = y
        out[k] = x
    return out


def pad(f: float, dur: float, ataque: float = 0.6, soltura: float = 0.9, corte: float = 1400) -> list[float]:
    s1 = tom(T_SERRA, f * 1.003, dur, 0, ataque, soltura, corte)
    s2 = tom(T_SERRA, f * 0.997, dur, 0, ataque, soltura, corte)
    return [(a + b) * 0.5 for a, b in zip(s1, s2)]


def karplus(f: float, dur: float, rng: random.Random, brilho: float = 0.5, perda: float = 0.996) -> list[float]:
    p = max(int(SR / f), 2)
    buf = [rng.uniform(-1, 1) for _ in range(p)]
    y = 0.0
    for i in range(p):  # suaviza o ruído inicial (menos brilho = mais "madeira")
        y += brilho * (buf[i] - y)
        buf[i] = y
    n = int(dur * SR)
    out = [0.0] * n
    for k in range(n):
        i = k % p
        nxt = buf[(k + 1) % p]
        out[k] = buf[i]
        buf[i] = perda * 0.5 * (buf[i] + nxt)
    fade = int(0.03 * SR)
    for k in range(max(n - fade, 0), n):
        out[k] *= (n - k) / fade
    return out


def kick(dur: float = 0.35) -> list[float]:
    n, fase, out = int(dur * SR), 0.0, []
    for k in range(n):
        t = k / SR
        fase += TAU * (45 + 110 * math.exp(-t / 0.035)) / SR
        out.append(math.sin(fase) * math.exp(-t / 0.16) + (0.3 * math.exp(-t / 0.003) if k < 100 else 0))
    return out


def ruido(dur: float, tau: float, rng: random.Random, hp: bool = True, lp: float | None = None,
          ataque: float = 0.001) -> list[float]:
    n, prev, y, out = int(dur * SR), 0.0, 0.0, []
    a = 1 - math.exp(-TAU * lp / SR) if lp else None
    na = max(int(ataque * SR), 1)
    for k in range(n):
        x = rng.uniform(-1, 1)
        if hp:
            x, prev = x - prev, x
        if a is not None:
            y += a * (x - y)
            x = y
        out.append(x * math.exp(-k / (tau * SR)) * (k / na if k < na else 1))
    return out


# ----------------------------------------------------------------------------- harmonia

def acorde(pc: int, q: str, base: int) -> list[int]:
    r = base + pc
    return [r, r + (3 if q == "m" else 4), r + 7]


# ----------------------------------------------------------------------------- arranjos

def arr_flat(mx: Mix, dur: float, rng: random.Random) -> None:
    bpm, prog = 112, [(9, "m"), (5, "M"), (0, "M"), (7, "M")]
    b = 60 / bpm
    compassos = math.ceil(dur / (4 * b)) + 1
    k_ = kick()
    for c in range(compassos):
        t0 = c * 4 * b
        pc, q = prog[c % 4]
        for m in acorde(pc, q, 48):
            mx.add(t0, pad(midi(m), 4 * b), 0.05, 0.5, 0.4)
        tons = acorde(pc, q, 60) + [acorde(pc, q, 60)[0] + 12]
        for i, idx in enumerate([0, 2, 1, 3, 0, 2, 1, 2]):
            if c == 0 and i < 2:
                continue
            f = midi(tons[idx])
            mx.add(t0 + i * b / 2 + rng.uniform(-0.004, 0.004),
                   tom(T_SERRA, f, 0.22, 0.12, 0.002, 0.05, 3200, 700), 0.13 * rng.uniform(0.8, 1.05),
                   0.3 if i % 2 else 0.7, 0.3)
        if c == 0:
            continue
        pausa = (c % 8 == 7)
        for bt in (0, 1, 2, 3):
            mx.add(t0 + bt * b, tom(T_BAIXO, midi(36 + pc), b * 0.8, 0.5, 0.005, 0.05, 700), 0.15, 0.5, 0)
        if not pausa:
            for bt in (0, 2) + ((2.5,) if c % 2 else ()):
                mx.add(t0 + bt * b, k_, 0.3, 0.5, 0.02)
            for bt in (0.5, 1.5, 2.5, 3.5):
                mx.add(t0 + bt * b, ruido(0.08, 0.02, rng), 0.06 * rng.uniform(0.8, 1.1), 0.62, 0.05)
            for bt in (1, 3):
                mx.add(t0 + bt * b, ruido(0.25, 0.07, rng, lp=5000), 0.09, 0.45, 0.25)


def arr_linha(mx: Mix, dur: float, rng: random.Random) -> None:
    bpm, prog = 110, [(5, "M"), (2, "m"), (10, "M"), (0, "M")]
    b = 60 / bpm
    compassos = math.ceil(dur / (4 * b)) + 1
    for c in range(compassos):
        t0 = c * 4 * b
        pc, q = prog[c % 4]
        for m in acorde(pc, q, 48):
            mx.add(t0, pad(midi(m), 4 * b, 0.8, 1.0, 1000), 0.03, 0.5, 0.4)
        tons = acorde(pc, q, 60)
        sobe = tons + [tons[0] + 12, tons[1] + 12, tons[2]]
        for i, pos in enumerate([0, 0.75, 1.5, 2, 2.75, 3.5]):
            mx.add(t0 + pos * b + rng.uniform(-0.005, 0.005),
                   tom(T_MARIMBA, midi(sobe[i]), 0.5, 0.22, 0.002, 0.05), 0.2 * rng.uniform(0.8, 1.05),
                   rng.uniform(0.35, 0.65), 0.25)
        if c == 0:
            continue
        for pos, m in ((0, 36 + pc), (1.5, 43 + pc), (2.5, 36 + pc), (3.5, 40 + pc if q == "M" else 39 + pc)):
            mx.add(t0 + pos * b, karplus(midi(m), b * 0.95, rng, 0.25, 0.995), 0.3, 0.5, 0.05)
        if c % 8 != 7:
            for i in range(8):
                mx.add(t0 + i * b / 2, ruido(0.1, 0.035, rng, ataque=0.012), (0.05 if i % 2 else 0.03), 0.6, 0.05)
            mx.add(t0 + 3 * b, tom(T_MADEIRA, 950, 0.06, 0.03), 0.08, 0.35, 0.2)


def arr_bola(mx: Mix, dur: float, rng: random.Random) -> None:
    bpm, prog = 124, [(2, "m"), (10, "M"), (5, "M"), (0, "M")]
    b = 60 / bpm
    compassos = math.ceil(dur / (4 * b)) + 1
    k_ = kick(0.3)
    for c in range(compassos):
        t0 = c * 4 * b
        pc, q = prog[c % 4]
        for m in acorde(pc, q, 48):
            mx.add(t0, pad(midi(m), 4 * b, 0.4, 0.6, 900), 0.03, 0.5, 0.4)
        for pos in (1.5, 3.0) if c % 2 else (0.75, 2.5):
            for m in acorde(pc, q, 60):
                mx.add(t0 + pos * b, tom(T_SERRA, midi(m), 0.12, 0.07, 0.002, 0.04, 4000, 800), 0.07, 0.5, 0.35)
        if c == 0:
            continue
        pausa = (c % 8 == 7)
        for i in range(8):
            m = 36 + pc + (12 if i % 2 else 0)
            mx.add(t0 + i * b / 2, tom(T_BAIXO, midi(m), b * 0.4, 0.15, 0.003, 0.03, 1000), 0.14, 0.5, 0)
        if pausa:
            continue
        for bt in range(4):
            mx.add(t0 + bt * b, k_, 0.3, 0.5, 0.02)
            mx.add(t0 + (bt + 0.5) * b, ruido(0.06, 0.018, rng), 0.06, 0.6, 0.05)
        for pos, f, pan in ((0.75, 820, 0.3), (1.75, 1100, 0.7), (2.75, 820, 0.3), (3.25, 640, 0.6)):
            mx.add(t0 + pos * b, tom(T_MADEIRA, f, 0.07, 0.025), 0.1 * rng.uniform(0.8, 1.1), pan, 0.2)


def arr_riso(mx: Mix, dur: float, rng: random.Random) -> None:
    bpm, prog = 100, [(7, "M"), (4, "m"), (0, "M"), (2, "M")]
    b = 60 / bpm
    sw = 0.66  # swing
    compassos = math.ceil(dur / (4 * b)) + 1
    k_ = kick(0.3)
    for c in range(compassos):
        t0 = c * 4 * b
        pc, q = prog[c % 4]
        tons = acorde(pc, q, 72)
        for m in acorde(pc, q, 55):
            mx.add(t0, tom(T_PIANO, midi(m), 3.5 * b, 1.2, 0.01, 0.3, 1800), 0.06, 0.45, 0.3)
        for pos, idx in ((0, 0), (1, 1), (1 + sw, 2), (2, 1), (3, 0), (3 + sw, 2)):
            if c % 4 == 3 and pos > 3:
                continue
            mx.add(t0 + pos * b + rng.uniform(-0.008, 0.008), tom(T_TOY, midi(tons[idx]), 0.4, 0.28, 0.002, 0.05),
                   0.12 * rng.uniform(0.8, 1.05), 0.62, 0.3)
        if c == 0:
            continue
        nxt = prog[(c + 1) % 4][0]
        anda = [36 + pc, 36 + pc + (3 if q == "m" else 4), 43 + pc, 36 + nxt - 1 if nxt else 47]
        for bt, m in enumerate(anda):
            mx.add(t0 + bt * b, karplus(midi(m), b * 0.9, rng, 0.18, 0.994), 0.36, 0.45, 0.05)
        for bt in (1, 3):
            mx.add(t0 + bt * b, ruido(0.35, 0.12, rng, lp=3500, ataque=0.01), 0.1, 0.55, 0.25)
        for bt in (0, 2 + sw):
            mx.add(t0 + bt * b, k_, 0.2, 0.5, 0.02)
        for bt in range(4):
            for off in (0, sw):
                mx.add(t0 + (bt + off) * b, ruido(0.12, 0.05, rng, lp=6000, ataque=0.02), 0.025, 0.4, 0.05)


def arr_tinta(mx: Mix, dur: float, rng: random.Random) -> None:
    bpm, prog = 70, [(3, "M"), (0, "m"), (8, "M"), (10, "M")]
    b = 60 / bpm
    compassos = math.ceil(dur / (4 * b)) + 1
    for c in range(compassos):
        t0 = c * 4 * b
        pc, q = prog[c % 4]
        for m in acorde(pc, q, 48):
            mx.add(t0, pad(midi(m), 4 * b, 1.4, 1.6, 900), 0.06, 0.5, 0.6)
        mx.add(t0, tom(T_SENO, midi(36 + pc), 4 * b, 0, 1.0, 1.2), 0.08, 0.5, 0.2)
        tons = acorde(pc, q, 72) + [acorde(pc, q, 72)[0] + 12]
        for pos in sorted(rng.sample([0, 1, 1.5, 2, 2.5, 3, 3.5], 3)):
            mx.add(t0 + pos * b + rng.uniform(-0.02, 0.02),
                   tom(T_PIANO, midi(rng.choice(tons)), 1.6, 1.4, 0.008, 0.6, 2200),
                   0.13 * rng.uniform(0.7, 1.0), rng.uniform(0.3, 0.7), 0.7)


ARRANJOS = {
    "00-flat-marca": arr_flat,
    "01-linha-continua": arr_linha,
    "02-bola-unica": arr_bola,
    "05-riso-stop-motion": arr_riso,
    "07-tinta-na-agua": arr_tinta,
}


# ----------------------------------------------------------------------------- saída

def gravar_wav(arq: Path, canais: list[list[float]], pico: float) -> None:
    dados = array("h")
    if len(canais) == 2:
        for a, b in zip(*canais):
            dados.append(int(max(-1, min(1, a / pico)) * 32000))
            dados.append(int(max(-1, min(1, b / pico)) * 32000))
    else:
        for a in canais[0]:
            dados.append(int(max(-1, min(1, a / pico)) * 32000))
    with wave.open(str(arq), "wb") as w:
        w.setnchannels(len(canais))
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(dados.tobytes())


def sintetizar(estilo: str, dur: float, semente: str, saida: Path) -> None:
    rng = random.Random(semente)
    mx = Mix(dur)
    ARRANJOS.get(estilo, arr_flat)(mx, dur, rng)
    pico = max(max(map(abs, mx.l)), max(map(abs, mx.r)), 1e-6) / 0.8
    with tempfile.TemporaryDirectory() as tmp:
        seco, rev = Path(tmp) / "seco.wav", Path(tmp) / "rev.wav"
        gravar_wav(seco, [mx.l, mx.r], pico)
        gravar_wav(rev, [mx.rv], pico)
        filtro = (
            "[1:a]aformat=channel_layouts=stereo,aecho=0.8:0.85:43|71|113|167:0.45|0.35|0.25|0.18,"
            "lowpass=f=5000,highpass=f=180,extrastereo=m=1.6[r];"
            "[0:a][r]amix=inputs=2:weights=1 0.55:normalize=0,highpass=f=35,"
            "equalizer=f=2200:t=q:w=1.2:g=-3.5,acompressor=threshold=0.25:ratio=2:attack=20:release=250,"
            f"atrim=0:{dur:.2f},afade=t=out:st={max(dur - 1.5, 0):.2f}:d=1.5"
        )
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(seco), "-i", str(rev), "-filter_complex", filtro,
                            "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k", str(saida)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            sys.exit(f"ffmpeg falhou:\n{r.stderr[-1500:]}")


def duracao(arq: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roteiro", type=Path, required=True)
    ap.add_argument("--duracao", type=float)
    ap.add_argument("--estilo", help="sobrescreve roteiro.json → estilo.id")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    roteiro = a.roteiro.resolve()
    proj = roteiro.parent
    saida = proj / "audio" / "trilha.mp3"
    if saida.exists() and not a.forcar:
        print(f"já existe: {saida}")
        return
    r = json.loads(roteiro.read_text(encoding="utf-8"))
    estilo = a.estilo or (r.get("estilo") or {}).get("id", "00-flat-marca")
    narr = proj / "audio" / "narracao.mp3"
    seg = a.duracao or (duracao(narr) if narr.exists() else 75.0)
    seg += 2.5
    saida.parent.mkdir(parents=True, exist_ok=True)
    sintetizar(estilo, seg, proj.name, saida)
    (proj / "audio" / "trilha.json").write_text(json.dumps(
        {"fonte": "sintetizada em código (trilha_sintetizada.py) — sem licença de terceiros", "estilo": estilo,
         "duracao_s": round(seg, 1), "semente": proj.name}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"trilha: {saida} ({seg:.1f}s, {estilo})")


if __name__ == "__main__":
    main()

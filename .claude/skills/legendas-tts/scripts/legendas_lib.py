"""Biblioteca de legendas do motion-studio (só biblioteca padrão).

Formato interno de palavra: {"texto": str, "inicio": float, "fim": float} em segundos.
Saídas:
  - Caption (Remotion @remotion/captions): {"text", "startMs", "endMs", "timestampMs", "confidence"}
  - SRT com blocos agrupados por estilo ("reels" ou "padrao").
"""
from __future__ import annotations

import difflib
import json
import os
import re
import unicodedata
from pathlib import Path

# ----------------------------------------------------------------------------- .env

def carregar_env(inicio: Path | None = None) -> None:
    """Carrega o primeiro .env encontrado subindo a partir de `inicio` (sem sobrescrever o ambiente)."""
    d = (inicio or Path.cwd()).resolve()
    for pasta in [d, *d.parents]:
        f = pasta / ".env"
        if f.is_file():
            for linha in f.read_text(encoding="utf-8").splitlines():
                linha = linha.strip()
                if not linha or linha.startswith("#") or "=" not in linha:
                    continue
                k, v = linha.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return


# ----------------------------------------------------------------------------- palavras

def palavras_de_alinhamento(alinhamento: dict, deslocamento: float = 0.0) -> list[dict]:
    """Converte o alinhamento por caractere da ElevenLabs em palavras com tempo."""
    chars = alinhamento.get("characters") or []
    ini = alinhamento.get("character_start_times_seconds") or []
    fim = alinhamento.get("character_end_times_seconds") or []
    palavras: list[dict] = []
    atual, t0, t1 = "", None, None
    for c, a, b in zip(chars, ini, fim):
        if c.isspace():
            if atual:
                palavras.append({"texto": atual, "inicio": t0 + deslocamento, "fim": t1 + deslocamento})
            atual, t0, t1 = "", None, None
            continue
        if not atual:
            t0 = a
        atual += c
        t1 = b
    if atual:
        palavras.append({"texto": atual, "inicio": t0 + deslocamento, "fim": t1 + deslocamento})
    return palavras


def palavras_de_stt(resposta: dict, deslocamento: float = 0.0) -> list[dict]:
    """Converte a resposta do Speech-to-Text (Scribe) em palavras com tempo."""
    out = []
    for w in resposta.get("words", []):
        if w.get("type", "word") != "word":
            continue
        t = (w.get("text") or "").strip()
        if t:
            out.append({"texto": t, "inicio": float(w["start"]) + deslocamento, "fim": float(w["end"]) + deslocamento})
    return out


_FRASE = re.compile(r"(?<=[.!?…])\s+")


def _distribuir(palavras_texto: list[str], inicio: float, fim: float) -> list[dict]:
    """Distribui palavras num intervalo proporcionalmente ao número de letras."""
    pesos = [max(1, len(p)) + 1 for p in palavras_texto]
    total, acc, out = sum(pesos), 0.0, []
    for p, w in zip(palavras_texto, pesos):
        a = inicio + (fim - inicio) * acc / total
        acc += w
        b = inicio + (fim - inicio) * acc / total
        out.append({"texto": p, "inicio": a, "fim": b})
    return out


def remapear_para_legenda(palavras_tts: list[dict], texto_legenda: str) -> list[dict]:
    """Quando a grafia falada (narracao_tts) difere da legenda (narracao), leva os tempos para o texto da legenda.

    1:1 se o número de palavras bate; senão, frase a frase (por pontuação) e, dentro de cada frase,
    proporcional ao tamanho das palavras.
    """
    alvo = texto_legenda.split()
    if not palavras_tts:
        return []
    if len(alvo) == len(palavras_tts):
        return [{"texto": a, "inicio": p["inicio"], "fim": p["fim"]} for a, p in zip(alvo, palavras_tts)]
    frases_alvo = [f.split() for f in _FRASE.split(texto_legenda.strip()) if f.strip()]
    # agrupa as palavras faladas em frases pela pontuação final
    frases_tts, atual = [], []
    for p in palavras_tts:
        atual.append(p)
        if re.search(r"[.!?…]$", p["texto"]):
            frases_tts.append(atual)
            atual = []
    if atual:
        frases_tts.append(atual)
    if len(frases_tts) == len(frases_alvo):
        out = []
        for fa, ft in zip(frases_alvo, frases_tts):
            out += _distribuir(fa, ft[0]["inicio"], ft[-1]["fim"])
        return out
    return _distribuir(alvo, palavras_tts[0]["inicio"], palavras_tts[-1]["fim"])


def _chave(palavra: str) -> str:
    """Forma comparável de uma palavra: minúscula, sem acento e sem pontuação."""
    s = unicodedata.normalize("NFKD", palavra.lower())
    return "".join(c for c in s if c.isalnum())


def alinhar_texto(palavras_stt: list[dict], texto: str) -> list[dict]:
    """Leva os tempos de uma transcrição (que pode errar ou pular palavras) para o texto conhecido.

    Palavras iguais (sem acento/pontuação) pegam o tempo da transcrição; as que ela escreveu diferente
    dividem o tempo das palavras trocadas; as que ela pulou (números, siglas) cabem entre as vizinhas.
    """
    alvo = texto.split()
    if not alvo or not palavras_stt:
        return []
    sm = difflib.SequenceMatcher(None, [_chave(p) for p in alvo], [_chave(p["texto"]) for p in palavras_stt],
                                 autojunk=False)
    out: list[dict] = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out += [{"texto": alvo[i1 + k], "inicio": palavras_stt[j1 + k]["inicio"], "fim": palavras_stt[j1 + k]["fim"]}
                    for k in range(i2 - i1)]
        elif op == "replace":
            out += _distribuir(alvo[i1:i2], palavras_stt[j1]["inicio"], palavras_stt[j2 - 1]["fim"])
        elif op == "delete":
            ini = out[-1]["fim"] if out else palavras_stt[0]["inicio"]
            fim = palavras_stt[j1]["inicio"] if j1 < len(palavras_stt) else palavras_stt[-1]["fim"]
            out += _distribuir(alvo[i1:i2], ini, max(ini, fim))
        # "insert": palavra só na transcrição (ruído, respiração): ignorada
    return out


def palavras_para_captions(palavras: list[dict]) -> list[dict]:
    """Formato Caption do @remotion/captions (texto com espaço antes, exceto a primeira palavra)."""
    out = []
    for i, p in enumerate(palavras):
        a, b = round(p["inicio"] * 1000), round(p["fim"] * 1000)
        c = {"text": (" " if i else "") + p["texto"], "startMs": a, "endMs": max(b, a + 1),
             "timestampMs": round((a + b) / 2), "confidence": None}
        if re.search(r"[.!?…]$", p["texto"]):
            c["pageBreakAfter"] = True  # fim de frase: a legenda animada começa página nova
        out.append(c)
    return out


def captions_para_palavras(captions: list[dict]) -> list[dict]:
    return [{"texto": c["text"].strip(), "inicio": c["startMs"] / 1000, "fim": c["endMs"] / 1000}
            for c in captions if c["text"].strip()]


# ----------------------------------------------------------------------------- blocos de legenda

ESTILOS = {
    # Reels/TikTok: blocos curtos de 1 linha, leitura rápida, acompanhando a fala
    "reels": {"max_chars": 22, "max_linhas": 1, "max_dur": 1.8, "min_dur": 0.5, "pausa": 0.35},
    # Padrão de legendagem (YouTube, institucional): até 2 linhas de 42 caracteres, 1–6 s, ≤ 17 caracteres/s
    "padrao": {"max_chars": 42, "max_linhas": 2, "max_dur": 6.0, "min_dur": 1.0, "pausa": 0.6, "cps": 17},
}


FUNCIONAIS = {"a", "o", "as", "os", "um", "uma", "de", "da", "do", "das", "dos", "na", "no", "nas", "nos",
              "em", "e", "ou", "pra", "pro", "para", "com", "por", "pela", "pelo", "que", "se", "seu", "sua",
              "the", "of", "to", "and", "in", "on", "for"}


def _quebrar_linhas(palavras: list[str], max_chars: int, max_linhas: int) -> list[str] | None:
    """Quebra em até `max_linhas` linhas equilibradas; None se não couber."""
    texto = " ".join(palavras)
    if len(texto) <= max_chars:
        return [texto]
    if max_linhas < 2:
        return None
    melhor = None
    for i in range(1, len(palavras)):
        a, b = " ".join(palavras[:i]), " ".join(palavras[i:])
        if len(a) <= max_chars and len(b) <= max_chars:
            custo = abs(len(a) - len(b)) - (8 if re.search(r"[,;:]$", palavras[i - 1]) else 0) + (12 if palavras[i - 1].lower() in FUNCIONAIS else 0)
            if melhor is None or custo < melhor[0]:
                melhor = (custo, [a, b])
    return melhor[1] if melhor else None


def agrupar(palavras: list[dict], estilo: str = "reels") -> list[dict]:
    """Agrupa palavras em blocos de legenda: {"inicio", "fim", "linhas": [...]}."""
    cfg = ESTILOS[estilo]
    blocos: list[dict] = []
    grupo: list[dict] = []

    def fechar():
        if grupo:
            linhas = _quebrar_linhas([p["texto"] for p in grupo], cfg["max_chars"], cfg["max_linhas"]) or [" ".join(p["texto"] for p in grupo)]
            blocos.append({"inicio": grupo[0]["inicio"], "fim": grupo[-1]["fim"], "linhas": linhas})

    for p in palavras:
        if grupo:
            candidato = [g["texto"] for g in grupo] + [p["texto"]]
            cabe = _quebrar_linhas(candidato, cfg["max_chars"], cfg["max_linhas"]) is not None
            longo = p["fim"] - grupo[0]["inicio"] > cfg["max_dur"]
            pausa = p["inicio"] - grupo[-1]["fim"] > cfg["pausa"]
            fim_frase = bool(re.search(r"[.!?…]$", grupo[-1]["texto"]))
            virgula = bool(re.search(r"[,;:]$", grupo[-1]["texto"])) and estilo == "reels"
            if not cabe or longo or pausa or fim_frase or virgula:
                # não termine um bloco em palavra funcional ("na", "de", "com"…): ela vai para o próximo
                levar = []
                if (not cabe or longo) and len(grupo) > 1 and grupo[-1]["texto"].lower() in FUNCIONAIS:
                    levar = [grupo.pop()]
                fechar()
                grupo = levar
        grupo.append(p)
    fechar()

    # durações mínimas e velocidade de leitura, sem sobrepor o bloco seguinte
    for i, b in enumerate(blocos):
        prox = blocos[i + 1]["inicio"] if i + 1 < len(blocos) else None
        alvo = b["inicio"] + cfg["min_dur"]
        if "cps" in cfg:
            chars = sum(len(l) for l in b["linhas"])
            alvo = max(alvo, b["inicio"] + chars / cfg["cps"])
        fim = max(b["fim"], alvo)
        if prox is not None:
            fim = min(fim, prox - 0.04)  # nunca sobrepõe o bloco seguinte
        b["fim"] = max(b["inicio"] + 0.1, fim)
    return blocos


def _tempo_srt(s: float) -> str:
    ms = max(0, round(s * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def blocos_para_srt(blocos: list[dict]) -> str:
    partes = []
    for i, b in enumerate(blocos, 1):
        partes.append(f"{i}\n{_tempo_srt(b['inicio'])} --> {_tempo_srt(b['fim'])}\n" + "\n".join(b["linhas"]) + "\n")
    return "\n".join(partes)


def salvar_legendas(palavras: list[dict], pasta: Path, estilo: str = "reels", nome: str = "legendas") -> dict:
    """Grava palavras.json (Caption do Remotion) e <nome>.srt. Devolve os caminhos."""
    pasta.mkdir(parents=True, exist_ok=True)
    caps = palavras_para_captions(palavras)
    p_json = pasta / "palavras.json"
    p_json.write_text(json.dumps(caps, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / ".estimado").unlink(missing_ok=True)  # agora os tempos vêm da voz (ver palavras_estimadas.py)
    p_srt = pasta / f"{nome}.srt"
    p_srt.write_text(blocos_para_srt(agrupar(palavras, estilo)), encoding="utf-8")
    return {"palavras": str(p_json), "srt": str(p_srt)}

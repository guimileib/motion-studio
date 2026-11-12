#!/usr/bin/env python3
"""Narração local com o VoiceStudio (API compatível com a OpenAI) + legendas SRT e palavras para o Remotion.

O VoiceStudio devolve só o áudio, sem timestamps: cada trecho gerado é transcrito pelo próprio VoiceStudio
(palavras com tempo) e os tempos são levados para o texto do roteiro.

Uso:
  # todas as cenas de um roteiro (gera audio/, legendas/ ao lado do roteiro.json)
  python tts_voicestudio.py --roteiro projetos/meu-video/roteiro.json

  # refazer só uma cena / forçar nova geração
  python tts_voicestudio.py --roteiro projetos/meu-video/roteiro.json --cenas fim --forcar

  # só reconstruir legendas a partir das transcrições já salvas
  python tts_voicestudio.py --roteiro projetos/meu-video/roteiro.json --so-legendas

  # texto avulso
  python tts_voicestudio.py --texto "Cansado de adivinhar quanto pedir?" --saida saida/teste

Precisa do VoiceStudio aberto (VOICESTUDIO_URL, padrão http://127.0.0.1:3900) e de ffmpeg para a mixagem.
Licença: os pesos do motor padrão (omnivoice) são CC-BY-NC. Em peça comercial use um motor Apache-2.0
que fale português (voxcpm2, moss-tts-nano).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from legendas_lib import alinhar_texto, carregar_env, remapear_para_legenda, salvar_legendas  # noqa: E402
from stt_elevenlabs import multipart  # noqa: E402
from tts_elevenlabs import duracao_audio, hash_texto, mixar  # noqa: E402

NAO_COMERCIAIS = ("omnivoice", "omnivoice-gguf", "omnivoice-subprocess")


def chamar(base: str, req: urllib.request.Request, chave: str) -> bytes:
    if chave:
        req.add_header("Authorization", f"Bearer {chave}")
    try:
        with urllib.request.urlopen(req, timeout=900) as r:  # na CPU uma cena pode levar minutos
            return r.read()
    except urllib.error.HTTPError as e:
        corpo = e.read().decode("utf-8", "replace")
        try:
            detalhe = json.loads(corpo)["error"]["message"]
        except (ValueError, KeyError, TypeError):
            detalhe = corpo[:600]
        sys.exit(f"VoiceStudio respondeu {e.code}: {detalhe}")
    except urllib.error.URLError as e:
        sys.exit(f"Não consegui acessar o VoiceStudio em {base} ({e.reason}). Abra o app e confira VOICESTUDIO_URL.")


def gerar(base: str, texto: str, cfg: dict, chave: str) -> bytes:
    corpo = {"model": cfg["modelo"], "input": texto, "voice": cfg["voz"], "language": cfg["idioma"],
             "speed": cfg["velocidade"], "response_format": "wav"}
    if cfg.get("instrucoes"):
        corpo["instructions"] = cfg["instrucoes"]
    if cfg.get("seed") is not None:
        corpo["seed"] = cfg["seed"]
    req = urllib.request.Request(f"{base}/v1/audio/speech", data=json.dumps(corpo).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json"})
    return chamar(base, req, chave)


def transcrever(base: str, arq: Path, idioma: str, chave: str) -> list[dict]:
    campos = {"model": "whisper-1", "language": idioma, "response_format": "verbose_json",
              "timestamp_granularities[]": "word"}
    corpo, ctype = multipart(campos, arq)
    req = urllib.request.Request(f"{base}/v1/audio/transcriptions", data=corpo, method="POST",
                                 headers={"Content-Type": ctype, "Accept": "application/json"})
    resp = json.loads(chamar(base, req, chave).decode("utf-8"))
    return [{"texto": w["word"].strip(), "inicio": float(w["start"]), "fim": float(w["end"])}
            for w in resp.get("words") or [] if w.get("word", "").strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roteiro", type=Path)
    ap.add_argument("--texto")
    ap.add_argument("--saida", type=Path, help="pasta de saída (modo --texto)")
    ap.add_argument("--cenas", help="ids separados por vírgula (padrão: todas)")
    ap.add_argument("--voz", help="perfil de voz do VoiceStudio, id ou nome (padrão: roteiro ou VOICESTUDIO_VOICE)")
    ap.add_argument("--modelo", help="motor do VoiceStudio (padrão: roteiro ou VOICESTUDIO_MODEL)")
    ap.add_argument("--velocidade", type=float)
    ap.add_argument("--estilo-legenda", choices=["reels", "padrao"])
    ap.add_argument("--forcar", action="store_true", help="gera de novo mesmo com cache")
    ap.add_argument("--so-legendas", action="store_true", help="não chama o VoiceStudio; usa as transcrições salvas")
    a = ap.parse_args()

    carregar_env(Path(__file__).resolve().parent)
    carregar_env()
    base = os.environ.get("VOICESTUDIO_URL", "http://127.0.0.1:3900").rstrip("/")
    chave = os.environ.get("VOICESTUDIO_API_KEY", "")

    if a.texto:
        rot = {"cenas": [{"id": "texto", "duracao_s": 600, "narracao": a.texto}], "voz": {}}
        pasta = a.saida or Path("saida")
    elif a.roteiro:
        rot = json.loads(a.roteiro.read_text(encoding="utf-8"))
        pasta = a.roteiro.parent
    else:
        ap.error("use --roteiro ou --texto")

    voz_cfg = dict(rot.get("voz") or {})
    vs = dict(voz_cfg.get("voicestudio") or {})
    cfg = {
        "modelo": a.modelo or vs.get("modelo") or os.environ.get("VOICESTUDIO_MODEL") or "omnivoice",
        "voz": a.voz or vs.get("voz") or os.environ.get("VOICESTUDIO_VOICE") or "default",
        "idioma": vs.get("idioma", "pt-BR"),
        "velocidade": a.velocidade or voz_cfg.get("velocidade", 1.0),
        "instrucoes": vs.get("instrucoes"),
        "seed": vs.get("seed"),
    }
    idioma_stt = cfg["idioma"].split("-")[0]
    estilo = a.estilo_legenda or rot.get("legenda_estilo", "reels")
    if not a.so_legendas and cfg["modelo"] in NAO_COMERCIAIS:
        print(f"! motor '{cfg['modelo']}': pesos de uso NÃO comercial (OmniVoice, CC-BY-NC). "
              "Para anúncio ou cliente use voxcpm2 ou moss-tts-nano.")

    dir_audio, dir_leg = pasta / "audio", pasta / "legendas"
    dir_audio.mkdir(parents=True, exist_ok=True)
    escolhidas = set(a.cenas.split(",")) if a.cenas else None

    inicio = 0.0
    segmentos, todas_palavras, relatorio = [], [], []
    for c in rot["cenas"]:
        c_ini = float(c.get("inicio_s", inicio))
        inicio = c_ini + float(c["duracao_s"])
        legenda = (c.get("narracao") or "").strip()
        if not legenda:
            continue
        # tags SSML da ElevenLabs (<break …/>) não valem aqui: a pausa vem da pontuação
        falado = " ".join(re.sub(r"<[^>]+>", " ", c.get("narracao_tts") or legenda).split())
        atraso = float(c.get("narracao_inicio_s", 0.15))
        arq_wav, arq_stt = dir_audio / f"{c['id']}.wav", dir_audio / f"{c['id']}.voicestudio.json"
        h = hash_texto(falado, json.dumps(cfg, sort_keys=True))

        precisa = escolhidas is None or c["id"] in escolhidas
        em_cache = arq_stt.exists() and arq_wav.exists() and json.loads(arq_stt.read_text("utf-8")).get("hash") == h
        if not a.so_legendas and precisa and (a.forcar or not em_cache):
            print(f"→ gerando {c['id']}: {falado[:60]}…")
            arq_wav.write_bytes(gerar(base, falado, cfg, chave))
            stt = transcrever(base, arq_wav, idioma_stt, chave)
            arq_stt.write_text(json.dumps({"hash": h, "texto": falado, "palavras": stt}, ensure_ascii=False),
                               encoding="utf-8")
        if not arq_stt.exists():
            print(f"! {c['id']}: sem transcrição salva, pulei")
            continue

        dados = json.loads(arq_stt.read_text("utf-8"))
        palavras = alinhar_texto(dados["palavras"], dados["texto"])
        if not palavras:
            print(f"! {c['id']}: a transcrição veio vazia; confira o áudio {arq_wav}")
            continue
        for p in palavras:
            p["inicio"] += c_ini + atraso
            p["fim"] += c_ini + atraso
        if dados["texto"] != legenda:
            palavras = remapear_para_legenda(palavras, legenda)
        todas_palavras += palavras
        segmentos.append((arq_wav, c_ini + atraso))

        dur = duracao_audio(arq_wav) or (palavras[-1]["fim"] - c_ini - atraso)
        vaga = float(c["duracao_s"]) - atraso
        estado = "ok"
        if dur > vaga + 0.05:
            estado = f"PASSA {dur - vaga:.2f}s — encurte o texto ou use velocidade {min(1.2, dur / vaga * cfg['velocidade']):.2f}"
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

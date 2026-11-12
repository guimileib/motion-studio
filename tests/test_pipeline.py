"""Testes offline do motion-studio (sem chamar APIs).

  python -m unittest discover -s tests -v

Simula o alinhamento da ElevenLabs, roda o tts_elevenlabs.py em --so-legendas e confere SRT,
palavras.json e a mixagem; testa o agrupamento de legendas e o remapeamento narracao_tts → narracao.
Roda o tts_voicestudio.py contra um VoiceStudio falso (servidor HTTP local).
"""
from __future__ import annotations

import http.server
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import wave
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPTS = RAIZ / ".claude/skills/legendas-tts/scripts"
sys.path.insert(0, str(SCRIPTS))
import legendas_lib as L  # noqa: E402


def alinhamento_falso(texto: str, cps: float = 14.0) -> dict:
    """Alinhamento por caractere com velocidade constante (≈ 2,5 palavras/s)."""
    chars = list(texto)
    ini = [i / cps for i in range(len(chars))]
    fim = [(i + 1) / cps for i in range(len(chars))]
    return {"characters": chars, "character_start_times_seconds": ini, "character_end_times_seconds": fim}


class TestLib(unittest.TestCase):
    def test_palavras_de_alinhamento(self):
        p = L.palavras_de_alinhamento(alinhamento_falso("A Veta te diz."), 2.0)
        self.assertEqual([x["texto"] for x in p], ["A", "Veta", "te", "diz."])
        self.assertAlmostEqual(p[0]["inicio"], 2.0)
        self.assertTrue(all(a["fim"] <= b["inicio"] + 1e-9 for a, b in zip(p, p[1:])))

    def test_remapear_mesma_contagem(self):
        tts = L.palavras_de_alinhamento(alinhamento_falso("Veta I.A."))
        r = L.remapear_para_legenda(tts, "Veta IA.")
        self.assertEqual([x["texto"] for x in r], ["Veta", "IA."])
        self.assertEqual(r[1]["inicio"], tts[1]["inicio"])

    def test_remapear_contagem_diferente(self):
        tts = L.palavras_de_alinhamento(alinhamento_falso("O sistema de éfe éle vê. Compre certo."))
        r = L.remapear_para_legenda(tts, "O sistema de FLV. Compre certo.")
        self.assertEqual(len(r), 6)
        self.assertAlmostEqual(r[0]["inicio"], tts[0]["inicio"])
        self.assertAlmostEqual(r[-1]["fim"], tts[-1]["fim"])
        # a 2ª frase começa onde a 2ª frase falada começa
        self.assertAlmostEqual(r[4]["inicio"], tts[6]["inicio"])

    def test_alinhar_texto_com_erros_da_transcricao(self):
        def stt(*palavras):
            return [{"texto": t, "inicio": i * 0.5, "fim": i * 0.5 + 0.4} for i, t in enumerate(palavras)]

        texto = "A Veta te dá 30 por cento."
        # sem pontuação, "Veta" ouvido como "beta" e "30" escrito por extenso: pegam o tempo da palavra trocada
        s = stt("a", "beta", "te", "dá", "trinta", "por", "cento")
        r = L.alinhar_texto(s, texto)
        self.assertEqual([x["texto"] for x in r], texto.split())
        self.assertEqual((r[1]["inicio"], r[1]["fim"]), (0.5, 0.9))
        self.assertEqual((r[4]["inicio"], r[4]["fim"]), (2.0, 2.4))
        self.assertEqual(r[-1]["fim"], s[-1]["fim"])
        # "30" pulado e um "hum" a mais: o número cabe entre as vizinhas, o ruído é ignorado
        s = stt("a", "veta", "hum", "te", "dá", "por", "cento")
        r = L.alinhar_texto(s, texto)
        self.assertEqual([x["texto"] for x in r], texto.split())
        self.assertEqual(r[2]["inicio"], 1.5)
        self.assertAlmostEqual(r[4]["inicio"], r[3]["fim"])
        self.assertAlmostEqual(r[4]["fim"], r[5]["inicio"])

    def test_agrupar_reels_e_padrao(self):
        txt = "Pedido calculado pela venda real, com margem contra ruptura. Menos falta na gôndola, menos perda na banca."
        p = L.palavras_de_alinhamento(alinhamento_falso(txt))
        reels = L.agrupar(p, "reels")
        self.assertTrue(all(len(b["linhas"]) == 1 and len(b["linhas"][0]) <= 22 for b in reels))
        padrao = L.agrupar(p, "padrao")
        self.assertTrue(all(len(b["linhas"]) <= 2 and all(len(l) <= 42 for l in b["linhas"]) for b in padrao))
        for a, b in zip(padrao, padrao[1:]):
            self.assertLessEqual(a["fim"], b["inicio"])
        for b in reels[:-1]:
            self.assertNotIn(b["linhas"][0].split()[-1].lower(), L.FUNCIONAIS)

    def test_sem_sobreposicao_quando_fala_estoura(self):
        p = L.palavras_de_alinhamento(alinhamento_falso("uma fala longa que passa do tempo da cena"), 0)
        q = L.palavras_de_alinhamento(alinhamento_falso("próxima cena"), p[-1]["fim"] - 0.5)
        blocos = L.agrupar(p + q, "padrao")
        for a, b in zip(blocos, blocos[1:]):
            self.assertLessEqual(a["fim"], b["inicio"])

    def test_srt_formato(self):
        srt = L.blocos_para_srt([{"inicio": 3661.5, "fim": 3662.25, "linhas": ["Olá", "mundo"]}])
        self.assertIn("01:01:01,500 --> 01:01:02,250\nOlá\nmundo", srt)

    def test_captions_remotion(self):
        caps = L.palavras_para_captions([{"texto": "A", "inicio": 0.1, "fim": 0.2}, {"texto": "Veta", "inicio": 0.25, "fim": 0.6}])
        self.assertEqual(caps[0]["text"], "A")
        self.assertEqual(caps[1]["text"], " Veta")
        self.assertTrue({"text", "startMs", "endMs", "timestampMs", "confidence"} <= set(caps[0]))


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg ausente")
class TestTTSOffline(unittest.TestCase):
    def test_roteiro_exemplo_so_legendas(self):
        rot_origem = RAIZ / "projetos/exemplo-veta-pedido-certo/roteiro.json"
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "audio").mkdir(parents=True)
            shutil.copy(rot_origem, proj / "roteiro.json")
            rot = json.loads(rot_origem.read_text("utf-8"))
            for c in rot["cenas"]:
                falado = c.get("narracao_tts") or c["narracao"]
                al = alinhamento_falso(falado)
                dur = al["character_end_times_seconds"][-1]
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
                                "-t", f"{dur:.2f}", str(proj / "audio" / f"{c['id']}.mp3")], check=True)
                (proj / "audio" / f"{c['id']}.alinhamento.json").write_text(json.dumps({"hash": "x", "alignment": al}), "utf-8")
            r = subprocess.run([sys.executable, str(SCRIPTS / "tts_elevenlabs.py"), "--roteiro", str(proj / "roteiro.json"), "--so-legendas"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            caps = json.loads((proj / "legendas/palavras.json").read_text("utf-8"))
            self.assertEqual(caps[0]["text"], "Cansado")
            self.assertAlmostEqual(caps[0]["startMs"], 150, delta=2)
            ultima = [c for c in caps if c["text"].strip() == "IA."]
            self.assertTrue(ultima, "a legenda usa 'IA.' (narracao), não a grafia falada")
            self.assertGreaterEqual(ultima[0]["startMs"], 16000 + 1200)
            self.assertTrue((proj / "legendas/legendas.srt").read_text("utf-8").startswith("1\n00:00:00,150"))
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                        str(proj / "audio/narracao.mp3")], capture_output=True, text=True).stdout)
            self.assertAlmostEqual(dur, 23.02, delta=0.1)
            # salva o exemplo usado pelo LegendasDemo do Remotion
            destino = RAIZ / "remotion/src/demo/legendas-exemplo.json"
            destino.write_text(json.dumps(caps, ensure_ascii=False, indent=1), "utf-8")


class VoiceStudioFalso(http.server.BaseHTTPRequestHandler):
    """Imita /v1/audio/speech (WAV mudo, 0,4 s por palavra) e /v1/audio/transcriptions (palavras com tempo)."""
    pedidos: list[dict] = []
    ultimo_texto = ""

    def do_POST(self):
        corpo = self.rfile.read(int(self.headers["Content-Length"]))
        if self.path == "/v1/audio/speech":
            pedido = json.loads(corpo)
            VoiceStudioFalso.pedidos.append(pedido)
            VoiceStudioFalso.ultimo_texto = pedido["input"]
            buf = io.BytesIO()
            with wave.open(buf, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(24000)
                w.writeframes(b"\0\0" * int(24000 * 0.4 * len(pedido["input"].split())))
            self._responder(buf.getvalue(), "audio/wav")
        elif self.path == "/v1/audio/transcriptions":
            assert b'name="timestamp_granularities[]"' in corpo and b"verbose_json" in corpo
            # como o Whisper: minúsculas, sem pontuação, e uma palavra ouvida errado
            palavras = [re.sub(r"[^\w]", "", p.lower()).replace("veta", "beta") for p in self.ultimo_texto.split()]
            words = [{"word": p, "start": i * 0.4, "end": i * 0.4 + 0.35} for i, p in enumerate(palavras)]
            self._responder(json.dumps({"text": " ".join(palavras), "words": words}).encode(), "application/json")
        else:
            self.send_error(404)

    def _responder(self, dados: bytes, tipo: str):
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def log_message(self, *args):
        pass


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg ausente")
class TestVoiceStudioOffline(unittest.TestCase):
    def test_roteiro_exemplo_com_servidor_falso(self):
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), VoiceStudioFalso)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                proj = Path(tmp) / "proj"
                proj.mkdir()
                shutil.copy(RAIZ / "projetos/exemplo-veta-pedido-certo/roteiro.json", proj / "roteiro.json")
                env = {**os.environ, "VOICESTUDIO_URL": f"http://127.0.0.1:{srv.server_port}",
                       "VOICESTUDIO_MODEL": "voxcpm2", "VOICESTUDIO_VOICE": "Locutora"}
                r = subprocess.run([sys.executable, str(SCRIPTS / "tts_voicestudio.py"), "--roteiro", str(proj / "roteiro.json")],
                                   capture_output=True, text=True, env=env)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(len(VoiceStudioFalso.pedidos), 4)
                self.assertEqual({(p["model"], p["voice"], p["language"]) for p in VoiceStudioFalso.pedidos},
                                 {("voxcpm2", "Locutora", "pt-BR")})
                caps = json.loads((proj / "legendas/palavras.json").read_text("utf-8"))
                self.assertEqual(caps[0]["text"], "Cansado")
                self.assertAlmostEqual(caps[0]["startMs"], 150, delta=2)
                self.assertIn(" Veta", [c["text"] for c in caps], "a legenda usa o texto do roteiro, não a transcrição")
                self.assertTrue([c for c in caps if c["text"].strip() == "IA."])
                dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                            str(proj / "audio/narracao.mp3")], capture_output=True, text=True).stdout)
                self.assertAlmostEqual(dur, 23.02, delta=0.1)
                self.assertIn("pedido", (proj / "audio/relatorio.txt").read_text("utf-8"))
                # segunda rodada: tudo em cache, nenhuma geração nova
                r = subprocess.run([sys.executable, str(SCRIPTS / "tts_voicestudio.py"), "--roteiro", str(proj / "roteiro.json")],
                                   capture_output=True, text=True, env=env)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(len(VoiceStudioFalso.pedidos), 4)
        finally:
            srv.shutdown()
            srv.server_close()


class TestBuscaMidia(unittest.TestCase):
    def test_melhor_arquivo_e_orientacao(self):
        sys.path.insert(0, str(RAIZ / ".claude/skills/busca-midia/scripts"))
        import buscar_midia as B
        arqs = [{"url": "a", "largura": 720, "altura": 1280}, {"url": "b", "largura": 1080, "altura": 1920},
                {"url": "c", "largura": 2160, "altura": 3840}]
        self.assertEqual(B.melhor_arquivo(arqs)["url"], "b")
        self.assertTrue(B.orientacao_ok(1080, 1920, "vertical"))
        self.assertFalse(B.orientacao_ok(1920, 1080, "vertical"))
        man = {"cenas": {"a": {"escolhido": 0, "candidatos": [{"fonte": "unsplash", "autor": "Ana", "autor_url": "u", "pagina": "p", "tipo": "foto", "licenca": "x"}]}}}
        self.assertIn("Photo by [Ana](u) on [Unsplash](p)", B.creditos(man))


class TestRoteiro(unittest.TestCase):
    def test_exemplo_soma_duracao(self):
        rot = json.loads((RAIZ / "projetos/exemplo-veta-pedido-certo/roteiro.json").read_text("utf-8"))
        self.assertAlmostEqual(sum(c["duracao_s"] for c in rot["cenas"]), rot["duracao_alvo_s"], places=3)
        tipos = json.loads((RAIZ / ".claude/skills/roteiro-persuasivo/templates/roteiro.schema.json").read_text("utf-8"))
        enum = tipos["properties"]["cenas"]["items"]["properties"]["transicao_saida"]["properties"]["tipo"]["enum"]
        for c in rot["cenas"]:
            self.assertIn(c["transicao_saida"]["tipo"], enum)


if __name__ == "__main__":
    unittest.main()

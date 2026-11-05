# Único (apaga a si mesmo): legendas mostram endereços escritos (www.legiscopio.com.br/baixar, @legiscopio,
# apoia.se/legiscopio) em vez da forma falada; aplica em scripts/video_longo.py e refaz o Resumo de 2 min de 2026-11-05.
import subprocess
import traceback
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARQ = ROOT / "scripts" / "video_longo.py"
VELHO = "def blocos_legenda(palavras, dur, texto):\n    if not palavras:\n        ws = texto.split()\n        palavras = [(dur * k / max(1, len(ws)), w) for k, w in enumerate(ws)]\n    else:\n        palavras = alinhar(palavras, texto)\n"
NOVO = "# Na LEGENDA, endereços e perfis falados por extenso aparecem escritos (a voz continua falando por extenso).\n# A ordem importa: as sequências mais longas primeiro.\nENDERECOS = [\n    (\"legiscopio ponto com ponto br barra baixar\", \"www.legiscopio.com.br/baixar\"),\n    (\"legiscopio ponto com ponto br\", \"www.legiscopio.com.br\"),\n    (\"apoia ponto se barra legiscopio\", \"apoia.se/legiscopio\"),\n    (\"arroba legiscopio\", \"@legiscopio\"),\n]\n\n\ndef _sem_acento(w):\n    import unicodedata\n    w = unicodedata.normalize(\"NFD\", w.lower())\n    return \"\".join(ch for ch in w if ch.isalnum() and not unicodedata.combining(ch))\n\n\ndef trocar_enderecos(palavras):\n    \"\"\"[(t, palavra)] -> mesma lista com 'legiscopio ponto com ponto br barra baixar' etc. na forma escrita.\"\"\"\n    toks = [(t, x) for t, w in palavras for x in w.split()]\n    out, k = [], 0\n    while k < len(toks):\n        achou = False\n        for falado, escrito in ENDERECOS:\n            alvo = falado.split()\n            n = len(alvo)\n            if k + n <= len(toks) and [_sem_acento(x) for _, x in toks[k:k + n]] == alvo:\n                ult = toks[k + n - 1][1]\n                resto = ult[len(ult.rstrip(\".,;:!?\")):]\n                out.append((toks[k][0], escrito + resto))\n                k += n\n                achou = True\n                break\n        if not achou:\n            out.append(toks[k])\n            k += 1\n    return out\n\n\ndef blocos_legenda(palavras, dur, texto):\n    if not palavras:\n        ws = texto.split()\n        palavras = [(dur * k / max(1, len(ws)), w) for k, w in enumerate(ws)]\n    else:\n        palavras = alinhar(palavras, texto)\n    palavras = trocar_enderecos(palavras)\n"
PASTA = ROOT / "videos" / "2026-11-05"
try:
    s = ARQ.read_text(encoding="utf-8")
    if "def trocar_enderecos" not in s:
        assert s.count(VELHO) == 1, "trecho de blocos_legenda não encontrado"
        ARQ.write_text(s.replace(VELHO, NOVO), encoding="utf-8")
    subprocess.run(["git", "add", str(ARQ)], check=True, cwd=ROOT)

    PASTA = ROOT / "videos" / "2026-11-05"
    (PASTA / ".resumo_render").unlink(missing_ok=True)
    sys.path.insert(0, str(ROOT / "scripts"))
    for m in ("short_video", "video_longo"):
        sys.modules.pop(m, None)
    import short_video  # noqa: E402
    import video_longo as vl  # noqa: E402

    short_video.gerar(PASTA / "resumo.json")
    mp4 = PASTA / "resumo.mp4"
    if mp4.exists():
        subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-sseof", "-14", "-i", str(mp4),
                        "-vf", "fps=1/2,scale=270:480,tile=6x1", "-frames:v", "1",
                        str(PASTA / "resumo_final_previa.png")], check=True)
    (PASTA / "legendas_erro.txt").unlink(missing_ok=True)
except Exception:
    (PASTA / "legendas_erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(ARQ)], check=True, cwd=ROOT)

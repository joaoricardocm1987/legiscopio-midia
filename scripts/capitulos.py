"""Capítulos do YouTube a partir do video.json + legendas.srt (gerados por video_longo).

Grava videos/<data>/capitulos.txt no formato que o YouTube reconhece:
  00:00 Introdução
  00:28 Título da cena
  ...
Regras do YouTube: 1º capítulo em 00:00, pelo menos 3 capítulos, cada um com 10 s ou mais
(aqui usamos no mínimo 25 s entre eles).
"""
import json
import re
import sys
from pathlib import Path


def _norm(t):
    return re.sub(r"[^a-z0-9à-ú ]", "", t.lower()).split()


def _srt(caminho):
    blocos = []
    for bloco in caminho.read_text(encoding="utf-8").strip().split("\n\n"):
        linhas = [l for l in bloco.strip().splitlines() if l.strip()]
        if len(linhas) < 3 or "-->" not in linhas[1]:
            continue
        ini = linhas[1].split("-->")[0].strip()
        h, m, rest = ini.split(":")
        s, ms = rest.split(",")
        blocos.append((int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000, " ".join(linhas[2:])))
    return blocos


def _tempo(t):
    t = int(t)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def gerar(caminho_json):
    p = Path(caminho_json)
    pasta = p.parent
    srt = pasta / "legendas.srt"
    if not srt.exists():
        print("sem legendas.srt; capítulos não gerados", pasta)
        return
    cfg = json.loads(p.read_text(encoding="utf-8"))
    blocos = _srt(srt)
    j, caps = 0, []
    for c in cfg.get("cenas", []):
        alvo = _norm(c.get("fala", ""))[:3]
        ini = None
        for k in range(j, len(blocos)):
            seguidas = _norm(" ".join(b[1] for b in blocos[k:k + 3]))
            if seguidas[:len(alvo)] == alvo:
                ini, j = blocos[k][0], k + 1
                break
        if ini is None:
            continue
        v = c.get("visual", {})
        tipo = v.get("tipo")
        if tipo == "capa":
            nome = "Introdução"
        elif tipo in ("redes", "fim"):
            nome = "Siga e apoie o Legiscópio"
        else:
            nome = (v.get("titulo") or "").strip()
        if not nome:
            continue
        if not caps:
            caps.append([0.0, nome])
        elif nome != caps[-1][1] and ini - caps[-1][0] >= 25:
            caps.append([ini, nome])
    texto = "\n".join(f"{_tempo(t)} {n}" for t, n in caps) if len(caps) >= 3 else ""
    (pasta / "capitulos.txt").write_text(texto + "\n", encoding="utf-8")
    print(f"capítulos: {len(caps)}", pasta)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        gerar(arg)

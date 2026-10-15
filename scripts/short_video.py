"""YouTube Short diário do Legiscópio (1080x1920, ~1 min): resumo do vídeo longo.

Lê videos/<data>/video.json, seção "short", e gera na mesma pasta:
  short.mp4   vídeo vertical com narração, mascote Lupa, visuais e legendas

Formato (dentro do video.json):
"short": {
  "cenas": [ {"fala": "...", "visual": {...}}, ... ],   (5 a 7 cenas, ~140 palavras no total)
  "youtube": {"titulo": "...", "descricao": "...", "tags": [...]}
}
Visuais: os mesmos do vídeo longo (capa, numero, comparacao, barras, lista, etapas, texto)
e mais "cta" {titulo?, subtitulo?} — chamada para o vídeo completo no canal (use na última cena).
"""
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from contextlib import contextmanager
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mascote  # noqa: E402
import video_longo as vl  # noqa: E402

VERSAO = "1"
W, H, FPS = 1080, 1920, vl.FPS
SR = vl.SR
PAUSA = 0.3
PAINEL = (70, 300, 1010, 1020)
MASC = 340
MASC_POS = (W // 2 - MASC // 2, 1290)
LEG_Y = 1060  # topo da faixa de legenda (acima da área coberta pelos botões do Shorts)


@contextmanager
def painel_vertical():
    antigo, tit = vl.PAINEL, vl.titulo_painel
    vl.PAINEL = PAINEL
    vl.titulo_painel = lambda d, t, y=None: tit(d, t, PAINEL[1] if y is None else y)
    try:
        yield
    finally:
        vl.PAINEL, vl.titulo_painel = antigo, tit


def fundo_base():
    img = Image.new("RGB", (W, H), vl.FUNDO)
    d = ImageDraw.Draw(img)
    lg = vl.logo(80)
    if lg:
        img.paste(lg, (70, 110), lg)
    d.rounded_rectangle([70, 215, 470, 265], radius=14, fill=vl.VERDE)
    d.text((270, 240), "RESUMO EM 1 MINUTO", font=vl.MO(24), fill=vl.LIMA, anchor="mm")
    d.text((W // 2, H - 70), "legiscopio.com.br · apoia.se/legiscopio", font=vl.MO(26), fill=vl.TEXTO2, anchor="ms")
    return img


def desenhar_cta(img, v, p):
    d = ImageDraw.Draw(img)
    x0, y0, x1, _ = PAINEL
    a = vl.suave(p)
    off = int(40 * (1 - a))
    y = y0 + 20 + off
    for l in vl.wrap(d, v.get("titulo", "Quer entender tudo?"), vl.BK(84), x1 - x0):
        d.text((x0, y), l, font=vl.BK(84), fill=vl.VERDE)
        y += 100
    y += 30
    d.rounded_rectangle([x0, y, x1, y + 330], radius=30, fill=vl.VERDE)
    d.text((x0 + 50, y + 40), "▶", font=vl.BK(90), fill=vl.LIMA)
    d.text((x0 + 170, y + 50), "Vídeo completo", font=vl.BK(70), fill=vl.BRANCO)
    d.text((x0 + 170, y + 140), "no canal", font=vl.BK(70), fill=vl.BRANCO)
    sub = v.get("subtitulo", "Legiscópio Explica · todos os detalhes")
    d.text((x0 + 50, y + 255), sub, font=vl.RG(38), fill=vl.LIMA_TX)
    y += 380
    vl.card(d, x0, y, x1, y + 120)
    d.text((x0 + 50, y + 60), "Inscreva-se no Legiscópio", font=vl.BD(50), fill=vl.TEXTO, anchor="lm")


def desenhar(img, v, p, t, dur):
    if v.get("tipo") == "cta":
        desenhar_cta(img, v, p)
        return
    with painel_vertical():
        vl.desenhar_visual(img, v, p, t, dur)


def deslocamento(v, dur):
    tela = Image.new("RGB", (W, H), vl.FUNDO)
    desenhar(tela, v, 1.0, dur, dur)
    bbox = ImageChops.difference(tela, Image.new("RGB", (W, H), vl.FUNDO)).getbbox()
    if not bbox:
        return 0
    alto = bbox[3] - bbox[1]
    alvo = PAINEL[1] + max(0, (PAINEL[3] - PAINEL[1] - alto) // 2)
    return max(0, alvo - bbox[1])


def visual_em(base, v, p, t, dur, dy):
    tela = Image.new("RGB", (W, H), vl.FUNDO)
    desenhar(tela, v, p, t, dur)
    out = base.copy()
    lim = min(PAINEL[3] + 30, LEG_Y - 10 - dy)
    faixa = tela.crop((0, PAINEL[1] - 20, W, lim))
    out.paste(faixa, (0, PAINEL[1] - 20 + dy))
    return out


def legenda_img(texto):
    f = vl.BD(54)
    tmp = Image.new("RGBA", (W, 320), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    linhas = vl.wrap(d, texto, f, W - 200)[:3]
    hh = len(linhas) * 70 + 40
    larg = max(d.textlength(l, font=f) for l in linhas) + 80
    x0 = (W - larg) / 2
    d.rounded_rectangle([x0, 0, x0 + larg, hh], radius=24, fill=(3, 60, 32, 235))
    for k, l in enumerate(linhas):
        d.text((W / 2, 20 + k * 70), l, font=f, fill=vl.BRANCO, anchor="mt")
    return tmp.crop((0, 0, W, hh)), hh


def blocos(palavras, dur, texto):
    bl = vl.blocos_legenda(palavras, dur, texto)
    # junta blocos curtos para legendas de até ~3 linhas no vertical
    out = []
    for ini, txt, fim in bl:
        if out and len(out[-1][1]) + len(txt) < 60 and not out[-1][1].endswith((".", "?", "!")):
            out[-1] = [out[-1][0], out[-1][1] + " " + txt, fim]
        else:
            out.append([ini, txt, fim])
    return out


def gerar(caminho_json):
    p = Path(caminho_json)
    pasta = p.parent
    cfg = json.loads(p.read_text(encoding="utf-8"))
    sh = cfg.get("short")
    if not sh or not sh.get("cenas"):
        print("sem seção 'short' em", p)
        return
    bruto = json.dumps({"voz": cfg.get("voz"), "velocidade": cfg.get("velocidade"), "short": sh},
                       sort_keys=True, ensure_ascii=False).encode()
    assinatura = hashlib.sha256(bruto + VERSAO.encode() + vl.VERSAO.encode()
                                + str(bool(os.environ.get("LEGIS_FAKE_TTS"))).encode()).hexdigest()
    marca = pasta / ".short_render"
    destino = pasta / "short.mp4"
    if marca.exists() and marca.read_text().strip() == assinatura and destino.exists():
        print("short sem mudanças", pasta)
        return
    voz = cfg.get("voz", "pt-BR-FranciscaNeural")
    taxa = cfg.get("velocidade", "+0%")
    tmp = pasta / "_tmp_short"
    tmp.mkdir(exist_ok=True)

    cenas = []
    for i, c in enumerate(sh["cenas"]):
        amostras, palavras = vl.tts(c["fala"], voz, taxa, tmp, i)
        dur = len(amostras) / 2 / SR
        cenas.append(dict(c, amostras=amostras, palavras=palavras, dur=dur + PAUSA))
        print(f"short cena {i + 1}/{len(sh['cenas'])}: {dur:.1f}s")

    silencio = bytes(int(PAUSA * SR) * 2)
    wav_total = tmp / "narracao.wav"
    with wave.open(str(wav_total), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(c["amostras"] + silencio for c in cenas))

    cmd = [vl.ffmpeg(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(wav_total),
           "-c:v", "libx264", "-preset", "veryfast", "-tune", "animation", "-crf", "22", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(destino)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    base = fundo_base()
    qg, t_glob = 0, 0.0
    for i, c in enumerate(cenas):
        dur = c["dur"]
        nq = int(round(dur * FPS))
        env = vl.envelope(c["amostras"], nq)
        legs = blocos(c["palavras"], dur - PAUSA, c["fala"])
        v = c.get("visual", {})
        dy = deslocamento(v, dur)
        cache_vis = chave_vis = cache_leg = chave_leg = None
        for q in range(nq):
            t = q / FPS
            tipo = v.get("tipo")
            lento = {"comparacao": 1.4, "barras": 2.0}.get(tipo, 0.7)
            prog = min(1.0, t / lento)
            chave = (round(prog, 2), int(t * 8)) if tipo == "lista" else round(prog, 2)
            if chave != chave_vis:
                cache_vis = visual_em(base, v, prog, t, dur, dy)
                chave_vis = chave
            quadro = cache_vis.copy()

            nivel = env[q] if q < len(env) else 0
            boca = "fechada" if nivel < 0.18 else ("meia" if nivel < 0.5 else "aberta")
            if i == len(cenas) - 1 and nivel < 0.18:
                boca = "sorriso"
            ciclo = (qg + i * 17) % (FPS * 4)
            olhos = "fechados" if ciclo < 3 else ("surpresos" if tipo == "numero" and t < 1.5 else "abertos")
            sp = mascote.sprite(boca, olhos, MASC)
            bob = int(6 * math.sin(qg / FPS * 2.2))
            quadro.paste(sp, (MASC_POS[0], MASC_POS[1] + bob), sp)

            atual = next((txt for ini, txt, fim in legs if ini <= t < fim), "")
            if atual != chave_leg:
                cache_leg = legenda_img(atual) if atual else None
                chave_leg = atual
            if cache_leg:
                li, _ = cache_leg
                quadro.paste(li, (0, LEG_Y), li)

            proc.stdin.write(quadro.tobytes())
            qg += 1
        t_glob += dur
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou")
    shutil.rmtree(tmp, ignore_errors=True)
    marca.write_text(assinatura + "\n")
    print(f"ok {destino} ({t_glob:.1f} s)")
    if t_glob > 62:
        print(f"AVISO: short com {t_glob:.1f}s (meta: até 60s)")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        gerar(arg)

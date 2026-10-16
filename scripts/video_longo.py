"""Vídeo explicativo diário do Legiscópio (YouTube, 1920x1080, ~8-10 min).

Lê videos/<data>/video.json e gera, na mesma pasta:
  video.mp4      vídeo com narração (voz neural), Lupa 2.0 (personagem) e gráficos
  thumb.jpg      miniatura 1280x720
  legendas.srt   legendas sincronizadas com a fala

Formato do video.json:
{
  "voz": "pt-BR-AntonioNeural",          (opcional)
  "velocidade": "+0%",                   (opcional)
  "thumb": {"linha1": "...", "linha2": "...", "destaque": "..."},
  "cenas": [
    {"fala": "texto narrado", "visual": {"tipo": "...", ...}},
    ...
  ]
}
Tipos de visual:
  capa       {titulo, subtitulo}
  numero     {valor, rotulo, titulo?}
  comparacao {titulo?, antes:{valor, rotulo}, depois:{valor, rotulo}}
  barras     {titulo, itens:[{rotulo, valor, texto?}], nota?}
  lista      {titulo, itens:[...]}             (itens aparecem ao longo da fala)
  etapas     {titulo, itens:[...], atual}      (linha do tempo; atual = índice)
  texto      {titulo, texto}                   (título com "?" deixa a Lupa pensativa)
  redes      {titulo?, itens?:[[rótulo, valor]], app?: true}  (redes sociais, site e app)
  fim        {}                                 (apoia.se, site, inscreva-se)

Chamada do meio: por padrão, no meio do vídeo a Lupa pede like, inscrição e sininho
sem trocar a tela (o visual anterior fica parado e aparece a barra animada).
Opcional no video.json: "cta_meio": false (desliga) ou "cta_meio_fala": "texto próprio".

A pose da Lupa é escolhida automaticamente pelo tipo de cena (pose_da_cena).
Vídeos de datas passadas que já existem não são regerados quando o código muda.
Para testar sem internet: LEGIS_FAKE_TTS=1 gera um áudio sintético.
"""
import asyncio
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cta_meio  # noqa: E402  (like, inscrever-se e sininho no meio do vídeo)
import personagem  # noqa: E402  (Lupa 2.0, corpo inteiro)

VERSAO = "4"
W, H, FPS = 1920, 1080, 24
SR = 24000
PAUSA = 0.45  # segundos de respiro entre cenas

FUNDO = (244, 247, 243)
VERDE = (5, 87, 47)
VERDE_ESC = (3, 60, 32)
TEXTO = (16, 37, 26)
TEXTO2 = (74, 93, 81)
OLIVA = (94, 127, 34)
BRANCO = (255, 255, 255)
LIMA = (185, 216, 106)
LIMA_TX = (228, 240, 200)
BORDA = (203, 214, 204)
TAG = (230, 237, 211)

ROOT = Path(__file__).resolve().parents[1]
N = "/usr/share/fonts/opentype/noto/"
DJ = "/usr/share/fonts/truetype/dejavu/"


def achar(*cs):
    for c in cs:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(", ".join(cs))


F_BLACK = achar(N + "NotoSansCJK-Black.ttc", N + "NotoSansCJK-Bold.ttc", DJ + "DejaVuSans-Bold.ttf")
F_BOLD = achar(N + "NotoSansCJK-Bold.ttc", DJ + "DejaVuSans-Bold.ttf")
F_REG = achar(N + "NotoSansCJK-Regular.ttc", DJ + "DejaVuSans.ttf")
F_MONO = achar(DJ + "DejaVuSansMono.ttf")
_fc = {}


def fonte(caminho, tam):
    k = (caminho, tam)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(caminho, tam, index=0) if caminho.endswith(".ttc") else ImageFont.truetype(caminho, tam)
    return _fc[k]


BK = lambda s: fonte(F_BLACK, s)  # noqa: E731
BD = lambda s: fonte(F_BOLD, s)  # noqa: E731
RG = lambda s: fonte(F_REG, s)  # noqa: E731
MO = lambda s: fonte(F_MONO, s)  # noqa: E731

LOGO = next((p for p in [ROOT / "artes" / "assets" / "logo-legiscopio.png", ROOT / "artes" / "logo-legiscopio.png"]
             if p.exists()), None)


def wrap(d, t, f, maxw):
    out, line = [], ""
    for w in str(t).split():
        test = (line + " " + w).strip()
        if d.textlength(test, font=f) <= maxw:
            line = test
        else:
            if line:
                out.append(line)
            line = w
    if line:
        out.append(line)
    return out


def suave(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ja_passou(nome_pasta):
    """True se a pasta (AAAA-MM-DD) é de um dia anterior a hoje (horário de Brasília)."""
    import datetime
    hoje = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%Y-%m-%d")
    return len(nome_pasta) == 10 and nome_pasta < hoje


# ------------------------------------------------------------------ Lupa 2.0

def pose_da_cena(v, t, i, n_cenas, nivel):
    """Escolhe a pose da Lupa conforme o tipo de visual da cena.
    Regra editorial: nada de comemorar resultado de votação (neutralidade)."""
    tipo = v.get("tipo", "texto")
    titulo = (v.get("titulo") or "") + " " + (v.get("texto") or "")
    if tipo == "capa":
        nome = "acenando" if t < 2.6 else "explicando"
    elif tipo == "numero":
        nome = "surpresa" if t < 1.6 else "apontando"
    elif tipo in ("comparacao", "barras", "etapas"):
        nome = "apontando"
    elif tipo == "lista":
        nome = "explicando" if int(t / 6) % 2 == 0 else "apontando"
    elif tipo == "redes":
        nome = "joinha"
    elif tipo == "fim":
        nome = "acenando" if t > 2 else "explicando"
    elif "?" in titulo:
        nome = "pensando"
    else:
        nome = "explicando"
    if nome == "surpresa" and nivel < 0.18:
        boca = "o"
    else:
        boca = "fechada" if nivel < 0.18 else ("meia" if nivel < 0.5 else "aberta")
        if i == n_cenas - 1 and nivel < 0.18:
            boca = "sorriso"
    olhos = "surpresos" if nome == "surpresa" else ("desconfiados" if nome == "pensando" else "abertos")
    return nome, boca, olhos


# ------------------------------------------------------------------ áudio

def ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "imageio-ffmpeg"], check=True)
        import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


async def _tts(texto, voz, taxa, mp3):
    import edge_tts
    try:
        com = edge_tts.Communicate(texto, voz, rate=taxa, boundary="WordBoundary")
    except TypeError:
        com = edge_tts.Communicate(texto, voz, rate=taxa)
    palavras = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                palavras.append((ch["offset"] / 1e7, ch["text"]))
    return palavras


def tts(texto, voz, taxa, pasta, i):
    """Devolve (amostras int16 mono a 24 kHz, [(inicio_s, palavra)])."""
    wav = pasta / f"cena{i:02d}.wav"
    if os.environ.get("LEGIS_FAKE_TTS"):
        palavras_txt = texto.split()
        dur = 0.36 * len(palavras_txt) + 0.3
        n = int(dur * SR)
        amostras = bytearray()
        palavras = []
        for k in range(n):
            t = k / SR
            idx = int(t / 0.36)
            env = abs(math.sin(math.pi * ((t % 0.36) / 0.36))) if idx < len(palavras_txt) else 0
            v = int(9000 * env * math.sin(2 * math.pi * 180 * t))
            amostras += v.to_bytes(2, "little", signed=True)
        for k, p in enumerate(palavras_txt):
            palavras.append((k * 0.36, p))
        return bytes(amostras), palavras
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "edge-tts"], check=True)
    mp3 = pasta / f"cena{i:02d}.mp3"
    for tentativa in range(4):
        try:
            palavras = asyncio.run(_tts(texto, voz, taxa, mp3))
            break
        except Exception as e:  # rede instável: tenta de novo
            print("TTS falhou, tentando de novo:", e)
            if tentativa == 3:
                raise
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", str(SR),
                    "-f", "s16le", str(wav)], check=True)
    return wav.read_bytes(), palavras


def envelope(amostras, nquadros):
    """Volume (0..1) por quadro de vídeo, para mexer a boca."""
    import array
    a = array.array("h")
    a.frombytes(amostras[: len(amostras) // 2 * 2])
    por = SR // FPS
    vals = []
    for q in range(nquadros):
        bloco = a[q * por:(q + 1) * por]
        if not bloco:
            vals.append(0.0)
            continue
        vals.append(math.sqrt(sum(x * x for x in bloco[::4]) / max(1, len(bloco[::4]))))
    ref = sorted(vals)[int(len(vals) * 0.95)] if vals else 1
    ref = ref or 1
    return [min(1.0, v / ref) for v in vals]


# ------------------------------------------------------------------ legendas

def _norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum())


def alinhar(palavras, texto):
    """Troca as palavras do TTS (sem pontuação) pelas do texto original, mantendo os tempos."""
    orig = texto.split()
    out, j = [], 0
    for t, w in palavras:
        nw = _norm(w)
        k = j
        while k < len(orig) and k < j + 4 and not (_norm(orig[k]) and (_norm(orig[k]).startswith(nw) or nw.startswith(_norm(orig[k])))):
            k += 1
        if k < len(orig) and k < j + 4:
            # inclui tokens pulados (ex.: "-") junto da palavra encontrada
            out.append((t, " ".join(orig[j:k + 1])))
            j = k + 1
        else:
            out.append((t, w))
    if out and j < len(orig):
        t, w = out[-1]
        out[-1] = (t, w + " " + " ".join(orig[j:]))
    return out


def blocos_legenda(palavras, dur, texto):
    if not palavras:
        ws = texto.split()
        palavras = [(dur * k / max(1, len(ws)), w) for k, w in enumerate(ws)]
    else:
        palavras = alinhar(palavras, texto)
    blocos, atual, ini = [], [], None
    for t, w in palavras:
        if ini is None:
            ini = t
        atual.append(w)
        if len(" ".join(atual)) > 46 or w.endswith((".", "?", "!", ":")):
            blocos.append([ini, " ".join(atual)])
            atual, ini = [], None
    if atual:
        blocos.append([ini, " ".join(atual)])
    for k in range(len(blocos)):
        fim = blocos[k + 1][0] if k + 1 < len(blocos) else dur
        blocos[k].append(fim)
    return blocos  # [inicio, texto, fim]


def srt_tempo(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


# ------------------------------------------------------------------ desenho

PAINEL = (80, 150, 1380, 860)  # área do conteúdo
_logo_cache = {}


def logo(alt):
    if alt not in _logo_cache and LOGO:
        lg = Image.open(LOGO).convert("RGBA")
        _logo_cache[alt] = lg.resize((round(lg.width * alt / lg.height), alt), Image.LANCZOS)
    return _logo_cache.get(alt)


def fundo_base():
    img = Image.new("RGB", (W, H), FUNDO)
    d = ImageDraw.Draw(img)
    lg = logo(84)
    if lg:
        img.paste(lg, (70, 34), lg)
    txt = "LEGISCÓPIO EXPLICA"
    f = MO(26)
    d.text((W - 70, 64), txt, font=f, fill=OLIVA, anchor="ra")
    d.text((70, H - 26), "legiscopio.com.br  ·  apoia.se/legiscopio", font=MO(20), fill=TEXTO2, anchor="ls")
    return img


def card(d, x0, y0, x1, y1, barra=True, cor=BRANCO, borda=VERDE):
    d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=cor, outline=borda, width=3)
    if barra:
        d.rounded_rectangle([x0, y0, x0 + 18, y1], radius=9, fill=VERDE)
        d.rectangle([x0 + 9, y0, x0 + 18, y1], fill=VERDE)


def titulo_painel(d, t, y=PAINEL[1]):
    if not t:
        return y
    f = BK(66)
    for l in wrap(d, t, f, PAINEL[2] - PAINEL[0]):
        d.text((PAINEL[0], y), l, font=f, fill=VERDE)
        y += 82
    return y + 34


def desenhar_visual(img, v, p, t, dur):
    """p = progresso da entrada (0..1); t = tempo na cena."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = PAINEL
    tipo = v.get("tipo", "texto")
    a = suave(p)
    off = int(40 * (1 - a))

    if tipo == "capa":
        f = BK(96)
        y = y0 + 120 + off
        for l in wrap(d, v.get("titulo", ""), f, x1 - x0):
            d.text((x0, y), l, font=f, fill=VERDE)
            y += 112
        if v.get("subtitulo"):
            y += 20
            for l in wrap(d, v["subtitulo"], RG(44), x1 - x0):
                d.text((x0, y), l, font=RG(44), fill=TEXTO2)
                y += 58

    elif tipo == "numero":
        y = titulo_painel(d, v.get("titulo")) + 20
        f = BK(int(300 * (0.85 + 0.15 * a)))
        while d.textlength(v["valor"], font=f) > x1 - x0 and f.size > 80:
            f = BK(f.size - 10)
        d.text((x0 - 6, y + off), v["valor"], font=f, fill=VERDE)
        y = d.textbbox((x0 - 6, y + off), v["valor"], font=f)[3] + 40
        for l in wrap(d, v.get("rotulo", ""), RG(54), x1 - x0):
            d.text((x0, y), l, font=RG(54), fill=TEXTO)
            y += 70

    elif tipo == "comparacao":
        y = titulo_painel(d, v.get("titulo")) + 10
        larg = (x1 - x0 - 120) // 2
        for k, lado in enumerate(["antes", "depois"]):
            item = v[lado]
            aa = suave(p * 2 - k)
            cx0 = x0 + k * (larg + 120)
            cor = BRANCO if k == 0 else VERDE
            card(d, cx0, y + int(40 * (1 - aa)), cx0 + larg, y + 500 + int(40 * (1 - aa)), barra=False, cor=cor,
                 borda=BORDA if k == 0 else VERDE)
            if aa <= 0:
                continue
            fv = BK(200)
            while d.textlength(item["valor"], font=fv) > larg - 60:
                fv = BK(fv.size - 10)
            yy = y + 70 + int(40 * (1 - aa))
            d.text((cx0 + larg // 2, yy), item["valor"], font=fv, fill=VERDE if k == 0 else BRANCO, anchor="mt")
            yy += fv.size + 40
            for l in wrap(d, item.get("rotulo", ""), RG(46), larg - 60):
                d.text((cx0 + larg // 2, yy), l, font=RG(46), fill=TEXTO2 if k == 0 else LIMA_TX, anchor="mt")
                yy += 58
        ax = x0 + larg + 60
        d.text((ax, y + 250), "→", font=BK(90), fill=OLIVA, anchor="mm")

    elif tipo == "barras":
        y = titulo_painel(d, v.get("titulo"))
        itens = v["itens"]
        vmax = max(float(i["valor"]) for i in itens) or 1
        h_item = min(150, (y1 - y - 40) // max(1, len(itens)))
        rot_w = 400
        for k, it in enumerate(itens):
            aa = suave(p * 1.6 - k * 0.25)
            yy = y + k * h_item
            rl = wrap(d, it["rotulo"], BD(42), rot_w - 20)[:2]
            meio = yy + 8 + (h_item - 34) // 2
            for kk, l in enumerate(rl):
                d.text((x0, meio + (kk - (len(rl) - 1) / 2) * 48), l, font=BD(42), fill=TEXTO, anchor="lm")
            bw = int((x1 - x0 - rot_w - 220) * float(it["valor"]) / vmax * aa)
            d.rounded_rectangle([x0 + rot_w, yy + 8, x0 + rot_w + max(bw, 6), yy + h_item - 26], radius=12,
                                fill=VERDE if k % 2 == 0 else OLIVA)
            if aa > 0.3:
                d.text((x0 + rot_w + bw + 20, yy + (h_item - 18) // 2), it.get("texto", str(it["valor"])),
                       font=BK(54), fill=VERDE, anchor="lm")
        if v.get("nota"):
            d.text((x0, y + len(itens) * h_item + 30), v["nota"], font=MO(28), fill=TEXTO2, anchor="ls")

    elif tipo == "lista":
        y = titulo_painel(d, v.get("titulo"))
        itens = v["itens"]
        janela = max(dur * 0.85, 1)
        tam = 50
        while tam > 32:
            f = RG(tam)
            total = sum(len(wrap(d, it, f, x1 - x0 - 100)) * int(tam * 1.28) + 44 for it in itens)
            if y + total <= y1 + 20:
                break
            tam -= 2
        f = RG(tam)
        lh = int(tam * 1.28)
        for k, it in enumerate(itens):
            ti = janela * k / max(1, len(itens))
            aa = suave((t - ti) / 0.5)
            if aa <= 0:
                break
            linhas = wrap(d, it, f, x1 - x0 - 100)
            hh = len(linhas) * lh + 44
            dx = int(40 * (1 - aa))
            d.ellipse([x0 + dx, y + 16, x0 + 44 + dx, y + 60], fill=VERDE)
            d.text((x0 + 22 + dx, y + 38), str(k + 1), font=BD(30), fill=BRANCO, anchor="mm")
            for kk, l in enumerate(linhas):
                d.text((x0 + 70 + dx, y + 6 + kk * lh), l, font=f, fill=TEXTO)
            y += hh

    elif tipo == "etapas":
        y = titulo_painel(d, v.get("titulo")) + 60
        itens = v["itens"]
        atual = v.get("atual", len(itens) - 1)
        n = len(itens)
        mx = 150
        passo = (x1 - x0 - 2 * mx) / max(1, n - 1)
        cy = y + 60
        d.line([(x0 + mx, cy), (x0 + mx + passo * (n - 1), cy)], fill=BORDA, width=12)
        fim_verde = x0 + mx + passo * min(atual, n - 1) * a
        d.line([(x0 + mx, cy), (fim_verde, cy)], fill=VERDE, width=12)
        for k, it in enumerate(itens):
            cx = x0 + mx + passo * k
            feito = k <= atual and a >= (k / max(1, atual) if atual else 1) - 0.01
            r = 42 if k == atual else 32
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=VERDE if feito else BRANCO, outline=VERDE, width=6)
            if feito:
                d.text((cx, cy), "✓" if k < atual else "●", font=BD(36), fill=BRANCO, anchor="mm")
            ff = BD(40) if k == atual else RG(38)
            for kk, l in enumerate(wrap(d, it, ff, min(passo * 0.95, 300) if n > 1 else 400)[:3]):
                d.text((cx, cy + 80 + kk * 48), l, font=ff, fill=TEXTO if k <= atual else TEXTO2, anchor="mt")

    elif tipo == "redes":
        y = titulo_painel(d, v.get("titulo", "Siga o Legiscópio"))
        itens = v.get("itens") or [["Instagram", "@legiscopio"], ["TikTok", "@legiscopio"], ["Site", "legiscopio.com.br"]]
        for k, (rot, val) in enumerate(itens):
            aa = suave(p * 2 - k * 0.35)
            if aa <= 0:
                continue
            dx = int(40 * (1 - aa))
            yy = y + k * 130
            card(d, x0 + dx, yy, x1 - 200 + dx, yy + 106)
            d.text((x0 + 50 + dx, yy + 53), rot, font=BD(40), fill=TEXTO2, anchor="lm")
            d.text((x0 + 330 + dx, yy + 53), val, font=BK(56), fill=VERDE, anchor="lm")
        if v.get("app", True):
            yy = y + len(itens) * 130 + 20
            aa = suave(p * 2 - len(itens) * 0.35)
            if aa > 0:
                d.rounded_rectangle([x0, yy, x1 - 200, yy + 150], radius=24, fill=VERDE)
                d.text((x0 + 40, yy + 26), "App em fase de testes", font=BK(48), fill=LIMA)
                d.text((x0 + 40, yy + 92), "Conheça pelo site · em breve no Android e iOS", font=RG(38), fill=LIMA_TX)

    elif tipo == "fim":
        f = BK(80)
        d.text((x0, y0 + 80 + off), "Gostou? Apoie o Legiscópio", font=f, fill=VERDE)
        card(d, x0, y0 + 230, x1, y0 + 420)
        d.text((x0 + 60, y0 + 270), "apoia.se/legiscopio", font=BK(72), fill=VERDE)
        d.text((x0 + 60, y0 + 360), "Projeto independente e gratuito de transparência parlamentar", font=RG(34),
               fill=TEXTO2)
        d.text((x0, y0 + 500), "Inscreva-se e ative o sininho  ·  legiscopio.com.br", font=BD(44), fill=TEXTO)

    else:  # texto
        y = titulo_painel(d, v.get("titulo"))
        f = RG(54)
        linhas = wrap(d, v.get("texto", ""), f, x1 - x0 - 110)
        hh = len(linhas) * 72 + 80
        card(d, x0, y + off, x1, y + hh + off)
        for k, l in enumerate(linhas):
            d.text((x0 + 60, y + 36 + k * 72 + off), l, font=f, fill=TEXTO)


def deslocamento(v, dur):
    """Quanto descer o conteúdo para ficar centralizado no painel (calculado no estado final)."""
    tela = Image.new("RGB", (W, H), FUNDO)
    desenhar_visual(tela, v, 1.0, dur, dur)
    from PIL import ImageChops
    bbox = ImageChops.difference(tela, Image.new("RGB", (W, H), FUNDO)).getbbox()
    if not bbox:
        return 0
    alto = bbox[3] - bbox[1]
    alvo_top = PAINEL[1] + max(0, (PAINEL[3] - PAINEL[1] - alto) // 2)
    return max(0, alvo_top - bbox[1])


def visual_em(base, v, p, t, dur, dy):
    tela = Image.new("RGB", (W, H), FUNDO)
    desenhar_visual(tela, v, p, t, dur)
    out = base.copy()
    fundo_lim = min(PAINEL[3] + 40, H - 60 - dy)
    faixa = tela.crop((0, PAINEL[1] - 20, W - 480, fundo_lim))
    out.paste(faixa, (0, PAINEL[1] - 20 + dy))
    return out


def legenda_img(texto):
    f = BD(44)
    tmp = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    linhas = wrap(d, texto, f, 1300)[:2]
    hh = len(linhas) * 58 + 36
    larg = max(d.textlength(l, font=f) for l in linhas) + 80
    x0 = (1450 - larg) / 2 + 30
    d.rounded_rectangle([x0, 0, x0 + larg, hh], radius=20, fill=(3, 60, 32, 235))
    for k, l in enumerate(linhas):
        d.text((x0 + larg / 2, 18 + k * 58), l, font=f, fill=BRANCO, anchor="mt")
    return tmp.crop((0, 0, W, hh)), hh


# ------------------------------------------------------------------ miniatura

def miniatura(cfg, destino):
    tw, th = 1280, 720
    img = Image.new("RGB", (tw, th), VERDE)
    d = ImageDraw.Draw(img)
    for k in range(0, tw + th, 48):  # listras sutis
        d.line([(k, 0), (k - th, th)], fill=(8, 96, 53), width=18)
    sp = personagem.pose("surpresa", "o", "surpresos", 780, 0.0, -1, espelho=True)
    img.paste(sp, (tw - sp.width + 140, 10), sp)
    th_cfg = cfg.get("thumb", {})
    y = 60
    for chave, tam, cor in [("linha1", 96, BRANCO), ("linha2", 96, BRANCO)]:
        t = th_cfg.get(chave, "")
        if not t:
            continue
        f = BK(tam)
        while d.textlength(t.upper(), font=f) > 800 and f.size > 50:
            f = BK(f.size - 6)
        d.text((56, y), t.upper(), font=f, fill=cor, stroke_width=4, stroke_fill=VERDE_ESC)
        y += f.size + 14
    if th_cfg.get("destaque"):
        t = th_cfg["destaque"]
        f = BK(150)
        while d.textlength(t, font=f) > 700 and f.size > 60:
            f = BK(f.size - 8)
        bw = d.textlength(t, font=f) + 60
        d.rounded_rectangle([40, y + 20, 40 + bw, y + 20 + f.size + 50], radius=24, fill=LIMA)
        d.text((70, y + 34), t, font=f, fill=VERDE_ESC)
    lg = logo(70)
    if lg:
        box = Image.new("RGBA", (lg.width + 30, lg.height + 20), (255, 255, 255, 235))
        img.paste(box, (40, th - lg.height - 50), box)
        img.paste(lg, (55, th - lg.height - 40), lg)
    img.save(destino, quality=92)


# ------------------------------------------------------------------ principal

def gerar(caminho_json):
    p = Path(caminho_json)
    pasta = p.parent
    bruto = p.read_bytes()
    assinatura = hashlib.sha256(bruto + VERSAO.encode() + str(bool(os.environ.get("LEGIS_FAKE_TTS"))).encode()).hexdigest()
    marca = pasta / ".video_render"
    if marca.exists() and marca.read_text().strip() == assinatura and (pasta / "video.mp4").exists():
        print("vídeo sem mudanças", pasta)
        return
    if (pasta / "video.mp4").exists() and ja_passou(pasta.name):
        print("vídeo de data passada já existe; não regera", pasta)
        return
    cfg = json.loads(bruto.decode("utf-8"))
    voz = cfg.get("voz", "pt-BR-AntonioNeural")
    taxa = cfg.get("velocidade", "+0%")
    tmp = pasta / "_tmp_video"
    tmp.mkdir(exist_ok=True)

    miniatura(cfg, pasta / "thumb.jpg")

    # 1) áudio de cada cena
    cenas = []
    for i, c in enumerate(cfg["cenas"]):
        amostras, palavras = tts(c["fala"], voz, taxa, tmp, i)
        dur = len(amostras) / 2 / SR
        cenas.append(dict(c, amostras=amostras, palavras=palavras, dur=dur + PAUSA))
        print(f"cena {i + 1}/{len(cfg['cenas'])}: {dur:.1f}s")

    # chamada do meio (like, inscrever-se, sininho): entra na divisa de cenas mais perto da metade
    if cfg.get("cta_meio", True) and len(cenas) >= 4:
        total = sum(c["dur"] for c in cenas)
        acum, melhor, dist = 0.0, None, None
        for k, c in enumerate(cenas[:-1]):
            acum += c["dur"]
            prox = cenas[k + 1].get("visual", {}).get("tipo")
            if k == 0 or c.get("visual", {}).get("tipo") in ("redes", "fim") or prox in ("redes", "fim"):
                continue
            if dist is None or abs(acum - total / 2) < dist:
                melhor, dist = k + 1, abs(acum - total / 2)
        if melhor:
            fala = cfg.get("cta_meio_fala") or cta_meio.FALA_PADRAO
            amostras, palavras = tts(fala, voz, taxa, tmp, 99)
            dur = len(amostras) / 2 / SR
            ant = cenas[melhor - 1]
            cenas.insert(melhor, dict(fala=fala, visual=ant.get("visual", {}), _cta=True, _ant_dur=ant["dur"],
                                      amostras=amostras, palavras=palavras, dur=dur + PAUSA,
                                      _mk=cta_meio.marcos(palavras, dur)))
            print(f"chamada do meio (like/inscrição/sino) antes da cena {melhor + 1}: {dur:.1f}s")

    silencio = bytes(int(PAUSA * SR) * 2)
    audio_total = b"".join(c["amostras"] + silencio for c in cenas)
    wav_total = tmp / "narracao.wav"
    with wave.open(str(wav_total), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(audio_total)

    # 2) vídeo
    destino = pasta / "video.mp4"
    cmd = [ffmpeg(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(wav_total),
           "-c:v", "libx264", "-preset", "veryfast", "-tune", "animation", "-crf", "23", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(destino)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    base = fundo_base()
    srt, n_srt, t_glob = [], 1, 0.0
    quadro_glob = 0
    for i, c in enumerate(cenas):
        dur = c["dur"]
        nq = int(round(dur * FPS))
        env = envelope(c["amostras"], nq)
        legs = blocos_legenda(c["palavras"], dur - PAUSA, c["fala"])
        for ini, txt, fim in legs:
            srt.append(f"{n_srt}\n{srt_tempo(t_glob + ini)} --> {srt_tempo(t_glob + fim)}\n{txt}\n")
            n_srt += 1
        cache_vis, chave_vis = None, None
        cta = c.get("_cta", False)
        dy = deslocamento(c.get("visual", {}), c["_ant_dur"] if cta else dur)
        cache_leg, chave_leg = None, None
        for q in range(nq):
            t = q / FPS
            pent = min(1.0, t / 0.7)
            v = c.get("visual", {})
            if cta:  # tela parada no estado final da cena anterior
                if cache_vis is None:
                    cache_vis = visual_em(base, v, 1.0, c["_ant_dur"], c["_ant_dur"], dy)
                chave = chave_vis = "cta"
            elif v.get("tipo") == "lista":
                chave = (round(pent, 2), int(t * 8))
            elif v.get("tipo") == "comparacao":
                chave = round(min(1.0, t / 1.4), 2)
            elif v.get("tipo") == "barras":
                chave = round(min(1.0, t / 2.0), 2)
            else:
                chave = round(pent, 2)
            if chave != chave_vis:
                prog = pent
                if v.get("tipo") == "comparacao":
                    prog = min(1.0, t / 1.4)
                elif v.get("tipo") == "barras":
                    prog = min(1.0, t / 2.0)
                cache_vis = visual_em(base, v, prog, t, dur, dy)
                chave_vis = chave
            quadro = cache_vis.copy()

            # barra da chamada do meio (entra de baixo e sai no final)
            if cta:
                bar = cta_meio.barra(t, c["_mk"], fonte_bd=BD(88), fonte_bk=BK(84))
                ent = suave(t / 0.4) * suave((dur - PAUSA - t + 0.2) / 0.4)
                by = int(660 + 80 * (1 - ent))
                if ent > 0.02:
                    if ent < 0.98:
                        bar = bar.copy()
                        bar.putalpha(bar.getchannel("A").point(lambda x: int(x * ent)))
                    quadro.paste(bar, (130, by), bar)

            # Lupa 2.0 (virada para o conteúdo, à esquerda)
            nivel = env[q] if q < len(env) else 0
            if cta:
                nome, boca, olhos = pose_da_cena({"tipo": "redes"}, t, i, len(cenas), nivel)
            else:
                nome, boca, olhos = pose_da_cena(v, t, i, len(cenas), nivel)
            ciclo = (quadro_glob + i * 17) % (FPS * 4)
            if ciclo < 3 and olhos == "abertos":
                olhos = "fechados"
            sp = personagem.pose(nome, boca, olhos, 660, quadro_glob / FPS, -1, espelho=True)
            quadro.paste(sp, (W - sp.width - 10, H - sp.height - 40), sp)

            # legenda
            atual = next((txt for ini, txt, fim in legs if ini <= t < fim), "")
            if atual != chave_leg:
                cache_leg = legenda_img(atual) if atual else None
                chave_leg = atual
            if cache_leg:
                li, hh = cache_leg
                quadro.paste(li, (0, H - 70 - hh), li)

            proc.stdin.write(quadro.tobytes())
            quadro_glob += 1
        t_glob += dur
        print(f"vídeo: cena {i + 1}/{len(cenas)} pronta ({t_glob / 60:.1f} min)")
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou")
    (pasta / "legendas.srt").write_text("\n".join(srt), encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)
    marca.write_text(assinatura + "\n")
    print(f"ok {destino} ({t_glob / 60:.1f} min)")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        gerar(arg)

"""Gera as artes diárias do Legiscópio a partir de posts/<data>/post.json.

Usa a paleta e o layout oficiais (os mesmos de artes/src/pls-setembro-2026.py
e artes/src/teste-voce-sabia-orientacao-bancada.py): fundo claro, verde
#05572F, logo no topo, kicker em mono à direita, cards brancos com barra verde.

Saídas, na mesma pasta do post.json:
  feed.png    1080x1350 (Instagram)
  tiktok.jpg  1080x1080 (TikTok; JPEG porque o TikTok não aceita PNG)

Campos do post.json:
  rotulo      kicker do topo (ex.: "Votação na Câmara")
  titulo      manchete (até ~80 caracteres)
  destaque    número ou fato curto em destaque (ex.: "346 a 46"), opcional
  detalhe     1 a 2 frases de contexto, opcional (vai num card branco)
  fonte       linha de fonte (ex.: "Fonte: Câmara dos Deputados · 03/09/2026")

O rodapé sempre traz "Apoie: apoia.se/legiscopio" e "legiscopio.com.br".
"""
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Paleta oficial do Legiscópio
FUNDO = "#F4F7F3"
VERDE = "#05572F"
TEXTO = "#10251A"
TEXTO2 = "#4A5D51"
OLIVA = "#5E7F22"
BRANCO = "#FFFFFF"

ROOT = Path(__file__).resolve().parents[1]
N = "/usr/share/fonts/opentype/noto/"
DJ = "/usr/share/fonts/truetype/dejavu/"


def achar(*cs):
    for c in cs:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(", ".join(cs))


F_BLACK = achar(N + "NotoSansCJK-Black.ttc", N + "NotoSansCJK-Bold.ttc", DJ + "DejaVuSans-Bold.ttf")
F_REG = achar(N + "NotoSansCJK-Regular.ttc", DJ + "DejaVuSans.ttf")
F_MONO = achar(DJ + "DejaVuSansMono.ttf")
F_MONOB = achar(DJ + "DejaVuSansMono-Bold.ttf", F_MONO)
BK = lambda s: ImageFont.truetype(F_BLACK, s, index=0)  # noqa: E731
RG = lambda s: ImageFont.truetype(F_REG, s, index=0)  # noqa: E731
MO = lambda s: ImageFont.truetype(F_MONO, s)  # noqa: E731
MB = lambda s: ImageFont.truetype(F_MONOB, s)  # noqa: E731

LOGO = next(
    (p for p in [ROOT / "artes" / "assets" / "logo-legiscopio.png", ROOT / "artes" / "logo-legiscopio.png"] if p.exists()),
    None,
)


def wrap(d, t, f, maxw):
    out, line = [], ""
    for w in t.split():
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


def espacado(d, x_dir, y, t, f, fill, esp):
    larg = sum(d.textlength(c, font=f) for c in t) + esp * (len(t) - 1)
    x = x_dir - larg
    for c in t:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + esp


def layout(post, W, H, k):
    """Desenha a arte com fator de escala k (1.0 = tamanho cheio). Devolve (img, cabe)."""
    ML, MR = 78, W - 78
    img = Image.new("RGB", (W, H), FUNDO)
    d = ImageDraw.Draw(img)
    s = lambda v: max(1, round(v * k))  # noqa: E731

    # cabeçalho: logo + kicker
    alt = 105 if H > W else 92
    if LOGO:
        lg = Image.open(LOGO).convert("RGBA")
        lg = lg.resize((round(lg.width * alt / lg.height), alt), Image.LANCZOS)
        img.paste(lg, (ML + 5, 60), lg)
    else:
        d.text((ML, 90), "Legiscópio", font=BK(44), fill=VERDE)
    if post.get("rotulo"):
        f = MO(26)
        txt = post["rotulo"].upper()
        while d.textlength(txt, font=f) + 5 * len(txt) > MR - ML - 260 and f.size > 18:
            f = MO(f.size - 2)
        espacado(d, MR, 60 + alt // 2 - 14, txt, f, OLIVA, 5)

    rodape_y = H - 120
    topo = 60 + alt + 40

    # monta os blocos (função de desenho + altura) e depois centraliza
    blocos = []

    def bloco_texto(linhas, f, cor, entre):
        a, _ = f.getmetrics()
        tops = [f.getbbox(l)[1] for l in linhas]
        top0 = min(tops)
        lh = round(f.size * entre)
        alt_b = lh * (len(linhas) - 1) + (a - top0) + round(f.size * 0.08)

        def desenhar(y0):
            yy = y0 - top0
            for l in linhas:
                d.text((ML - (4 if f.size > 120 else 0), yy), l, font=f, fill=cor)
                yy += lh
        return desenhar, alt_b

    ft = BK(s(76 if H > W else 64))
    blocos.append((*bloco_texto(wrap(d, post["titulo"], ft, MR - ML), ft, VERDE, 1.12), s(60)))

    if post.get("destaque"):
        fd = BK(s(170 if H > W else 132))
        while d.textlength(post["destaque"], font=fd) > MR - ML and fd.size > 60:
            fd = BK(fd.size - 6)
        blocos.append((*bloco_texto([post["destaque"]], fd, VERDE, 1.0), s(44)))

    if post.get("detalhe"):
        fr = RG(s(33 if H > W else 30))
        linhas = wrap(d, post["detalhe"], fr, MR - ML - 72)
        lh = round(fr.size * 1.38)
        pad = s(32)
        h = pad * 2 + len(linhas) * lh - round(fr.size * 0.3)

        def card(y0, linhas=linhas, fr=fr, lh=lh, pad=pad, h=h):
            d.rounded_rectangle([ML, y0, MR, y0 + h], radius=22, fill=BRANCO, outline=VERDE, width=2)
            d.rounded_rectangle([ML, y0, ML + 16, y0 + h], radius=8, fill=VERDE)
            d.rectangle([ML + 8, y0, ML + 16, y0 + h], fill=VERDE)
            yy = y0 + pad - round(fr.size * 0.22)
            for l in linhas:
                d.text((ML + 44, yy), l, font=fr, fill=TEXTO)
                yy += lh
        blocos.append((card, h, 0))

    total = sum(h + g for _, h, g in blocos) - blocos[-1][2]
    livre = rodape_y - topo
    cabe = total <= livre
    y = topo + max(0, (livre - total) * 2 // 5)
    for desenhar, h, g in blocos:
        desenhar(y)
        y += h + g

    # rodapé: fonte (até 2 linhas) à esquerda; apoio + URL à direita
    url = "legiscopio.com.br"
    apoio = "apoia.se/legiscopio"
    fu = MB(23)
    fa = MO(21)
    larg_dir = max(d.textlength(url, font=fu), d.textlength("Apoie: " + apoio, font=fa))
    if post.get("fonte"):
        ff = MO(21)
        maxw = MR - ML - larg_dir - 30
        fl = wrap(d, post["fonte"], ff, maxw)[:2]
        yy = H - 64 - 28 * (len(fl) - 1)
        for linha in fl:
            d.text((ML, yy), linha, font=ff, fill=TEXTO2)
            yy += 28
    x_ap = MR - d.textlength(apoio, font=fa)
    d.text((x_ap, H - 94), apoio, font=fa, fill=OLIVA)
    d.text((x_ap, H - 94), "Apoie: ", font=fa, fill=TEXTO2, anchor="ra")
    d.text((MR, H - 64), url, font=fu, fill=VERDE, anchor="ra")
    return img, cabe


def render(post, W, H):
    k = 1.0
    while True:
        img, cabe = layout(post, W, H, k)
        if cabe or k <= 0.6:
            return img
        k -= 0.05


def main(paths):
    for p in paths:
        p = Path(p)
        post = json.loads(p.read_text(encoding="utf-8"))
        render(post, 1080, 1350).save(p.parent / "feed.png", optimize=True)
        render(post, 1080, 1080).convert("RGB").save(p.parent / "tiktok.jpg", quality=92, optimize=True)
        print("ok", p.parent)


if __name__ == "__main__":
    main(sys.argv[1:])

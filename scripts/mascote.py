"""Lupa, o mascote do Legiscópio: uma lupa simpática desenhada em código.

sprite(boca, olhos, tamanho) devolve uma imagem RGBA.
  boca:  "fechada" | "meia" | "aberta" | "sorriso"
  olhos: "abertos" | "fechados" | "surpresos"
"""
from functools import lru_cache

from PIL import Image, ImageDraw

VERDE = (5, 87, 47)
VERDE_ESC = (3, 60, 32)
LIMA = (185, 216, 106)
LENTE = (232, 244, 236)
BRILHO = (255, 255, 255)
PELE = (16, 37, 26)
BOCA_IN = (120, 30, 40)
LINGUA = (226, 110, 120)

ESCALA = 4  # desenha grande e reduz (antisserrilhado)


@lru_cache(maxsize=64)
def sprite(boca="fechada", olhos="abertos", tamanho=420, aceno=0):
    S = ESCALA
    W = H = 500 * S
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = lambda v: int(v * S)  # noqa: E731

    # cabo
    d.line([(s(330), s(330)), (s(450), s(455))], fill=VERDE_ESC, width=s(62))
    d.line([(s(330), s(330)), (s(450), s(455))], fill=VERDE, width=s(46))
    d.ellipse([s(425), s(430), s(480), s(485)], fill=VERDE)
    d.line([(s(300), s(300)), (s(345), s(345))], fill=LIMA, width=s(30))

    # aro e lente
    cx, cy, r = 210, 210, 175
    d.ellipse([s(cx - r - 14), s(cy - r - 14), s(cx + r + 14), s(cy + r + 14)], fill=VERDE_ESC)
    d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=VERDE)
    rl = r - 26
    d.ellipse([s(cx - rl), s(cy - rl), s(cx + rl), s(cy + rl)], fill=LENTE)
    # brilho do vidro
    d.arc([s(cx - rl + 18), s(cy - rl + 18), s(cx + rl - 18), s(cy + rl - 18)], 200, 250, fill=BRILHO, width=s(14))

    # olhos
    ex, ey, er = 55, -25, 30
    for lado in (-1, 1):
        x = cx + lado * ex
        y = cy + ey
        if olhos == "fechados":
            d.arc([s(x - er), s(y - 10), s(x + er), s(y + 25)], 200, 340, fill=PELE, width=s(9))
            continue
        rr = er + (8 if olhos == "surpresos" else 0)
        d.ellipse([s(x - rr), s(y - rr - 4), s(x + rr), s(y + rr + 4)], fill=(255, 255, 255), outline=PELE, width=s(5))
        p = 14 if olhos != "surpresos" else 12
        d.ellipse([s(x - p + 4), s(y - p + 2), s(x + p + 4), s(y + p + 2)], fill=PELE)
        d.ellipse([s(x + 2), s(y - 6), s(x + 10), s(y + 2)], fill=(255, 255, 255))
        # sobrancelha
        d.line([(s(x - 26), s(y - rr - 22)), (s(x + 24), s(y - rr - 26 - (6 if olhos == "surpresos" else 0)))],
               fill=PELE, width=s(8))

    # bochechas
    for lado in (-1, 1):
        x = cx + lado * 100
        d.ellipse([s(x - 22), s(cy + 30), s(x + 22), s(cy + 52)], fill=(244, 190, 190))

    # boca
    my = cy + 62
    if boca == "fechada":
        d.arc([s(cx - 40), s(my - 30), s(cx + 40), s(my + 18)], 20, 160, fill=PELE, width=s(8))
    elif boca == "sorriso":
        d.chord([s(cx - 50), s(my - 34), s(cx + 50), s(my + 34)], 0, 180, fill=BOCA_IN, outline=PELE, width=s(6))
    else:
        h = 20 if boca == "meia" else 40
        d.ellipse([s(cx - 34), s(my - h // 2), s(cx + 34), s(my + h // 2 + 10)], fill=BOCA_IN, outline=PELE, width=s(6))
        if boca == "aberta":
            d.ellipse([s(cx - 18), s(my + 8), s(cx + 18), s(my + h // 2 + 6)], fill=LINGUA)

    return im.resize((tamanho, tamanho), Image.LANCZOS)


if __name__ == "__main__":
    tela = Image.new("RGB", (4 * 440, 460), (244, 247, 243))
    for i, (b, o, a) in enumerate([("fechada", "abertos", 0), ("meia", "abertos", 0),
                                   ("aberta", "surpresos", 40), ("sorriso", "fechados", 0)]):
        sp = sprite(b, o, 420, a)
        tela.paste(sp, (i * 440 + 10, 20), sp)
    tela.save("mascote_preview.png")

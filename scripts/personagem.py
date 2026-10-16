"""Lupa 2.0 — personagem de corpo inteiro do Legiscópio (cabeça de lupa).

pose(nome, boca, olhos, tamanho, t, olhar, espelho) -> RGBA
  nome:    neutro | apontando | pensando | comemorando | acenando | explicando | surpresa | joinha
  boca:    fechada | meia | aberta | sorriso | o
  olhos:   abertos | fechados | surpresos | desconfiados
  t:       tempo (s) para pequenas animações (aceno, respiração)
  olhar:   -1..1 (para onde as pupilas olham na horizontal, no resultado final)
  espelho: True vira o personagem para a esquerda (para apontar para conteúdo à esquerda)
"""
import math
import os
from functools import lru_cache

from PIL import Image, ImageDraw

VERDE = (5, 87, 47)
VERDE_ESC = (3, 60, 32)
VERDE_CLARO = (20, 120, 68)
LIMA = (185, 216, 106)
LENTE = (232, 244, 236)
BRANCO = (255, 255, 255)
TINTA = (16, 37, 26)
BOCA_IN = (120, 30, 40)
LINGUA = (226, 110, 120)
BOCHECHA = (244, 190, 190)
SAPATO = (24, 30, 28)
CALCA = (30, 52, 44)

S = 2            # super-amostragem
W0, H0 = 800, 900  # unidades lógicas (largura extra para os braços)

# ângulos (graus) do braço: (ombro, cotovelo), 0 = para baixo, positivo = para fora
POSES = {
    "neutro":      {"esq": (12, 8),    "dir": (12, 8),    "mao_d": "aberta", "mao_e": "aberta", "inclina": 0},
    "apontando":   {"esq": (14, 10),   "dir": (100, 105), "mao_d": "dedo",   "mao_e": "aberta", "inclina": -6},
    "pensando":    {"esq": "cintura",  "dir": "queixo",   "mao_d": "punho",  "mao_e": "punho",  "inclina": 8},
    "comemorando": {"esq": (150, 165), "dir": (150, 165), "mao_d": "punho",  "mao_e": "punho",  "inclina": 0},
    "acenando":    {"esq": (12, 8),    "dir": (135, 175), "mao_d": "aberta", "mao_e": "aberta", "inclina": -4},
    "explicando":  {"esq": (45, 95),   "dir": (45, 95),   "mao_d": "aberta", "mao_e": "aberta", "inclina": 0},
    "surpresa":    {"esq": (35, 150),  "dir": (35, 150),  "mao_d": "aberta", "mao_e": "aberta", "inclina": 0},
    "joinha":      {"esq": (12, 8),    "dir": (40, 150),  "mao_d": "joinha", "mao_e": "aberta", "inclina": -5},
}

LOGO = next((c for c in [os.environ.get("LEGIS_LOGO", ""),
                         os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artes", "logo-legiscopio.png")]
             if c and os.path.exists(c)), None)


def s(v):
    return int(round(v * S))


def _cabeca(boca, olhos, olhar):
    """Cabeça-lupa desenhada num quadrado 400x400 (unidades)."""
    T = 400
    im = Image.new("RGBA", (s(T), s(T)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = 200
    r = 175
    d.ellipse([s(cx - r - 14), s(cy - r - 14), s(cx + r + 14), s(cy + r + 14)], fill=VERDE_ESC)
    d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=VERDE)
    # parafusos do aro
    for ang in (35, 145, 215, 325):
        a = math.radians(ang)
        px, py = cx + (r - 12) * math.cos(a), cy + (r - 12) * math.sin(a)
        d.ellipse([s(px - 6), s(py - 6), s(px + 6), s(py + 6)], fill=LIMA)
    rl = r - 28
    d.ellipse([s(cx - rl), s(cy - rl), s(cx + rl), s(cy + rl)], fill=LENTE)
    d.arc([s(cx - rl + 18), s(cy - rl + 18), s(cx + rl - 18), s(cy + rl - 18)], 200, 250, fill=BRANCO, width=s(14))
    d.arc([s(cx - rl + 18), s(cy - rl + 18), s(cx + rl - 18), s(cy + rl - 18)], 258, 268, fill=BRANCO, width=s(14))

    # olhos (maiores e mais expressivos)
    ex, ey, er = 58, -28, 36
    for lado in (-1, 1):
        x, y = cx + lado * ex, cy + ey
        if olhos == "fechados":
            d.arc([s(x - er), s(y - 12), s(x + er), s(y + 30)], 200, 340, fill=TINTA, width=s(10))
            d.line([(s(x - 28), s(y - 40)), (s(x + 26), s(y - 46))], fill=TINTA, width=s(9))
            continue
        rr = er + (8 if olhos == "surpresos" else 0)
        topo = y - rr - 4
        d.ellipse([s(x - rr), s(topo), s(x + rr), s(y + rr + 4)], fill=BRANCO, outline=TINTA, width=s(5))
        p = 16 if olhos != "surpresos" else 13
        px = x + 10 * olhar
        d.ellipse([s(px - p), s(y - p + 4), s(px + p), s(y + p + 4)], fill=TINTA)
        d.ellipse([s(px + 2), s(y - 6), s(px + 11), s(y + 3)], fill=BRANCO)
        if olhos == "desconfiados":  # pálpebra
            d.chord([s(x - rr), s(topo), s(x + rr), s(y + rr + 4)], 180, 360, fill=VERDE_CLARO, outline=TINTA, width=s(5))
        # sobrancelhas
        if olhos == "surpresos":
            d.arc([s(x - 30), s(topo - 30), s(x + 30), s(topo + 6)], 200, 340, fill=TINTA, width=s(9))
        elif olhos == "desconfiados":
            d.line([(s(x - 30 * lado), s(topo - 4)), (s(x + 30 * lado), s(topo - 18))], fill=TINTA, width=s(9))
        else:
            d.line([(s(x - 28), s(topo - 12)), (s(x + 26), s(topo - 18))], fill=TINTA, width=s(9))

    for lado in (-1, 1):
        x = cx + lado * 102
        d.ellipse([s(x - 24), s(cy + 28), s(x + 24), s(cy + 52)], fill=BOCHECHA)

    my = cy + 66
    if boca == "fechada":
        d.arc([s(cx - 42), s(my - 32), s(cx + 42), s(my + 18)], 20, 160, fill=TINTA, width=s(9))
    elif boca == "sorriso":
        d.chord([s(cx - 54), s(my - 36), s(cx + 54), s(my + 38)], 0, 180, fill=BOCA_IN, outline=TINTA, width=s(6))
        d.chord([s(cx - 40), s(my + 14), s(cx + 40), s(my + 38)], 0, 180, fill=LINGUA)
        d.rectangle([s(cx - 40), s(my), s(cx + 40), s(my + 8)], fill=BRANCO)
    elif boca == "o":
        d.ellipse([s(cx - 20), s(my - 6), s(cx + 20), s(my + 34)], fill=BOCA_IN, outline=TINTA, width=s(6))
    else:
        h = 22 if boca == "meia" else 44
        d.ellipse([s(cx - 36), s(my - h // 2), s(cx + 36), s(my + h // 2 + 10)], fill=BOCA_IN, outline=TINTA, width=s(6))
        if boca == "aberta":
            d.ellipse([s(cx - 20), s(my + 8), s(cx + 20), s(my + h // 2 + 6)], fill=LINGUA)
    return im


def _mao(d, x, y, ang, tipo, lado):
    """Mão de luva branca no ponto (x, y); ang = direção do antebraço (rad)."""
    r = 26
    d.ellipse([s(x - r), s(y - r), s(x + r), s(y + r)], fill=BRANCO, outline=TINTA, width=s(5))
    dx, dy = math.sin(ang) * lado, math.cos(ang)
    if tipo == "dedo":
        fx, fy = x + dx * 52, y + dy * 52
        d.line([(s(x), s(y)), (s(fx), s(fy))], fill=TINTA, width=s(30))
        d.ellipse([s(fx - 15), s(fy - 15), s(fx + 15), s(fy + 15)], fill=TINTA)
        d.line([(s(x), s(y)), (s(fx), s(fy))], fill=BRANCO, width=s(20))
        d.ellipse([s(fx - 10), s(fy - 10), s(fx + 10), s(fy + 10)], fill=BRANCO)
        d.ellipse([s(x - r + 5), s(y - r + 5), s(x + r - 5), s(y + r - 5)], fill=BRANCO)
    elif tipo == "joinha":
        d.rounded_rectangle([s(x - 16), s(y - 62), s(x + 8), s(y - 4)], radius=s(12), fill=BRANCO, outline=TINTA, width=s(5))
        d.ellipse([s(x - r + 5), s(y - r + 5), s(x + r - 5), s(y + r - 5)], fill=BRANCO)
        for k in range(3):
            d.arc([s(x - 4), s(y - 14 + k * 11), s(x + 22), s(y - 2 + k * 11)], 270, 90, fill=TINTA, width=s(3))
    elif tipo == "aberta":
        for k in (-1, 0, 1):
            a2 = ang + k * 0.5
            fx, fy = x + math.sin(a2) * lado * 30, y + math.cos(a2) * 30
            d.ellipse([s(fx - 14), s(fy - 14), s(fx + 14), s(fy + 14)], fill=BRANCO, outline=TINTA, width=s(5))
        d.ellipse([s(x - r + 5), s(y - r + 5), s(x + r - 5), s(y + r - 5)], fill=BRANCO)


L1, L2 = 92, 86


def _ik(ombro, alvo, lado):
    """Ângulos (graus, convenção das POSES) para a mão chegar ao alvo."""
    ox, oy = ombro
    tx, ty = alvo
    dx, dy = (tx - ox) * lado, ty - oy
    dist = min(math.hypot(dx, dy), L1 + L2 - 1)
    base = math.atan2(dx, dy)
    cos_a = (L1 ** 2 + dist ** 2 - L2 ** 2) / (2 * L1 * dist)
    a = math.acos(max(-1, min(1, cos_a)))
    t1 = base + a  # cotovelo para fora
    ex, ey = math.sin(t1) * L1, math.cos(t1) * L1
    t2 = math.atan2(dx - ex, dy - ey)
    return math.degrees(t1), math.degrees(t2)


def _braco(d, ombro, a1, a2, lado, mao):
    t1, t2 = math.radians(a1), math.radians(a2)
    ox, oy = ombro
    cx_, cy_ = ox + math.sin(t1) * L1 * lado, oy + math.cos(t1) * L1
    hx, hy = cx_ + math.sin(t2) * L2 * lado, cy_ + math.cos(t2) * L2
    pts = [(s(ox), s(oy)), (s(cx_), s(cy_)), (s(hx), s(hy))]
    d.line(pts, fill=VERDE_ESC, width=s(40), joint="curve")
    d.line(pts, fill=VERDE, width=s(28), joint="curve")
    for px, py in [(ox, oy), (cx_, cy_)]:
        d.ellipse([s(px - 14), s(py - 14), s(px + 14), s(py + 14)], fill=VERDE)
    _mao(d, hx, hy, t2, mao, lado)


@lru_cache(maxsize=8)
def _cracha(w, h):
    """Logo do Legiscópio (ícone + nome) encaixada no crachá."""
    if not LOGO:
        return None
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.crop(lg.getbbox())
    k = min(w / lg.width, h / lg.height)
    lg = lg.resize((max(1, int(lg.width * k)), max(1, int(lg.height * k))), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(lg, ((w - lg.width) // 2, (h - lg.height) // 2))
    return out


@lru_cache(maxsize=300)
def _pose_cache(nome, boca, olhos, tamanho, fase, olhar_q, espelho):
    t = fase / 12.0
    im = _pose(nome, boca, olhos, tamanho, t, (-olhar_q if espelho else olhar_q) / 4.0, espelho)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if espelho else im


def pose(nome="neutro", boca="fechada", olhos="abertos", tamanho=600, t=0.0, olhar=0.0, espelho=False):
    if nome in ("acenando", "comemorando"):
        fase = int(round(t * 12)) % 24  # gesto animado: ciclo de 2 s, 12 passos/s
    else:
        fase = (int(round(t * 4)) % 8) * 3  # só respiração: 4 passos/s (menos variações = render rápido)
    return _pose_cache(nome, boca, olhos, tamanho, fase, int(round(olhar * 4)), bool(espelho))


def _pose(nome, boca, olhos, tamanho, t, olhar, espelho=False):
    P = dict(POSES[nome])
    resp = math.sin(t * math.pi) * 4  # respiração
    im = Image.new("RGBA", (s(W0), s(H0)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W0 // 2

    d.ellipse([s(cx - 120), s(826), s(cx + 120), s(858)], fill=(0, 0, 0, 40))
    # pernas e sapatos
    for lado in (-1, 1):
        x0 = cx + lado * 36
        d.line([(s(x0), s(690)), (s(x0 + lado * 6), s(820))], fill=CALCA, width=s(40))
        d.ellipse([s(x0 + lado * 6 - 34 + lado * 14), s(800), s(x0 + lado * 6 + 34 + lado * 14), s(842)], fill=SAPATO)

    # corpo (paletó verde com camisa e gravata lima)
    top = 470 - resp
    d.rounded_rectangle([s(cx - 92), s(top), s(cx + 92), s(712)], radius=s(70), fill=VERDE_ESC)
    d.rounded_rectangle([s(cx - 84), s(top + 6), s(cx + 84), s(704)], radius=s(64), fill=VERDE)
    d.polygon([(s(cx - 44), s(top + 6)), (s(cx + 44), s(top + 6)), (s(cx), s(top + 92))], fill=BRANCO)
    d.polygon([(s(cx - 12), s(top + 14)), (s(cx + 12), s(top + 14)), (s(cx + 18), s(top + 112)),
               (s(cx), s(top + 132)), (s(cx - 18), s(top + 112))], fill=LIMA)
    d.polygon([(s(cx - 14), s(top + 6)), (s(cx + 14), s(top + 6)), (s(cx), s(top + 24))], fill=LIMA)
    # crachá com a logo do Legiscópio (preso por um clipe)
    bx0, by0, bx1, by1 = cx + 22, top + 64, cx + 82, top + 128
    d.rounded_rectangle([s(bx0 + 22), s(by0 - 10), s(bx0 + 38), s(by0 + 4)], radius=s(3), fill=(190, 198, 192))
    d.rounded_rectangle([s(bx0), s(by0), s(bx1), s(by1)], radius=s(8), fill=BRANCO, outline=VERDE_ESC, width=s(2))
    cr = _cracha(s(bx1 - bx0 - 8), s(by1 - by0 - 8))
    if cr is not None:
        if espelho:
            cr = cr.transpose(Image.FLIP_LEFT_RIGHT)
        im.alpha_composite(cr, (s(bx0 + 4), s(by0 + 4)))

    # pescoço = cabo da lupa
    d.rounded_rectangle([s(cx - 22), s(top - 56), s(cx + 22), s(top + 14)], radius=s(10), fill=VERDE_ESC)
    d.rectangle([s(cx - 22), s(top - 34), s(cx + 22), s(top - 20)], fill=LIMA)

    # braços
    a_e, a_d = P["esq"], P["dir"]
    if nome == "acenando":
        a_d = (a_d[0], a_d[1] + 18 * math.sin(t * 2 * math.pi * 2))
    if nome == "comemorando":
        k = (math.sin(t * 2 * math.pi * 2) + 1) / 2
        a_e = (a_e[0] - 15 * k, a_e[1] - 10 * k)
        a_d = (a_d[0] - 15 * (1 - k), a_d[1] - 10 * (1 - k))
    om_e, om_d = (cx - 88, top + 40), (cx + 88, top + 40)
    alvos = {"queixo": (cx + 40, top - 22), "cintura": (cx - 96, top + 165)}
    if isinstance(a_e, str):
        a_e = _ik(om_e, alvos[a_e], -1)
    if isinstance(a_d, str):
        a_d = _ik(om_d, alvos[a_d], 1)
    _braco(d, om_e, *a_e, -1, P["mao_e"])
    if nome != "pensando":
        _braco(d, om_d, *a_d, 1, P["mao_d"])

    # cabeça (pode inclinar)
    cab = _cabeca(boca, olhos, olhar)
    inc = P["inclina"] + (2 * math.sin(t * math.pi) if nome in ("neutro", "explicando") else 0)
    if nome == "pensando":
        inc += 3 * math.sin(t * math.pi)
    cab = cab.rotate(inc, resample=Image.BICUBIC)
    pulo = -10 * abs(math.sin(t * 2 * math.pi * 2)) if nome == "comemorando" else 0
    im.alpha_composite(cab, (s(cx - 200), s(top - 400 + 20 + pulo)))

    # no "pensando" o braço direito passa por cima (mão no queixo)
    if nome == "pensando":
        im2 = Image.new("RGBA", im.size, (0, 0, 0, 0))
        _braco(ImageDraw.Draw(im2), om_d, *a_d, 1, P["mao_d"])
        im.alpha_composite(im2)

    return im.resize((int(tamanho * W0 / H0), tamanho), Image.LANCZOS)

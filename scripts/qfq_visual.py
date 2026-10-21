"""Identidade visual da série "Quem Faz o Quê?" (Legiscópio).

Desenha os quadros-chave (storyboard) e, na produção, os quadros animados.
Cores fixas por nível de governo: Município laranja, Estado azul, União roxo.
Fora da rotina diária: usa video_longo e personagem só como bibliotecas.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import personagem  # noqa: E402
import video_longo as vl  # noqa: E402

W, H = 1920, 1080
MUN = (224, 123, 57)
EST = (47, 109, 181)
UNI = (107, 79, 168)
VERDE, LIMA, FUNDO = vl.VERDE, vl.LIMA, vl.FUNDO
TINTA, CINZA = vl.TEXTO, (150, 160, 154)
CINZA_CL = (226, 230, 227)
BRANCO = (255, 255, 255)
NIVEL = {"municipio": MUN, "estado": EST, "uniao": UNI}
NOME_NIVEL = {"municipio": "MUNICÍPIO", "estado": "ESTADO", "uniao": "UNIÃO"}
BK, BD, RG, MO = vl.BK, vl.BD, vl.RG, vl.MO


def claro(c, k=0.82):
    return tuple(int(v + (255 - v) * k) for v in c)


# ------------------------------------------------------------------ ícones planos (desenhados à mão)

def icone(d, nome, cx, cy, s, cor, fundo=None):
    """Ícone plano centrado em (cx, cy), tamanho s (lado do quadrado)."""
    u = s / 100.0
    f = fundo or BRANCO

    def R(x0, y0, x1, y1, **k):
        d.rectangle([cx + x0 * u, cy + y0 * u, cx + x1 * u, cy + y1 * u], **k)

    def RR(x0, y0, x1, y1, r, **k):
        d.rounded_rectangle([cx + x0 * u, cy + y0 * u, cx + x1 * u, cy + y1 * u], radius=r * u, **k)

    def E(x0, y0, x1, y1, **k):
        d.ellipse([cx + x0 * u, cy + y0 * u, cx + x1 * u, cy + y1 * u], **k)

    def P(pts, **k):
        d.polygon([(cx + x * u, cy + y * u) for x, y in pts], **k)

    def L(pts, w, **k):
        d.line([(cx + x * u, cy + y * u) for x, y in pts], width=max(1, int(w * u)), **k)

    if nome == "poste":
        R(-4, -40, 4, 46, fill=cor)
        L([(0, -40), (24, -40), (30, -32)], 7, fill=cor)
        P([(18, -32), (42, -32), (36, -22), (24, -22)], fill=cor)
        R(-14, 40, 14, 48, fill=cor)
    elif nome == "poste_aceso":
        icone(d, "poste", cx, cy, s, cor)
        P([(24, -22), (36, -22), (54, 20), (6, 20)], fill=claro(LIMA, 0.4))
    elif nome == "prefeitura":
        P([(-46, -18), (0, -44), (46, -18)], fill=cor)
        for x in (-34, -14, 6, 26):
            R(x, -14, x + 8, 30, fill=cor)
        R(-48, 30, 48, 40, fill=cor)
        R(-48, -18, 48, -12, fill=cor)
    elif nome == "camara":
        d.pieslice([cx - 30 * u, cy - 44 * u, cx + 30 * u, cy + 4 * u], 180, 360, fill=cor)
        R(-46, -18, 46, -12, fill=cor)
        for x in (-38, -20, -2, 16, 34):
            R(x, -12, x + 6, 28, fill=cor)
        R(-48, 28, 48, 38, fill=cor)
    elif nome == "escola":
        P([(-44, -10), (0, -40), (44, -10)], fill=cor)
        R(-38, -10, 38, 38, fill=cor)
        R(-10, 12, 10, 38, fill=f)
        R(-30, -2, -16, 10, fill=f)
        R(16, -2, 30, 10, fill=f)
        R(-1, -48, 1, -34, fill=cor)
        P([(1, -48), (16, -44), (1, -40)], fill=cor)
    elif nome == "ubs":
        RR(-42, -34, 42, 38, 8, fill=cor)
        R(-8, -22, 8, 18, fill=f)
        R(-20, -10, 20, 6, fill=f)
    elif nome == "hospital":
        R(-44, -30, 44, 40, fill=cor)
        R(-14, -48, 14, -30, fill=cor)
        R(-5, -44, 5, -34, fill=f)
        R(-9, -40, 9, -38, fill=f)
        for x in (-34, -14, 6, 26):
            R(x, -16, x + 8, -6, fill=f)
            R(x, 4, x + 8, 14, fill=f)
        R(-8, 22, 8, 40, fill=f)
    elif nome == "viatura":
        RR(-46, -6, 46, 22, 6, fill=cor)
        P([(-26, -6), (-16, -26), (16, -26), (26, -6)], fill=cor)
        R(-6, -34, 6, -26, fill=cor)
        E(-34, 12, -14, 32, fill=TINTA)
        E(14, 12, 34, 32, fill=TINTA)
        R(-12, -20, 12, -8, fill=f)
    elif nome == "onibus":
        RR(-44, -34, 44, 26, 8, fill=cor)
        R(-36, -24, 36, 0, fill=f)
        E(-32, 18, -14, 36, fill=TINTA)
        E(14, 18, 32, 36, fill=TINTA)
        R(-4, -24, 4, 0, fill=cor)
    elif nome == "rodovia":
        P([(-14, -46), (14, -46), (46, 46), (-46, 46)], fill=cor)
        for y in (-34, -10, 16):
            R(-2, y, 2, y + 12, fill=f)
    elif nome == "lixo":
        RR(-46, -20, 18, 22, 4, fill=cor)
        RR(18, -8, 46, 22, 4, fill=cor)
        R(26, -2, 40, 8, fill=f)
        E(-36, 14, -18, 32, fill=TINTA)
        E(20, 14, 38, 32, fill=TINTA)
    elif nome == "cofre":
        RR(-40, -32, 40, 36, 8, fill=cor)
        E(-16, -14, 16, 18, fill=f)
        E(-8, -6, 8, 10, fill=cor)
        R(-30, 36, -18, 44, fill=cor)
        R(18, 36, 30, 44, fill=cor)
    elif nome == "moeda":
        E(-30, -30, 30, 30, fill=cor)
        E(-22, -22, 22, 22, outline=f, width=max(2, int(4 * u)))
        d.text((cx, cy), "R$", font=BK(max(10, int(26 * u))), fill=f, anchor="mm")
    elif nome == "balanca":
        R(-3, -40, 3, 36, fill=cor)
        R(-40, -34, 40, -28, fill=cor)
        R(-22, 36, 22, 44, fill=cor)
        for sx in (-1, 1):
            L([(sx * 34, -30), (sx * 46, 2)], 3, fill=cor)
            L([(sx * 34, -30), (sx * 22, 2)], 3, fill=cor)
            d.pieslice([cx + (sx * 34 - 14) * u, cy - 10 * u, cx + (sx * 34 + 14) * u, cy + 16 * u], 0, 180, fill=cor)
    elif nome == "documento":
        P([(-30, -42), (14, -42), (32, -24), (32, 42), (-30, 42)], fill=cor)
        for y in (-16, 0, 16):
            R(-20, y, 22, y + 5, fill=f)
    elif nome == "carimbo":
        RR(-12, -44, 12, -12, 6, fill=cor)
        RR(-34, -12, 34, 8, 4, fill=cor)
        R(-40, 22, 40, 30, fill=cor)
    elif nome == "celular":
        RR(-24, -44, 24, 44, 8, fill=cor)
        R(-18, -34, 18, 30, fill=f)
        E(-4, 34, 4, 42, fill=f)
    elif nome == "berco":
        R(-42, -10, 42, -4, fill=cor)
        R(-42, 24, 42, 30, fill=cor)
        R(-44, -24, -38, 40, fill=cor)
        R(38, -24, 44, 40, fill=cor)
        for x in (-26, -12, 2, 16, 30):
            R(x - 2, -4, x + 2, 24, fill=cor)
    elif nome == "torre":
        P([(0, -46), (24, 44), (14, 44), (0, -6), (-14, 44), (-24, 44)], fill=cor)
        R(-30, -24, 30, -18, fill=cor)
        R(-22, 6, 22, 12, fill=cor)
    elif nome == "urna":
        RR(-40, -14, 40, 40, 6, fill=cor)
        R(-20, -10, 20, -4, fill=f)
        P([(-12, -44), (16, -40), (10, -10), (-16, -14)], fill=claro(cor, 0.5))
    elif nome == "casa":
        P([(-44, -6), (0, -42), (44, -6)], fill=cor)
        R(-34, -6, 34, 40, fill=cor)
        R(-8, 14, 8, 40, fill=f)
    elif nome == "pessoa":
        E(-12, -44, 12, -20, fill=cor)
        d.pieslice([cx - 30 * u, cy - 16 * u, cx + 30 * u, cy + 44 * u], 180, 360, fill=cor)
        R(-30, 14, 30, 22, fill=cor)
    elif nome == "lupa_icone":
        E(-34, -38, 14, 10, outline=cor, width=max(3, int(9 * u)))
        L([(8, 4), (36, 34)], 12, fill=cor)
    elif nome == "check":
        L([(-30, 0), (-8, 24), (32, -24)], 12, fill=cor)
    elif nome == "x":
        L([(-26, -26), (26, 26)], 12, fill=cor)
        L([(-26, 26), (26, -26)], 12, fill=cor)
    elif nome == "megafone":
        P([(-36, -12), (10, -36), (10, 36), (-36, 12)], fill=cor)
        R(-44, -12, -36, 12, fill=cor)
        R(-30, 12, -18, 34, fill=cor)
    elif nome == "lampada":
        E(-26, -44, 26, 8, fill=cor)
        R(-14, 8, 14, 26, fill=cor)
        R(-10, 30, 10, 36, fill=cor)
    else:
        E(-30, -30, 30, 30, fill=cor)


def selo_icone(img, nome, cx, cy, r, cor, contorno=False):
    """Círculo com ícone dentro (cheio = cor; contorno = branco com borda)."""
    d = ImageDraw.Draw(img)
    if contorno:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BRANCO, outline=cor, width=max(3, r // 14))
        icone(d, nome, cx, cy, r * 1.15, cor)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cor)
        icone(d, nome, cx, cy, r * 1.15, BRANCO, fundo=cor)


# ------------------------------------------------------------------ moldura da série

def base(ep_num, ep_nome, cor_ep=MUN, fundo=FUNDO):
    img = Image.new("RGB", (W, H), fundo)
    d = ImageDraw.Draw(img)
    # faixa tricolor no topo
    for k, c in enumerate((UNI, EST, MUN)):
        d.rectangle([k * W / 3, 0, (k + 1) * W / 3, 10], fill=c)
    d.text((70, 58), "QUEM FAZ O QUÊ?", font=BK(30), fill=VERDE, anchor="ls")
    w = d.textlength(f"EP. {ep_num} · {ep_nome.upper()}", font=MO(22)) + 36
    d.rounded_rectangle([70, 74, 70 + w, 112], radius=10, fill=cor_ep)
    d.text((88, 93), f"EP. {ep_num} · {ep_nome.upper()}", font=MO(22), fill=BRANCO, anchor="lm")
    lg = vl.logo(56)
    if lg:
        img.paste(lg, (W - 70 - lg.width, 34), lg)
    return img


def titulo(d, txt, y=170, x=70, tam=64, cor=TINTA, maxw=1780):
    f = BK(tam)
    for l in vl.wrap(d, txt, f, maxw):
        d.text((x, y), l, font=f, fill=cor)
        y += int(tam * 1.18)
    return y


def legenda(img, txt):
    """Legenda queimada (estilo da série) na base."""
    if not txt:
        return
    d = ImageDraw.Draw(img)
    f = BD(38)
    linhas = vl.wrap(d, txt, f, 1300)[:2]
    hh = len(linhas) * 50 + 30
    larg = max(d.textlength(l, font=f) for l in linhas) + 70
    x0, y0 = (W - larg) / 2, H - 60 - hh
    d.rounded_rectangle([x0, y0, x0 + larg, y0 + hh], radius=18, fill=(16, 37, 26))
    for k, l in enumerate(linhas):
        d.text((W / 2, y0 + 15 + k * 50), l, font=f, fill=BRANCO, anchor="mt")


def lupa(img, pose="explicando", tam=430, x=None, y=None, espelho=True, boca="fechada", olhos="abertos"):
    sp = personagem.pose(pose, boca, olhos, tam, 0.3, -1 if espelho else 1, espelho=espelho)
    img.paste(sp, (W - sp.width - 20 if x is None else x, H - sp.height - 30 if y is None else y), sp)


def chip(d, x, y, txt, cor, fonte=None, cheio=True, pad=22, alt=56):
    f = fonte or BD(30)
    w = d.textlength(txt, font=f) + 2 * pad
    if cheio:
        d.rounded_rectangle([x, y, x + w, y + alt], radius=alt // 2, fill=cor)
        d.text((x + w / 2, y + alt / 2), txt, font=f, fill=BRANCO, anchor="mm")
    else:
        d.rounded_rectangle([x, y, x + w, y + alt], radius=alt // 2, fill=BRANCO, outline=cor, width=4)
        d.text((x + w / 2, y + alt / 2), txt, font=f, fill=cor, anchor="mm")
    return w


def cartao(d, x0, y0, x1, y1, cor=CINZA, fill=BRANCO, w=4, r=22):
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=cor, width=w)


def seta(d, p0, p1, cor=CINZA, w=6, ponta=20, tracejada=False):
    x0, y0 = p0
    x1, y1 = p1
    ang = math.atan2(y1 - y0, x1 - x0)
    fim = (x1 - ponta * 0.8 * math.cos(ang), y1 - ponta * 0.8 * math.sin(ang))
    if tracejada:
        n = int(math.hypot(fim[0] - x0, fim[1] - y0) // 22)
        for k in range(n):
            if k % 2 == 0:
                a = (x0 + (fim[0] - x0) * k / n, y0 + (fim[1] - y0) * k / n)
                b = (x0 + (fim[0] - x0) * (k + 1) / n, y0 + (fim[1] - y0) * (k + 1) / n)
                d.line([a, b], fill=cor, width=w)
    else:
        d.line([p0, fim], fill=cor, width=w)
    d.polygon([(x1, y1),
               (x1 - ponta * math.cos(ang - 0.45), y1 - ponta * math.sin(ang - 0.45)),
               (x1 - ponta * math.cos(ang + 0.45), y1 - ponta * math.sin(ang + 0.45))], fill=cor)


# ------------------------------------------------------------------ quadro "De quem é a responsabilidade?"

def quadro_resp(img, x0, y0, x1, y1, estados, problema=None, icone_prob=None, titulo_q=True):
    """estados: dict nivel -> 'cheio' | 'contorno' | 'pontilhado' | 'apagado'."""
    d = ImageDraw.Draw(img)
    if titulo_q:
        d.text((x0, y0), "DE QUEM É A RESPONSABILIDADE?", font=BK(40), fill=VERDE)
        y0 += 70
    if problema:
        cartao(d, x0, y0, x1, y0 + 110, cor=TINTA, w=3)
        if icone_prob:
            icone(d, icone_prob, x0 + 70, y0 + 55, 70, TINTA)
        d.text((x0 + 130, y0 + 55), problema, font=BD(38), fill=TINTA, anchor="lm")
        y0 += 140
    alt = (y1 - y0 - 40) / 3
    for k, niv in enumerate(("uniao", "estado", "municipio")):
        c = NIVEL[niv]
        st = estados.get(niv, "apagado")
        ya, yb = y0 + k * (alt + 20), y0 + k * (alt + 20) + alt
        if st == "cheio":
            d.rounded_rectangle([x0, ya, x1, yb], radius=20, fill=c)
            tc = BRANCO
        elif st == "contorno":
            d.rounded_rectangle([x0, ya, x1, yb], radius=20, fill=BRANCO, outline=c, width=6)
            tc = c
        elif st == "pontilhado":
            d.rounded_rectangle([x0, ya, x1, yb], radius=20, fill=BRANCO)
            for xx in range(int(x0) + 10, int(x1) - 10, 26):
                d.line([(xx, ya + 3), (xx + 13, ya + 3)], fill=c, width=6)
                d.line([(xx, yb - 3), (xx + 13, yb - 3)], fill=c, width=6)
            tc = c
        else:
            d.rounded_rectangle([x0, ya, x1, yb], radius=20, fill=CINZA_CL)
            tc = CINZA
        d.text((x0 + 36, (ya + yb) / 2), NOME_NIVEL[niv], font=BK(40), fill=tc, anchor="lm")
        papel = {"cheio": "executa", "contorno": "financia / regula", "pontilhado": "fiscaliza"}.get(st, "")
        if papel:
            d.text((x1 - 36, (ya + yb) / 2), papel, font=BD(30), fill=tc, anchor="rm")


def legenda_quadro(d, x, y):
    for k, (txt, st) in enumerate((("cheio = executa", "cheio"), ("contorno = financia / regula", "contorno"),
                                   ("pontilhado = fiscaliza", "pontilhado"))):
        yy = y + k * 46
        if st == "cheio":
            d.rounded_rectangle([x, yy, x + 44, yy + 30], radius=8, fill=TINTA)
        elif st == "contorno":
            d.rounded_rectangle([x, yy, x + 44, yy + 30], radius=8, outline=TINTA, width=4)
        else:
            for xx in range(x, x + 44, 14):
                d.line([(xx, yy + 15), (xx + 7, yy + 15)], fill=TINTA, width=5)
        d.text((x + 60, yy + 15), txt, font=RG(28), fill=TINTA, anchor="lm")


# ------------------------------------------------------------------ mapa estilizado do Brasil (provisório)
# Contorno aproximado, só para storyboard. Na produção: malha oficial do IBGE simplificada.
BRASIL = [(0.30, 0.02), (0.42, 0.06), (0.52, 0.03), (0.62, 0.10), (0.74, 0.14), (0.86, 0.22), (0.98, 0.30),
          (0.97, 0.40), (0.90, 0.50), (0.86, 0.62), (0.80, 0.72), (0.70, 0.78), (0.62, 0.88), (0.54, 0.98),
          (0.48, 0.92), (0.44, 0.84), (0.38, 0.74), (0.40, 0.64), (0.30, 0.56), (0.20, 0.52), (0.10, 0.46),
          (0.02, 0.36), (0.06, 0.24), (0.16, 0.18), (0.22, 0.08)]


def mapa_brasil(d, x0, y0, w, h, cor, contorno=None, k=4):
    pts = [(x0 + px * w, y0 + py * h) for px, py in BRASIL]
    d.polygon(pts, fill=cor)
    if contorno:
        d.line(pts + [pts[0]], fill=contorno, width=k)

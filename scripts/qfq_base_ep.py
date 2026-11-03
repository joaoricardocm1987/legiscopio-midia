"""Layouts comuns dos episódios 3 a 5 da série "Quem Faz o Quê?".

Não é importado: cada qfq_epN.py executa este arquivo no próprio namespace (o qfq_render troca o ImageDraw
do módulo do episódio para separar as camadas), define EPN, EPNOME e COR e lista as cenas.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qfq_visual as q  # noqa: E402

M, E, U, V = q.MUN, q.EST, q.UNI, q.VERDE


def novo():
    img = q.base(EPN, EPNOME, COR)
    return img, ImageDraw.Draw(img)


def _linhas(d, txt, f, w):
    return q.vl.wrap(d, txt, f, w)


def g_gancho(frase, balao, icone, cor, pose="pensando"):
    img = Image.new("RGB", (q.W, q.H), (22, 34, 52))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 760, q.W, q.H], fill=(40, 46, 56))
    for x in (60, 1500):
        d.rectangle([x, 380, x + 360, 760], fill=(52, 62, 80))
        for wy in (430, 540, 650):
            for wx in (x + 40, x + 200):
                d.rectangle([wx, wy, wx + 90, wy + 60], fill=(250, 214, 120))
    q.selo_icone(img, icone, 960, 600, 170, cor)
    w = d.textlength(balao, font=q.BK(60)) + 120
    d.rounded_rectangle([960 - w / 2, 300, 960 + w / 2, 410], radius=55, fill=q.BRANCO)
    d.text((960, 355), balao, font=q.BK(60), fill=cor, anchor="mm")
    d.text((960, 150), frase, font=q.BK(62), fill=q.BRANCO, anchor="mm")
    q.lupa(img, pose, 380, x=1460, y=640, espelho=True)
    return img


def g_abertura():
    img = Image.new("RGB", (q.W, q.H), q.VERDE)
    d = ImageDraw.Draw(img)
    for k, c in enumerate((U, E, M)):
        d.rectangle([0, 300 + k * 60, q.W, 352 + k * 60], fill=c)
    d.rectangle([0, 420, q.W, 700], fill=COR if COR != q.VERDE else (16, 37, 26))
    d.text((960, 230), "QUEM FAZ O QUÊ?", font=q.BK(120), fill=q.BRANCO, anchor="mm")
    d.text((960, 520), f"Episódio {EPN}: {EPNOME}", font=q.BK(92), fill=q.BRANCO, anchor="mm")
    d.text((960, 640), "Uma série do Legiscópio", font=q.RG(44), fill=q.BRANCO, anchor="mm")
    q.lupa(img, "acenando", 360, x=1540, y=700)
    return img


def g_respostas(titulo, casos):
    img, d = novo()
    q.titulo(d, titulo, 150)
    for k, (ic, a, b, c) in enumerate(casos):
        y = 290 + k * 210
        q.cartao(d, 100, y, 1820, y + 180, cor=c, w=5)
        d.text((170, y + 90), str(k + 1), font=q.BK(70), fill=c, anchor="mm")
        q.icone(d, ic, 300, y + 90, 110, q.TINTA)
        d.text((390, y + 60), a, font=q.BD(40), fill=q.TINTA, anchor="lm")
        q.icone(d, "check", 410, y + 125, 44, c)
        d.text((450, y + 125), b, font=q.BK(36), fill=c, anchor="lm")
    return img


def g_selos(titulo, sub, itens, nota=None, nota_cor=None):
    img, d = novo()
    q.titulo(d, titulo, 150)
    if sub:
        d.text((70, 250), sub, font=q.RG(34), fill=q.TINTA)
    n = len(itens)
    passo = 1700 / n
    for k, (ic, t, s, c) in enumerate(itens):
        x = 110 + passo * (k + 0.5)
        q.selo_icone(img, ic, x, 470, 110 if n > 3 else 125, c)
        f = q.BK(38 if n > 3 else 44)
        lt = _linhas(d, t, f, passo - 40)
        for j, l in enumerate(lt):
            d.text((x, 630 + j * 48), l, font=f, fill=c, anchor="mm")
        for j, l in enumerate(_linhas(d, s, q.RG(30), passo - 50)):
            d.text((x, 630 + 48 * len(lt) + 22 + j * 40), l, font=q.RG(30), fill=q.TINTA, anchor="mm")
    if nota:
        nc = nota_cor or COR
        q.cartao(d, 120, 860, 1800, 960, cor=nc, w=4, fill=q.claro(nc, 0.88))
        d.text((960, 910), nota, font=q.BD(34), fill=nc, anchor="mm")
    return img


def g_linhas(titulo, sub, itens, nota=None):
    img, d = novo()
    q.titulo(d, titulo, 150)
    y0 = 270
    if sub:
        d.text((70, 250), sub, font=q.RG(34), fill=q.TINTA)
        y0 = 310
    n = len(itens)
    alt = min(170, ((900 if nota else 1010) - y0) / n - 18)
    ft, fs, dy = (q.BK(40), q.RG(31), 27) if alt >= 140 else (q.BK(36), q.RG(29), 23)
    for k, (ic, t, s, chip, c) in enumerate(itens):
        y = y0 + k * (alt + 18)
        q.cartao(d, 120, y, 1800, y + alt, cor=c, w=5)
        q.icone(d, ic, 220, y + alt / 2, min(90, alt - 30), c)
        d.text((310, y + alt / 2 - dy), t, font=ft, fill=c, anchor="lm")
        d.text((310, y + alt / 2 + dy), s, font=fs, fill=q.TINTA, anchor="lm")
        if chip:
            w = d.textlength(chip, font=q.BK(30)) + 52
            q.chip(d, 1760 - w, y + alt / 2 - 30, chip, c, fonte=q.BK(30), alt=60, pad=26)
    if nota:
        q.cartao(d, 120, 920, 1800, 1010, cor=COR, w=4, fill=q.claro(COR, 0.88))
        d.text((960, 965), nota, font=q.BD(33), fill=COR, anchor="mm")
    return img


def g_lista(titulo, sub, itens, icone=None, nota=None, cor=None):
    c = cor or COR
    img, d = novo()
    q.titulo(d, titulo, 150)
    if sub:
        d.text((70, 250), sub, font=q.RG(34), fill=q.TINTA)
    x0 = 120 if not icone else 700
    if icone:
        q.selo_icone(img, icone, 360, 560, 170, c)
    y = 360
    for t in itens:
        ls = _linhas(d, t, q.BD(40), 1780 - x0 - 80)
        q.icone(d, "check", x0 + 20, y + 24, 56, c)
        for j, l in enumerate(ls):
            d.text((x0 + 70, y + j * 50), l, font=q.BD(40), fill=q.TINTA)
        y += 50 * len(ls) + 45
    if nota:
        q.cartao(d, 120, 880, 1800, 980, cor=c, w=4, fill=q.claro(c, 0.88))
        d.text((960, 930), nota, font=q.BD(34), fill=c, anchor="mm")
    return img


def g_fluxo(titulo, sub, nos, nota=None):
    img, d = novo()
    q.titulo(d, titulo, 150)
    if sub:
        d.text((70, 250), sub, font=q.RG(34), fill=q.TINTA)
    n = len(nos)
    passo = 1700 / n
    xs = [110 + passo * (k + 0.5) for k in range(n)]
    for k, (ic, t, c) in enumerate(nos):
        x = xs[k]
        q.selo_icone(img, ic, x, 480, 95 if n > 4 else 110, c)
        for j, l in enumerate(_linhas(d, t, q.BD(32), passo - 30)):
            d.text((x, 620 + j * 42), l, font=q.BD(32), fill=q.TINTA, anchor="mm")
        if k < n - 1:
            q.seta(d, (x + 115, 480), (xs[k + 1] - 115, 480), cor=q.CINZA)
    if nota:
        q.cartao(d, 120, 840, 1800, 950, cor=COR, w=4, fill=q.claro(COR, 0.88))
        d.text((960, 895), nota, font=q.BD(34), fill=COR, anchor="mm")
    return img


def g_numeros(titulo, sub, itens, nota=None):
    img, d = novo()
    q.titulo(d, titulo, 150)
    if sub:
        d.text((70, 250), sub, font=q.RG(34), fill=q.TINTA)
    n = len(itens)
    passo = 1700 / n
    for k, (v, r, c) in enumerate(itens):
        x0 = 110 + passo * k + 20
        q.cartao(d, x0, 330, x0 + passo - 40, 760, cor=c, w=5)
        d.text((x0 + (passo - 40) / 2, 480), v, font=q.BK(110 if len(v) < 6 else 80), fill=c, anchor="mm")
        for j, l in enumerate(_linhas(d, r, q.BD(32), passo - 90)):
            d.text((x0 + (passo - 40) / 2, 620 + j * 42), l, font=q.BD(32), fill=q.TINTA, anchor="mm")
    if nota:
        q.cartao(d, 120, 840, 1800, 950, cor=COR, w=4, fill=q.claro(COR, 0.88))
        d.text((960, 895), nota, font=q.BD(34), fill=COR, anchor="mm")
    return img


def g_cta():
    img = Image.new("RGB", (q.W, q.H), q.VERDE)
    d = ImageDraw.Draw(img)
    d.text((960, 300), "Ajude a explicação a chegar a mais gente", font=q.BD(56), fill=q.BRANCO, anchor="mm")
    q.lupa(img, "joinha", 380, x=120, y=640, espelho=False)
    return img


def g_teste(casos, rodape):
    img, d = novo()
    q.titulo(d, "Teste rápido: de quem é?" if EPN < 4 else "Teste rápido", 150, tam=72)
    for k, (ic, t) in enumerate(casos):
        y = 300 + k * 190
        q.cartao(d, 100, y, 1500, y + 160, cor=q.TINTA, w=3)
        d.text((170, y + 80), str(k + 1), font=q.BK(70), fill=q.VERDE, anchor="mm")
        q.icone(d, ic, 300, y + 80, 100, q.TINTA)
        d.text((380, y + 80), t, font=q.BD(40), fill=q.TINTA, anchor="lm")
        d.text((1440, y + 80), "?", font=q.BK(90), fill=q.CINZA, anchor="mm")
    d.text((800, 920), rodape, font=q.BK(40), fill=q.VERDE, anchor="mm")
    q.lupa(img, "pensando", 400, x=1500, y=560)
    return img


def g_fim(chips, prox1, prox2, pergunta1, pergunta2="(sem citar nomes de pessoas)"):
    img = Image.new("RGB", (q.W, q.H), q.VERDE)
    d = ImageDraw.Draw(img)
    cc = COR if COR != q.VERDE else (16, 37, 26)
    for k, t in enumerate(chips):
        q.chip(d, 120, 160 + k * 110, t, cc, fonte=q.BK(44), alt=88, pad=40)
    q.mapa_brasil(d, 1150, 120, 560, 560, q.claro(COR, 0.3) if COR != q.VERDE else q.claro(q.LIMA, 0.2))
    d.text((120, 500), pergunta1, font=q.BD(40), fill=q.BRANCO)
    d.text((120, 550), pergunta2, font=q.RG(34), fill=q.LIMA)
    d.text((120, 650), "App para Android: legiscopio.com.br/baixar", font=q.BK(44), fill=q.BRANCO)
    d.text((120, 720), "Apoie: apoia.se/legiscopio", font=q.BK(44), fill=q.LIMA)
    d.text((120, 850), prox1, font=q.BK(48), fill=q.BRANCO)
    d.text((120, 915), prox2, font=q.RG(36), fill=q.LIMA)
    lg = q.vl.logo(90)
    if lg:
        box = Image.new("RGB", (lg.width + 40, lg.height + 30), q.BRANCO)
        img.paste(box, (q.W - box.width - 80, q.H - box.height - 60))
        img.paste(lg, (q.W - box.width - 60, q.H - box.height - 45), lg)
    return img


def g_miniatura(grande, sub, icone, cor_sub):
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), (22, 34, 52))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 820, W, H], fill=(40, 46, 56))
    for x in (-60, 330):
        d.rectangle([x, 520, x + 300, 820], fill=(52, 62, 80))
        for wy in (560, 680):
            for wx in (x + 40, x + 190):
                d.rectangle([wx, wy, wx + 70, wy + 60], fill=(250, 214, 120))
    q.selo_icone(img, icone, 820, 700, 200, COR if COR != q.VERDE else (40, 150, 90))
    for k, c in enumerate((U, E, M)):
        d.rectangle([k * W / 3, 0, (k + 1) * W / 3, 22], fill=c)
    t = f"EP. {EPN} · {EPNOME.upper()}"
    w = d.textlength(t, font=q.BK(52)) + 70
    d.rounded_rectangle([60, 60, 60 + w, 150], radius=45, fill=COR if COR != q.VERDE else (40, 150, 90))
    d.text((60 + w / 2, 105), t, font=q.BK(52), fill=q.BRANCO, anchor="mm")
    tam = 176
    while d.textlength(grande, font=q.BK(tam)) > 1500:
        tam -= 8
    d.text((60, 190), grande, font=q.BK(tam), fill=q.BRANCO)
    d.text((66, 400), sub, font=q.BD(76), fill=cor_sub)
    sp = q.personagem.pose("pensando", "fechada", "abertos", 760, 0.3, -1, espelho=True)
    img.paste(sp, (W - sp.width + 10, H - sp.height + 40), sp)
    lg = q.vl.logo(110)
    if lg:
        box = Image.new("RGB", (lg.width + 50, lg.height + 36), q.BRANCO)
        img.paste(box, (60, H - box.height - 50))
        img.paste(lg, (85, H - box.height - 32), lg)
    return img.resize((1280, 720), Image.LANCZOS)


def _fab(f, i):
    def criar():
        import qfq_render
        return qfq_render.Cena(f, sys.modules[__name__], {})
    return criar

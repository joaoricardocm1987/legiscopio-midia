"""Episódio 2 da série "Quem Faz o Quê?" (Estado): quadros-chave usados pelo qfq_render.

Cada função desenha o quadro final da cena; o motor separa cada desenho numa camada que entra em sequência
durante a narração (a Lupa é animada à parte, sem falar).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qfq_visual as q  # noqa: E402

M, E, U = q.MUN, q.EST, q.UNI


def novo():
    img = q.base(2, "Estado", E)
    return img, ImageDraw.Draw(img)


def c1():
    img = Image.new("RGB", (q.W, q.H), (22, 34, 52))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 760, q.W, q.H], fill=(40, 46, 56))
    for x in (60, 1500):
        d.rectangle([x, 380, x + 360, 760], fill=(52, 62, 80))
        for wy in (430, 540, 650):
            for wx in (x + 40, x + 200):
                d.rectangle([wx, wy, wx + 90, wy + 60], fill=(250, 214, 120))
    q.icone(d, "viatura", 960, 640, 420, E)
    d.rounded_rectangle([660, 300, 1260, 420], radius=60, fill=q.BRANCO)
    q.icone(d, "celular", 740, 360, 90, q.TINTA)
    d.text((1000, 360), "LIGUEI 190", font=q.BK(64), fill=E, anchor="mm")
    d.text((960, 140), "Quem atende? E o que mais o estado faz?", font=q.BK(64), fill=q.BRANCO, anchor="mm")
    q.lupa(img, "pensando", 380, x=1460, y=640, espelho=True)
    return img


def c2():
    img = Image.new("RGB", (q.W, q.H), q.VERDE)
    d = ImageDraw.Draw(img)
    for k, c in enumerate((U, E, M)):
        d.rectangle([0, 300 + k * 60, q.W, 352 + k * 60], fill=c)
    d.rectangle([0, 420, q.W, 700], fill=E)
    d.text((960, 230), "QUEM FAZ O QUÊ?", font=q.BK(120), fill=q.BRANCO, anchor="mm")
    d.text((960, 520), "Episódio 2: Estado", font=q.BK(96), fill=q.BRANCO, anchor="mm")
    d.text((960, 640), "Uma série do Legiscópio", font=q.RG(44), fill=q.BRANCO, anchor="mm")
    q.lupa(img, "acenando", 360, x=1540, y=700)
    return img


def c3():
    img, d = novo()
    q.titulo(d, "Respostas do teste do episódio 1", 150)
    casos = (("torre", "Luz acabou em todas as casas da rua", "Distribuidora (concessão da União)", U),
             ("berco", "Sem vaga na creche (3 anos)", "Município: educação infantil", M),
             ("rodovia", "Buraco em rodovia estadual", "Órgão estadual de estradas ou concessionária", E))
    for k, (ic, a, b, c) in enumerate(casos):
        y = 290 + k * 210
        q.cartao(d, 100, y, 1820, y + 180, cor=c, w=5)
        d.text((170, y + 90), str(k + 1), font=q.BK(70), fill=c, anchor="mm")
        q.icone(d, ic, 300, y + 90, 110, q.TINTA)
        d.text((390, y + 60), a, font=q.BD(40), fill=q.TINTA, anchor="lm")
        q.icone(d, "check", 410, y + 125, 44, c)
        d.text((450, y + 125), b, font=q.BK(38), fill=c, anchor="lm")
    return img


def c4():
    img, d = novo()
    q.titulo(d, "26 estados + o Distrito Federal", 150)
    d.text((70, 250), "Cada um tem a sua Constituição estadual (CF, art. 25)", font=q.RG(34), fill=q.TINTA)
    q.mapa_brasil(d, 1120, 300, 680, 680, q.claro(E, 0.7), contorno=E, k=8)
    d.ellipse([1120 + 0.62 * 680 - 16, 300 + 0.55 * 680 - 16, 1120 + 0.62 * 680 + 16, 300 + 0.55 * 680 + 16], fill=E)
    q.icone(d, "documento", 160, 420, 120, E)
    d.text((250, 400), "Constituição estadual", font=q.BK(44), fill=E, anchor="lm")
    d.text((250, 450), "+ leis estaduais", font=q.BD(34), fill=q.TINTA, anchor="lm")
    q.cartao(d, 90, 560, 1000, 820, cor=E, w=5, fill=q.claro(E, 0.88))
    d.text((130, 610), "PODERES REMANESCENTES", font=q.BK(42), fill=E)
    for j, l in enumerate(("O que a Constituição não proíbe", "aos estados fica com eles")):
        d.text((130, 690 + j * 52), l, font=q.BD(36), fill=q.TINTA)
    return img


def c5():
    img, d = novo()
    q.titulo(d, "Quem governa o estado", 150)
    d.text((70, 250), "Eleição direta · mandato de 4 anos", font=q.BD(36), fill=q.TINTA)
    q.icone(d, "urna", 260, 560, 220, q.VERDE)
    q.seta(d, (400, 520), (720, 420), cor=q.CINZA)
    q.seta(d, (400, 600), (720, 700), cor=q.CINZA)
    q.selo_icone(img, "prefeitura", 820, 420, 90, E)
    d.text((940, 400), "GOVERNADOR + VICE", font=q.BK(44), fill=E, anchor="lm")
    d.text((940, 450), "Poder Executivo · secretários de estado", font=q.RG(32), fill=q.TINTA, anchor="lm")
    q.selo_icone(img, "camara", 820, 700, 90, E, contorno=True)
    d.text((940, 680), "DEPUTADOS ESTADUAIS", font=q.BK(44), fill=E, anchor="lm")
    d.text((940, 730), "Assembleia Legislativa · Poder Legislativo", font=q.RG(32), fill=q.TINTA, anchor="lm")
    x = 120
    for t in ("2º turno se ninguém passar de 50% dos válidos", "1 reeleição seguida"):
        x += q.chip(d, x, 880, t, E, fonte=q.BD(32), alt=70, pad=30) + 30
    return img


def c6():
    img, d = novo()
    q.titulo(d, "Assembleia Legislativa: quantos deputados?", 150)
    d.text((70, 250), "CF, art. 27: o triplo da bancada federal até 36; depois, +1 por deputado federal acima de 12", font=q.RG(32), fill=q.TINTA)
    barras = (("Menores bancadas", 8, 24), ("Exemplo: 12 federais", 12, 36), ("São Paulo", 70, 94))
    for k, (t, fed, est) in enumerate(barras):
        y = 360 + k * 170
        d.text((90, y + 45), t, font=q.BD(36), fill=q.TINTA, anchor="lm")
        d.text((90, y + 95), f"{fed} deputados federais", font=q.RG(28), fill=q.CINZA, anchor="lm")
        w = int(est * 11.5)
        d.rounded_rectangle([600, y + 20, 600 + w, y + 110], radius=20, fill=E)
        d.text((620 + w, y + 65), str(est), font=q.BK(64), fill=E, anchor="lm")
    q.cartao(d, 90, 880, 1500, 970, cor=E, w=3)
    d.text((130, 925), "No Distrito Federal: Câmara Legislativa", font=q.BD(36), fill=q.TINTA, anchor="lm")
    return img


def c7():
    img, d = novo()
    q.titulo(d, "O estado tem os três Poderes", 150)
    cols = (("prefeitura", "EXECUTIVO", "Governador e secretarias"), ("camara", "LEGISLATIVO", "Assembleia Legislativa"),
            ("balanca", "JUDICIÁRIO", "Tribunal de Justiça e juízes estaduais"))
    for k, (ic, t, s) in enumerate(cols):
        x = 330 + k * 630
        q.selo_icone(img, ic, x, 430, 120, E)
        d.text((x, 600), t, font=q.BK(46), fill=E, anchor="mm")
        for j, l in enumerate(q.vl.wrap(d, s, q.RG(32), 480)):
            d.text((x, 655 + j * 42), l, font=q.RG(32), fill=q.TINTA, anchor="mm")
    x = 120
    for t in ("Ministério Público estadual", "Defensoria Pública", "Tribunal de Contas do Estado"):
        x += q.chip(d, x, 860, t, q.claro(E, 0.25), fonte=q.BD(32), alt=70, pad=30) + 30
    return img


def c8():
    img, d = novo()
    q.titulo(d, "Segurança pública: as forças do estado", 150)
    d.text((70, 250), "CF, art. 144 · todas subordinadas ao governador", font=q.RG(34), fill=q.TINTA)
    itens = (("viatura", "POLÍCIA MILITAR", "policiamento ostensivo"), ("lupa_icone", "POLÍCIA CIVIL", "investiga crimes"),
             ("megafone", "BOMBEIROS", "defesa civil e incêndios"), ("balanca", "POLÍCIA PENAL", "presídios estaduais"))
    for k, (ic, t, s) in enumerate(itens):
        x = 250 + k * 470
        q.selo_icone(img, ic, x, 470, 110, E)
        d.text((x, 630), t, font=q.BK(38), fill=E, anchor="mm")
        d.text((x, 685), s, font=q.RG(30), fill=q.TINTA, anchor="mm")
    q.cartao(d, 120, 790, 1800, 900, cor=U, w=4, fill=q.claro(U, 0.88))
    d.text((960, 845), "Exceção: no Distrito Federal, polícias e bombeiros são mantidos pela União", font=q.BD(34), fill=U, anchor="mm")
    return img


def c9():
    img, d = novo()
    q.titulo(d, "E as outras polícias?", 150)
    itens = (("POLÍCIA FEDERAL", "crimes contra a União, tráfico internacional", U, "UNIÃO"),
             ("POLÍCIA RODOVIÁRIA FEDERAL", "patrulha as rodovias federais", U, "UNIÃO"),
             ("GUARDA MUNICIPAL", "protege bens, serviços e instalações da cidade", M, "MUNICÍPIO"))
    for k, (t, s, c, niv) in enumerate(itens):
        y = 300 + k * 200
        q.cartao(d, 120, y, 1800, y + 170, cor=c, w=5)
        q.icone(d, "viatura" if k < 2 else "pessoa", 230, y + 85, 110, c)
        d.text((330, y + 60), t, font=q.BK(42), fill=c, anchor="lm")
        d.text((330, y + 115), s, font=q.RG(32), fill=q.TINTA, anchor="lm")
        q.chip(d, 1500, y + 55, niv, c, fonte=q.BK(30), alt=60, pad=26)
    return img


def c10():
    img, d = novo()
    q.titulo(d, "Educação: ensino médio é do estado", 150)
    d.text((70, 250), "CF, art. 211: estados atuam prioritariamente no fundamental e no médio", font=q.RG(34), fill=q.TINTA)
    etapas = (("Creche e pré-escola", M, 0), ("Ensino fundamental", E, 1), ("Ensino médio", E, 1))
    for k, (t, c, on) in enumerate(etapas):
        y = 760 - k * 150
        d.rounded_rectangle([120 + k * 60, y, 1100, y + 110], radius=16, fill=c if on else q.claro(c, 0.75))
        d.text((160 + k * 60, y + 55), t, font=q.BD(38), fill=q.BRANCO if on else c, anchor="lm")
    q.selo_icone(img, "escola", 1450, 480, 150, E)
    d.text((1450, 690), "Escola estadual", font=q.BK(44), fill=E, anchor="mm")
    d.text((1450, 750), "+ universidades estaduais", font=q.BD(34), fill=q.TINTA, anchor="mm")
    return img


def c11():
    img, d = novo()
    q.titulo(d, "Saúde: o estado coordena o SUS no território", 150)
    d.text((70, 250), "Lei 8.080/1990 (Lei do SUS), art. 17", font=q.RG(34), fill=q.TINTA)
    q.selo_icone(img, "hospital", 400, 520, 150, E)
    d.text((400, 730), "Alta complexidade e", font=q.BK(38), fill=E, anchor="mm")
    d.text((400, 780), "referência regional", font=q.BK(38), fill=E, anchor="mm")
    for k, t in enumerate(("Apoio técnico e financeiro aos municípios", "Hemocentros", "Laboratórios centrais")):
        y = 380 + k * 110
        q.icone(d, "check", 820, y, 60, E)
        d.text((870, y), t, font=q.BD(40), fill=q.TINTA, anchor="lm")
    q.cartao(d, 760, 740, 1820, 900, cor=q.CINZA, w=3)
    d.text((800, 790), "Há hospitais municipais, federais e filantrópicos no SUS:", font=q.BD(32), fill=q.TINTA, anchor="lm")
    d.text((800, 845), "descubra quem administra antes de reclamar", font=q.BK(34), fill=E, anchor="lm")
    return img


def c12():
    img, d = novo()
    q.titulo(d, "Estradas e trânsito", 150)
    q.cartao(d, 100, 290, 920, 880, cor=E, w=5)
    q.selo_icone(img, "rodovia", 510, 470, 120, E)
    d.text((510, 650), "RODOVIAS ESTADUAIS", font=q.BK(42), fill=E, anchor="mm")
    d.text((510, 710), "órgão de estradas (em geral, DER)", font=q.RG(32), fill=q.TINTA, anchor="mm")
    d.text((510, 755), "ou concessionária", font=q.RG(32), fill=q.TINTA, anchor="mm")
    q.cartao(d, 1000, 290, 1820, 880, cor=E, w=5)
    q.selo_icone(img, "documento", 1410, 470, 120, E)
    d.text((1410, 650), "DETRAN", font=q.BK(42), fill=E, anchor="mm")
    d.text((1410, 710), "registro e licenciamento de veículos", font=q.RG(32), fill=q.TINTA, anchor="mm")
    d.text((1410, 755), "carteira de motorista", font=q.RG(32), fill=q.TINTA, anchor="mm")
    return img


def c13():
    img = Image.new("RGB", (q.W, q.H), q.VERDE)
    d = ImageDraw.Draw(img)
    d.text((960, 300), "Ajude a explicação a chegar a mais gente", font=q.BD(56), fill=q.BRANCO, anchor="mm")
    q.lupa(img, "joinha", 380, x=120, y=640, espelho=False)
    return img


def c14():
    img, d = novo()
    q.titulo(d, "Duas tarefas pouco conhecidas", 150)
    q.cartao(d, 100, 290, 920, 880, cor=E, w=5)
    d.ellipse([390, 350, 630, 590], fill=E)
    d.polygon([(510, 395), (565, 480), (575, 530), (545, 565), (475, 565), (445, 530), (455, 480)], fill=q.BRANCO)
    d.polygon([(510, 470), (535, 515), (530, 550), (490, 550), (485, 515)], fill=E)
    d.text((510, 650), "GÁS CANALIZADO", font=q.BK(42), fill=E, anchor="mm")
    d.text((510, 710), "serviço estadual, direto ou", font=q.RG(32), fill=q.TINTA, anchor="mm")
    d.text((510, 755), "por concessão (CF, art. 25, §2º)", font=q.RG(32), fill=q.TINTA, anchor="mm")
    q.cartao(d, 1000, 290, 1820, 880, cor=E, w=5)
    for k, (x, y) in enumerate(((1300, 430), (1520, 430), (1410, 560))):
        q.icone(d, "casa", x, y, 100, M)
    q.seta(d, (1340, 430), (1480, 430), cor=E, w=5)
    q.seta(d, (1490, 470), (1430, 530), cor=E, w=5)
    d.text((1410, 670), "REGIÕES METROPOLITANAS", font=q.BK(40), fill=E, anchor="mm")
    d.text((1410, 730), "por lei complementar estadual", font=q.RG(32), fill=q.TINTA, anchor="mm")
    d.text((1410, 775), "transporte, saneamento...", font=q.RG(32), fill=q.TINTA, anchor="mm")
    return img


def c15():
    img, d = novo()
    q.titulo(d, "De onde vem o dinheiro: impostos estaduais", 150)
    q.icone(d, "cofre", 1450, 600, 300, E)
    fontes = (("documento", "ICMS", "mercadorias e alguns serviços", (300, 360)), ("viatura", "IPVA", "propriedade de veículos", (300, 620)),
              ("casa", "ITCMD", "heranças e doações", (300, 880)))
    for ic, s, t, (x, y) in fontes:
        q.selo_icone(img, ic, x, y, 80, E)
        esq = x < 960
        d.text((x + 100 if esq else x - 100, y - 22), s, font=q.BK(46), fill=E, anchor="lm" if esq else "rm")
        d.text((x + 100 if esq else x - 100, y + 28), t, font=q.RG(30), fill=q.TINTA, anchor="lm" if esq else "rm")
        q.seta(d, (900, y), (1270, 600 + (y - 620) // 3), cor=q.claro(E, 0.4), w=4, tracejada=True)
    d.text((1450, 830), "O ICMS é a maior receita", font=q.BD(34), fill=q.TINTA, anchor="mm")
    d.text((1450, 875), "própria dos estados", font=q.BD(34), fill=q.TINTA, anchor="mm")
    return img


def c16():
    img, d = novo()
    q.titulo(d, "O dinheiro que sai e o que chega", 150)
    q.selo_icone(img, "prefeitura", 960, 560, 120, E)
    d.text((960, 730), "ESTADO", font=q.BK(40), fill=E, anchor="mm")
    q.selo_icone(img, "prefeitura", 1560, 560, 90, M)
    d.text((1560, 690), "MUNICÍPIOS", font=q.BK(36), fill=M, anchor="mm")
    d.text((1560, 740), "25% do ICMS · 50% do IPVA", font=q.BD(30), fill=q.TINTA, anchor="mm")
    q.seta(d, (1100, 560), (1440, 560), cor=M, w=8)
    q.selo_icone(img, "prefeitura", 360, 560, 90, U)
    d.text((360, 690), "UNIÃO", font=q.BK(36), fill=U, anchor="mm")
    d.text((360, 740), "FPE: parte do IR e do IPI", font=q.BD(30), fill=q.TINTA, anchor="mm")
    q.seta(d, (480, 560), (820, 560), cor=U, w=8)
    return img


def c17():
    img, d = novo()
    q.titulo(d, "Reforma tributária: o ICMS vai dar lugar ao IBS", 150)
    d.text((70, 250), "Emenda Constitucional 132/2023", font=q.RG(34), fill=q.TINTA)
    anos = (("2028", 100), ("2029", 90), ("2030", 80), ("2031", 70), ("2032", 60), ("2033", 0))
    for k, (a, p) in enumerate(anos):
        x = 160 + k * 280
        h = int(4.2 * p)
        d.rounded_rectangle([x, 760 - h, x + 120, 760], radius=10, fill=E if p else q.CINZA_CL)
        hi = int(4.2 * (100 - p))
        if hi:
            d.rounded_rectangle([x + 140, 760 - hi, x + 200, 760], radius=10, fill=q.VERDE)
        d.text((x + 100, 800), a, font=q.BK(38), fill=q.TINTA, anchor="mm")
        d.text((x + 60, 740 - h), f"{p}%" if p else "fim", font=q.BD(30), fill=E if p else q.CINZA, anchor="mb")
    d.line([(120, 760), (1820, 760)], fill=q.TINTA, width=4)
    d.rounded_rectangle([1080, 250, 1120, 290], radius=6, fill=E)
    d.text((1135, 270), "ICMS (alíquota vigente)", font=q.RG(28), fill=q.TINTA, anchor="lm")
    d.rounded_rectangle([1450, 250, 1490, 290], radius=6, fill=q.VERDE)
    d.text((1505, 270), "IBS (estados + municípios)", font=q.RG(28), fill=q.TINTA, anchor="lm")
    d.text((960, 880), "Ilustrativo. O IPVA continua e pode variar conforme o impacto ambiental do veículo", font=q.RG(30), fill=q.CINZA, anchor="mm")
    return img


def c18():
    img, d = novo()
    q.titulo(d, "Orçamento e fiscalização", 150)
    itens = (("PPA", "4 anos"), ("LDO", "regras do ano"), ("LOA", "quanto e em quê"))
    for k, (s, t) in enumerate(itens):
        x = 110 + k * 300
        q.cartao(d, x, 290, x + 260, 520, cor=E, w=5)
        d.text((x + 130, 380), s, font=q.BK(60), fill=E, anchor="mm")
        d.text((x + 130, 450), t, font=q.RG(28), fill=q.TINTA, anchor="mm")
    d.text((110, 580), "Governador envia → Assembleia vota", font=q.BD(38), fill=q.TINTA)
    nos = ((1150, "prefeitura", "Governador presta contas"), (1480, "balanca", "TCE: parecer prévio"), (1780, "camara", "Assembleia julga"))
    for k, (x, ic, t) in enumerate(nos):
        q.selo_icone(img, ic, x, 400, 80, E)
        for j, l in enumerate(q.vl.wrap(d, t, q.BD(30), 260)):
            d.text((x, 520 + j * 40), l, font=q.BD(30), fill=q.TINTA, anchor="mm")
        if k < 2:
            q.seta(d, (x + 95, 400), (nos[k + 1][0] - 95, 400), cor=q.CINZA)
    q.cartao(d, 110, 720, 1810, 860, cor=q.VERDE, w=4)
    q.icone(d, "lupa_icone", 190, 790, 80, q.VERDE)
    d.text((260, 790), "A Assembleia fiscaliza o governo com o auxílio do Tribunal de Contas do Estado", font=q.BD(34), fill=q.TINTA, anchor="lm")
    return img


def c19():
    img, d = novo()
    q.titulo(d, "Como cobrar o estado", 150)
    passos = (("celular", "Canal oficial", "do órgão ou da secretaria"), ("carimbo", "Protocolo", "anote o número"),
              ("megafone", "Ouvidoria", "do estado: 30 dias + 30 (Lei 13.460/2017)"), ("camara", "Deputado estadual", "requerimento de informação"))
    for k, (ic, t, s) in enumerate(passos):
        x, y = 120 + k * 430, 780 - k * 140
        d.rounded_rectangle([x, y, x + 400, 920], radius=18, fill=q.claro(E, 0.85 - k * 0.15))
        q.selo_icone(img, ic, x + 70, y + 70, 50, E)
        d.text((x + 140, y + 50), f"{k + 1}. {t}", font=q.BK(27), fill=q.TINTA, anchor="lm")
        for j, l in enumerate(q.vl.wrap(d, s, q.RG(26), 250)):
            d.text((x + 140, y + 92 + j * 32), l, font=q.RG(26), fill=q.TINTA, anchor="lm")
    q.icone(d, "lupa_icone", 170, 330, 100, E)
    d.text((240, 310), "Gastos: portal da transparência", font=q.BD(34), fill=q.TINTA, anchor="lm")
    d.text((240, 355), "do governo do estado", font=q.RG(30), fill=q.TINTA, anchor="lm")
    return img


def c20():
    img, d = novo()
    q.titulo(d, "Teste rápido: de quem é?", 150, tam=72)
    casos = (("documento", "Tirar ou renovar o passaporte"), ("viatura", "Tirar a primeira carteira de motorista"),
             ("rodovia", "Rodovia federal cheia de buracos"))
    for k, (ic, t) in enumerate(casos):
        y = 300 + k * 190
        q.cartao(d, 100, y, 1500, y + 160, cor=q.TINTA, w=3)
        d.text((170, y + 80), str(k + 1), font=q.BK(70), fill=q.VERDE, anchor="mm")
        q.icone(d, ic, 300, y + 80, 100, q.TINTA)
        d.text((380, y + 80), t, font=q.BD(40), fill=q.TINTA, anchor="lm")
        d.text((1440, y + 80), "?", font=q.BK(90), fill=q.CINZA, anchor="mm")
    d.text((800, 920), "Responda nos comentários · respostas no Ep. 3", font=q.BK(40), fill=q.VERDE, anchor="mm")
    q.lupa(img, "pensando", 400, x=1500, y=560)
    return img


def c21():
    img = Image.new("RGB", (q.W, q.H), q.VERDE)
    d = ImageDraw.Draw(img)
    for k, (t, c) in enumerate((("TRÊS PODERES", E), ("POLÍCIA · ENSINO MÉDIO · HOSPITAIS", E), ("ICMS EM TRANSIÇÃO", E))):
        q.chip(d, 120, 160 + k * 110, t, c, fonte=q.BK(44), alt=88, pad=40)
    q.mapa_brasil(d, 1150, 120, 560, 560, q.claro(U, 0.3))
    d.text((1430, 720), "Próximo: Ep. 3 · UNIÃO", font=q.BK(48), fill=q.BRANCO, anchor="mm")
    d.text((1430, 780), "Previdência · moeda · fronteiras", font=q.RG(34), fill=q.LIMA, anchor="mm")
    d.text((120, 520), "Qual serviço estadual faz falta na sua região?", font=q.BD(40), fill=q.BRANCO)
    d.text((120, 570), "(sem citar nomes de pessoas)", font=q.RG(34), fill=q.LIMA)
    d.text((120, 690), "App para Android: legiscopio.com.br/baixar", font=q.BK(44), fill=q.BRANCO)
    d.text((120, 760), "Apoie: apoia.se/legiscopio", font=q.BK(44), fill=q.LIMA)
    lg = q.vl.logo(90)
    if lg:
        box = Image.new("RGB", (lg.width + 40, lg.height + 30), q.BRANCO)
        img.paste(box, (120, 900))
        img.paste(lg, (140, 915), lg)
    return img


FUNCS = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20, c21]
CUES = {}


def _fab(f, i):
    def criar():
        import qfq_render
        return qfq_render.Cena(f, sys.modules[__name__], CUES.get(i))
    return criar


CENAS = [_fab(f, i) for i, f in enumerate(FUNCS)]

SHORT = {
    "selo": "Episódio 2 · Estado",
    "cenas": [
        {"cena": 1, "narracao": "Você liga 190. Quem atende é a Polícia Militar, e ela é do estado, não da prefeitura."},
        {"cena": 8, "narracao": "A Polícia Militar faz o policiamento nas ruas. A Polícia Civil investiga os crimes. Os bombeiros cuidam da defesa civil, e a Polícia Penal, dos presídios. Todas respondem ao governador."},
        {"cena": 10, "narracao": "O estado também cuida do ensino médio: a grande maioria dos alunos da rede pública nessa etapa estuda em escolas estaduais."},
        {"cena": 12, "narracao": "E das rodovias estaduais e do Detran, que faz o licenciamento dos veículos e a carteira de motorista."},
        {"cena": 15, "narracao": "Quem paga a conta? Principalmente o ICMS, que, com a reforma tributária, deixa de existir em 2033."},
        {"cena": 2, "narracao": "Quem faz o quê no seu estado? O episódio completo está no canal."},
    ],
}


def miniatura():
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), (22, 34, 52))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 820, W, H], fill=(40, 46, 56))
    for x in (-60, 330):
        d.rectangle([x, 520, x + 300, 820], fill=(52, 62, 80))
        for wy in (560, 680):
            for wx in (x + 40, x + 190):
                d.rectangle([wx, wy, wx + 70, wy + 60], fill=(250, 214, 120))
    q.icone(d, "viatura", 780, 700, 520, E)
    for k, c in enumerate((U, E, M)):
        d.rectangle([k * W / 3, 0, (k + 1) * W / 3, 22], fill=c)
    t = "EP. 2 · ESTADO"
    w = d.textlength(t, font=q.BK(52)) + 70
    d.rounded_rectangle([60, 60, 60 + w, 150], radius=45, fill=E)
    d.text((60 + w / 2, 105), t, font=q.BK(52), fill=q.BRANCO, anchor="mm")
    d.text((60, 190), "LIGOU 190?", font=q.BK(176), fill=q.BRANCO)
    d.text((66, 400), "O que é do governo do estado", font=q.BD(76), fill=(160, 200, 245))
    sp = q.personagem.pose("pensando", "fechada", "abertos", 760, 0.3, -1, espelho=True)
    img.paste(sp, (W - sp.width + 10, H - sp.height + 40), sp)
    lg = q.vl.logo(110)
    if lg:
        box = Image.new("RGB", (lg.width + 50, lg.height + 36), q.BRANCO)
        img.paste(box, (60, H - box.height - 50))
        img.paste(lg, (85, H - box.height - 32), lg)
    return img.resize((1280, 720), Image.LANCZOS)

"""Episódio 1 da série "Quem Faz o Quê?" (Município): quadros-chave usados pelo qfq_render.

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
    img = q.base(1, "Município", M)
    return img, ImageDraw.Draw(img)


def c1():
    img = Image.new("RGB", (q.W, q.H), (22, 34, 52))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 760, q.W, q.H], fill=(40, 46, 56))
    for k, x in enumerate((120, 520, 1180, 1560)):
        d.rectangle([x, 470, x + 300, 760], fill=(52, 62, 80))
        d.polygon([(x - 20, 470), (x + 150, 360), (x + 320, 470)], fill=(60, 70, 90))
        for wx in (x + 40, x + 190):
            d.rectangle([wx, 540, wx + 70, 610], fill=(250, 214, 120))
    q.icone(d, "poste", 960, 560, 420, (120, 128, 140))
    d.rounded_rectangle([1560, 300, 1840, 390], radius=16, fill=q.BRANCO)
    d.text((1700, 345), "DIA 7", font=q.BK(50), fill=q.TINTA, anchor="mm")
    d.text((960, 120), "Você reclama com quem?", font=q.BK(70), fill=q.BRANCO, anchor="mm")
    x = 420
    for t in ("PREFEITO", "VEREADOR", "COMPANHIA DE ENERGIA"):
        x += q.chip(d, x, 200, t, q.CINZA) + 30
    q.lupa(img, "pensando", 420, x=1450, y=620, espelho=True)
    return img


def c2():
    img = Image.new("RGB", (q.W, q.H), q.VERDE)
    d = ImageDraw.Draw(img)
    for k, c in enumerate((U, E, M)):
        d.rectangle([0, 300 + k * 60, q.W, 352 + k * 60], fill=c)
    d.rectangle([0, 420, q.W, 700], fill=M)
    d.text((960, 230), "QUEM FAZ O QUÊ?", font=q.BK(120), fill=q.BRANCO, anchor="mm")
    d.text((960, 520), "Episódio 1: Município", font=q.BK(96), fill=q.BRANCO, anchor="mm")
    d.text((960, 640), "Uma série do Legiscópio", font=q.RG(44), fill=q.BRANCO, anchor="mm")
    q.lupa(img, "acenando", 360, x=1540, y=700)
    return img


def c3():
    img, d = novo()
    q.titulo(d, "O Brasil é uma federação", 150)
    d.text((70, 250), "Constituição, art. 18: União, estados, DF e municípios, todos autônomos", font=q.RG(34), fill=q.TINTA)
    q.mapa_brasil(d, 1120, 320, 680, 680, q.claro(U, 0.75), contorno=U, k=8)
    for (px, py) in ((0.5, 0.4), (0.62, 0.55), (0.38, 0.5), (0.7, 0.35), (0.55, 0.7)):
        d.ellipse([1120 + px * 680 - 9, 320 + py * 680 - 9, 1120 + px * 680 + 9, 320 + py * 680 + 9], fill=M)
    y = 360
    for t in ("GOVERNO PRÓPRIO", "LEIS LOCAIS", "TRIBUTOS PRÓPRIOS"):
        q.chip(d, 70, y, t, M, fonte=q.BK(40), alt=84, pad=36)
        y += 120
    q.icone(d, "documento", 140, 790, 110, M)
    d.text((220, 790), "Lei Orgânica = a \"constituição\" da cidade", font=q.BD(38), fill=q.TINTA, anchor="lm")
    return img


def c4():
    img, d = novo()
    q.titulo(d, "Da sua rua ao município", 150)
    boxes = [(80, 300, 560, 820, "SUA RUA"), (660, 300, 1180, 820, "SEU BAIRRO"), (1280, 300, 1840, 820, "O MUNICÍPIO")]
    for k, (x0, y0, x1, y1, t) in enumerate(boxes):
        q.cartao(d, x0, y0, x1, y1, cor=M, w=6)
        d.text(((x0 + x1) / 2, y1 - 50), t, font=q.BK(40), fill=M, anchor="mm")
        if k < 2:
            q.seta(d, (x1 + 15, 560), (boxes[k + 1][0] - 15, 560), cor=M)
    q.icone(d, "poste", 220, 520, 200, q.TINTA)
    q.icone(d, "casa", 420, 560, 150, q.TINTA)
    for (x, y) in ((760, 430), (900, 470), (1060, 430), (800, 600), (1000, 620)):
        q.icone(d, "casa", x, y, 90, q.TINTA)
    d.rounded_rectangle([1340, 360, 1780, 720], radius=30, fill=q.claro(M, 0.7), outline=M, width=5)
    d.rounded_rectangle([1400, 420, 1600, 560], radius=20, fill=M)
    d.text((1500, 490), "urbana", font=q.BD(30), fill=q.BRANCO, anchor="mm")
    d.text((1660, 640), "zona rural", font=q.RG(28), fill=M, anchor="mm")
    d.ellipse([1640, 420, 1720, 500], fill=q.claro(M, 0.3))
    d.text((1680, 520), "distrito", font=q.RG(26), fill=M, anchor="mm")
    return img


def c5():
    img, d = novo()
    q.titulo(d, "Quem governa a cidade", 150)
    d.text((70, 250), "Eleição direta · mandato de 4 anos", font=q.BD(36), fill=q.TINTA)
    q.icone(d, "urna", 260, 560, 220, q.VERDE)
    q.seta(d, (400, 520), (720, 420), cor=q.CINZA)
    q.seta(d, (400, 600), (720, 700), cor=q.CINZA)
    q.selo_icone(img, "prefeitura", 820, 420, 90, M)
    d.text((940, 400), "PREFEITURA", font=q.BK(44), fill=M, anchor="lm")
    d.text((940, 450), "Prefeito + vice · Poder Executivo", font=q.RG(32), fill=q.TINTA, anchor="lm")
    q.selo_icone(img, "camara", 820, 700, 90, M, contorno=True)
    d.text((940, 680), "CÂMARA MUNICIPAL", font=q.BK(44), fill=M, anchor="lm")
    d.text((940, 730), "Vereadores · Poder Legislativo", font=q.RG(32), fill=q.TINTA, anchor="lm")
    d.text((70, 880), "Limite de vereadores:", font=q.BD(32), fill=q.TINTA)
    d.rounded_rectangle([420, 880, 1500, 920], radius=20, fill=q.claro(M, 0.7))
    d.rounded_rectangle([420, 880, 520, 920], radius=20, fill=M)
    d.text((470, 950), "9", font=q.BK(36), fill=M, anchor="mm")
    d.text((1450, 950), "55", font=q.BK(36), fill=M, anchor="mm")
    d.text((960, 960), "cresce com a população", font=q.RG(28), fill=q.TINTA, anchor="mm")
    return img


def c6():
    img, d = novo()
    q.titulo(d, "Executivo faz. Legislativo fiscaliza.", 150)
    q.cartao(d, 80, 280, 860, 860, cor=M, w=6)
    d.rectangle([80, 280, 860, 360], fill=M)
    d.text((470, 320), "EXECUTIVO · PREFEITURA", font=q.BK(38), fill=q.BRANCO, anchor="mm")
    for k, (t, ic) in enumerate((("Saúde", "ubs"), ("Educação", "escola"), ("Obras", "rodovia"), ("Transporte", "onibus"))):
        x, y = 140 + (k % 2) * 370, 400 + (k // 2) * 220
        q.cartao(d, x, y, x + 320, y + 180, cor=q.claro(M, 0.3), w=3)
        q.icone(d, ic, x + 80, y + 90, 90, M)
        d.text((x + 150, y + 90), t, font=q.BD(34), fill=q.TINTA, anchor="lm")
    q.cartao(d, 1060, 280, 1840, 860, cor=M, w=6, fill=q.claro(M, 0.88))
    d.text((1450, 320), "LEGISLATIVO · CÂMARA", font=q.BK(38), fill=M, anchor="mm")
    q.icone(d, "camara", 1450, 470, 180, M)
    for k, t in enumerate(("Faz leis municipais", "Aprova o orçamento", "Fiscaliza a prefeitura")):
        d.text((1130, 620 + k * 60), "• " + t, font=q.BD(34), fill=q.TINTA)
    for k, t in enumerate(("projetos de lei", "orçamento", "pedidos de informação")):
        y = 420 + k * 130
        q.seta(d, (880, y), (1040, y), cor=q.CINZA, w=5)
        q.seta(d, (1040, y + 40), (880, y + 40), cor=q.CINZA, w=5)
        d.text((960, y - 22), t, font=q.RG(22), fill=q.TINTA, anchor="mm")
    d.text((960, 930), "O município não tem Judiciário próprio", font=q.RG(32), fill=q.CINZA, anchor="mm")
    return img


def c7():
    img, d = novo()
    q.titulo(d, "Vereador faz obra?", 150)
    for k, t in enumerate(("Tapa buraco", "Asfalta rua", "Contrata obra")):
        y = 330 + k * 120
        q.icone(d, "x", 120, y + 30, 70, q.CINZA)
        d.text((180, y + 30), t, font=q.BD(48), fill=q.CINZA, anchor="lm")
        d.line([(180, y + 32), (180 + d.textlength(t, font=q.BD(48)), y + 32)], fill=q.CINZA, width=4)
    for k, t in enumerate(("Faz e vota leis", "Vota o orçamento", "Fiscaliza o prefeito", "Indicações e requerimentos")):
        y = 330 + k * 110
        q.icone(d, "check", 820, y + 30, 70, M)
        d.text((880, y + 30), t, font=q.BD(48), fill=q.TINTA, anchor="lm")
    q.cartao(d, 760, 790, 1700, 900, cor=M, w=4, fill=q.claro(M, 0.85))
    q.icone(d, "documento", 830, 845, 70, M)
    d.text((890, 845), "Indicação = pedido, não ordem", font=q.BK(42), fill=M, anchor="lm")
    return img


def c8():
    img, d = novo()
    q.titulo(d, "O que é da prefeitura", 150)
    d.text((70, 250), "Constituição, art. 30, V: serviços públicos de interesse local", font=q.RG(34), fill=q.TINTA)
    itens = (("lixo", "Coleta de lixo"), ("poste_aceso", "Iluminação"), ("rodovia", "Vias municipais"),
             ("onibus", "Ônibus urbano"), ("casa", "Uso do solo"))
    for k, (ic, t) in enumerate(itens):
        x = 200 + k * 360
        q.selo_icone(img, ic, x, 470, 110, M)
        d.text((x, 620), t, font=q.BD(34), fill=q.TINTA, anchor="mm")
    q.cartao(d, 120, 720, 1800, 870, cor=M, w=4)
    q.icone(d, "documento", 210, 795, 90, M)
    d.text((290, 765), "Plano diretor: obrigatório em cidades com mais de 20 mil habitantes", font=q.BD(36), fill=q.TINTA)
    d.text((290, 815), "aprovado por lei municipal e revisto a cada 10 anos", font=q.RG(32), fill=q.TINTA)
    return img


def c9():
    img, d = novo()
    q.titulo(d, "Saúde e educação: tarefas divididas", 150)
    d.text((70, 250), "Competência comum (Constituição, art. 23)", font=q.RG(34), fill=q.TINTA)
    q.cartao(d, 80, 320, 900, 900, cor=M, w=5)
    q.selo_icone(img, "ubs", 490, 480, 110, M)
    q.seta(d, (180, 360), (380, 450), cor=U, w=5, tracejada=True)
    q.seta(d, (800, 360), (600, 450), cor=E, w=5, tracejada=True)
    d.text((490, 640), "UBS: em regra, municipal", font=q.BK(40), fill=M, anchor="mm")
    d.text((490, 700), "com cooperação técnica e financeira", font=q.RG(30), fill=q.TINTA, anchor="mm")
    d.text((490, 740), "da União e do estado", font=q.RG(30), fill=q.TINTA, anchor="mm")
    q.cartao(d, 1020, 320, 1840, 900, cor=M, w=5)
    etapas = (("Creche e pré-escola (até 5 anos)", M, 1), ("Ensino fundamental", M, 1), ("Ensino médio → próximo episódio", E, 0))
    for k, (t, c, on) in enumerate(etapas):
        y = 760 - k * 150
        d.rounded_rectangle([1080 + k * 40, y, 1780, y + 110], radius=16, fill=c if on else q.claro(c, 0.75))
        d.text((1110 + k * 40, y + 55), t, font=q.BD(32), fill=q.BRANCO if on else c, anchor="lm")
    q.icone(d, "berco", 1430, 400, 110, M)
    return img


def c10():
    img, d = novo()
    q.quadro_resp(img, 80, 150, 1080, 900, {"uniao": "contorno", "estado": "apagado", "municipio": "apagado"},
                  problema="A rua inteira ficou sem luz", icone_prob="torre")
    d.text((1160, 230), "Casos do dia a dia", font=q.BK(40), fill=q.TINTA)
    casos = (("Rua inteira sem luz", "distribuidora (concessão da União)", U),
             ("Lâmpada do poste apagada", "prefeitura (em regra)", M),
             ("Escola estadual", "estado", E),
             ("Rodovia estadual ou federal", "estado, União ou concessionária", E),
             ("Policiamento", "estado", E))
    for k, (a, b, c) in enumerate(casos):
        y = 310 + k * 120
        q.cartao(d, 1160, y, 1840, y + 100, cor=c, w=4)
        d.text((1190, y + 30), a, font=q.BD(32), fill=q.TINTA, anchor="lm")
        d.text((1190, y + 72), "→ " + b, font=q.RG(28), fill=c, anchor="lm")
    q.legenda_quadro(d, 80, 930)
    return img


def c11():
    img = Image.new("RGB", (q.W, q.H), q.VERDE)
    d = ImageDraw.Draw(img)
    d.text((960, 300), "Ajude a explicação a chegar a mais gente", font=q.BD(56), fill=q.BRANCO, anchor="mm")
    q.lupa(img, "joinha", 380, x=120, y=640, espelho=False)
    return img


def c12():
    img, d = novo()
    q.titulo(d, "O orçamento da cidade: PPA, LDO e LOA", 150)
    itens = (("PPA", "planos para 4 anos"), ("LDO", "prioridades e regras do ano seguinte"), ("LOA", "quanto será gasto, e em quê"))
    for k, (s, t) in enumerate(itens):
        x = 110 + k * 600
        q.cartao(d, x, 300, x + 520, 640, cor=M, w=5)
        q.icone(d, "documento", x + 260, 400, 130, M)
        d.text((x + 260, 520), s, font=q.BK(64), fill=M, anchor="mm")
        d.text((x + 260, 590), t, font=q.RG(28), fill=q.TINTA, anchor="mm")
        if k < 2:
            q.seta(d, (x + 530, 470), (x + 590, 470), cor=M)
    d.text((110, 700), "Prefeito envia → Câmara analisa e vota", font=q.BD(40), fill=q.TINTA)
    q.icone(d, "megafone", 160, 830, 100, M)
    d.text((240, 830), "Audiências públicas: dá para opinar antes da votação (LRF)", font=q.BD(36), fill=q.TINTA, anchor="lm")
    return img


def c13():
    img, d = novo()
    q.titulo(d, "Quem confere as contas do prefeito", 150)
    nos = ((230, "prefeitura", "Prefeito presta contas", M), (730, "balanca", "Tribunal de Contas: parecer prévio", E),
           (1280, "camara", "Câmara julga", M))
    for k, (x, ic, t, c) in enumerate(nos):
        q.selo_icone(img, ic, x, 470, 110, c)
        for j, l in enumerate(q.vl.wrap(d, t, q.BD(34), 400)):
            d.text((x, 620 + j * 44), l, font=q.BD(34), fill=q.TINTA, anchor="mm")
        if k < 2:
            q.seta(d, (x + 130, 470), (nos[k + 1][0] - 130, 470), cor=q.CINZA)
    d.rounded_rectangle([1530, 380, 1820, 560], radius=20, fill=q.claro(M, 0.8))
    d.text((1675, 440), "2/3", font=q.BK(80), fill=M, anchor="mm")
    d.text((1675, 515), "para derrubar o parecer", font=q.RG(24), fill=q.TINTA, anchor="mm")
    q.cartao(d, 120, 790, 1800, 900, cor=q.VERDE, w=4)
    q.icone(d, "pessoa", 190, 845, 80, q.VERDE)
    d.text((260, 845), "Contas abertas a qualquer contribuinte por 60 dias por ano (CF, art. 31)", font=q.BD(34), fill=q.TINTA, anchor="lm")
    return img


def c14():
    img, d = novo()
    q.titulo(d, "De onde vem o dinheiro: receitas próprias", 150)
    q.icone(d, "cofre", 960, 600, 260, M)
    fontes = (("casa", "IPTU", "imóveis urbanos"), ("documento", "ITBI", "compra e venda de imóvel"),
              ("celular", "ISS", "serviços"), ("carimbo", "TAXAS", "serviço ou fiscalização"),
              ("poste_aceso", "CIP", "iluminação pública"))
    pos = ((300, 340), (300, 620), (300, 880), (1620, 400), (1620, 760))
    for (ic, s, t), (x, y) in zip(fontes, pos):
        q.selo_icone(img, ic, x, y, 70, M)
        d.text((x + 90 if x < 960 else x - 90, y - 20), s, font=q.BK(40), fill=M, anchor="lm" if x < 960 else "rm")
        d.text((x + 90 if x < 960 else x - 90, y + 25), t, font=q.RG(28), fill=q.TINTA, anchor="lm" if x < 960 else "rm")
        q.seta(d, (x + (80 if x < 960 else -80), y), (960 + (-140 if x < 960 else 140), 600), cor=q.claro(M, 0.4), w=4, tracejada=True)
    d.text((960, 960), "Cada cobrança depende de lei municipal", font=q.BD(32), fill=q.TINTA, anchor="mm")
    return img


def c15():
    img, d = novo()
    q.titulo(d, "Transferências: o dinheiro que chega de fora", 150)
    q.selo_icone(img, "prefeitura", 960, 800, 110, M)
    d.text((960, 950), "COFRE DO MUNICÍPIO", font=q.BK(34), fill=M, anchor="mm")
    q.selo_icone(img, "prefeitura", 420, 380, 90, E)
    d.text((420, 500), "ESTADO", font=q.BK(36), fill=E, anchor="mm")
    d.text((420, 545), "25% do ICMS · 50% do IPVA", font=q.BD(30), fill=q.TINTA, anchor="mm")
    q.selo_icone(img, "prefeitura", 1500, 380, 90, U)
    d.text((1500, 500), "UNIÃO", font=q.BK(36), fill=U, anchor="mm")
    d.text((1500, 545), "FPM (parte do IR e do IPI)", font=q.BD(30), fill=q.TINTA, anchor="mm")
    q.seta(d, (500, 590), (860, 760), cor=E, w=8)
    q.seta(d, (1420, 590), (1060, 760), cor=U, w=8)
    for k, (t, ic) in enumerate((("SUS → saúde", "ubs"), ("FUNDEB → educação", "escola"))):
        x = 100 + k * 1240
        q.cartao(d, x, 820, x + 480, 920, cor=q.VERDE, w=3)
        q.icone(d, ic, x + 55, 870, 60, q.VERDE)
        d.text((x + 100, 870), t, font=q.BD(30), fill=q.TINTA, anchor="lm")
    return img


def c16():
    img, d = novo()
    q.titulo(d, "Reforma tributária: o ISS vai dar lugar ao IBS", 150)
    d.text((70, 250), "Emenda Constitucional 132/2023", font=q.RG(34), fill=q.TINTA)
    anos = (("2028", 100), ("2029", 90), ("2030", 80), ("2031", 70), ("2032", 60), ("2033", 0))
    for k, (a, p) in enumerate(anos):
        x = 160 + k * 280
        h = int(4.2 * p)
        d.rounded_rectangle([x, 760 - h, x + 120, 760], radius=10, fill=M if p else q.CINZA_CL)
        hi = int(4.2 * (100 - p))
        if hi:
            d.rounded_rectangle([x + 140, 760 - hi, x + 200, 760], radius=10, fill=E)
        d.text((x + 100, 800), a, font=q.BK(38), fill=q.TINTA, anchor="mm")
        d.text((x + 60, 740 - h), f"{p}%" if p else "fim", font=q.BD(30), fill=M if p else q.CINZA, anchor="mb")
    d.line([(120, 760), (1820, 760)], fill=q.TINTA, width=4)
    d.rounded_rectangle([1080, 250, 1120, 290], radius=6, fill=M)
    d.text((1135, 270), "ISS (alíquota vigente)", font=q.RG(28), fill=q.TINTA, anchor="lm")
    d.rounded_rectangle([1450, 250, 1490, 290], radius=6, fill=E)
    d.text((1505, 270), "IBS (estados + municípios)", font=q.RG(28), fill=q.TINTA, anchor="lm")
    d.text((960, 880), "Ilustrativo: o IBS cresce enquanto o ISS cai; a partilha segue em transição até 2077", font=q.RG(30), fill=q.CINZA, anchor="mm")
    return img


def c17():
    img, d = novo()
    q.titulo(d, "Como pedir do jeito certo", 150)
    passos = (("celular", "Canal oficial", "site, app, 156 onde existir, presencial"), ("carimbo", "Anote o protocolo", "o número que prova o pedido"),
              ("megafone", "Ouvidoria", "30 dias + 30 (Lei 13.460/2017)"), ("camara", "Vereador", "indicação ou requerimento"))
    for k, (ic, t, s) in enumerate(passos):
        x, y = 120 + k * 430, 780 - k * 140
        d.rounded_rectangle([x, y, x + 400, 920], radius=18, fill=q.claro(M, 0.85 - k * 0.15))
        q.selo_icone(img, ic, x + 70, y + 70, 50, M)
        d.text((x + 140, y + 50), f"{k + 1}. {t}", font=q.BK(27), fill=q.TINTA, anchor="lm")
        for j, l in enumerate(q.vl.wrap(d, s, q.RG(26), 250)):
            d.text((x + 140, y + 92 + j * 32), l, font=q.RG(26), fill=q.TINTA, anchor="lm")
    return img


def c18():
    img, d = novo()
    q.titulo(d, "Siga o dinheiro: portal da transparência", 150)
    q.cartao(d, 100, 280, 1500, 900, cor=q.CINZA, w=3)
    d.rectangle([100, 280, 1500, 340], fill=q.CINZA_CL)
    d.rounded_rectangle([200, 296, 1100, 326], radius=14, fill=q.BRANCO)
    d.text((220, 311), "site oficial da prefeitura / transparência", font=q.RG(22), fill=q.CINZA, anchor="lm")
    cols = ("Data", "Favorecido", "Valor", "Processo", "Licitação")
    for j, c in enumerate(cols):
        d.text((150 + j * 270, 390), c, font=q.BD(28), fill=q.TINTA)
    for i in range(6):
        y = 450 + i * 70
        d.line([(130, y - 12), (1470, y - 12)], fill=q.CINZA_CL, width=2)
        for j in range(5):
            d.rounded_rectangle([150 + j * 270, y, 150 + j * 270 + 200, y + 26], radius=8, fill=q.CINZA_CL)
    q.icone(d, "lupa_icone", 1100, 600, 260, M)
    d.text((1580, 420), "Câmara:", font=q.BK(36), fill=M)
    for k, t in enumerate(("projetos", "votações", "indicações")):
        d.text((1580, 480 + k * 50), "• " + t, font=q.BD(32), fill=q.TINTA)
    d.text((960, 960), "Irregularidade? Tribunal de Contas e Ministério Público (LRF, art. 73-A)", font=q.BD(32), fill=q.TINTA, anchor="mm")
    return img


def c19():
    img, d = novo()
    q.titulo(d, "Teste rápido: de quem é?", 150, tam=72)
    casos = (("torre", "A luz acabou em todas as casas da rua"), ("berco", "Sem vaga na creche para criança de 3 anos"),
             ("rodovia", "Buraco em rodovia estadual dentro da cidade"))
    for k, (ic, t) in enumerate(casos):
        y = 300 + k * 190
        q.cartao(d, 100, y, 1500, y + 160, cor=q.TINTA, w=3)
        d.text((170, y + 80), str(k + 1), font=q.BK(70), fill=q.VERDE, anchor="mm")
        q.icone(d, ic, 300, y + 80, 100, q.TINTA)
        d.text((380, y + 80), t, font=q.BD(40), fill=q.TINTA, anchor="lm")
        d.text((1440, y + 80), "?", font=q.BK(90), fill=q.CINZA, anchor="mm")
    d.text((800, 920), "Responda nos comentários · respostas no Ep. 2", font=q.BK(40), fill=q.VERDE, anchor="mm")
    q.lupa(img, "pensando", 400, x=1500, y=560)
    return img


def c20():
    img = Image.new("RGB", (q.W, q.H), q.VERDE)
    d = ImageDraw.Draw(img)
    for k, (t, c) in enumerate((("PREFEITURA EXECUTA", M), ("CÂMARA LEGISLA E FISCALIZA", M), ("VOCÊ ACOMPANHA", q.LIMA))):
        q.chip(d, 120, 160 + k * 110, t, c, fonte=q.BK(44), alt=88, pad=40)
    q.mapa_brasil(d, 1150, 120, 560, 560, q.claro(U, 0.6))
    d.ellipse([1150 + 0.62 * 560 - 70, 120 + 0.62 * 560 - 70, 1150 + 0.62 * 560 + 70, 120 + 0.62 * 560 + 70], fill=E)
    d.text((1430, 720), "Próximo: Ep. 2 · ESTADO", font=q.BK(48), fill=q.BRANCO, anchor="mm")
    d.text((1430, 780), "polícia · ensino médio · hospital estadual", font=q.RG(34), fill=q.LIMA, anchor="mm")
    d.text((120, 620), "Comente um problema real da sua cidade", font=q.BD(40), fill=q.BRANCO)
    d.text((120, 670), "(sem citar nomes de pessoas)", font=q.RG(34), fill=q.LIMA)
    d.text((120, 800), "www.legiscopio.com.br · apoia.se/legiscopio", font=q.BK(44), fill=q.BRANCO)
    lg = q.vl.logo(90)
    if lg:
        box = Image.new("RGB", (lg.width + 40, lg.height + 30), q.BRANCO)
        img.paste(box, (120, 900))
        img.paste(lg, (140, 915), lg)
    return img


FUNCS = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20]
CUES = {}


def _fab(f, i):
    def criar():
        import qfq_render
        return qfq_render.Cena(f, sys.modules[__name__], CUES.get(i))
    return criar


CENAS = [_fab(f, i) for i, f in enumerate(FUNCS)]

SHORT = {
    "selo": "Episódio 1 · Município",
    "cenas": [
        {"cena": 1, "narracao": "O poste da sua rua apagou. De quem é a responsabilidade?"},
        {"cena": 10, "narracao": "Se a lâmpada do poste apagou, mas as casas têm energia, é iluminação pública: em regra, da prefeitura. Se a luz acabou na rua inteira, o caso é com a distribuidora de energia."},
        {"cena": 7, "narracao": "E o vereador? Ele não conserta poste nem faz obra. Vereador faz leis, vota o orçamento e fiscaliza o prefeito, com o auxílio do Tribunal de Contas. Ele pode cobrar a prefeitura, mas quem executa é o Executivo."},
        {"cena": 17, "narracao": "O caminho, então: registre o pedido no canal oficial da prefeitura e guarde o número do protocolo. Sem solução? Procure a ouvidoria, que tem trinta dias, prorrogáveis uma vez, para enviar a decisão final."},
        {"cena": 18, "narracao": "E acompanhe os gastos no portal da transparência, no site oficial da prefeitura."},
        {"cena": 2, "narracao": "Quem faz o quê na sua cidade? O episódio completo está no canal."},
    ],
}

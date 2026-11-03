"""Episódio 4 da série "Quem Faz o Quê?" (Como nasce uma lei): quadros-chave usados pelo qfq_render."""
from pathlib import Path as _P

exec(compile(_P(__file__).with_name("qfq_base_ep.py").read_text(encoding="utf-8"), "qfq_base_ep.py", "exec"))
# os layouts (g_*) leem EPN/EPNOME/COR deste módulo na hora de desenhar

EPN, EPNOME, COR = 4, "Como nasce uma lei", V

FUNCS = [
    lambda: g_gancho("Como um papel com número vira lei?", "PL 1234/2026", "documento", V),
    g_abertura,
    lambda: g_respostas("Respostas do teste do episódio 3", (
        ("pessoa", "Aposentadoria do INSS atrasou", "União: o INSS é uma autarquia federal", U),
        ("escola", "Falta vaga no ensino médio público", "Estado: prioridade no ensino médio", E),
        ("lixo", "O lixo não foi recolhido", "Município: serviço de interesse local", M))),
    lambda: g_linhas("As siglas das propostas", None, (
        ("documento", "PL", "projeto de lei ordinária: o mais comum", None, V),
        ("documento", "PLP", "lei complementar: exige maioria absoluta", None, V),
        ("documento", "PEC", "proposta de emenda à Constituição", None, V),
        ("prefeitura", "MP", "medida provisória, editada pelo Presidente", None, U),
        ("camara", "PDL", "decreto legislativo: assuntos só do Congresso", None, V))),
    lambda: g_selos("Quem pode propor um projeto de lei", "CF, art. 61",
                    (("camara", "PARLAMENTARES", "deputados, senadores e comissões", V), ("prefeitura", "PRESIDENTE", "da República", U),
                     ("balanca", "TRIBUNAIS E PGR", "STF, tribunais superiores e PGR, nos casos previstos", V), ("pessoa", "CIDADÃOS", "iniciativa popular", M)),
                    nota="Iniciativa popular: 1% do eleitorado, em pelo menos 5 estados, com 0,3% em cada um"),
    lambda: g_fluxo("Casa iniciadora e Casa revisora", "Uma lei federal precisa passar pelas duas",
                    (("camara", "Câmara: projetos de deputados, do Presidente, dos tribunais e populares", V),
                     ("camara", "Senado: projetos de senadores", V)),
                    nota="A Casa onde começa é a iniciadora; a outra é a revisora"),
    lambda: g_lista("Nas comissões", None,
                    ("Comissões temáticas: Saúde, Educação, Finanças...", "Um relator estuda o texto e apresenta parecer",
                     "A CCJ confere se respeita a Constituição", "Muitas vezes a comissão decide sem o Plenário (salvo recurso de 1/10 da Casa)"),
                    icone="documento"),
    lambda: g_selos("Quando o projeto anda mais rápido", None,
                    (("megafone", "URGÊNCIA REGIMENTAL", "aprovada pelos parlamentares: vai direto ao Plenário", V),
                     ("prefeitura", "URGÊNCIA CONSTITUCIONAL", "pedida pelo Presidente: 45 dias em cada Casa", U),
                     ("x", "PAUTA TRANCADA", "se o prazo vencer, as outras votações param (com exceções)", q.CINZA))),
    lambda: g_numeros("Votação no Plenário", "Simbólica ou nominal (no painel, com o voto de cada um registrado)",
                      (("maioria", "dos presentes: lei ordinária (com maioria absoluta na sessão)", V), ("257", "deputados: lei complementar", V),
                       ("41", "senadores: lei complementar", V))),
    lambda: g_fluxo("Na Casa revisora", None,
                    (("check", "Aprovou igual: vai ao Presidente", V), ("x", "Rejeitou: arquivado", q.CINZA),
                     ("documento", "Mudou: volta à iniciadora, que decide só as mudanças", V))),
    lambda: g_selos("Sanção ou veto", "15 dias úteis · CF, art. 66",
                    (("check", "SANÇÃO", "concorda e o projeto vira lei", V), ("carimbo", "SANÇÃO TÁCITA", "se o Presidente ficar em silêncio", V),
                     ("x", "VETO", "total ou parcial: inconstitucional ou contra o interesse público", U))),
    lambda: g_numeros("Derrubar o veto", "Sessão conjunta do Congresso",
                      (("257", "deputados (maioria absoluta)", V), ("41", "senadores (maioria absoluta)", V)),
                      nota="Se o veto cair, o trecho vetado vira lei"),
    g_cta,
    lambda: g_fluxo("Quando a lei começa a valer", None,
                    (("carimbo", "Promulgação", V), ("documento", "Publicação no Diário Oficial", V), ("check", "Vigência", V)),
                    nota="Se a lei não disser, vale 45 dias depois de publicada"),
    lambda: g_numeros("O caminho da PEC", "2 turnos em cada Casa · sem sanção: promulgada pelas Mesas",
                      (("308", "deputados (3/5)", V), ("49", "senadores (3/5)", V)),
                      nota="Cláusulas pétreas: federação, voto, separação dos Poderes, direitos individuais"),
    lambda: g_numeros("Medida provisória", "Vale na hora · relevância e urgência",
                      (("60+60", "dias para o Congresso votar", U), ("45", "dias: depois disso, tranca a pauta", U), ("0", "se não votar: perde a validade", q.CINZA)),
                      nota="Aprovada, vira lei de conversão"),
    lambda: g_lista("Por que alguns projetos ficam parados", None,
                    ("Não há prazo geral para votar um projeto", "Presidentes das Casas e das comissões, com os líderes, definem a pauta",
                     "Muitos projetos podem ser arquivados ao fim da legislatura (4 anos)"), icone="carimbo", cor=q.CINZA),
    lambda: g_selos("Como participar", None,
                    (("celular", "e-CIDADANIA (SENADO)", "ideia com 20 mil apoios em 4 meses vai a uma comissão", V),
                     ("pessoa", "LEGISLAÇÃO PARTICIPATIVA (CÂMARA)", "sugestões de entidades da sociedade civil", V),
                     ("megafone", "AUDIÊNCIAS E CONSULTAS", "sobre projetos em discussão", V))),
    lambda: g_lista("Acompanhe a tramitação", None,
                    ("Ficha de tramitação nos sites da Câmara e do Senado", "No app do Legiscópio: favorite a proposição",
                     "Receba notificação quando ela mudar de situação", "Veja como cada parlamentar votou nas votações nominais"), icone="celular"),
    lambda: g_teste((("documento", "PEC aprovada precisa de sanção?"), ("x", "O Congresso pode derrubar um veto?"),
                     ("pessoa", "Cidadãos podem apresentar projeto de lei?")), "Responda nos comentários · respostas no Ep. 5"),
    lambda: g_fim(("COMISSÕES + PLENÁRIO", "SANÇÃO OU VETO", "PEC: 3/5 · MP: VALE NA HORA"),
                  "Próximo: Ep. 5 · QUEM FISCALIZA QUEM", "último episódio da série", "Qual projeto você quer acompanhar?", "conte nos comentários"),
]

CENAS = [_fab(f, i) for i, f in enumerate(FUNCS)]

SHORT = {
    "selo": "Episódio 4 · Como nasce uma lei",
    "cenas": [
        {"cena": 1, "narracao": "Como um papel com número vira lei?"},
        {"cena": 7, "narracao": "Primeiro, o projeto passa pelas comissões, onde um relator dá parecer. Depois, vai ao Plenário."},
        {"cena": 10, "narracao": "Aprovado numa Casa, vai para a outra. Se ela mudar o texto, ele volta para a primeira, que dá a palavra final."},
        {"cena": 11, "narracao": "Aí o Presidente sanciona ou veta. E o Congresso pode derrubar o veto, com a maioria absoluta de deputados e de senadores."},
        {"cena": 2, "narracao": "Quer entender a PEC e a medida provisória? O episódio completo está no canal."},
    ],
}


def miniatura():
    return g_miniatura("VIROU LEI?", "Da ideia à sanção", "documento", (170, 230, 190))

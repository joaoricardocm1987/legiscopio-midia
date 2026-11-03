"""Episódio 5 da série "Quem Faz o Quê?" (Quem fiscaliza): quadros-chave usados pelo qfq_render."""
from pathlib import Path as _P

exec(compile(_P(__file__).with_name("qfq_base_ep.py").read_text(encoding="utf-8"), "qfq_base_ep.py", "exec"))
# os layouts (g_*) leem EPN/EPNOME/COR deste módulo na hora de desenhar

EPN, EPNOME, COR = 5, "Quem fiscaliza", V

FUNCS = [
    lambda: g_gancho("Obra pela metade, paga inteira. Quem descobre?", "QUEM FISCALIZA?", "lupa_icone", V),
    g_abertura,
    lambda: g_respostas("Respostas do teste do episódio 4", (
        ("documento", "PEC aprovada precisa de sanção?", "Não: é promulgada pelas Mesas da Câmara e do Senado", V),
        ("x", "O Congresso pode derrubar um veto?", "Sim: maioria absoluta de deputados e de senadores", V),
        ("pessoa", "Cidadãos podem apresentar projeto?", "Sim: iniciativa popular, com 1% do eleitorado", V))),
    lambda: g_selos("Freios e contrapesos", "CF, art. 2º: Poderes independentes e harmônicos",
                    (("prefeitura", "EXECUTIVO", "veta leis · indica ministros do STF", U), ("camara", "LEGISLATIVO", "derruba vetos · aprova indicações no Senado", V),
                     ("balanca", "JUDICIÁRIO", "declara leis inconstitucionais", U))),
    lambda: g_fluxo("Controle externo", "O Legislativo fiscaliza, com o auxílio dos Tribunais de Contas",
                    (("camara", "Congresso, Assembleias e Câmaras Municipais", V), ("balanca", "TCU, TCEs e, em alguns lugares, TCMs", V)),
                    nota="Tribunais de Contas não fazem parte do Judiciário"),
    lambda: g_lista("O que fazem os Tribunais de Contas", None,
                    ("Auditam obras, contratos e licitações", "Julgam as contas de quem administra dinheiro público",
                     "Aplicam multas e mandam devolver valores", "Contas rejeitadas podem levar à inelegibilidade (Ficha Limpa)"), icone="balanca"),
    lambda: g_selos("Controle interno", "Dentro do próprio Executivo",
                    (("lupa_icone", "CGU", "Controladoria-Geral da União", U), ("lupa_icone", "CONTROLADORIAS", "dos estados e de muitos municípios", E),
                     ("documento", "AUDITORIAS", "e aviso ao Tribunal de Contas", V))),
    lambda: g_lista("Ministério Público", "Não pertence a nenhum dos três Poderes · CF, arts. 127 e 129",
                    ("Defende o patrimônio público e a ordem jurídica", "Inquérito civil e ação civil pública",
                     "Ação de improbidade administrativa", "Denúncia criminal à Justiça"), icone="megafone"),
    lambda: g_linhas("Polícia investiga, Justiça julga", "Foro por prerrogativa de função, nos crimes comuns", (
        ("balanca", "DEPUTADOS FEDERAIS E SENADORES", "julgados pelo Supremo Tribunal Federal", "STF", U),
        ("balanca", "GOVERNADORES", "julgados pelo Superior Tribunal de Justiça", "STJ", E),
        ("balanca", "PREFEITOS", "julgados pelo Tribunal de Justiça do estado", "TJ", M))),
    lambda: g_numeros("Impeachment do Presidente", "Crime de responsabilidade · julgamento presidido pelo presidente do STF",
                      (("342", "deputados (2/3) para autorizar o processo", V), ("54", "senadores (2/3) para condenar", V)),
                      nota="Governadores e prefeitos também respondem, com regras próprias"),
    lambda: g_lista("Cassação de mandato", None,
                    ("Por exemplo, por quebra de decoro parlamentar", "Quem decide é a própria Casa",
                     "Maioria absoluta, em votação aberta", "Antes, o caso costuma passar pelo Conselho de Ética"), icone="camara"),
    lambda: g_selos("Justiça Eleitoral", None,
                    (("urna", "ELEIÇÕES", "organiza e fiscaliza", V), ("cofre", "CONTAS DE CAMPANHA", "analisa as prestações de contas", V),
                     ("x", "CASSAÇÃO", "por abuso de poder ou compra de votos", V))),
    g_cta,
    lambda: g_selos("Transparência", None,
                    (("cofre", "LRF", "receitas e despesas em tempo real", V), ("documento", "LEI DE ACESSO", "qualquer pessoa pede dados, sem explicar o motivo", V),
                     ("megafone", "IMPRENSA LIVRE", "protegida pela Constituição", V))),
    lambda: g_selos("Controle social", "A própria população fiscaliza",
                    (("ubs", "CONSELHOS", "de saúde: metade das vagas é dos usuários", V), ("megafone", "AUDIÊNCIAS PÚBLICAS", "dá para opinar e perguntar", V),
                     ("cofre", "ORÇAMENTO PARTICIPATIVO", "em algumas cidades", V))),
    lambda: g_lista("Como denunciar", None,
                    ("Ouvidoria do órgão", "Tribunal de Contas: qualquer cidadão pode denunciar (CF, art. 74)",
                     "Ministério Público", "Ação popular: anula ato que lesa o patrimônio público, em regra sem custas"), icone="megafone"),
    lambda: g_lista("O seu voto também fiscaliza", None,
                    ("Acompanhe o mandato inteiro, não só a campanha", "Votações", "Projetos apresentados", "Gastos"), icone="urna"),
    lambda: g_linhas("A série em um quadro", None, (
        ("prefeitura", "MUNICÍPIO", "limpeza urbana, iluminação, educação infantil, atenção básica", None, M),
        ("prefeitura", "ESTADO", "policiamento, ensino médio, hospitais de referência, rodovias estaduais", None, E),
        ("prefeitura", "UNIÃO", "moeda, defesa, Previdência, concessões nacionais, leis nacionais", None, U)),
        nota="Em todos os níveis: quem executa presta contas a quem fiscaliza"),
    lambda: g_lista("Acompanhe com o Legiscópio", "Dados oficiais do Congresso no celular",
                    ("Votações e como cada parlamentar votou", "Gastos da cota parlamentar", "Propostas em tramitação",
                     "Favoritos com notificações"), icone="celular"),
    lambda: g_lista("Sua vez", None,
                    ("Qual tema você quer numa próxima série?", "Conte nos comentários",
                     "Compartilhe com quem também quer entender quem faz o quê"), icone="pessoa"),
    lambda: g_fim(("FREIOS E CONTRAPESOS", "TRIBUNAIS DE CONTAS · MP · JUSTIÇA", "VOCÊ TAMBÉM FISCALIZA"),
                  "Obrigado por acompanhar a série!", "Quem Faz o Quê? · Legiscópio", "Qual tema você quer na próxima série?", "conte nos comentários"),
]

CENAS = [_fab(f, i) for i, f in enumerate(FUNCS)]

SHORT = {
    "selo": "Episódio 5 · Quem fiscaliza",
    "cenas": [
        {"cena": 1, "narracao": "Uma obra pública ficou pela metade, mas foi paga inteira. Quem descobre?"},
        {"cena": 6, "narracao": "Os Tribunais de Contas auditam obras e contratos, julgam as contas de quem gasta dinheiro público e podem mandar devolver valores."},
        {"cena": 8, "narracao": "O Ministério Público pode propor ações de improbidade e apresentar denúncia criminal à Justiça."},
        {"cena": 16, "narracao": "E você pode denunciar à ouvidoria, ao Tribunal de Contas ou ao Ministério Público."},
        {"cena": 2, "narracao": "Quem fiscaliza quem? O episódio completo está no canal."},
    ],
}


def miniatura():
    return g_miniatura("QUEM FISCALIZA?", "Tribunais, MP e você", "lupa_icone", (170, 230, 190))

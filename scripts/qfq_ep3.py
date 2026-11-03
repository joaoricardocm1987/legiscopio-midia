"""Episódio 3 da série "Quem Faz o Quê?" (União): quadros-chave usados pelo qfq_render."""
from pathlib import Path as _P

exec(compile(_P(__file__).with_name("qfq_base_ep.py").read_text(encoding="utf-8"), "qfq_base_ep.py", "exec"))
# os layouts (g_*) leem EPN/EPNOME/COR deste módulo na hora de desenhar

EPN, EPNOME, COR = 3, "União", U

FUNCS = [
    lambda: g_gancho("Quem emite o seu passaporte?", "POLÍCIA FEDERAL", "documento", U),
    g_abertura,
    lambda: g_respostas("Respostas do teste do episódio 2", (
        ("documento", "Tirar ou renovar o passaporte", "União: Polícia Federal", U),
        ("viatura", "Primeira carteira de motorista", "Estado: Detran", E),
        ("rodovia", "Rodovia federal com buracos", "União: DNIT, ou concessionária fiscalizada pela ANTT", U))),
    lambda: g_selos("A União tem os três Poderes federais", "Representa o país como um todo · CF, arts. 21 e 22",
                    (("prefeitura", "EXECUTIVO", "Presidente e ministérios", U), ("camara", "LEGISLATIVO", "Congresso Nacional", U),
                     ("balanca", "JUDICIÁRIO", "STF, tribunais superiores e Justiça Federal", U)),
                    nota="Só a União faz leis de trânsito, por isso o Código vale no país todo"),
    lambda: g_lista("Quem governa: o Presidente da República", "Chefe de Estado e chefe de governo",
                    ("Eleito com o vice, a cada 4 anos", "2º turno se ninguém passar de 50% dos votos válidos",
                     "Pode ser reeleito uma vez para o mandato seguinte", "Nomeia os ministros de Estado"), icone="urna"),
    lambda: g_numeros("Congresso Nacional: duas Casas", "Câmara dos Deputados + Senado Federal",
                      (("513", "deputados federais · mandato de 4 anos", U), ("8 a 70", "deputados por estado, conforme a população", U),
                       ("81", "senadores · 3 por estado e 3 pelo DF", U), ("8 anos", "mandato de senador · renova 1/3 e 2/3", U))),
    lambda: g_linhas("Judiciário e órgãos federais", None, (
        ("balanca", "SUPREMO TRIBUNAL FEDERAL", "11 ministros · guarda da Constituição", "STF", U),
        ("balanca", "SUPERIOR TRIBUNAL DE JUSTIÇA", "uniformiza a interpretação das leis federais", "STJ", U),
        ("documento", "JUSTIÇA FEDERAL E ESPECIALIZADAS", "Trabalho, Eleitoral e Militar", None, U),
        ("lupa_icone", "MPU · DPU · TCU", "Ministério Público, Defensoria e Tribunal de Contas da União", None, U))),
    lambda: g_selos("O que só a União faz", "CF, art. 21",
                    (("pessoa", "RELAÇÕES EXTERIORES", "e defesa nacional", U), ("moeda", "MOEDA", "emitida pelo Banco Central", U),
                     ("documento", "CORREIOS", "serviço postal", U), ("torre", "CONCESSÕES", "energia, telecom, aviação", U)),
                    nota="A distribuidora de energia da sua cidade atua por concessão da União"),
    lambda: g_linhas("Agências reguladoras federais", "Fiscalizam as empresas que prestam serviços concedidos", (
        ("torre", "ANEEL", "energia elétrica", None, U), ("celular", "ANATEL", "telecomunicações", None, U),
        ("rodovia", "ANAC · ANTT", "aviação civil · transportes terrestres", None, U),
        ("ubs", "ANVISA · ANS", "vigilância sanitária · planos de saúde", None, U)),
        nota="A empresa não resolveu? A agência é o próximo passo"),
    lambda: g_selos("Previdência e assistência", "Regime Geral de Previdência Social",
                    (("pessoa", "INSS", "aposentadorias, pensões e auxílios", U), ("documento", "BPC", "benefício da assistência, operado pelo INSS", U),
                     ("casa", "TRANSFERÊNCIA DE RENDA", "programas federais, com cadastro feito nos municípios", U))),
    lambda: g_selos("Saúde e educação: o papel da União", None,
                    (("ubs", "MINISTÉRIO DA SAÚDE", "coordena o SUS e repassa recursos", U), ("escola", "UNIVERSIDADES E INSTITUTOS FEDERAIS", "ensino superior e técnico", U),
                     ("cofre", "AJUDA A ESTADOS E CIDADES", "função redistributiva e complementação ao FUNDEB", U))),
    lambda: g_selos("Estradas, portos e aeroportos", None,
                    (("rodovia", "RODOVIAS FEDERAIS", "DNIT ou concessionária (ANTT)", U), ("viatura", "PRF", "patrulha as rodovias federais", U),
                     ("onibus", "PORTOS E AEROPORTOS", "direto ou por concessão", U))),
    g_cta,
    lambda: g_linhas("De onde vem o dinheiro da União", "CF, arts. 153 e 195", (
        ("cofre", "IMPOSTO DE RENDA", "pessoas e empresas", None, U), ("documento", "IPI · IOF · IMPORTAÇÃO E EXPORTAÇÃO", "produtos industrializados, operações financeiras e comércio exterior", None, U),
        ("casa", "ITR", "propriedades rurais", None, U), ("ubs", "CONTRIBUIÇÕES SOCIAIS", "INSS, PIS e Cofins financiam a seguridade social", None, U))),
    lambda: g_fluxo("Fundos de participação", "Parte do IR e do IPI vai para estados e municípios",
                    (("cofre", "IR + IPI arrecadados pela União", U), ("prefeitura", "FPE: estados", E), ("prefeitura", "FPM: municípios", M)),
                    nota="Ajuda quem arrecada menos (vimos nos episódios 1 e 2)"),
    lambda: g_linhas("Reforma tributária: tributos federais", "Emenda Constitucional 132/2023", (
        ("documento", "CBS", "substitui o PIS e a Cofins a partir de 2027", "2027", U),
        ("cofre", "IVA DUAL", "CBS (União) + IBS (estados e municípios)", None, U),
        ("documento", "IPI", "alíquotas zeradas, exceto produtos com industrialização na Zona Franca de Manaus", None, U),
        ("x", "IMPOSTO SELETIVO", "sobre bens e serviços prejudiciais à saúde ou ao meio ambiente", None, U))),
    lambda: g_fluxo("Orçamento federal", "PPA · LDO · LOA",
                    (("prefeitura", "Presidente envia", U), ("camara", "Comissão Mista de Orçamento", U), ("camara", "Congresso vota", U)),
                    nota="Emendas de deputados e senadores: parte tem execução obrigatória"),
    lambda: g_fluxo("Quem fiscaliza a União", None,
                    (("prefeitura", "Presidente presta contas", U), ("balanca", "TCU: parecer prévio", U), ("camara", "Congresso julga", U)),
                    nota="CGU faz o controle interno · CPI: 1/3 da Casa, fato determinado e prazo certo"),
    lambda: g_lista("Como cobrar a União", None,
                    ("Reclamação: ouvidoria pela plataforma Fala.BR (30 + 30 dias)",
                     "Pedido de informação: Lei de Acesso à Informação (20 + 10 dias)",
                     "Gastos: Portal da Transparência do governo federal",
                     "Votos e projetos de deputados e senadores: app do Legiscópio"), icone="megafone"),
    lambda: g_teste((("pessoa", "Aposentadoria do INSS atrasou"), ("escola", "Falta vaga no ensino médio público"),
                     ("lixo", "O caminhão de lixo não passou na sua rua")), "Responda nos comentários · respostas no Ep. 4"),
    lambda: g_fim(("MOEDA · DEFESA · PREVIDÊNCIA", "LEIS NACIONAIS", "REPARTE COM ESTADOS E CIDADES"),
                  "Próximo: Ep. 4 · COMO NASCE UMA LEI", "da ideia à sanção", "Qual episódio mais te ajudou?", "conte nos comentários"),
]

CENAS = [_fab(f, i) for i, f in enumerate(FUNCS)]

SHORT = {
    "selo": "Episódio 3 · União",
    "cenas": [
        {"cena": 1, "narracao": "Quem emite o seu passaporte? Não é a prefeitura nem o estado: é a Polícia Federal, da União."},
        {"cena": 8, "narracao": "Só a União cuida das relações com outros países, da defesa e da moeda, emitida pelo Banco Central. E concede serviços como energia elétrica e telecomunicações."},
        {"cena": 9, "narracao": "Por isso existem as agências reguladoras federais, como a ANEEL e a ANATEL. Se a empresa não resolver, a agência é o próximo passo."},
        {"cena": 10, "narracao": "A Previdência também é federal: o INSS paga aposentadorias, pensões e auxílios."},
        {"cena": 2, "narracao": "Quem faz o quê no Brasil? O episódio completo está no canal."},
    ],
}


def miniatura():
    return g_miniatura("PASSAPORTE?", "O que é da União", "documento", (200, 185, 240))

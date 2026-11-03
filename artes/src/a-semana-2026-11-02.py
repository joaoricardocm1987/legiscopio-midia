# Único (apaga a si mesmo): ajusta o gerador da agenda (tira recursos REC da pauta e as sessões do Senado que não são
# de votação) e gera o carrossel desta semana (2 a 6/11/2026) com resumos em posts/2026-11-03/semana/.
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "scripts" / "agenda.py"
s = p.read_text(encoding="utf-8")
TROCAS = [
    ('FORA_PAUTA = {"REQ", "RIC", "INC", "RQS", "RQN"}', 'FORA_PAUTA = {"REQ", "RIC", "INC", "RQS", "RQN", "REC"}'),
    ('''        if (s.get("SituacaoSessao") or "").lower().startswith("cancel"):
            continue
        mats = []''', '''        if (s.get("SituacaoSessao") or "").lower().startswith("cancel"):
            continue
        tsess = (s.get("TipoSessao") or "").lower()
        if "não deliberativa" in tsess or "especial" in tsess or "solene" in tsess:
            continue  # sessões de debates e homenagens: fora da agenda de votações
        mats = []'''),
]
for velho, novo in TROCAS:
    if velho in s:
        s = s.replace(velho, novo)
p.write_text(s, encoding="utf-8")

PASTA = ROOT / "posts" / "2026-11-03" / "semana"
PASTA.mkdir(parents=True, exist_ok=True)
RESUMOS = {
    "PL 2879/2011": "Placas de sinalização nas travessias de pedestres",
    "PL 1932/2021": "Controle em tempo real do estoque de remédios no SUS",
    "PL 3099/2019": "Cria o Dia Nacional do Autocuidado",
    "PL 2994/2020": "Regras para o turismo colaborativo",
    "PL 2726/2022": "Política de convivência sociocultural e economia solidária",
    "PL 2374/2023": "Merenda escolar (PNAE) também em escolas comunitárias",
    "PL 5902/2023": "Uso de drones sobre presídios no Código Penal",
    "PL 4674/2024": "Ultrassom morfológico na rede pública de saúde",
    "PL 2475/2025": "Maus-tratos com morte do animal como crime hediondo",
    "PL 3220/2025": "Cria o Dia Nacional da Consolidação da Independência",
    "PL 4159/2025": "Inclui Padre Inácio Rolim no Livro dos Heróis da Pátria",
    "PL 5815/2025": "Programa de acompanhamento anual da saúde de crianças",
    "PL 5542/2026": "Tornozeleira em medida protetiva da Lei Maria da Penha",
    "PL 565/2020": "Ações de educação em saúde no SUS",
    "PL 5974/2023": "Obras adaptadas para pessoas com deficiência intelectual",
    "PEC 18/2025": "PEC da Segurança Pública",
    "PL 186/2025": "Cursos e campanhas sobre parentalidade positiva",
    "PL 5782/2023": "Campanha Setembro em Flor (tumores ginecológicos)",
    "PDS 240/2011": "Acordo de cooperação em defesa Brasil–Guiana",
    "PDL 575/2026": "Acordo de cooperação espacial Brasil–Venezuela",
    "PL 6461/2019": "Cria o Estatuto do Aprendiz",
    "PL 2234/2024": "ECA: obrigatoriedade da educação básica",
    "PDL 344/2024": "Acordo de cooperação em educação Brasil–Croácia",
    "PDL 359/2024": "Protocolo sobre exposições internacionais",
    "PDL 618/2026": "Protocolo do Mercosul sobre compromisso democrático",
}
(PASTA / "agenda_resumos.json").write_text(json.dumps(RESUMOS, ensure_ascii=False, indent=1), encoding="utf-8")
try:
    sys.path.insert(0, str(ROOT / "scripts"))
    import agenda  # noqa: E402
    agenda.gerar("2026-11-02", PASTA)
except Exception:
    (PASTA / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA)], check=True, cwd=ROOT)

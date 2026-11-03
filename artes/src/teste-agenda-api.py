# Teste único (apaga a si mesmo): verifica, a partir do GitHub Actions, os endpoints de agenda da Câmara e do Senado
# e guarda amostras em videos/_teste-agenda/ para montar o gerador de stories/carrossel da agenda.
import json
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "videos" / "_teste-agenda"
OUT.mkdir(parents=True, exist_ok=True)
URLS = {
    "camara_eventos": "https://dadosabertos.camara.leg.br/api/v2/eventos?dataInicio=2026-11-03&dataFim=2026-11-07&ordem=ASC&ordenarPor=dataHoraInicio&itens=200",
    "senado_plenario_dia": "https://legis.senado.leg.br/dadosabertos/plenario/agenda/dia/20261103.json",
    "senado_plenario_mes": "https://legis.senado.leg.br/dadosabertos/plenario/agenda/mes/20261101.json",
    "senado_comissao_agenda": "https://legis.senado.leg.br/dadosabertos/comissao/agenda/20261103/20261107.json",
    "senado_comissao_agenda2": "https://legis.senado.leg.br/dadosabertos/comissao/agenda/20261103.json",
    "senado_agendareuniao": "https://legis.senado.leg.br/dadosabertos/agendareuniao/20261103.json",
}
log = []
for nome, url in URLS.items():
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "legiscopio-midia"})
        with urllib.request.urlopen(req, timeout=40) as r:
            dados = r.read()
        (OUT / f"{nome}.json").write_bytes(dados[:400000])
        log.append(f"{nome}: OK {len(dados)} bytes")
    except Exception as e:
        log.append(f"{nome}: ERRO {e!r}")
(OUT / "log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(OUT)], check=True, cwd=ROOT)

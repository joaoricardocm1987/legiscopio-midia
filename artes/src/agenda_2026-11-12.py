# Agenda do Congresso do dia (stories) e, às segundas, o carrossel da semana: posts/2026-11-12/agenda_*.png, semana_*.png
# e agenda.json (lista dos arquivos). Usa posts/2026-11-12/agenda_resumos.json se a rotina tiver escrito os resumos.
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "posts" / "2026-11-12"
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import agenda  # noqa: E402
    agenda.gerar("2026-11-12")
    (PASTA / "agenda_erro.txt").unlink(missing_ok=True)
except Exception:
    traceback.print_exc()
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / "agenda_erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
subprocess.run(["git", "add", "-A", str(PASTA)], check=True, cwd=ROOT)
# resumos: 25 itens

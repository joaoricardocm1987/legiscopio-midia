# Teste único (apaga a si mesmo): roda o gerador de agenda com dados reais em videos/_teste-agenda/real-*/
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "videos" / "_teste-agenda"
try:
    import agenda  # noqa: E402
    agenda.gerar("2026-11-04", OUT / "real-dia")
    agenda.gerar("2026-11-09", OUT / "real-semana-prox")
    agenda.gerar("2026-11-02", OUT / "real-semana-atual")
except Exception:
    (OUT / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(OUT)], check=True, cwd=ROOT)

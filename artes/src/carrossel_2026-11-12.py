# Carrossel do tema do dia: posts/2026-11-12/carrossel.json -> carrossel_1.png … carrossel_N.png
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAR = ROOT / "posts" / "2026-11-12" / "carrossel.json"
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import carrossel  # noqa: E402
    carrossel.gerar(CAR)
    (CAR.parent / "carrossel_erro.txt").unlink(missing_ok=True)
except Exception:
    traceback.print_exc()
    (CAR.parent / "carrossel_erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
subprocess.run(["git", "add", str(CAR.parent)], check=False, cwd=ROOT)

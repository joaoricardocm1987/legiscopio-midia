# Short avulso de 2026-10-23 (dia sem vídeo longo): só videos/2026-10-23/short.json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHORT = ROOT / "videos" / "2026-10-23" / "short.json"

sys.path.insert(0, str(ROOT / "scripts"))
import short_video  # noqa: E402

short_video.gerar(SHORT)
subprocess.run(["git", "add", str(SHORT.parent)], check=True, cwd=ROOT)

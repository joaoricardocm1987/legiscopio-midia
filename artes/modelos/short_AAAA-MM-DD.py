# Short avulso de AAAA-MM-DD (dia sem vídeo longo): só videos/AAAA-MM-DD/short.json
# MODELO: copie para artes/src/short_<data>.py trocando AAAA-MM-DD pela data.
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHORT = ROOT / "videos" / "AAAA-MM-DD" / "short.json"

sys.path.insert(0, str(ROOT / "scripts"))
import short_video  # noqa: E402

short_video.gerar(SHORT)
subprocess.run(["git", "add", str(SHORT.parent)], check=True, cwd=ROOT)

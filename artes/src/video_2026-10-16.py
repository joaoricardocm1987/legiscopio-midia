# Vídeo explicativo de 2026-10-16 (v2: redes sociais, site e app no final)
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "videos" / "2026-10-16" / "video.json"

sys.path.insert(0, str(ROOT / "scripts"))
import video_longo  # noqa: E402

video_longo.gerar(VIDEO)
subprocess.run(["git", "add", str(VIDEO.parent)], check=True, cwd=ROOT)

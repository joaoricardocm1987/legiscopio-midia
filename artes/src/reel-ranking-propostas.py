# Reel "Ranking das propostas" (Lupa narrando, formato das referências): videos/reel-ranking-propostas/short.json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHORT = ROOT / "videos" / "reel-ranking-propostas" / "short.json"
sys.path.insert(0, str(ROOT / "scripts"))
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "numpy", "edge-tts"], check=True)
    import short_video  # noqa: E402
    short_video.gerar(SHORT)
finally:
    subprocess.run(["git", "add", str(SHORT.parent)], check=False, cwd=ROOT)
    Path(__file__).unlink(missing_ok=True)

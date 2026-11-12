# Vídeos de 2026-11-12: explicativo longo + Short de 1 min + Resumo de 2 min (Reels/TikTok) + capítulos
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "videos" / "2026-11-12" / "video.json"

sys.path.insert(0, str(ROOT / "scripts"))
import video_longo  # noqa: E402
import short_video  # noqa: E402
import capitulos  # noqa: E402

video_longo.gerar(VIDEO)
short_video.gerar(VIDEO)
short_video.gerar(VIDEO.with_name("resumo.json"))  # Resumo de ~2 min (só se resumo.json existir)
capitulos.gerar(VIDEO)
subprocess.run(["git", "add", str(VIDEO.parent)], check=True, cwd=ROOT)

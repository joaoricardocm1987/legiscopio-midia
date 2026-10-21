# Série "Quem Faz o Quê?" — Ep. 1 (Município). Vídeo avulso, fora da rotina diária.
# Gera a narração (voz 5: Thalita, +6%, -2 Hz) com cache em videos/quem-faz-o-que/ep1/audio
# e renderiza video.mp4 + short.mp4 + legendas.srt + capitulos.txt (só quando algo mudou).
# Revisão 1: prévia para aprovação.
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "quem-faz-o-que" / "ep1"

sys.path.insert(0, str(ROOT / "scripts"))
try:
    import qfq_render  # noqa: E402
    qfq_render.gerar(PASTA, "qfq_ep1")
    (PASTA / "erro.txt").unlink(missing_ok=True)
except Exception:
    traceback.print_exc()
    (PASTA / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
subprocess.run(["git", "add", str(PASTA)], check=True, cwd=ROOT)

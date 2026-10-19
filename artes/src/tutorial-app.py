# Tutorial do app Legiscópio (vídeo avulso, fora da rotina diária).
# 1) gera/confere o cache da narração em videos/tutorial-app/audio
# 2) se as capturas estiverem em videos/tutorial-app/telas, renderiza tutorial.mp4 + short.mp4 + thumb.jpg
# Revisão 2: data de lançamento no Android (23/10/2026) e endereços escritos na legenda.
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "tutorial-app"

sys.path.insert(0, str(ROOT / "scripts"))
import tutorial_app  # noqa: E402

tutorial_app.preparar_audio(PASTA)
if len(list((PASTA / "telas").glob("*.png"))) >= 22:
    tutorial_app.gerar(PASTA)
else:
    print("capturas ainda não estão no repositório; só a narração foi preparada")
subprocess.run(["git", "add", str(PASTA)], check=True, cwd=ROOT)

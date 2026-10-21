# Série "Quem Faz o Quê?" — Ep. 1 (Município). Vídeo avulso, fora da rotina diária.
# Gera a narração (voz 5: Thalita, +6%, -2 Hz) com cache em videos/quem-faz-o-que/ep1/audio
# e renderiza video.mp4 + short.mp4 + legendas.srt + capitulos.txt (só quando algo mudou).
# Revisão 2: prévia para aprovação; repete se o serviço de voz falhar no meio (o cache guarda o que já foi feito).
import subprocess
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "quem-faz-o-que" / "ep1"

sys.path.insert(0, str(ROOT / "scripts"))
for tentativa in range(5):
    try:
        import qfq_render  # noqa: E402
        qfq_render.gerar(PASTA, "qfq_ep1")
        (PASTA / "erro.txt").unlink(missing_ok=True)
        break
    except Exception:
        traceback.print_exc()
        (PASTA / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
        time.sleep(30 * (tentativa + 1))
subprocess.run(["git", "add", str(PASTA)], check=True, cwd=ROOT)

# Único (apaga a si mesmo): re-renderiza short.mp4 e thumb.jpg de videos/tutorial-app-v3 sem o personagem Lupa.
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
PASTA = ROOT / "videos" / "tutorial-app-v3"
log = []
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "numpy", "edge-tts"], check=True)
    from PIL import Image
    import personagem
    import tutorial_app as tu
    import video_longo as vl
    personagem.pose = lambda *a, **k: Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    cfg = json.loads((PASTA / "tutorial.json").read_text(encoding="utf-8"))
    telas = tu.carregar_telas(PASTA, cfg.get("borrar", {}))
    tu.miniatura(PASTA, cfg, telas)
    log.append("thumb.jpg sem lupa")
    (PASTA / ".tutorial_short_render").unlink(missing_ok=True)
    tu.gerar(PASTA, so_short=True)
    mp4 = PASTA / "short.mp4"
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(mp4), "-vf", "fps=1/4,scale=216:384,tile=8x2",
                    "-frames:v", "1", str(PASTA / "previa_short.jpg")], check=False)
    dur = subprocess.run([vl.ffmpeg(), "-i", str(mp4)], capture_output=True, text=True).stderr
    log.append("short sem lupa: " + str(mp4.stat().st_size) + " bytes " +
               next((l.strip() for l in dur.splitlines() if "Duration" in l), ""))
except BaseException:
    log.append(traceback.format_exc())
(PASTA / "log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(Path(__file__))], check=False, cwd=ROOT)

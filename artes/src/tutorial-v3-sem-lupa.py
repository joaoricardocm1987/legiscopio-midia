# Único (apaga a si mesmo): re-renderiza videos/tutorial-app-v3/tutorial.mp4 sem o personagem Lupa.
# Short e miniatura ficam como estão (miniatura é restaurada do backup).
import shutil
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
    thumb = PASTA / "thumb.jpg"
    bkp = Path("/tmp/thumb_bkp.jpg")
    shutil.copy(thumb, bkp)
    (PASTA / ".tutorial_render").unlink(missing_ok=True)
    tu.gerar(PASTA)
    shutil.copy(bkp, thumb)
    mp4 = PASTA / "tutorial.mp4"
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(mp4), "-vf", "fps=1/20,scale=384:216,tile=6x6",
                    "-frames:v", "1", str(PASTA / "previa_tutorial.jpg")], check=False)
    dur = subprocess.run([vl.ffmpeg(), "-i", str(mp4)], capture_output=True, text=True).stderr
    log.append("sem lupa: tutorial.mp4 " + str(mp4.stat().st_size) + " bytes " +
               next((l.strip() for l in dur.splitlines() if "Duration" in l), ""))
except BaseException:
    log.append(traceback.format_exc())
(PASTA / "log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(Path(__file__))], check=False, cwd=ROOT)

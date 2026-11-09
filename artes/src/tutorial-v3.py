# Único (apaga a si mesmo): baixa as telas do tutorial v3 do Drive e gera tutorial.mp4, short.mp4 e thumb.jpg
# em videos/tutorial-app-v3 com scripts/tutorial_app.py.
import subprocess
import sys
import traceback
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
PASTA = ROOT / "videos" / "tutorial-app-v3"
ZIP_ID = "1h56LG4B0XqbJfXENhPjeDazULIt4EGgF"
log = []
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "numpy", "gdown", "edge-tts"], check=True)
    import gdown
    # legenda: "legiscopio ponto com ponto br barra baixar" -> www.legiscopio.com.br/baixar
    ta = ROOT / "scripts" / "tutorial_app.py"
    s = ta.read_text(encoding="utf-8")
    novo = '    "legiscopio ponto com ponto br barra baixar": "www.legiscopio.com.br/baixar",\n'
    velho = '    "legiscopio ponto com ponto br": "www.legiscopio.com.br",\n'
    if novo not in s and velho in s:
        ta.write_text(s.replace(velho, novo + velho), encoding="utf-8")
        log.append("TROCAS: /baixar adicionado")
    import tutorial_app as tu
    import video_longo as vl
    z = Path("/tmp/telas_v3.zip")
    gdown.download(id=ZIP_ID, output=str(z), quiet=True)
    telas = PASTA / "telas"
    telas.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        for n in zf.namelist():
            if n.lower().endswith(".png"):
                (telas / Path(n).name).write_bytes(zf.read(n))
    log.append(f"telas: {len(list(telas.glob('*.png')))}")
    tu.gerar(PASTA)
    for nome, vf in (("tutorial", "fps=1/20,scale=384:216,tile=6x6"), ("short", "fps=1/4,scale=216:384,tile=8x2")):
        mp4 = PASTA / f"{nome}.mp4"
        if mp4.exists():
            subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(mp4), "-vf", vf, "-frames:v", "1",
                            str(PASTA / f"previa_{nome}.jpg")], check=False)
            dur = subprocess.run([vl.ffmpeg(), "-i", str(mp4)], capture_output=True, text=True).stderr
            linha = next((l.strip() for l in dur.splitlines() if "Duration" in l), "")
            log.append(f"{nome}.mp4: {mp4.stat().st_size} bytes {linha}")
except BaseException:
    log.append(traceback.format_exc())
PASTA.mkdir(parents=True, exist_ok=True)
(PASTA / "log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(ROOT / "scripts"), str(Path(__file__))], check=False, cwd=ROOT)

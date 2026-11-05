# Único (apaga a si mesmo): prévia do Resumo de 2 min de 2026-11-05 (resumo.mp4) + folha de quadros resumo_previa.png
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "2026-11-05"
sys.path.insert(0, str(ROOT / "scripts"))
import short_video  # noqa: E402
import video_longo as vl  # noqa: E402

short_video.gerar(PASTA / "resumo.json")
mp4 = PASTA / "resumo.mp4"
if mp4.exists():
    out = subprocess.run([vl.ffmpeg(), "-i", str(mp4)], capture_output=True, text=True).stderr
    dur = 0.0
    for l in out.splitlines():
        if "Duration:" in l:
            h, m, s = l.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = int(h) * 3600 + int(m) * 60 + float(s)
    (PASTA / "resumo_duracao.txt").write_text(f"{dur:.1f}\n")
    passo = max(dur / 12, 1)
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(mp4),
                    "-vf", f"fps=1/{passo:.2f},scale=270:480,tile=6x2", "-frames:v", "1",
                    str(PASTA / "resumo_previa.png")], check=True)
Path(__file__).unlink()
subprocess.run(["git", "add", str(PASTA)], check=True, cwd=ROOT)

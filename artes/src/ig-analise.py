# Único (apaga a si mesmo): baixa os 2 vídeos do Drive (Reel do Instagram de 08/11), transcreve e gera
# folhas de quadros para escolher os melhores trechos. Saída em videos/rosto/ig-2026-11-08/analise/.
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
PASTA = ROOT / "videos" / "rosto" / "ig-2026-11-08"
AN = PASTA / "analise"
AN.mkdir(parents=True, exist_ok=True)
LOG = AN / "log.txt"
IDS = {"A": "1Q_72x8r4UzRokOZbxjtMmwXUAv-hFTKY", "B": "1QdD4kPZaGk_uk281k_jUUPeGRF_6hg0f"}
log = []
try:
    import rosto_editor as re_
    import video_longo as vl
    re_.pip("gdown")
    import gdown
    tmp = Path("/tmp/ig")
    tmp.mkdir(exist_ok=True)
    for k, fid in IDS.items():
        try:
            dst = tmp / f"{k}.mp4"
            gdown.download(id=fid, output=str(dst), quiet=True)
            if not dst.exists() or dst.stat().st_size < 10000:
                log.append(f"{k}: download falhou (o link está como 'qualquer pessoa com o link'?)")
                continue
            info = subprocess.run([vl.ffmpeg(), "-hide_banner", "-i", str(dst)], capture_output=True, text=True).stderr
            log.append(f"{k}: {dst.stat().st_size} bytes | " + " | ".join(
                l.strip() for l in info.splitlines() if "Stream" in l or "Duration" in l or "rotate" in l))
            sub = tmp / k
            sub.mkdir(exist_ok=True)
            base, wav = re_.normalizar(dst, sub)
            pal = re_.transcrever(wav, "", AN / f"transcricao_{k}.json")
            # texto com tempos, por frase (pausas > 0.45 s)
            linhas, atual = [], []
            for p in pal:
                if atual and p[0] - atual[-1][1] > 0.45:
                    linhas.append(atual)
                    atual = []
                atual.append(p)
            if atual:
                linhas.append(atual)
            (AN / f"texto_{k}.txt").write_text("\n".join(
                f"[{g[0][0]:7.2f} - {g[-1][1]:7.2f}] " + " ".join(p[2] for p in g) for g in linhas) + "\n",
                encoding="utf-8")
            import re as _re
            inf2 = subprocess.run([vl.ffmpeg(), "-hide_banner", "-i", str(base)], capture_output=True, text=True).stderr
            m = _re.search(r"Duration: (\d+):(\d+):([\d.]+)", inf2)
            dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 60.0
            passo = max(2, dur / 24)
            folha = AN / f"quadros_{k}.jpg"
            for vf in (f"fps=1/{passo:.2f},scale=216:384,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                       f"text='%{{pts\\:hms}}':x=6:y=6:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=8x3",
                       f"fps=1/{passo:.2f},scale=216:384,tile=8x3"):
                subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(base), "-vf", vf, "-frames:v", "1",
                                str(folha)], check=False)
                if folha.exists():
                    break
            log.append(f"{k}: {len(pal)} palavras, {dur:.1f}s, quadros a cada {passo:.1f}s")
        except Exception:
            log.append(f"{k}: " + traceback.format_exc())
except Exception:
    log.append(traceback.format_exc())
LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(Path(__file__))], check=False, cwd=ROOT)

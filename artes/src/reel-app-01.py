# Reel "conheça o app" 01 — etapa 1: baixa Video1 (fala) e Tela (gravação do app) do Drive e transcreve a fala.
# Saída: videos/reel-app-01/transcricao.json + info.txt (os vídeos brutos não vão para o git).
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "reel-app-01"
DRIVE = "https://drive.google.com/drive/folders/1JxmUrCivL90R7X1qjdmL4u3nqd_J-0cU"
TMP = Path("/tmp/reel-app-01")
sys.path.insert(0, str(ROOT / "scripts"))
PASTA.mkdir(parents=True, exist_ok=True)
try:
    if not (PASTA / "transcricao.json").exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "gdown", "numpy", "faster-whisper"], check=True)
        import gdown
        TMP.mkdir(parents=True, exist_ok=True)
        gdown.download_folder(url=DRIVE, output=str(TMP), quiet=False, use_cookies=False)
        vids = {p.name: p for p in TMP.rglob("*") if p.suffix.lower() in (".mp4", ".mov", ".m4v")}
        info = []
        for nome, p in vids.items():
            r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p)], capture_output=True, text=True).stderr
            info.append(nome + " | " + " | ".join(l.strip() for l in r.splitlines() if "Duration" in l or "Stream" in l))
        (PASTA / "info.txt").write_text("\n".join(info) + "\n", encoding="utf-8")
        fala = next(p for n, p in vids.items() if n.lower().startswith("video1"))
        wav = TMP / "fala.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(fala), "-ac", "1", "-ar", "16000", str(wav)], check=True)
        import rosto_editor  # noqa: E402
        roteiro = "Legiscópio, Câmara dos Deputados, Senado Federal, Congresso, aplicativo, Android, iOS, votação, proposição, apoia.se"
        rosto_editor.transcrever(wav, roteiro, PASTA / "transcricao.json")
    (PASTA / "erro.txt").unlink(missing_ok=True)
except Exception:
    traceback.print_exc()
    (PASTA / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
subprocess.run(["git", "add", str(PASTA)], check=True, cwd=ROOT)

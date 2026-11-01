# Vídeo novo do Drive (31/10) — etapa 1: baixa a pasta, acha o(s) vídeo(s) novo(s), transcreve e
# guarda uma cópia do original (se couber) para a edição.
import json
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "novo-02"
DRIVE = "https://drive.google.com/drive/folders/1JxmUrCivL90R7X1qjdmL4u3nqd_J-0cU"
TMP = Path("/tmp/novo-02")
CONHECIDOS = {"video1.mp4", "tela.mp4", "2026-10-29 20-37-30.mp4"}
sys.path.insert(0, str(ROOT / "scripts"))
PASTA.mkdir(parents=True, exist_ok=True)
# Revisão 1
try:
    if not (PASTA / "info.txt").exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "gdown", "numpy", "faster-whisper"], check=True)
        import gdown
        import video_longo as vl
        FF = vl.ffmpeg()
        TMP.mkdir(parents=True, exist_ok=True)
        gdown.download_folder(url=DRIVE, output=str(TMP), quiet=False, use_cookies=False)
        todos = [p for p in TMP.rglob("*") if p.is_file()]
        info = []
        novos = []
        for p in sorted(todos):
            r = subprocess.run([FF, "-hide_banner", "-i", str(p)], capture_output=True, text=True).stderr
            info.append(f"{p.name} | {p.stat().st_size} bytes | " + " | ".join(
                l.strip() for l in r.splitlines() if "Duration" in l or "Stream" in l or "rotate" in l or "creation_time" in l))
            if p.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm", ".mkv") and p.name.lower() not in CONHECIDOS:
                novos.append(p)
        (PASTA / "info.txt").write_text("\n".join(info) + "\n", encoding="utf-8")
        import rosto_editor  # noqa: E402
        for i, p in enumerate(novos, 1):
            wav = TMP / f"n{i}.wav"
            subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(p), "-ac", "1", "-ar", "16000", str(wav)], check=True)
            rosto_editor.transcrever(wav, "Legiscópio, Câmara dos Deputados, Senado Federal, Congresso, aplicativo, Android, iOS, apoia.se",
                                     PASTA / f"transcricao_{i}.json")
            (PASTA / f"nome_{i}.txt").write_text(p.name, encoding="utf-8")
            if p.stat().st_size < 90_000_000:
                shutil.copy(p, PASTA / f"original_{i}{p.suffix.lower()}")
            else:  # grande demais para o git: cópia em boa qualidade e menor
                subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(p), "-c:v", "libx264", "-crf", "20", "-preset",
                                "medium", "-vf", "scale='min(1080,iw)':-2", "-c:a", "aac", "-b:a", "192k",
                                str(PASTA / f"original_{i}.mp4")], check=True)
    (PASTA / "erro.txt").unlink(missing_ok=True)
except Exception:
    traceback.print_exc()
    (PASTA / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
subprocess.run(["git", "add", str(PASTA)], check=True, cwd=ROOT)

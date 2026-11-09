# Referências de Reels: baixa a pasta do Drive, transcreve cada vídeo e monta folhas de quadros para análise.
# Saída: videos/referencias/ (resumo.md, NN_quadros.jpg). Os vídeos brutos não vão para o git.
# Revisão 2: áudio lido com wave/numpy (o PyAV do runner não aceita o arquivo direto).
import json
import re
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "referencias"
DRIVE = "https://drive.google.com/drive/folders/1SRJq-LFI2H1mXnbJKjDNhuTWo1ZIGojy"
TMP = Path("/tmp/referencias")
sys.path.insert(0, str(ROOT / "scripts"))
PASTA.mkdir(parents=True, exist_ok=True)
try:
    if not (PASTA / "resumo.md").exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "gdown", "numpy", "faster-whisper"], check=True)
        import gdown
        import video_longo as vl
        from PIL import Image, ImageDraw, ImageFont
        from faster_whisper import WhisperModel
        FF = vl.ffmpeg()
        TMP.mkdir(parents=True, exist_ok=True)
        gdown.download_folder(url=DRIVE, output=str(TMP), quiet=False, use_cookies=False)
        vids = sorted(p for p in TMP.rglob("*") if p.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm", ".mkv"))
        modelo = WhisperModel("small", device="cpu", compute_type="int8")
        try:
            fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        except Exception:
            fonte = ImageFont.load_default()
        linhas = ["# Referências de Reels\n"]
        for i, v in enumerate(vids, 1):
            info = subprocess.run([FF, "-hide_banner", "-i", str(v)], capture_output=True, text=True).stderr
            m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
            dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0
            res = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", info)
            # cortes (mudanças de cena)
            sc = subprocess.run([FF, "-hide_banner", "-i", str(v), "-vf", "select='gt(scene,0.3)',showinfo", "-an", "-f", "null", "-"],
                                capture_output=True, text=True).stderr
            cortes = [round(float(x), 1) for x in re.findall(r"pts_time:([\d.]+)", sc)]
            # quadros: 0 a 3 s a cada 0,5 s e depois a cada 2 s
            ts = [0, 0.5, 1, 1.5, 2, 2.5, 3] + [t for t in range(5, int(dur), 2)]
            ts = [t for t in ts if t < max(dur - 0.1, 0.1)][:36]
            fr = []
            for t in ts:
                out = TMP / f"f_{i}_{t}.jpg"
                subprocess.run([FF, "-y", "-loglevel", "error", "-ss", str(t), "-i", str(v), "-frames:v", "1",
                                "-vf", "scale=300:-2", str(out)], check=False)
                if out.exists():
                    fr.append((t, Image.open(out).convert("RGB")))
            if fr:
                w, h = fr[0][1].size
                cols = 6
                rows = (len(fr) + cols - 1) // cols
                folha = Image.new("RGB", (cols * w, rows * (h + 30)), "white")
                d = ImageDraw.Draw(folha)
                for k, (t, im) in enumerate(fr):
                    x, y = (k % cols) * w, (k // cols) * (h + 30)
                    folha.paste(im.resize((w, h)), (x, y + 30))
                    d.text((x + 6, y + 3), f"{t}s", fill="black", font=fonte)
                folha.save(PASTA / f"{i:02d}_quadros.jpg", quality=80)
            # transcrição
            wav = TMP / f"a_{i}.wav"
            subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(v), "-ac", "1", "-ar", "16000", str(wav)], check=False)
            texto = []
            if wav.exists():
                try:
                    import wave
                    import numpy as np
                    with wave.open(str(wav)) as wf:
                        aud = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
                    segs, _ = modelo.transcribe(aud, language="pt", vad_filter=True, beam_size=5)
                    texto = [f"[{s.start:.1f}s] {s.text.strip()}" for s in segs]
                except Exception as e:
                    texto = [f"(erro na transcrição: {e})"]
            linhas.append(f"## {i:02d}. {v.name}\n")
            linhas.append(f"- Duração: {dur:.1f}s · Resolução: {res.group(1)}x{res.group(2) if res else '?'} · Cortes: {len(cortes)} ({cortes[:40]})\n" if res else f"- Duração: {dur:.1f}s · Cortes: {len(cortes)}\n")
            linhas.append("- Fala:\n\n" + ("\n".join(texto) if texto else "(sem fala detectada)") + "\n")
        (PASTA / "resumo.md").write_text("\n".join(linhas), encoding="utf-8")
    (PASTA / "erro.txt").unlink(missing_ok=True)
except Exception:
    traceback.print_exc()
    (PASTA / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
Path(__file__).unlink(missing_ok=True)

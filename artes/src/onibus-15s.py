# Vídeo de 15 s (1920x1080) para a TV dos ônibus: videos/onibus-15s/onibus.html -> onibus_15s.mp4
# v3: telas de 3 s + 3 s + 9 s; sem a Lupa; QR grande, preto no branco, com margem branca (4 módulos).
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "videos" / "onibus-15s"
FPS = 30
sys.path.insert(0, str(ROOT / "scripts"))
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright", "numpy", "qrcode[pil]"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True)
    import qrcode
    from PIL import Image
    import video_longo as vl
    q = qrcode.QRCode(border=4, box_size=20, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data("https://www.legiscopio.com.br/baixar")
    q.make(fit=True)
    q.make_image(fill_color="black", back_color="white").convert("RGB").save(P / "qr.png")
    lg = Image.open(ROOT / "artes" / "logo-legiscopio.png")
    lg.crop(lg.getbbox()).save(P / "logo_c.png")
    for f in ("feed.png", "perfil_cota_emendas.png"):
        shutil.copy(ROOT / "videos" / "tutorial-app-v3" / "telas" / f, P / f)
    for velho in P.glob("quadro_*.jpg"):
        velho.unlink()
    FF = vl.ffmpeg()
    saida = P / "onibus_15s.mp4"
    cmd = [FF, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "128k", "-t", "15", "-shortest", "-movflags", "+faststart", str(saida)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto((P / "onibus.html").as_uri())
        pg.wait_for_timeout(3000)
        for i in range(15 * FPS):
            pg.evaluate(f"setT({i / FPS})")
            proc.stdin.write(pg.screenshot(type="png"))
            if i in (60, 150, 300):
                pg.screenshot(path=str(P / f"quadro_{i // FPS:02d}s.jpg"), type="jpeg", quality=85)
        b.close()
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou")
    (P / "erro.txt").unlink(missing_ok=True)
except Exception:
    traceback.print_exc()
    (P / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
Path(__file__).unlink(missing_ok=True)

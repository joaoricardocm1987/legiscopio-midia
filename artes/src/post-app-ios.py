# Post de divulgação "Chegou no iPhone": renderiza feed (1080x1350) e story (1080x1920) a partir de posts/app-ios/post.html.
import subprocess, sys, shutil, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "posts" / "app-ios"
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright", "numpy"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True)
    sys.path.insert(0, str(ROOT / "scripts"))
    from PIL import Image
    import personagem
    m = personagem.pose("comemorando", boca="sorriso", tamanho=900); m.crop(m.getbbox()).save(P / "mascote_c.png")
    l = Image.open(ROOT / "artes" / "logo-legiscopio.png"); l.crop(l.getbbox()).save(P / "logo_c.png")
    shutil.copy(ROOT / "videos" / "tutorial-app-v3" / "telas" / "votacao.png", P / "votacao.png")
    V = {"feed": (1350, "--H:1350px;--rod:220px;--t0:50px;--ts:300px;--tl:690px;--tf:330px;--mx:470px;--mh:310px;--h1:160px;--sub:52px;--pill:96px;--li:36px;--fw:370px;--h2:44px"),
         "story": (1920, "--H:1920px;--rod:400px;--pb:150px;--t0:200px;--ts:470px;--tl:900px;--tf:780px;--mx:470px;--mh:380px;--h1:170px;--sub:56px;--pill:104px;--li:38px;--fw:400px;--h2:46px")}
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        for k, (h, v) in V.items():
            pg = b.new_page(viewport={"width": 1080, "height": h})
            pg.goto((P / "post.html").as_uri() + "#" + urllib.parse.quote(v)); pg.wait_for_timeout(3000)
            pg.screenshot(path=str(P / f"{k}.png"))
            Image.open(P / f"{k}.png").convert("RGB").save(P / f"{k}.jpg", quality=88, optimize=True)
            (P / f"{k}.png").unlink()
        b.close()
    (P / "erro.txt").unlink(missing_ok=True)
except Exception:
    import traceback; (P / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
Path(__file__).unlink(missing_ok=True)

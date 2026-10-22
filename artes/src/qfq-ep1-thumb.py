# Série "Quem Faz o Quê?" — miniatura do Ep. 1 (videos/quem-faz-o-que/ep1/thumb.jpg, 1280x720).
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from PIL import Image, ImageDraw  # noqa: E402
import personagem  # noqa: E402
import qfq_visual as q  # noqa: E402

W, H = 1920, 1080
img = Image.new("RGB", (W, H), (22, 34, 52))
d = ImageDraw.Draw(img)
d.rectangle([0, 820, W, H], fill=(40, 46, 56))
for x in (-60, 330):
    d.rectangle([x, 560, x + 300, 820], fill=(52, 62, 80))
    d.polygon([(x - 20, 560), (x + 150, 450), (x + 320, 560)], fill=(60, 70, 90))
    for wx in (x + 40, x + 190):
        d.rectangle([wx, 620, wx + 70, 690], fill=(250, 214, 120))
q.icone(d, "poste", 820, 610, 480, (120, 128, 140))
for k, c in enumerate((q.UNI, q.EST, q.MUN)):
    d.rectangle([k * W / 3, 0, (k + 1) * W / 3, 22], fill=c)
t = "EP. 1 · MUNICÍPIO"
w = d.textlength(t, font=q.BK(52)) + 70
d.rounded_rectangle([60, 60, 60 + w, 150], radius=45, fill=q.MUN)
d.text((60 + w / 2, 105), t, font=q.BK(52), fill=q.BRANCO, anchor="mm")
d.text((60, 190), "QUEM CONSERTA?", font=q.BK(176), fill=q.BRANCO)
d.text((66, 400), "Prefeito ou vereador?", font=q.BD(84), fill=(255, 196, 140))
sp = personagem.pose("pensando", "fechada", "abertos", 760, 0.3, -1, espelho=True)
img.paste(sp, (W - sp.width + 10, H - sp.height + 40), sp)
lg = q.vl.logo(110)
if lg:
    box = Image.new("RGB", (lg.width + 50, lg.height + 36), q.BRANCO)
    img.paste(box, (60, H - box.height - 50))
    img.paste(lg, (85, H - box.height - 32), lg)
dest = ROOT / "videos" / "quem-faz-o-que" / "ep1" / "thumb.jpg"
img.resize((1280, 720), Image.LANCZOS).save(dest, quality=92)
subprocess.run(["git", "add", str(dest)], check=True, cwd=ROOT)

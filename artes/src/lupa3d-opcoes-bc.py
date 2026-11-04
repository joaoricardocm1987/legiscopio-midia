# Único (apaga a si mesmo): opções B e C, uma por vez (o plano só aceita 1 tarefa na fila), Meshy Image to Image
# (nano-banana, ~3 créditos cada), a partir da Lupa 2D atual. Saída: artes/3d/opcoes/lupa3d_B|C.png + log_bc.txt
import base64
import io
import json
import os
import subprocess
import sys
import time
import traceback
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artes" / "3d" / "opcoes"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))
API = "https://api.meshy.ai/openapi/v1/image-to-image"
BASE = ("Keep EXACTLY the same character design: a friendly mascot whose head is a round magnifying glass "
        "(thick dark green rim with four small lime-green dots, light mint glass lens) with the face inside the lens "
        "(big round eyes, eyebrows, pink cheeks, small smile), dark green suit, white shirt collar, lime green tie, "
        "small white ID badge with a green logo on the chest, white cartoon gloves, dark gray pants, black shoes. "
        "Full body, front view, standing, arms slightly open, plain white background, no text. ")
ESTILOS = {
    "B": "Render it as a 3D anime-style character (cel-shaded 3D, like modern anime 3D CG): clean toon shading, "
         "crisp outlines, vibrant flat colors with soft gradients, expressive anime eyes inside the lens.",
    "C": "Render it as a cute 3D collectible toy figure: matte vinyl and soft plastic materials, rounded shapes, "
         "studio product lighting, slight tilt-shift look.",
}
log = []


def req(metodo, url, corpo=None):
    r = urllib.request.Request(url, method=metodo, data=json.dumps(corpo).encode() if corpo else None,
                               headers={"Authorization": "Bearer " + os.environ["MESHY_API_KEY"],
                                        "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode())


try:
    if not os.environ.get("MESHY_API_KEY"):
        raise RuntimeError("MESHY_API_KEY não está disponível no workflow")
    import personagem  # noqa: E402
    from PIL import Image
    im = personagem.pose("explicando", "fechada", "abertos", 900, 0.3, 0)
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    buf = io.BytesIO()
    bg.convert("RGB").save(buf, "PNG")
    ref = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    for k, estilo in ESTILOS.items():
        try:
            t = req("POST", API, {"ai_model": "nano-banana", "prompt": BASE + estilo, "reference_image_urls": [ref],
                                  "aspect_ratio": "3:4"})
        except urllib.error.HTTPError as e:
            log.append(f"{k}: ERRO {e.code} {e.read().decode()[:400]}")
            continue
        tid = t["result"]
        log.append(f"{k}: tarefa {tid}")
        fim = time.time() + 600
        while time.time() < fim:
            time.sleep(10)
            t = req("GET", f"{API}/{tid}")
            if t.get("status") in ("SUCCEEDED", "FAILED", "CANCELED"):
                log.append(f"{k}: {t.get('status')} créditos={t.get('consumed_credits')} erro={t.get('task_error')}")
                for j, u in enumerate(t.get("image_urls") or []):
                    with urllib.request.urlopen(u, timeout=120) as resp:
                        (OUT / f"lupa3d_{k}{'' if j == 0 else j}.png").write_bytes(resp.read())
                break
        else:
            log.append(f"{k}: não terminou a tempo")
except Exception:
    log.append(traceback.format_exc())
(OUT / "log_bc.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(OUT)], check=True, cwd=ROOT)

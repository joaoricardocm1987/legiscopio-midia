# Único (apaga a si mesmo): 2ª rodada A/B/C com prompt forçando 3D, uma tarefa por vez (limite de fila do plano).
# Meshy Image to Image (nano-banana, ~3 créditos cada). Saída: artes/3d/opcoes/lupa3d_v2_A|B|C.png + log_v2.txt
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
BASE = ("Transform this flat 2D cartoon mascot into a fully three-dimensional CGI character render. "
        "This must NOT look like a flat vector drawing: show real volume, depth, perspective, soft shadows, "
        "highlights, reflections and material textures, as a frame from a modern 3D animated production. "
        "Keep the character recognizable: a mascot whose head is a big round magnifying glass with a thick dark green rim "
        "(four small lime-green dots on the rim) and a transparent glass lens with the face inside it "
        "(big expressive eyes, eyebrows, pink cheeks, friendly smile), dark green suit jacket, white shirt collar, "
        "lime green tie, small white ID badge on the chest, white gloves, dark gray trousers, black shoes. "
        "Full body, three-quarter front view, standing, arms slightly open in a welcoming pose, "
        "plain light gray studio background, no text, no logo letters. ")
ESTILOS = {
    "A": "Style: high-end 3D animated feature film character: physically based materials, "
         "subsurface scattering, fabric texture on the suit, refractive glass lens, cinematic three-point lighting, "
         "ambient occlusion, shallow depth of field.",
    "B": "Style: modern Japanese anime 3D CGI (cel-shaded 3D like contemporary anime series made in 3D): "
         "toon shading with two-tone shadows, clean ink outlines, rim light, vibrant colors, glossy anime eyes, "
         "but clearly a 3D model with volume and perspective.",
    "C": "Style: collectible vinyl designer toy photographed in a studio: chunky rounded proportions, matte vinyl and "
         "glossy plastic materials, visible soft shadows on the floor, macro product photography, realistic lighting.",
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
                        (OUT / f"lupa3d_v2_{k}{'' if j == 0 else j}.png").write_bytes(resp.read())
                break
        else:
            log.append(f"{k}: não terminou a tempo")
except Exception:
    log.append(traceback.format_exc())
(OUT / "log_v2.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(OUT)], check=True, cwd=ROOT)

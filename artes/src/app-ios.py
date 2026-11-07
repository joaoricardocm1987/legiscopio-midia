# Único (apaga a si mesmo): o app do Legiscópio já está no iOS. Tira o "iOS em breve" das artes e vídeos
# (scripts/agenda.py, tutorial_app.py, rosto_editor.py, video_longo.py) e refaz o resumo de 2 min de 2026-11-07.
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / "scripts"
PASTA = ROOT / "videos" / "2026-11-07"
LOG = PASTA / "ios_log.txt"
log = []

TROCAS = {
    "agenda.py": [
        ('"Android: legiscopio.com.br/baixar", font=BK(52)', '"www.legiscopio.com.br/baixar", font=BK(52)'),
        ('"iOS em breve · grátis e sem anúncios", font=RG(40)', '"Android e iOS · grátis e sem anúncios", font=RG(40)'),
    ],
    "tutorial_app.py": [
        ('"Android: já disponível · iOS: em breve"', '"Android e iOS: já disponível"'),
    ],
    "rosto_editor.py": [
        ('caixa_txt(d, "ANDROID", (W - d.textbbox((0, 0), "ANDROID", font=BK(90))[2] - 60) / 2,',
         'caixa_txt(d, "ANDROID E iOS", (W - d.textbbox((0, 0), "ANDROID E iOS", font=BK(90))[2] - 60) / 2,'),
        ('"iOS em breve · grátis e sem anúncios", font=BD(42)', '"grátis e sem anúncios", font=BD(42)'),
    ],
    "video_longo.py": [
        ('v.get("app_texto", "Já no Android · iOS em breve")', 'v.get("app_texto", "Android e iOS · grátis")'),
    ],
}

try:
    for nome, trocas in TROCAS.items():
        arq = S / nome
        s = arq.read_text(encoding="utf-8")
        for velho, novo in trocas:
            n = s.count(velho)
            if n:
                s = s.replace(velho, novo)
                log.append(f"{nome}: trocado ({n}x) {velho[:40]!r}")
            elif novo in s:
                log.append(f"{nome}: já estava ok {novo[:40]!r}")
            else:
                log.append(f"{nome}: NÃO ACHADO {velho[:40]!r}")
        arq.write_text(s, encoding="utf-8")
    rest = subprocess.run(["grep", "-rn", "-i", "em breve", str(S)], capture_output=True, text=True).stdout
    log.append("restos de 'em breve' em scripts/:\n" + (rest or "(nenhum)"))
    subprocess.run(["git", "add", str(S)], check=True, cwd=ROOT)

    rj = PASTA / "resumo.json"
    r = json.loads(rj.read_text(encoding="utf-8"))
    f = r["cenas"][-1]["fala"]
    if "de graça para Android:" in f:
        r["cenas"][-1]["fala"] = f.replace("de graça para Android:", "de graça para Android e iPhone:")
        rj.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        log.append("resumo.json: fala final com Android e iPhone")
    for nome in (".resumo_render", "resumo.mp4"):
        (PASTA / nome).unlink(missing_ok=True)
    sys.path.insert(0, str(S))
    import short_video  # noqa: E402
    import video_longo  # noqa: E402
    short_video.gerar(rj)
    mp4 = PASTA / "resumo.mp4"
    if mp4.exists():
        dur = subprocess.run([video_longo.ffmpeg(), "-i", str(mp4)], capture_output=True, text=True).stderr
        dur = next((l.strip() for l in dur.splitlines() if "Duration" in l), "")
        log.append(f"resumo.mp4 refeito: {mp4.stat().st_size} bytes {dur}")
    else:
        log.append("resumo.mp4 NÃO gerado")
except Exception:
    log.append(traceback.format_exc())
LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(Path(__file__))], check=False, cwd=ROOT)

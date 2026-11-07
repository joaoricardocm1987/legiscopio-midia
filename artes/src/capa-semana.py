# Único (apaga a si mesmo): novo visual "capa_semana" (abertura dos vídeos de sábado: "Resumão da semana na
# Câmara e no Senado"), aplicado em scripts/video_longo.py e scripts/capitulos.py; usa no vídeo de 2026-11-07 e refaz.
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VL = ROOT / "scripts" / "video_longo.py"
CAP = ROOT / "scripts" / "capitulos.py"
PASTA = ROOT / "videos" / "2026-11-07"
LOG = PASTA / "capa_semana_log.txt"
log = []
BLOCO = '    if tipo == "capa_semana":  # abertura do sábado: "Resumão da semana na Câmara e no Senado"\n        cx0, cy0, cx1, cy1 = x0, y0 + 10 + off, x1 + 20, y0 + 650 + off\n        cartao = Image.new("RGB", (cx1 - cx0, cy1 - cy0), VERDE)\n        dc = ImageDraw.Draw(cartao)\n        for k in range(-cartao.height, cartao.width, 56):  # listras sutis, como na miniatura\n            dc.line([(k, cartao.height), (k + cartao.height, 0)], fill=(8, 96, 53), width=20)\n        masc = Image.new("L", cartao.size, 0)\n        ImageDraw.Draw(masc).rounded_rectangle([0, 0, cartao.width - 1, cartao.height - 1], radius=36, fill=255)\n        img.paste(cartao, (cx0, cy0), masc)\n        px = cx0 + 70\n        y = cy0 + 50\n        tag = (v.get("tag") or "TODO SÁBADO").upper()\n        ft = BD(34)\n        tw = d.textlength(tag, font=ft)\n        d.rounded_rectangle([px, y, px + tw + 48, y + 58], radius=29, fill=LIMA)\n        d.text((px + 24, y + 29), tag, font=ft, fill=VERDE_ESC, anchor="lm")\n        y += 96\n        f = BK(122)\n        for l in wrap(d, (v.get("titulo") or "Resumão da semana").upper(), f, cx1 - cx0 - 140):\n            d.text((px, y), l, font=f, fill=BRANCO, stroke_width=3, stroke_fill=VERDE_ESC)\n            y += 132\n        y += 26\n        fs = BD(64)\n        for l in wrap(d, v.get("subtitulo") or "na Câmara e no Senado", fs, cx1 - cx0 - 140):\n            d.text((px, y), l, font=fs, fill=LIMA)\n            y += 78\n        if v.get("periodo"):\n            y += 10\n            d.text((px, y), v["periodo"], font=RG(46), fill=LIMA_TX)\n\n'
ANCORA = '    if tipo == "capa":\n        f = BK(96)'
TROCAS_VL = [
    (ANCORA, BLOCO + ANCORA.replace("    if tipo", "    elif tipo", 1)),
    ('    if tipo == "capa":\n        nome = "acenando" if t < 2.6 else "explicando"',
     '    if tipo in ("capa", "capa_semana"):\n        nome = "acenando" if t < 2.6 else "explicando"'),
    ('  capa       {titulo, subtitulo}',
     '  capa       {titulo, subtitulo}\n  capa_semana {titulo?, subtitulo?, periodo, tag?}  (abertura do sábado: "Resumão da semana")'),
]

try:
    s = VL.read_text(encoding="utf-8")
    if 'tipo == "capa_semana"' not in s:
        for velho, novo in TROCAS_VL:
            if velho.startswith("  capa ") and s.count(velho) != 1:
                log.append("docstring: linha da capa não achada (ignorado)")
                continue
            assert s.count(velho) == 1, f"trecho não encontrado: {velho[:50]!r}"
            s = s.replace(velho, novo)
        VL.write_text(s, encoding="utf-8")
        log.append("video_longo.py: capa_semana adicionada")
    c = CAP.read_text(encoding="utf-8")
    if '"capa_semana"' not in c:
        velho = '        if tipo == "capa":\n            nome = "Introdução"'
        assert c.count(velho) == 1, "capitulos: trecho não encontrado"
        c = c.replace(velho, '        if tipo in ("capa", "capa_semana"):\n            nome = "Introdução"')
        CAP.write_text(c, encoding="utf-8")
        log.append("capitulos.py: capa_semana = Introdução")
    subprocess.run(["git", "add", str(VL), str(CAP)], check=True, cwd=ROOT)

    vj = PASTA / "video.json"
    cfg = json.loads(vj.read_text(encoding="utf-8"))
    cfg["cenas"][0]["visual"] = {"tipo": "capa_semana", "titulo": "Resumão da semana",
                                 "subtitulo": "na Câmara e no Senado", "periodo": "3 a 5 de novembro de 2026"}
    vj.write_text(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for nome in (".video_render", "video.mp4", "legendas.srt", "capitulos.txt", "cta_abertura_previa.png",
                 "cta_abertura_log.txt"):
        (PASTA / nome).unlink(missing_ok=True)
    sys.path.insert(0, str(ROOT / "scripts"))
    import video_longo  # noqa: E402
    import capitulos  # noqa: E402
    video_longo.gerar(vj)
    capitulos.gerar(vj)
    mp4 = PASTA / "video.mp4"
    if mp4.exists():
        subprocess.run([video_longo.ffmpeg(), "-y", "-loglevel", "error", "-ss", "2", "-t", "32", "-i", str(mp4),
                        "-vf", "fps=1/4,scale=480:270,tile=4x2", "-frames:v", "1",
                        str(PASTA / "capa_semana_previa.png")], check=True)
        log.append(f"video.mp4 refeito: {mp4.stat().st_size} bytes")
except Exception:
    log.append(traceback.format_exc())
LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(Path(__file__))], check=False, cwd=ROOT)

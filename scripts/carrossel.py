"""Carrossel do tema do dia (Instagram/Facebook, 1080x1350).

Lê posts/<data>/carrossel.json e grava posts/<data>/carrossel_1.png … carrossel_N.png.

Formato do JSON:
{
  "slides": [
    {"tipo": "capa", "rotulo": "Votação na Câmara", "titulo": "...", "destaque": "PL 2.475/2025", "subtitulo": "..."},
    {"tipo": "texto", "titulo": "...", "itens": ["...", "..."]},                     # 2 a 4 itens
    {"tipo": "jogo", "titulo": "O que está em jogo",
     "sim_rotulo": "Se aprovar", "sim": ["...", "..."],
     "nao_rotulo": "Se não aprovar", "nao": ["...", "..."]},
    {"tipo": "visoes", "titulo": "O que dizem especialistas",
     "itens": [{"lado": "Quem defende", "quem": "Nome", "cargo": "função, instituição",
                "texto": "resumo da posição", "onde": "Veículo, DD/MM/AAAA"}, ...]},   # 2 a 4 itens
    {"tipo": "final", "pergunta": "...", "fonte": "Fontes: ..."}
  ]
}
"""
import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSAO = "1"

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;font-family:'Poppins',sans-serif;background:#f4f6f1;color:#0f3d24;position:relative}
.faixa{position:absolute;top:0;left:0;right:0;height:14px;display:flex}.faixa div{flex:1}
.topo{position:absolute;top:44px;left:70px;right:70px;display:flex;align-items:center;justify-content:space-between}
.topo img{height:70px}
.pag{font-size:28px;font-weight:700;color:#5b7a66}
.verde{background:radial-gradient(circle at 80% 70%,#1f8a4c 0%,#16703d 45%,#0f5a30 100%);color:#fff}
.verde .pag{color:#cfe8d6}
.rot{display:inline-block;background:#f7d548;color:#0d3b20;font-weight:800;font-size:32px;padding:10px 26px;border-radius:40px}
h1{font-weight:900;line-height:1.08}
.dest{display:inline-block;background:#bfe06a;color:#0d3b20;font-weight:900;border-radius:30px;padding:6px 30px 10px}
.arrasta{position:absolute;bottom:70px;right:70px;font-size:32px;font-weight:700;color:#e8f5e9}
.box{position:absolute;left:70px;right:70px;top:170px;bottom:110px;display:flex;flex-direction:column}
h2{font-size:64px;font-weight:900;color:#0f5a30;line-height:1.1;margin-bottom:34px}
.it{display:flex;gap:22px;align-items:flex-start;margin-bottom:34px;font-size:41px;font-weight:600;line-height:1.3;color:#173d27}
.it b{flex:none;width:52px;height:52px;border-radius:50%;background:#0f5a30;color:#fff;display:flex;align-items:center;justify-content:center;font-size:28px;margin-top:2px}
.col{border-radius:28px;padding:36px 38px;margin-bottom:34px}
.col h3{font-size:44px;font-weight:900;margin-bottom:14px}
.col li{font-size:37px;font-weight:600;line-height:1.3;margin:0 0 10px 30px}
.sim{background:#e3f1d3;border-left:14px solid #6aa83a}
.nao{background:#eceff1;border-left:14px solid #7b8a93}
.vis{background:#fff;border-radius:24px;padding:24px 30px;margin-bottom:20px;box-shadow:0 4px 14px rgba(0,0,0,.06)}
.vis .lado{display:inline-block;font-size:24px;font-weight:800;color:#fff;background:#0f5a30;border-radius:20px;padding:4px 16px;margin-bottom:10px}
.vis .lado.c{background:#5a6b74}
.vis .quem{font-size:30px;font-weight:800}
.vis .cargo{font-size:24px;font-weight:600;color:#5b7a66}
.vis p{font-size:29px;font-weight:500;line-height:1.32;margin-top:8px}
.vis .onde{font-size:22px;color:#7a8a80;margin-top:6px}
.nota{font-size:22px;color:#6b7c72;margin-top:auto}
.fim h2{color:#fff}
.fim .perg{font-size:52px;font-weight:800;line-height:1.2;margin-bottom:60px}
.fim .app{background:#fff;color:#0f3d24;border-radius:30px;padding:36px 40px;display:flex;align-items:center;gap:30px}
.fim .app img{height:140px}
.fim .app div{font-size:34px;font-weight:700;line-height:1.35}
.fim .app b{font-size:40px;color:#0f5a30}
.fim .fonte{font-size:24px;color:#d7ecdc;margin-top:auto;line-height:1.35}
"""


def e(t):
    return html.escape(str(t or ""))


def topo(i, n, logo):
    return (f'<div class="faixa"><div style="background:#6a4fb3"></div><div style="background:#2f6fc7"></div>'
            f'<div style="background:#e07a2e"></div></div><div class="topo"><img src="{logo}"><span class="pag">{i}/{n}</span></div>')


def slide(s, i, n, logo, logo_branco):
    t = s.get("tipo")
    if t == "capa":
        corpo = (f'<div class="box" style="top:250px"><span class="rot" style="align-self:flex-start">{e(s.get("rotulo"))}</span>'
                 f'<h1 style="font-size:84px;margin-top:40px">{e(s.get("titulo"))}</h1>'
                 + (f'<div style="margin-top:44px"><span class="dest" style="font-size:64px">{e(s.get("destaque"))}</span></div>' if s.get("destaque") else "")
                 + (f'<p style="font-size:38px;font-weight:600;margin-top:44px;color:#e8f5e9;line-height:1.3">{e(s.get("subtitulo"))}</p>' if s.get("subtitulo") else "")
                 + '</div><div class="arrasta">Arraste para o lado →</div>')
        return "verde", topo(i, n, logo_branco) + corpo
    if t == "texto":
        its = "".join(f'<div class="it"><b>{k + 1}</b><span>{e(x)}</span></div>' for k, x in enumerate(s.get("itens", [])))
        nota = f'<div class="nota">{e(s.get("nota"))}</div>' if s.get("nota") else ""
        return "", topo(i, n, logo) + f'<div class="box"><h2>{e(s.get("titulo"))}</h2>{its}{nota}</div>'
    if t == "jogo":
        sim = "".join(f"<li>{e(x)}</li>" for x in s.get("sim", []))
        nao = "".join(f"<li>{e(x)}</li>" for x in s.get("nao", []))
        nota = f'<div class="nota">{e(s.get("nota"))}</div>' if s.get("nota") else ""
        return "", topo(i, n, logo) + (
            f'<div class="box"><h2>{e(s.get("titulo") or "O que está em jogo")}</h2>'
            f'<div class="col sim"><h3>{e(s.get("sim_rotulo") or "Se aprovar")}</h3><ul>{sim}</ul></div>'
            f'<div class="col nao"><h3>{e(s.get("nao_rotulo") or "Se não aprovar")}</h3><ul>{nao}</ul></div>{nota}</div>')
    if t == "visoes":
        vs = ""
        for v in s.get("itens", []):
            critico = any(w in (v.get("lado") or "").lower() for w in ("crít", "crit", "contra", "ressalva"))
            vs += (f'<div class="vis"><span class="lado{" c" if critico else ""}">{e(v.get("lado"))}</span>'
                   f'<div class="quem">{e(v.get("quem"))}</div><div class="cargo">{e(v.get("cargo"))}</div>'
                   f'<p>{e(v.get("texto"))}</p><div class="onde">{e(v.get("onde"))}</div></div>')
        nota = s.get("nota") or "Opiniões resumidas pelo Legiscópio; links na legenda."
        return "", topo(i, n, logo) + (f'<div class="box"><h2>{e(s.get("titulo") or "O que dizem especialistas")}</h2>'
                                       f'{vs}<div class="nota">{e(nota)}</div></div>')
    if t == "final":
        return "verde fim", topo(i, n, logo_branco) + (
            f'<div class="box" style="top:220px"><div class="perg">{e(s.get("pergunta") or "E você, o que acha? Comenta aí.")}</div>'
            f'<div class="app"><img src="{logo}"><div><b>Acompanhe essa proposta no app</b><br>'
            f'Grátis · Android e iPhone<br>www.legiscopio.com.br/baixar</div></div>'
            f'<p style="font-size:32px;font-weight:700;margin-top:40px">Apoie o Legiscópio: apoia.se/legiscopio</p>'
            f'<div class="fonte">{e(s.get("fonte"))}</div></div>')
    raise ValueError(f"tipo de slide desconhecido: {t}")


def gerar(caminho_json):
    p = Path(caminho_json)
    pasta = p.parent
    bruto = p.read_bytes()
    cfg = json.loads(bruto.decode("utf-8"))
    slides = cfg["slides"]
    import hashlib
    assinatura = hashlib.sha256(bruto + VERSAO.encode()).hexdigest()
    marca = pasta / ".carrossel_render"
    if marca.exists() and marca.read_text().strip() == assinatura and (pasta / "carrossel_1.png").exists():
        print("carrossel sem mudanças", pasta)
        return
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=False)
    from playwright.sync_api import sync_playwright
    from PIL import Image
    logo = ROOT / "artes" / "logo-legiscopio.png"
    lg = Image.open(logo)
    lg = lg.crop(lg.getbbox())
    tmp = pasta / "_logo_c.png"
    lg.save(tmp)
    # versão para fundo verde: logo dentro de um selo branco
    lb = Image.new("RGBA", (lg.width + 80, lg.height + 60), (255, 255, 255, 255))
    lb.paste(lg, (40, 30), lg)
    tmpb = pasta / "_logo_b.png"
    lb.save(tmpb)
    for velho in pasta.glob("carrossel_*.png"):
        velho.unlink()
    n = len(slides)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            classe, corpo = slide(s, i, n, tmp.name, tmpb.name)
            doc = ('<!doctype html><html><head><meta charset="utf-8">'
                   '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800;900&display=swap" rel="stylesheet">'
                   f'<style>{CSS}</style></head><body class="{classe}">{corpo}</body></html>')
            arq = pasta / f"_slide_{i}.html"
            arq.write_text(doc, encoding="utf-8")
            pg.goto(arq.as_uri())
            pg.wait_for_timeout(1200)
            pg.screenshot(path=str(pasta / f"carrossel_{i}.png"))
            arq.unlink()
        b.close()
    tmp.unlink(missing_ok=True)
    tmpb.unlink(missing_ok=True)
    marca.write_text(assinatura + "\n")
    print(f"ok {n} slides em {pasta}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        gerar(a)

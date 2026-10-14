"""Gera as artes diárias do Legiscópio a partir de posts/<data>/post.json.

Usa a paleta e o layout oficiais (os mesmos de artes/src/pls-setembro-2026.py
e artes/src/teste-voce-sabia-orientacao-bancada.py): fundo claro, verde
#05572F, logo no topo, kicker em mono à direita, cards brancos com barra verde.

Saídas, na mesma pasta do post.json:
  feed.png    1080x1350  feed do Instagram e do Facebook
  tiktok.jpg  1080x1080  foto do TikTok (JPEG; o TikTok não aceita PNG)
  story.png   1080x1920  stories do Instagram e do Facebook
  reel.mp4    1080x1920  vídeo de ~10 s para Reels (Instagram/Facebook) e TikTok

Campos do post.json:
  rotulo      kicker do topo (ex.: "Votação na Câmara")
  titulo      manchete (até ~80 caracteres)
  destaque    número ou fato curto em destaque (ex.: "346 a 46"), opcional
  detalhe     1 a 2 frases de contexto, opcional (vai num card branco)
  fonte       linha de fonte (ex.: "Fonte: Câmara dos Deputados · 03/09/2026")

O rodapé sempre traz "Apoie: apoia.se/legiscopio" e "legiscopio.com.br".
Se post.json não mudou desde a última geração (arquivo .render), nada é refeito.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RENDER_VERSION = "3"  # mude para forçar regerar tudo

# Paleta oficial do Legiscópio
FUNDO = "#F4F7F3"
VERDE = "#05572F"
TEXTO = "#10251A"
TEXTO2 = "#4A5D51"
OLIVA = "#5E7F22"
BRANCO = "#FFFFFF"

ROOT = Path(__file__).resolve().parents[1]
N = "/usr/share/fonts/opentype/noto/"
DJ = "/usr/share/fonts/truetype/dejavu/"


def achar(*cs):
    for c in cs:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(", ".join(cs))


F_BLACK = achar(N + "NotoSansCJK-Black.ttc", N + "NotoSansCJK-Bold.ttc", DJ + "DejaVuSans-Bold.ttf")
F_REG = achar(N + "NotoSansCJK-Regular.ttc", DJ + "DejaVuSans.ttf")
F_MONO = achar(DJ + "DejaVuSansMono.ttf")
F_MONOB = achar(DJ + "DejaVuSansMono-Bold.ttf", F_MONO)
BK = lambda s: ImageFont.truetype(F_BLACK, s, index=0)  # noqa: E731
RG = lambda s: ImageFont.truetype(F_REG, s, index=0)  # noqa: E731
MO = lambda s: ImageFont.truetype(F_MONO, s)  # noqa: E731
MB = lambda s: ImageFont.truetype(F_MONOB, s)  # noqa: E731

LOGO = next(
    (p for p in [ROOT / "artes" / "assets" / "logo-legiscopio.png", ROOT / "artes" / "logo-legiscopio.png"] if p.exists()),
    None,
)

# Formatos. topo/base = margens de segurança (em stories e Reels a interface
# do app cobre o alto e o pé da tela).
FORMATOS = {
    "feed": dict(W=1080, H=1350, topo=60, base=0, logo=105, titulo=76, destaque=170, detalhe=33),
    "quadrado": dict(W=1080, H=1080, topo=60, base=0, logo=92, titulo=64, destaque=132, detalhe=30),
    "vertical": dict(W=1080, H=1920, topo=200, base=330, logo=130, titulo=100, destaque=230, detalhe=42),
}


def wrap(d, t, f, maxw):
    out, line = [], ""
    for w in t.split():
        test = (line + " " + w).strip()
        if d.textlength(test, font=f) <= maxw:
            line = test
        else:
            if line:
                out.append(line)
            line = w
    if line:
        out.append(line)
    return out


def espacado(d, x_dir, y, t, f, fill, esp):
    larg = sum(d.textlength(c, font=f) for c in t) + esp * (len(t) - 1)
    x = x_dir - larg
    for c in t:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + esp


def layout(post, fmt, k):
    """Desenha a arte com fator de escala k. Devolve (img, cabe, faixas).

    faixas = lista de (y0, y1) de cada bloco visual, de cima para baixo
    (cabeçalho, título, destaque, card, rodapé) — usada na animação.
    """
    W, H = fmt["W"], fmt["H"]
    T, B = fmt["topo"], fmt["base"]
    ML, MR = 78, W - 78
    img = Image.new("RGB", (W, H), FUNDO)
    d = ImageDraw.Draw(img)
    s = lambda v: max(1, round(v * k))  # noqa: E731
    faixas = []

    # cabeçalho: logo + kicker
    alt = fmt["logo"]
    if LOGO:
        lg = Image.open(LOGO).convert("RGBA")
        lg = lg.resize((round(lg.width * alt / lg.height), alt), Image.LANCZOS)
        img.paste(lg, (ML + 5, T), lg)
    else:
        d.text((ML, T + 30), "Legiscópio", font=BK(44), fill=VERDE)
    if post.get("rotulo"):
        f = MO(26)
        txt = post["rotulo"].upper()
        while d.textlength(txt, font=f) + 5 * len(txt) > MR - ML - 260 and f.size > 18:
            f = MO(f.size - 2)
        espacado(d, MR, T + alt // 2 - 14, txt, f, OLIVA, 5)
    faixas.append((max(0, T - 20), T + alt + 10))

    rodape_y = H - B - 120
    topo = T + alt + 40

    blocos = []

    def bloco_texto(linhas, f, cor, entre):
        a, _ = f.getmetrics()
        top0 = min(f.getbbox(l)[1] for l in linhas)
        lh = round(f.size * entre)
        alt_b = lh * (len(linhas) - 1) + (a - top0) + round(f.size * 0.08)

        def desenhar(y0):
            yy = y0 - top0
            for l in linhas:
                d.text((ML - (4 if f.size > 120 else 0), yy), l, font=f, fill=cor)
                yy += lh
        return desenhar, alt_b

    ft = BK(s(fmt["titulo"]))
    blocos.append((*bloco_texto(wrap(d, post["titulo"], ft, MR - ML), ft, VERDE, 1.12), s(60)))

    if post.get("destaque"):
        fd = BK(s(fmt["destaque"]))
        while d.textlength(post["destaque"], font=fd) > MR - ML and fd.size > 60:
            fd = BK(fd.size - 6)
        blocos.append((*bloco_texto([post["destaque"]], fd, VERDE, 1.0), s(44)))

    if post.get("detalhe"):
        fr = RG(s(fmt["detalhe"]))
        linhas = wrap(d, post["detalhe"], fr, MR - ML - 72)
        lh = round(fr.size * 1.38)
        pad = s(32)
        h = pad * 2 + len(linhas) * lh - round(fr.size * 0.3)

        def card(y0, linhas=linhas, fr=fr, lh=lh, pad=pad, h=h):
            d.rounded_rectangle([ML, y0, MR, y0 + h], radius=22, fill=BRANCO, outline=VERDE, width=2)
            d.rounded_rectangle([ML, y0, ML + 16, y0 + h], radius=8, fill=VERDE)
            d.rectangle([ML + 8, y0, ML + 16, y0 + h], fill=VERDE)
            yy = y0 + pad - round(fr.size * 0.22)
            for l in linhas:
                d.text((ML + 44, yy), l, font=fr, fill=TEXTO)
                yy += lh
        blocos.append((card, h, 0))

    total = sum(h + g for _, h, g in blocos) - blocos[-1][2]
    livre = rodape_y - topo
    cabe = total <= livre
    y = topo + max(0, (livre - total) * 2 // 5)
    for desenhar, h, g in blocos:
        desenhar(y)
        faixas.append((y - 6, y + h + 6))
        y += h + g

    # rodapé: fonte (até 2 linhas) à esquerda; apoio + URL à direita
    url = "legiscopio.com.br"
    apoio = "apoia.se/legiscopio"
    fu = MB(23 if H < 1900 else 27)
    fa = MO(21 if H < 1900 else 25)
    base_y = H - B - 64
    larg_dir = max(d.textlength(url, font=fu), d.textlength("Apoie: " + apoio, font=fa))
    if post.get("fonte"):
        ff = MO(21 if H < 1900 else 24)
        maxw = MR - ML - larg_dir - 30
        fl = wrap(d, post["fonte"], ff, maxw)[:2]
        yy = base_y - 30 * (len(fl) - 1)
        for linha in fl:
            d.text((ML, yy), linha, font=ff, fill=TEXTO2)
            yy += 30
    x_ap = MR - d.textlength(apoio, font=fa)
    d.text((x_ap, base_y - 32), apoio, font=fa, fill=OLIVA)
    d.text((x_ap, base_y - 32), "Apoie: ", font=fa, fill=TEXTO2, anchor="ra")
    d.text((MR, base_y), url, font=fu, fill=VERDE, anchor="ra")
    faixas.append((base_y - 50, base_y + 40))
    return img, cabe, faixas


def render(post, nome):
    fmt = FORMATOS[nome]
    k = 1.0
    while True:
        img, cabe, faixas = layout(post, fmt, k)
        if cabe or k <= 0.6:
            return img, faixas
        k -= 0.05


# ---------------------------------------------------------------- vídeo

def ffmpeg_exe():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "imageio-ffmpeg"], check=True)
        import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def suave(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def video(img, faixas, destino, dur=10.0, fps=30):
    """Anima a arte final: cada faixa entra de baixo para cima, em sequência."""
    W, H = img.size
    fundo = Image.new("RGB", (W, H), FUNDO)
    pedacos = [(y0, img.crop((0, y0, W, y1))) for y0, y1 in faixas]
    inicio, passo, entrada, desl = 0.2, 0.45, 0.6, 40
    cmd = [
        ffmpeg_exe(), "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-r", str(fps), "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(destino),
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(dur * fps)
    for i in range(total):
        t = i / fps
        quadro = fundo.copy()
        for n, (y0, pc) in enumerate(pedacos):
            a = suave((t - inicio - n * passo) / entrada)
            if a <= 0:
                continue
            dy = round(desl * (1 - a))
            if a >= 1:
                quadro.paste(pc, (0, y0))
            else:
                base = quadro.crop((0, y0 + dy, W, y0 + dy + pc.height))
                quadro.paste(Image.blend(base, pc, a), (0, y0 + dy))
        p.stdin.write(quadro.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg falhou")


# ---------------------------------------------------------------- principal

def main(paths):
    for p in paths:
        p = Path(p)
        pasta = p.parent
        bruto = p.read_bytes()
        assinatura = hashlib.sha256(bruto + RENDER_VERSION.encode()).hexdigest()
        marca = pasta / ".render"
        saidas = ["feed.png", "tiktok.jpg", "story.png", "reel.mp4"]
        if marca.exists() and marca.read_text().strip() == assinatura and all((pasta / s).exists() for s in saidas):
            print("sem mudanças", pasta)
            continue
        post = json.loads(bruto.decode("utf-8"))
        render(post, "feed")[0].save(pasta / "feed.png", optimize=True)
        render(post, "quadrado")[0].convert("RGB").save(pasta / "tiktok.jpg", quality=92, optimize=True)
        story, faixas = render(post, "vertical")
        story.save(pasta / "story.png", optimize=True)
        try:
            video(story, faixas, pasta / "reel.mp4")
        except Exception as e:  # o vídeo nunca deve impedir as imagens
            print("AVISO: vídeo não gerado:", e)
        else:
            marca.write_text(assinatura + "\n")
        print("ok", pasta)


if __name__ == "__main__":
    main(sys.argv[1:])

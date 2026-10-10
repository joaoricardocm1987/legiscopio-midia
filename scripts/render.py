"""Gera as artes do Legiscópio a partir de posts/<data>/post.json.

Saídas, na mesma pasta do post.json:
  feed.png    1080x1350 (Instagram)
  tiktok.jpg  1080x1080 (TikTok)

Campos do post.json:
  rotulo    texto curto acima do título (ex.: "VOTAÇÃO NA CÂMARA")
  titulo    manchete (até ~90 caracteres)
  destaque  número ou fato em destaque (ex.: "346 a 46"), opcional
  detalhe   uma ou duas frases de contexto, opcional
  fonte     linha de fonte (ex.: "Fonte: Câmara dos Deputados, 03/09/2026")
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

NAVY = (15, 42, 68)
YELLOW = (242, 183, 5)
WHITE = (255, 255, 255)
SOFT = (200, 214, 230)

FONT_DIRS = [Path("/usr/share/fonts/truetype/dejavu")]


def font(bold, size):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for d in FONT_DIRS:
        p = d / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise SystemExit(f"Fonte {name} não encontrada")


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, bold, start, minimum, max_w, max_lines):
    size = start
    while size > minimum:
        f = font(bold, size)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 4
    f = font(bold, minimum)
    return f, wrap(draw, text, f, max_w)[:max_lines]


def render(post, W, H):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    pad = 90
    max_w = W - 2 * pad
    d.rectangle([0, 0, W, 18], fill=YELLOW)

    blocks = []  # (lines, font, color, gap_after)
    if post.get("rotulo"):
        f = font(True, 30)
        blocks.append(([post["rotulo"].upper()], f, YELLOW, 28))
    f, lines = fit(d, post["titulo"], True, 72 if H > W else 64, 40, max_w, 4)
    blocks.append((lines, f, WHITE, 40))
    if post.get("destaque"):
        f, lines = fit(d, post["destaque"], True, 120 if H > W else 100, 56, max_w, 2)
        blocks.append((lines, f, YELLOW, 36))
    if post.get("detalhe"):
        f, lines = fit(d, post["detalhe"], False, 36, 26, max_w, 5 if H > W else 3)
        blocks.append((lines, f, SOFT, 0))

    def lh(f):
        a, b = f.getmetrics()
        return int((a + b) * 1.15)

    total = sum(lh(f) * len(ls) + g for ls, f, _, g in blocks)
    footer_h = 150
    y = max(70, (H - footer_h - total) // 2 + 20)
    for ls, f, color, gap in blocks:
        for line in ls:
            d.text((pad, y), line, font=f, fill=color)
            y += lh(f)
        y += gap

    d.line([pad, H - 130, W - pad, H - 130], fill=(45, 75, 105), width=2)
    if post.get("fonte"):
        d.text((pad, H - 108), post["fonte"], font=font(False, 24), fill=SOFT)
    brand = "Legiscópio"
    fb = font(True, 34)
    d.text((pad, H - 72), brand, font=fb, fill=WHITE)
    url = "legiscopio.com.br"
    fu = font(False, 26)
    d.text((W - pad - d.textlength(url, font=fu), H - 66), url, font=fu, fill=SOFT)
    return img


def main(paths):
    for p in paths:
        p = Path(p)
        post = json.loads(p.read_text(encoding="utf-8"))
        render(post, 1080, 1350).save(p.parent / "feed.png", optimize=True)
        render(post, 1080, 1080).save(p.parent / "tiktok.jpg", quality=92)
        print("ok", p.parent)


if __name__ == "__main__":
    main(sys.argv[1:])

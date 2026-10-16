"""Chamada do meio do vídeo: like, inscrever-se e sininho.

A Lupa fala sem trocar a tela (o último visual fica congelado) e aparece uma barra
com o joinha, o botão "Inscrever-se" e o sininho, que são "clicados" no momento em
que cada palavra é dita.
"""
import math

from PIL import Image, ImageDraw

FALA_PADRAO = ("Rapidinho: se este vídeo está te ajudando, deixa o seu like, se inscreve no canal "
               "e ativa o sininho pra não perder os próximos. Agora, vamos continuar!")

VERDE = (5, 87, 47)
VERDE_ESC = (3, 60, 32)
CINZA = (150, 160, 154)
CINZA_CL = (229, 232, 230)
TINTA = (16, 37, 26)
BRANCO = (255, 255, 255)
VERMELHO = (204, 0, 0)
AMARELO = (246, 196, 50)

S = 2  # super-amostragem do desenho


def _suave(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def _pulo(x):
    """0..1 -> pequeno 'pop' (sobe e volta)."""
    if x <= 0 or x >= 1:
        return 0.0
    return math.sin(x * math.pi)


def marcos(palavras, dur):
    """Instantes (s) em que 'like', 'inscreve' e 'sininho' são ditos."""
    alvos = {"like": None, "inscre": None, "sinin": None}
    for t, w in palavras or []:
        lw = "".join(ch for ch in w.lower() if ch.isalpha())
        for k in alvos:
            if alvos[k] is None and lw.startswith(k):
                alvos[k] = t
    padrao = {"like": dur * 0.30, "inscre": dur * 0.45, "sinin": dur * 0.62}
    return [alvos[k] if alvos[k] is not None else padrao[k] for k in ("like", "inscre", "sinin")]


def _joinha(d, cx, cy, r, ativo, f):
    cor = VERDE if ativo else CINZA
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BRANCO if not ativo else (232, 244, 236), outline=cor, width=int(6 * f))
    u = r / 50.0
    # manga
    d.rounded_rectangle([cx - 30 * u, cy - 4 * u, cx - 16 * u, cy + 30 * u], radius=4 * u, fill=cor)
    # mão
    d.rounded_rectangle([cx - 12 * u, cy - 6 * u, cx + 26 * u, cy + 30 * u], radius=8 * u, fill=cor)
    # polegar
    d.rounded_rectangle([cx - 10 * u, cy - 34 * u, cx + 4 * u, cy + 2 * u], radius=7 * u, fill=cor)
    for k in range(3):
        y = cy + 2 * u + k * 9 * u
        d.line([(cx + 4 * u, y), (cx + 26 * u, y)], fill=BRANCO if not ativo else (232, 244, 236), width=max(1, int(3 * u)))


def _sino(img, cx, cy, r, ativo, ang, f):
    camada = Image.new("RGBA", (int(r * 2.6), int(r * 2.6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    c = camada.width / 2
    cor = AMARELO if ativo else CINZA
    borda = TINTA if ativo else CINZA
    u = r / 50.0
    # corpo do sino
    d.pieslice([c - 30 * u, c - 38 * u, c + 30 * u, c + 22 * u], 180, 360, fill=cor, outline=borda, width=int(4 * f))
    d.polygon([(c - 30 * u, c - 8 * u), (c + 30 * u, c - 8 * u), (c + 40 * u, c + 22 * u), (c - 40 * u, c + 22 * u)],
              fill=cor, outline=borda)
    d.rectangle([c - 28 * u, c - 9 * u, c + 28 * u, c - 6 * u], fill=cor)
    d.rounded_rectangle([c - 44 * u, c + 20 * u, c + 44 * u, c + 30 * u], radius=4 * u, fill=cor, outline=borda,
                        width=int(3 * f))
    d.ellipse([c - 9 * u, c + 28 * u, c + 9 * u, c + 44 * u], fill=cor, outline=borda, width=int(3 * f))
    d.ellipse([c - 6 * u, c - 46 * u, c + 6 * u, c - 34 * u], fill=cor, outline=borda, width=int(3 * f))
    if ativo:  # ondas de "tocando"
        for k in (1, 2):
            rr = 50 * u + k * 12 * u
            d.arc([c - rr, c - rr - 6 * u, c + rr, c + rr - 6 * u], 205, 245, fill=AMARELO, width=int(5 * f))
            d.arc([c - rr, c - rr - 6 * u, c + rr, c + rr - 6 * u], 295, 335, fill=AMARELO, width=int(5 * f))
    camada = camada.rotate(ang, resample=Image.BICUBIC, center=(c, c - 40 * u))
    img.alpha_composite(camada, (int(cx - c), int(cy - c)))


def _cursor(d, x, y, esc, f):
    pts = [(0, 0), (0, 46), (12, 35), (21, 55), (29, 51), (20, 32), (36, 32)]
    pts = [(x + px * esc * f, y + py * esc * f) for px, py in pts]
    d.polygon(pts, fill=BRANCO, outline=TINTA)
    d.line(pts + [pts[0]], fill=TINTA, width=max(1, int(3 * f)))


def barra(t, mk, largura=1180, fonte_bd=None, fonte_bk=None):
    """Imagem RGBA da barra (like · inscrever-se · sininho) no instante t da cena."""
    t_like, t_insc, t_sino = mk
    W0, H0 = largura, 190
    img = Image.new("RGBA", (W0 * S, H0 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = S
    d.rounded_rectangle([6 * f, 10 * f, (W0 - 6) * f, (H0 - 4) * f], radius=34 * f, fill=(0, 0, 0, 40))
    d.rounded_rectangle([0, 0, (W0 - 10) * f, (H0 - 14) * f], radius=34 * f, fill=BRANCO, outline=(203, 214, 204),
                        width=3 * f)
    cy = (H0 - 14) / 2 * f

    # 1) joinha
    ativo_like = t >= t_like
    esc = 1 + 0.25 * _pulo((t - t_like) / 0.35)
    jx = 110 * f
    _joinha(d, jx, cy, 58 * f * esc, ativo_like, f)
    if fonte_bd:
        d.text((jx + 80 * f, cy), "Gostei", font=fonte_bd, fill=VERDE if ativo_like else CINZA,
               anchor="lm")

    # 2) botão inscrever-se
    ativo_insc = t >= t_insc
    esc2 = 1 - 0.08 * _pulo((t - t_insc) / 0.25)
    bx0, bx1 = 360 * f, 820 * f
    bw = (bx1 - bx0) * esc2
    bh = 104 * f * esc2
    bcx = (bx0 + bx1) / 2
    d.rounded_rectangle([bcx - bw / 2, cy - bh / 2, bcx + bw / 2, cy + bh / 2], radius=bh / 2,
                        fill=CINZA_CL if ativo_insc else VERMELHO)
    if fonte_bk:
        d.text((bcx, cy), "INSCRITO ✓" if ativo_insc else "INSCREVER-SE", font=fonte_bk,
               fill=TINTA if ativo_insc else BRANCO, anchor="mm")

    # 3) sininho
    ativo_sino = t >= t_sino
    ang = 18 * math.sin((t - t_sino) * 18) * max(0.0, 1 - (t - t_sino) / 1.2) if ativo_sino else 0
    _sino(img, 980 * f, cy - 6 * f, 54 * f, ativo_sino, ang, f)

    # cursor: vai até cada botão um pouco antes do clique
    alvos = [(t_like, (jx + 10 * f, cy + 10 * f)), (t_insc, (bcx + 120 * f, cy + 14 * f)),
             (t_sino, (980 * f + 10 * f, cy + 20 * f))]
    pos = None
    ini = (W0 * f * 0.55, H0 * f * 1.2)
    ant_t, ant_p = max(0.0, t_like - 0.9), ini
    for tk, pk in alvos:
        if t < tk:
            k = _suave((t - (tk - 0.6)) / 0.6) if t > tk - 0.6 else 0.0
            pos = (ant_p[0] + (pk[0] - ant_p[0]) * k, ant_p[1] + (pk[1] - ant_p[1]) * k)
            if t < ant_t:
                pos = ant_p
            break
        ant_t, ant_p = tk, pk
    if pos is None:
        pos = ant_p
    clique = min(abs(t - tk) for tk, _ in alvos)
    esc_c = 1 - 0.18 * (1 - min(1, clique / 0.15))
    if t_like - 0.9 <= t <= t_sino + 1.5:
        _cursor(d, pos[0], pos[1], esc_c, f)

    return img.resize((W0, H0), Image.LANCZOS)

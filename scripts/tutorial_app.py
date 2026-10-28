"""Vídeo-tutorial do app Legiscópio (independente da rotina diária).

Lê videos/tutorial-app/tutorial.json (longo, 1920x1080) e short.json (vertical, 1080x1920).
Cada cena mostra uma captura real do app dentro de um celular e acende "destaques"
(holofote + anel pulsando + toque + lupa de aumento) no instante em que a palavra "em" é dita.

Usa video_longo / personagem / cta_meio só como bibliotecas: nada da rotina é alterado.

Formato da cena:
  {"tela": "feed_tudo.png", "secao": "ABA FEED", "titulo": "...", "capitulo": "...",
   "transicao": "lado" | "rolar", "tipo": "capa" | "fim",
   "fala": "...",
   "destaques": [{"caixa": [x0,y0,x1,y1], "em": "palavra", "rotulo": "...", "toque": true}]}
Coordenadas das caixas no espaço da captura (380x608). "borrar": {tela: [[caixas]]} pixeliza
nomes, fotos e dados pessoais antes de tudo.
"""
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cta_meio  # noqa: E402
import personagem  # noqa: E402
import video_longo as vl  # noqa: E402

VERSAO = "1"
FPS, SR = vl.FPS, vl.SR
PAUSA = 0.4
T_TRANS = 0.45  # duração da transição entre telas
T_MOVE = 0.45  # holofote indo de um destaque ao outro
SW, SH = 380, 608  # tamanho das capturas


# ------------------------------------------------------------------ telas

def carregar_telas(pasta, borrar):
    telas = {}
    for p in sorted((pasta / "telas").glob("*.png")):
        im = Image.open(p).convert("RGB")
        if im.size != (SW, SH):
            im = im.resize((SW, SH), Image.LANCZOS)
        for x0, y0, x1, y1 in borrar.get(p.name, []):
            reg = im.crop((x0, y0, x1, y1))
            w, h = reg.size
            pix = reg.resize((max(1, w // 9), max(1, h // 9)), Image.BILINEAR).resize((w, h), Image.NEAREST)
            im.paste(pix.filter(ImageFilter.GaussianBlur(3)), (x0, y0))
        telas[p.name] = im
    return telas


class Celular:
    """Moldura de celular com a tela escalada."""

    def __init__(self, escala):
        self.k = escala
        self.sw, self.sh = round(SW * escala), round(SH * escala)
        b = round(14 * escala)
        topo = round(26 * escala)
        self.b, self.topo = b, topo
        self.W, self.H = self.sw + 2 * b, self.sh + topo + b + round(14 * escala)
        m = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(m)
        r = round(46 * escala)
        d.rounded_rectangle([0, 0, self.W - 1, self.H - 1], radius=r, fill=(18, 28, 22, 255))
        d.rounded_rectangle([3, 3, self.W - 4, self.H - 4], radius=r - 3, outline=(70, 86, 76, 255), width=2)
        cx = self.W // 2
        d.rounded_rectangle([cx - 46 * escala, topo * 0.32, cx + 46 * escala, topo * 0.32 + 12 * escala],
                            radius=6 * escala, fill=(45, 58, 50, 255))
        self.moldura = m
        # sombra
        s = Image.new("RGBA", (self.W + 80, self.H + 80), (0, 0, 0, 0))
        ImageDraw.Draw(s).rounded_rectangle([40, 52, self.W + 40, self.H + 52], radius=r, fill=(0, 40, 20, 70))
        self.sombra = s.filter(ImageFilter.GaussianBlur(18))
        self.mascara = Image.new("L", (self.sw, self.sh), 0)
        ImageDraw.Draw(self.mascara).rounded_rectangle([0, 0, self.sw - 1, self.sh - 1], radius=round(10 * escala),
                                                       fill=255)
        self._cache = {}

    def tela(self, im):
        key = id(im)
        if key not in self._cache:
            self._cache[key] = im.resize((self.sw, self.sh), Image.LANCZOS)
        return self._cache[key]

    def caixa(self, c):
        return [c[0] * self.k, c[1] * self.k, c[2] * self.k, c[3] * self.k]


def lerp(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def holofote(tela, cx, alfa, pulso, toque_k, cel):
    """Escurece tudo fora da caixa cx (em px da tela escalada) e desenha anel e toque."""
    out = tela.convert("RGBA")
    if alfa <= 0.01 or cx is None:
        return out
    pad = 5 * cel.k
    x0, y0, x1, y1 = cx[0] - pad, cx[1] - pad, cx[2] + pad, cx[3] + pad
    r = min(14 * cel.k, (y1 - y0) / 2, (x1 - x0) / 2)
    escuro = Image.new("L", out.size, int(150 * alfa))
    ImageDraw.Draw(escuro).rounded_rectangle([x0, y0, x1, y1], radius=r, fill=0)
    out.paste(Image.new("RGBA", out.size, (4, 22, 12, 255)), (0, 0), escuro)
    d = ImageDraw.Draw(out)
    a = int(255 * alfa)
    e = 3 + 3 * pulso
    d.rounded_rectangle([x0 - e, y0 - e, x1 + e, y1 + e], radius=r + e,
                        outline=(185, 216, 106, int(a * (0.55 - 0.35 * pulso))), width=max(2, int(4 * cel.k)))
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=(185, 216, 106, a), width=max(3, int(3 * cel.k)))
    if toque_k is not None and 0 <= toque_k <= 1:
        cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
        rr = (14 + 40 * toque_k) * cel.k
        d.ellipse([cxm - rr, cym - rr, cxm + rr, cym + rr], outline=(255, 255, 255, int(220 * (1 - toque_k))),
                  width=max(3, int(4 * cel.k)))
        rp = 13 * cel.k * (1 - 0.25 * math.sin(math.pi * min(1, toque_k * 2)))
        d.ellipse([cxm - rp, cym - rp, cxm + rp, cym + rp], fill=(255, 255, 255, int(170 * (1 - toque_k))))
    return out


def tempos_destaques(c, palavras, dur):
    """Instante de cada destaque: quando a palavra-chave é dita (em ordem)."""
    ds = c.get("destaques", [])
    out, j, ult = [], 0, 0.15
    for k, d in enumerate(ds):
        alvo = vl._norm(d.get("em", ""))
        achou = None
        for m in range(j, len(palavras)):
            if alvo and vl._norm(palavras[m][1]).startswith(alvo[: max(3, min(len(alvo), 6))]):
                achou = m
                break
        if achou is not None:
            t = max(ult, palavras[achou][0] - 0.15)
            j = achou + 1
        else:
            t = max(ult, dur * (k + 0.5) / max(1, len(ds)))
        out.append(t)
        ult = t + 0.3
    return out


def estado_holofote(ds, ts, t, cel):
    """(caixa atual interpolada, alfa, pulso, toque_k, índice ativo)."""
    if not ds or t < ts[0] - 0.05:
        return None, 0.0, 0.0, None, -1
    k = max(i for i, ti in enumerate(ts) if ti <= t + 0.05)
    t0 = ts[k]
    cx = cel.caixa(ds[k]["caixa"])
    if k > 0:
        ant = cel.caixa(ds[k - 1]["caixa"])
        m = vl.suave((t - t0) / T_MOVE)
        cx = lerp(ant, cx, m)
        alfa = 1.0
    else:
        alfa = vl.suave((t - t0) / 0.35)
    pulso = 0.5 + 0.5 * math.sin((t - t0) * 2 * math.pi / 1.1)
    toque = None
    if ds[k].get("toque"):
        tk = (t - t0 - T_MOVE * (k > 0)) / 0.6
        if 0 <= tk <= 1:
            toque = tk
    return cx, alfa, pulso, toque, k


# ------------------------------------------------------------------ áudio

AUDIO = None  # pasta do cache de narração (videos/tutorial-app/audio)
FALA_CTA = ("Rapidinho: se este tutorial está te ajudando, deixa o seu like, "
            "se inscreve no canal e ativa o sininho pra não perder os próximos. Agora, vamos continuar!")


def _chave(texto, voz, taxa):
    return hashlib.sha256(f"{voz}|{taxa}|{texto}".encode()).hexdigest()[:16]


def tts(texto, voz, taxa, tmp, i):
    """vl.tts com cache em disco (mp3 + tempos das palavras), para o áudio ser feito uma vez só."""
    if os.environ.get("LEGIS_FAKE_TTS") or AUDIO is None:
        return vl.tts(texto, voz, taxa, tmp, i)
    k = _chave(texto, voz, taxa)
    mp3, js = AUDIO / f"{k}.mp3", AUDIO / f"{k}.json"
    if not (mp3.exists() and js.exists()):
        import asyncio
        AUDIO.mkdir(parents=True, exist_ok=True)
        try:
            import edge_tts  # noqa: F401
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "edge-tts"], check=True)
        for tentativa in range(4):
            try:
                palavras = asyncio.run(vl._tts(texto, voz, taxa, mp3))
                break
            except Exception as e:
                print("TTS falhou, tentando de novo:", e)
                if tentativa == 3:
                    raise
        js.write_text(json.dumps(palavras, ensure_ascii=False), encoding="utf-8")
    palavras = [tuple(x) for x in json.loads(js.read_text(encoding="utf-8"))]
    wav = tmp / f"c{i:02d}.raw"
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", str(SR),
                    "-f", "s16le", str(wav)], check=True)
    return wav.read_bytes(), palavras


def preparar_audio(pasta):
    """Só gera (ou confere) o cache de narração de todas as falas."""
    global AUDIO
    pasta = Path(pasta)
    AUDIO = pasta / "audio"
    cfg = json.loads((pasta / "tutorial.json").read_text(encoding="utf-8"))
    sj = pasta / "short.json"
    falas = [c["fala"] for c in cfg["cenas"]] + [cfg.get("cta_meio_fala") or FALA_CTA]
    if sj.exists():
        falas += [c["fala"] for c in json.loads(sj.read_text(encoding="utf-8"))["cenas"]]
    tmp = pasta / "_tmp_audio"
    tmp.mkdir(exist_ok=True)
    for i, f in enumerate(falas):
        tts(f, cfg.get("voz", "pt-BR-FranciscaNeural"), cfg.get("velocidade", "-5%"), tmp, i)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"narração pronta: {len(falas)} falas em {AUDIO}")


# fala -> legenda: o que é dito por extenso aparece escrito como endereço
TROCAS = {
    "legiscopio ponto com ponto br": "www.legiscopio.com.br",
    "apoia ponto se barra legiscopio": "apoia.se/legiscopio",
}


def legendas(palavras, dur, fala):
    """vl.blocos_legenda, trocando endereços falados por extenso pela forma escrita."""
    if not palavras:
        return vl.blocos_legenda(palavras, dur, fala)
    al = [(t, w) for t, w in vl.alinhar(palavras, fala)]
    for falado, escrito in TROCAS.items():
        alvo = falado.split()
        out, k = [], 0
        while k < len(al):
            achou = False
            for n in range(1, len(alvo) + 1):
                if k + n > len(al):
                    break
                trecho = " ".join(w for _, w in al[k:k + n])
                limpo = trecho.rstrip(".,;:!?")
                if vl._norm(limpo) == vl._norm(falado) and limpo.lower().split() == alvo:
                    resto = trecho[len(limpo):]
                    out.append((al[k][0], escrito + ("⁠" if resto == "." else resto)))
                    k += n
                    achou = True
                    break
            if not achou:
                out.append(al[k])
                k += 1
        al = out
    # blocos de até ~46 caracteres, quebrando ANTES da palavra que estouraria o limite
    blocos, atual, ini = [], [], None
    for t, w in al:
        if atual and len(" ".join(atual + [w])) > 46:
            blocos.append([ini, " ".join(atual).replace("⁠", "")])
            atual, ini = [], None
        if ini is None:
            ini = t
        atual.append(w)
        if w.endswith((".", "?", "!", ":", "⁠")):
            blocos.append([ini, " ".join(atual).replace("⁠", "")])
            atual, ini = [], None
    if atual:
        blocos.append([ini, " ".join(atual).replace("⁠", "")])
    for k in range(len(blocos)):
        blocos[k].append(blocos[k + 1][0] if k + 1 < len(blocos) else dur)
    return blocos


def narrar(cenas, cfg, tmp):
    voz = cfg.get("voz", "pt-BR-FranciscaNeural")
    taxa = cfg.get("velocidade", "-5%")
    out = []
    for i, c in enumerate(cenas):
        amostras, palavras = tts(c["fala"], voz, taxa, tmp, i)
        dur = len(amostras) / 2 / SR
        out.append(dict(c, amostras=amostras, palavras=palavras, dur=dur + PAUSA, voz_dur=dur))
        print(f"cena {i + 1}/{len(cenas)}: {dur:.1f}s")
    return out


def escrever_wav(cenas, destino):
    silencio = bytes(int(PAUSA * SR) * 2)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(c["amostras"] + silencio for c in cenas))


def abrir_ffmpeg(W, H, wav, destino):
    cmd = [vl.ffmpeg(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(wav),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(destino)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def pose(c, t, nivel, ativo_t, ultima):
    tipo = c.get("tipo")
    if c.get("_cta"):
        nome = "joinha" if t > c["_mk"][0] else "explicando"
    elif tipo == "capa":
        nome = "acenando" if t < 2.6 else "explicando"
    elif tipo == "fim":
        nome = "acenando" if t > 2 else "explicando"
    elif ativo_t is not None and 0 <= ativo_t < 1.3:
        nome = "apontando"
    else:
        nome = "explicando"
    boca = "fechada" if nivel < 0.18 else ("meia" if nivel < 0.5 else "aberta")
    if ultima and nivel < 0.18:
        boca = "sorriso"
    return nome, boca, "abertos"


def piscar(qg, olhos):
    return "fechados" if qg % (FPS * 4) < 3 and olhos == "abertos" else olhos


# ------------------------------------------------------------------ tela do celular no instante t

def tela_no_instante(c, ant, t, telas, cel, ts):
    """Imagem RGBA da tela (já com holofote), com transição a partir da cena anterior."""
    im = cel.tela(telas[c["tela"]])
    if c.get("_cta"):
        ds, ts_ = c.get("_ds", []), c.get("_ts", [])
        cx, alfa, pulso, _, _ = estado_holofote(ds, ts_, 1e9, cel)
        return holofote(im, cx, alfa * 0.6, 0, None, cel)
    ds = c.get("destaques", [])
    cx, alfa, pulso, toque, k = estado_holofote(ds, ts, t, cel)
    atual = holofote(im, cx, alfa, pulso, toque, cel)
    if ant is None or t >= T_TRANS or ant["tela"] == c["tela"] and not c.get("transicao"):
        return atual
    m = vl.suave(t / T_TRANS)
    velho = holofote(cel.tela(telas[ant["tela"]]), None, 0, 0, None, cel)
    comp = Image.new("RGBA", atual.size, (255, 255, 255, 255))
    if c.get("transicao") == "rolar":
        dy = int(cel.sh * m)
        comp.paste(velho, (0, -dy))
        comp.paste(atual, (0, cel.sh - dy))
    elif ant["tela"] != c["tela"]:
        dx = int(cel.sw * m)
        comp.paste(velho, (-dx, 0))
        comp.paste(atual, (cel.sw - dx, 0))
    else:
        return atual
    return comp


def montar_celular(tela_rgba, cel):
    m = cel.moldura.copy()
    tela = tela_rgba.copy()
    tela.putalpha(cel.mascara)
    m.alpha_composite(tela, (cel.b, cel.topo))
    return m


# ------------------------------------------------------------------ longo (1920x1080)

LW, LH = 1920, 1080
CEL_X, CEL_Y = 820, 70
ESQ = (70, 600)  # coluna de texto


def fundo_longo():
    img = Image.new("RGB", (LW, LH), vl.FUNDO)
    d = ImageDraw.Draw(img)
    lg = vl.logo(84)
    if lg:
        img.paste(lg, (70, 34), lg)
    d.text((LW - 70, 64), "TUTORIAL DO APP", font=vl.MO(26), fill=vl.OLIVA, anchor="ra")
    d.text((LW - 70, 104), "app.legiscopio.com.br", font=vl.MO(22), fill=vl.TEXTO2, anchor="ra")
    d.text((70, LH - 26), "legiscopio.com.br  ·  apoia.se/legiscopio", font=vl.MO(20), fill=vl.TEXTO2, anchor="ls")
    return img


def coluna_texto(c, k_ativo, t_ativo, n_cena, t):
    """Camada RGBA da coluna esquerda: seção, título e rótulo do destaque."""
    x0, x1 = ESQ
    cam = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    ent = vl.suave(t / 0.5)
    off = int(30 * (1 - ent))
    a = int(255 * ent)
    y = 170 + off
    sec = c.get("secao", "")
    if sec:
        f = vl.MO(24)
        w = d.textlength(sec, font=f) + 40
        d.rounded_rectangle([x0, y, x0 + w, y + 46], radius=12, fill=vl.VERDE + (a,))
        d.text((x0 + 20, y + 23), sec, font=f, fill=vl.LIMA + (a,), anchor="lm")
        y += 72
    f = vl.BK(60)
    for l in vl.wrap(d, c.get("titulo", ""), f, x1 - x0 + 120)[:3]:
        d.text((x0, y), l, font=f, fill=vl.VERDE + (a,))
        y += 74
    y += 26
    if c.get("tipo") == "capa":
        for l in ["Tela por tela,", "pra que serve", "cada botão."]:
            d.text((x0, y), l, font=vl.BD(46), fill=vl.TEXTO + (a,))
            y += 62
        return cam, y
    if c.get("tipo") == "fim":
        d.rounded_rectangle([x0, y, x1 + 130, y + 200], radius=26, fill=vl.VERDE + (a,))
        d.text((x0 + 40, y + 34), "Acesse", font=vl.BD(36), fill=vl.LIMA_TX + (a,))
        d.text((x0 + 40, y + 84), "www.legiscopio.com.br", font=vl.BK(50), fill=vl.BRANCO + (a,))
        d.text((x0 + 40, y + 154), "Android: já disponível · iOS: em breve", font=vl.RG(28), fill=vl.LIMA_TX + (a,))
        return cam, y + 220
    ds = c.get("destaques", [])
    if k_ativo >= 0:
        dd = ds[k_ativo]
        e2 = vl.suave(t_ativo / 0.35)
        aa = int(255 * e2)
        yy = y + int(20 * (1 - e2))
        num = f"{k_ativo + 1}"
        d.ellipse([x0, yy, x0 + 64, yy + 64], fill=vl.LIMA + (aa,))
        d.text((x0 + 32, yy + 32), num, font=vl.BK(36), fill=vl.VERDE_ESC + (aa,), anchor="mm")
        fr = vl.BD(44)
        ly = yy + 6
        for l in vl.wrap(d, dd.get("rotulo", ""), fr, x1 - x0 + 40)[:2]:
            d.text((x0 + 88, ly), l, font=fr, fill=vl.TEXTO + (aa,))
            ly += 56
        y = max(ly, yy + 70) + 30
        # pontinhos de progresso
        for m in range(len(ds)):
            cor = vl.VERDE if m == k_ativo else vl.BORDA
            d.ellipse([x0 + m * 26, y, x0 + m * 26 + 14, y + 14], fill=cor + (a,))
        y += 44
    return cam, y


def lupa_aumento(tela_orig, caixa, y_topo, t_ativo, cel):
    """Recorte ampliado da área destacada (só para áreas pequenas)."""
    x0, y0, x1, y1 = caixa
    w, h = x1 - x0, y1 - y0
    larg_max, alt_max = 640, max(120, 880 - y_topo)
    esc = min(larg_max / w, alt_max / h, 3.2)
    if esc < 2.0 or alt_max < 120:
        return None
    pad = 2
    rec = tela_orig.crop((max(0, x0 - pad), max(0, y0 - pad), min(SW, x1 + pad), min(SH, y1 + pad)))
    rec = rec.resize((round(rec.width * esc), round(rec.height * esc)), Image.LANCZOS)
    e = vl.suave((t_ativo - 0.15) / 0.35)
    if e <= 0.01:
        return None
    card = Image.new("RGBA", (rec.width + 24, rec.height + 24), (0, 0, 0, 0))
    dc = ImageDraw.Draw(card)
    dc.rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=22, fill=(255, 255, 255, 255),
                         outline=vl.LIMA + (255,), width=5)
    m = Image.new("L", rec.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, rec.width - 1, rec.height - 1], radius=16, fill=255)
    card.paste(rec, (12, 12), m)
    if e < 0.99:
        card = card.resize((max(1, int(card.width * (0.85 + 0.15 * e))),
                            max(1, int(card.height * (0.85 + 0.15 * e)))), Image.LANCZOS)
        card.putalpha(card.getchannel("A").point(lambda v: int(v * e)))
    return card


def legenda_longa(texto):
    f = vl.BD(34)
    tmp = Image.new("RGBA", (LW, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    linhas = vl.wrap(d, texto, f, 700)[:2]
    hh = len(linhas) * 46 + 28
    larg = max(d.textlength(l, font=f) for l in linhas) + 56
    d.rounded_rectangle([0, 0, larg, hh], radius=18, fill=(3, 60, 32, 235))
    for k, l in enumerate(linhas):
        d.text((28, 14 + k * 46), l, font=f, fill=vl.BRANCO)
    return tmp.crop((0, 0, int(larg) + 2, hh)), hh


def gerar_longo(pasta, cfg, telas, tmp):
    cel = Celular(1.48)
    cenas = narrar(cfg["cenas"], cfg, tmp)
    # chamada do meio (like / inscrever-se / sininho) na divisa mais perto da metade
    total = sum(c["dur"] for c in cenas)
    acum, melhor, dist = 0.0, None, None
    for k, c in enumerate(cenas[:-1]):
        acum += c["dur"]
        if k == 0 or cenas[k + 1].get("tipo") == "fim":
            continue
        if dist is None or abs(acum - total / 2) < dist:
            melhor, dist = k + 1, abs(acum - total / 2)
    if melhor:
        fala = cfg.get("cta_meio_fala") or FALA_CTA
        amostras, palavras = tts(fala, cfg.get("voz", "pt-BR-FranciscaNeural"), cfg.get("velocidade", "-5%"), tmp, 99)
        dur = len(amostras) / 2 / SR
        ant = cenas[melhor - 1]
        ts_ant = tempos_destaques(ant, ant["palavras"], ant["voz_dur"])
        cenas.insert(melhor, dict(fala=fala, tela=ant["tela"], secao=ant.get("secao"), titulo=ant.get("titulo"),
                                  _cta=True, _ds=ant.get("destaques", []), _ts=ts_ant, destaques=[],
                                  amostras=amostras, palavras=palavras, dur=dur + PAUSA, voz_dur=dur,
                                  _mk=cta_meio.marcos(palavras, dur)))
    wav = tmp / "narracao.wav"
    escrever_wav(cenas, wav)
    destino = pasta / "tutorial.mp4"
    proc = abrir_ffmpeg(LW, LH, wav, destino)
    base = fundo_longo()
    srt, caps, n_srt, t_glob, qg = [], [], 1, 0.0, 0
    for i, c in enumerate(cenas):
        dur = c["dur"]
        nq = int(round(dur * FPS))
        env = vl.envelope(c["amostras"], nq)
        legs = legendas(c["palavras"], c["voz_dur"], c["fala"])
        for ini, txt, fim in legs:
            srt.append(f"{n_srt}\n{vl.srt_tempo(t_glob + ini)} --> {vl.srt_tempo(t_glob + fim)}\n{txt}\n")
            n_srt += 1
        if c.get("capitulo"):
            caps.append((t_glob, c["capitulo"]))
        ds = c.get("destaques", [])
        ts = tempos_destaques(c, c["palavras"], c["voz_dur"])
        ant = cenas[i - 1] if i > 0 else None
        cache_leg = chave_leg = None
        cache_col = chave_col = None
        for q in range(nq):
            t = q / FPS
            cx, alfa, pulso, toque, k = estado_holofote(ds, ts, t, cel)
            t_ativo = t - ts[k] if k >= 0 else None
            quadro = base.copy()
            # celular
            tela = tela_no_instante(c, ant, t, telas, cel, ts)
            cel_img = montar_celular(tela, cel)
            quadro.paste(cel.sombra, (CEL_X - 40, CEL_Y - 40), cel.sombra)
            quadro.paste(cel_img, (CEL_X, CEL_Y), cel_img)
            # coluna da esquerda
            if c.get("_cta"):
                chave = ("cta", min(1.0, round(t / 0.5, 2)))
                if chave != chave_col:
                    cache_col = coluna_texto(dict(c, destaques=[]), -1, None, i, 9)
                    chave_col = chave
                quadro.paste(cache_col[0], (0, 0), cache_col[0])
                bar = cta_meio.barra(t, c["_mk"], fonte_bd=vl.BD(88), fonte_bk=vl.BK(84))
                bar = bar.resize((700, round(bar.height * 700 / bar.width)), Image.LANCZOS)
                ent = vl.suave(t / 0.4) * vl.suave((dur - PAUSA - t + 0.2) / 0.4)
                if ent > 0.02:
                    if ent < 0.98:
                        bar = bar.copy()
                        bar.putalpha(bar.getchannel("A").point(lambda x: int(x * ent)))
                    quadro.paste(bar, (40, int(520 + 60 * (1 - ent))), bar)
            else:
                chave = (k, round(min(1.0, t / 0.5), 2), round(min(1.0, (t_ativo or 0) / 0.5), 2))
                if chave != chave_col:
                    col, y_fim = coluna_texto(c, k, t_ativo, i, t)
                    if k >= 0:
                        lz = lupa_aumento(telas[c["tela"]], ds[k]["caixa"], y_fim, t_ativo, cel)
                        if lz is not None:
                            col.alpha_composite(lz, (ESQ[0], y_fim))
                    cache_col = (col, y_fim)
                    chave_col = chave
                quadro.paste(cache_col[0], (0, 0), cache_col[0])
            # Lupa 2.0
            nivel = env[q] if q < len(env) else 0
            nome, boca, olhos = pose(c, t, nivel, t_ativo, i == len(cenas) - 1)
            sp = personagem.pose(nome, boca, piscar(qg, olhos), 640, qg / FPS, -1, espelho=True)
            quadro.paste(sp, (LW - sp.width + 30, LH - sp.height - 30), sp)
            # legenda (embaixo, à esquerda)
            atual = next((txt for ini, txt, fim in legs if ini <= t < fim), "")
            if atual != chave_leg:
                cache_leg = legenda_longa(atual) if atual else None
                chave_leg = atual
            if cache_leg:
                li, hh = cache_leg
                quadro.paste(li, (ESQ[0] - 10, LH - 60 - hh), li)
            proc.stdin.write(quadro.convert("RGB").tobytes())
            qg += 1
        t_glob += dur
        print(f"tutorial: cena {i + 1}/{len(cenas)} ({t_glob / 60:.1f} min)")
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou")
    (pasta / "legendas.srt").write_text("\n".join(srt), encoding="utf-8")
    linhas = []
    for t0, nome in caps:
        m, s = divmod(int(t0), 60)
        linhas.append(f"{m:02d}:{s:02d} {nome}")
    (pasta / "capitulos.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"ok {destino} ({t_glob / 60:.1f} min)")
    return cel


def miniatura(pasta, cfg, telas):
    img = Image.new("RGB", (1280, 720), vl.FUNDO)
    d = ImageDraw.Draw(img)
    cel = Celular(0.98)
    tela = holofote(cel.tela(telas["votos.png"]), cel.caixa([318, 222, 372, 560]), 1.0, 0.5, None, cel)
    ci = montar_celular(tela, cel).rotate(-6, resample=Image.BICUBIC, expand=True)
    img.paste(ci, (700, 20), ci)
    lg = vl.logo(70)
    if lg:
        img.paste(lg, (50, 40), lg)
    th = cfg.get("thumb", {})
    y = 190
    for l, cor in ((th.get("linha1", "O Congresso"), vl.VERDE), (th.get("linha2", "no seu celular"), vl.TEXTO)):
        for p in vl.wrap(d, l, vl.BK(92), 640):
            d.text((50, y), p, font=vl.BK(92), fill=cor)
            y += 104
    d.rounded_rectangle([50, y + 20, 470, y + 100], radius=20, fill=vl.VERDE)
    d.text((260, y + 60), "TUTORIAL", font=vl.BK(48), fill=vl.LIMA, anchor="mm")
    sp = personagem.pose("surpresa", "o", "surpresos", 420, 0, -1, espelho=True)
    img.paste(sp, (1280 - sp.width + 40, 720 - sp.height + 20), sp)
    img.save(pasta / "thumb.jpg", quality=92)


# ------------------------------------------------------------------ Short (1080x1920)

VW, VH = 1080, 1920
V_CEL_Y = 286
V_LEG_Y = 1520


def fundo_vertical():
    img = Image.new("RGB", (VW, VH), vl.FUNDO)
    d = ImageDraw.Draw(img)
    lg = vl.logo(80)
    if lg:
        img.paste(lg, (60, 60), lg)
    d.rounded_rectangle([VW - 400, 62, VW - 60, 112], radius=14, fill=vl.VERDE)
    d.text((VW - 230, 87), "TUTORIAL DO APP", font=vl.MO(24), fill=vl.LIMA, anchor="mm")
    return img


def rotulo_vertical(c, k, t_ativo):
    ds = c.get("destaques", [])
    txt = ds[k]["rotulo"] if k >= 0 else c.get("titulo", "")
    f = vl.BK(46)
    tmp = Image.new("RGBA", (VW, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    l = vl.wrap(d, txt, f, 900)[0] if txt else ""
    if not l:
        return None
    w = d.textlength(l, font=f) + 60
    x0 = (VW - w) / 2
    d.rounded_rectangle([x0, 0, x0 + w, 80], radius=40, fill=vl.LIMA + (255,))
    d.text((VW / 2, 40), l, font=f, fill=vl.VERDE_ESC, anchor="mm")
    return tmp.crop((0, 0, VW, 82))


def gerar_short(pasta, cfg, sh, telas, tmp):
    cel = Celular(1.85)
    cx_cel = (VW - cel.W) // 2
    cenas = narrar(sh["cenas"], cfg, tmp)
    wav = tmp / "narracao_short.wav"
    escrever_wav(cenas, wav)
    destino = pasta / "short.mp4"
    proc = abrir_ffmpeg(VW, VH, wav, destino)
    base = fundo_vertical()
    t_glob, qg = 0.0, 0
    for i, c in enumerate(cenas):
        dur = c["dur"]
        nq = int(round(dur * FPS))
        env = vl.envelope(c["amostras"], nq)
        legs = legendas(c["palavras"], c["voz_dur"], c["fala"])
        ds = c.get("destaques", [])
        ts = tempos_destaques(c, c["palavras"], c["voz_dur"])
        ant = cenas[i - 1] if i > 0 else None
        cache_leg = chave_leg = None
        cache_rot = chave_rot = None
        for q in range(nq):
            t = q / FPS
            _, _, _, _, k = estado_holofote(ds, ts, t, cel)
            t_ativo = t - ts[k] if k >= 0 else None
            quadro = base.copy()
            tela = tela_no_instante(c, ant, t, telas, cel, ts)
            ci = montar_celular(tela, cel)
            quadro.paste(cel.sombra, (cx_cel - 40, V_CEL_Y - 40), cel.sombra)
            quadro.paste(ci, (cx_cel, V_CEL_Y), ci)
            if (k, c.get("titulo")) != chave_rot:
                cache_rot = rotulo_vertical(c, k, t_ativo)
                chave_rot = (k, c.get("titulo"))
            if cache_rot is not None:
                quadro.paste(cache_rot, (0, 178), cache_rot)
            nivel = env[q] if q < len(env) else 0
            nome, boca, olhos = pose(c, t, nivel, t_ativo, i == len(cenas) - 1)
            if nome == "apontando":
                nome = "explicando"
            sp = personagem.pose(nome, boca, piscar(qg, olhos), 470, qg / FPS, 0)
            quadro.paste(sp, (-40, VH - sp.height - 20), sp)
            atual = next((txt for ini, txt, fim in legs if ini <= t < fim), "")
            if atual != chave_leg:
                cache_leg = legenda_vertical(atual) if atual else None
                chave_leg = atual
            if cache_leg:
                quadro.paste(cache_leg, (0, V_LEG_Y), cache_leg)
            proc.stdin.write(quadro.convert("RGB").tobytes())
            qg += 1
        t_glob += dur
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou")
    print(f"ok {destino} ({t_glob:.1f} s)")
    if t_glob > 62:
        print(f"AVISO: short com {t_glob:.1f}s (meta: até 60s)")


def legenda_vertical(texto):
    f = vl.BD(50)
    tmp = Image.new("RGBA", (VW, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    linhas = vl.wrap(d, texto, f, 540)[:2]
    hh = len(linhas) * 64 + 36
    larg = max(d.textlength(l, font=f) for l in linhas) + 60
    x0 = 370 + (540 + 60 - larg) / 2
    d.rounded_rectangle([x0, 0, x0 + larg, hh], radius=22, fill=(3, 60, 32, 235))
    for k, l in enumerate(linhas):
        d.text((x0 + larg / 2, 18 + k * 64), l, font=f, fill=vl.BRANCO, anchor="mt")
    return tmp.crop((0, 0, VW, hh))


# ------------------------------------------------------------------ entrada

def gerar(pasta, so_short=False):
    global AUDIO
    pasta = Path(pasta)
    AUDIO = pasta / "audio"
    tj = pasta / "tutorial.json"
    cfg = json.loads(tj.read_text(encoding="utf-8"))
    sj = pasta / "short.json"
    sh = json.loads(sj.read_text(encoding="utf-8")) if sj.exists() else None
    telas = carregar_telas(pasta, cfg.get("borrar", {}))
    for c in cfg["cenas"] + (sh["cenas"] if sh else []):
        if c["tela"] not in telas:
            raise SystemExit(f"tela não encontrada: {c['tela']}")
    fake = str(bool(os.environ.get("LEGIS_FAKE_TTS"))).encode()
    hash_telas = b"".join(sorted(hashlib.sha256((pasta / "telas" / n).read_bytes()).digest() for n in telas))
    dep = b"".join((Path(m.__file__).read_bytes()) for m in (vl, personagem, cta_meio))
    tmp = pasta / "_tmp_tutorial"
    tmp.mkdir(exist_ok=True)
    if not so_short:
        ass = hashlib.sha256(tj.read_bytes() + hash_telas + VERSAO.encode() + fake
                             + hashlib.sha256(Path(__file__).read_bytes() + dep).digest()).hexdigest()
        marca = pasta / ".tutorial_render"
        if marca.exists() and marca.read_text().strip() == ass and (pasta / "tutorial.mp4").exists():
            print("tutorial sem mudanças")
        else:
            miniatura(pasta, cfg, telas)
            gerar_longo(pasta, cfg, telas, tmp)
            marca.write_text(ass + "\n")
    if sh:
        ass = hashlib.sha256(sj.read_bytes() + tj.read_bytes() + hash_telas + VERSAO.encode() + fake
                             + hashlib.sha256(Path(__file__).read_bytes() + dep).digest()).hexdigest()
        marca = pasta / ".tutorial_short_render"
        if marca.exists() and marca.read_text().strip() == ass and (pasta / "short.mp4").exists():
            print("short do tutorial sem mudanças")
        else:
            gerar_short(pasta, cfg, sh, telas, tmp)
            marca.write_text(ass + "\n")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    gerar(args[0] if args else Path(__file__).resolve().parents[1] / "videos" / "tutorial-app",
          so_short="--so-short" in sys.argv)

"""Motor de vídeo da série "Quem Faz o Quê?" (Legiscópio). Fora da rotina diária.

Cada episódio tem um módulo de cenas (qfq_ep1.py, …) e uma pasta videos/quem-faz-o-que/epN/ com roteiro.json:
  {"voz": "...", "taxa": "+6%", "tom": "-2Hz", "cenas": [{"n", "titulo", "narracao"}...], "youtube": {...}}
Uma cena = fundo + elementos (camadas RGBA) que entram quando a palavra-gatilho é dita + a Lupa (sem falar).
Narração com cache em disco (videos/.../audio), legendas queimadas, trilha de fundo e cta animado no meio.
"""
import asyncio
import hashlib
import importlib
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cta_meio  # noqa: E402
import personagem  # noqa: E402
import qfq_visual as q  # noqa: E402
import tutorial_app as ta  # noqa: E402  (legendas com endereços escritos)
import video_longo as vl  # noqa: E402

VERSAO = "1"
W, H, FPS, SR = q.W, q.H, 24, vl.SR
PAUSA = 0.5
T_EL = 0.45      # entrada de um elemento
T_CENA = 0.3     # fusão entre cenas


# ------------------------------------------------------------------ cena

PASSIVOS = {"textlength", "textbbox", "multiline_textbbox", "textsize", "font", "fontmode", "mode", "ink", "fill"}
WRAP_Q = ("icone", "selo_icone", "titulo", "chip", "cartao", "seta", "quadro_resp", "legenda_quadro", "mapa_brasil")


class _Gravador:
    """Executa a função do quadro-chave e separa cada desenho de alto nível numa camada (o que mudou na imagem)."""

    def __init__(self):
        self.img = None
        self.prev = None
        self.passos = []
        self.depth = 0
        self.lupa = None

    def registrar(self, img):
        if self.img is None and img.size == (W, H):
            self.img = img
            self.prev = img.convert("RGB").copy()
            self.inicio = self.prev.copy()

    def passo(self):
        if self.depth or self.img is None:
            return
        from PIL import ImageChops
        cur = self.img.convert("RGB")
        dif = ImageChops.difference(cur, self.prev)
        bb = dif.getbbox()
        if not bb:
            return
        m = dif.crop(bb).convert("L").point(lambda v: 255 if v else 0)
        lay = cur.crop(bb).convert("RGBA")
        lay.putalpha(m)
        self.passos.append([lay, bb])
        self.prev = cur.copy()


class _DrawProxy:
    def __init__(self, d, g):
        self._d, self._g = d, g

    def __getattr__(self, nome):
        a = getattr(self._d, nome)
        if not callable(a) or nome in PASSIVOS:
            return a

        def w(*args, **kw):
            self._g.depth += 1
            try:
                return a(*args, **kw)
            finally:
                self._g.depth -= 1
                self._g.passo()
        return w


def _juntar(a, b):
    (la, ba), (lb, bbx) = a, b
    bb = (min(ba[0], bbx[0]), min(ba[1], bbx[1]), max(ba[2], bbx[2]), max(ba[3], bbx[3]))
    lay = Image.new("RGBA", (bb[2] - bb[0], bb[3] - bb[1]), (0, 0, 0, 0))
    lay.alpha_composite(la, (ba[0] - bb[0], ba[1] - bb[1]))
    lay.alpha_composite(lb, (bbx[0] - bb[0], bbx[1] - bb[1]))
    return [lay, bb]


def _area(bb):
    return (bb[2] - bb[0]) * (bb[3] - bb[1])


def gravar(fn, modulo):
    """Roda fn() (função de quadro-chave do storyboard) e devolve (fundo RGB, [camadas], spec da Lupa)."""
    g = _Gravador()
    from PIL import ImageDraw as _ID
    orig_q = {n: getattr(q, n) for n in WRAP_Q + ("lupa", "base")}

    class _FakeID:
        @staticmethod
        def Draw(img, *a, **k):
            g.registrar(img)
            d = _ID.Draw(img, *a, **k)
            return _DrawProxy(d, g) if img is g.img else d

    def embrulha(nome):
        f = orig_q[nome]

        def w(*a, **k):
            g.depth += 1
            try:
                return f(*a, **k)
            finally:
                g.depth -= 1
                g.passo()
        return w

    def base(*a, **k):
        img = orig_q["base"](*a, **k)
        g.registrar(img)
        return img

    def lupa(img, pose="explicando", tam=430, x=None, y=None, espelho=True, boca="fechada", olhos="abertos"):
        g.lupa = dict(pose=pose, tam=tam, x=x, y=y, espelho=espelho)

    orig_mod_id = modulo.ImageDraw
    try:
        for n in WRAP_Q:
            setattr(q, n, embrulha(n))
        q.lupa, q.base = lupa, base
        modulo.ImageDraw = _FakeID
        img = fn()
        g.registrar(img)
        g.passo()
    finally:
        for n, f in orig_q.items():
            setattr(q, n, f)
        modulo.ImageDraw = orig_mod_id
    return g.inicio, g.passos, g.lupa


class Cena:
    def __init__(self, fn, modulo, cues=None, max_el=7):
        self.fn, self.modulo, self.cues, self.max_el = fn, modulo, cues or {}, max_el

    def preparar(self):
        inicio, passos, self.lupa = gravar(self.fn, self.modulo)
        # passos grandes no começo viram fundo
        while passos and _area(passos[0][1]) > 0.4 * W * H:
            lay, bb = passos.pop(0)
            inicio = inicio.convert("RGBA")
            inicio.alpha_composite(lay, (bb[0], bb[1]))
        while len(passos) > self.max_el:
            k = min(range(len(passos) - 1), key=lambda i: _area(passos[i][1]) + _area(passos[i + 1][1]))
            passos[k:k + 2] = [_juntar(passos[k], passos[k + 1])]
        self.fundo = inicio.convert("RGB")
        self.els = [{"lay": lay, "pos": (bb[0], bb[1]), "cue": self.cues.get(i), "mov": "sobe"}
                    for i, (lay, bb) in enumerate(passos)]


def tempo_cue(cue, palavras, dur, k, n):
    if isinstance(cue, (int, float)):
        return float(cue) * dur
    if cue:
        alvo = vl._norm(cue.split()[0])
        alvo2 = [vl._norm(x) for x in cue.split()]
        for m in range(len(palavras)):
            if vl._norm(palavras[m][1]).startswith(alvo[:max(3, min(len(alvo), 7))]):
                ok = all(m + j < len(palavras) and vl._norm(palavras[m + j][1]).startswith(alvo2[j][:5])
                         for j in range(1, len(alvo2)))
                if ok:
                    return max(0.0, palavras[m][0] - 0.1)
    if n <= 1:
        return 0.3
    return 0.3 + k * min(2.5, dur * 0.7 / (n - 1))


def suave(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def quadro_cena(c, t):
    img = c.fundo.copy().convert("RGBA")
    for e in c.els:
        a = suave((t - e["t0"]) / T_EL)
        if a <= 0:
            continue
        lay = e["lay"]
        if a < 0.999:
            lay = lay.copy()
            lay.putalpha(lay.getchannel("A").point(lambda v, a=a: int(v * a)))
            dy = int(30 * (1 - a)) if e["mov"] == "sobe" else 0
            x, y = e["pos"]
            img.alpha_composite(lay, (x, max(0, min(H - lay.height, y + dy))))
        else:
            img.alpha_composite(lay, e["pos"])
    return img


def lupa_em(img, spec, t, tglob, ts):
    if not spec:
        return
    pose = spec.get("pose", "explicando")
    for cue_t, p in ts:
        if t >= cue_t:
            pose = p
    olhos = "fechados" if int(tglob * FPS) % (FPS * 4) < 3 else spec.get("olhos", "abertos")
    esp = spec.get("espelho", True)
    sp = personagem.pose(pose, spec.get("boca", "fechada"), olhos, spec.get("tam", 400), tglob, -1 if esp else 1,
                         espelho=esp)
    x = W - sp.width - 20 if spec.get("x") is None else spec["x"]
    y = H - sp.height - 30 if spec.get("y") is None else spec["y"]
    img.alpha_composite(sp, (int(x), int(y)))


# ------------------------------------------------------------------ áudio

def tts(texto, voz, taxa, tom, pasta_audio, tmp, i):
    """mp3 + tempos das palavras, com cache em disco."""
    if os.environ.get("LEGIS_FAKE_TTS"):
        return vl.tts(texto, voz, taxa, tmp, i)
    k = hashlib.sha256(f"{voz}|{taxa}|{tom}|{texto}".encode()).hexdigest()[:16]
    mp3, js = pasta_audio / f"{k}.mp3", pasta_audio / f"{k}.json"
    if not (mp3.exists() and js.exists()):
        pasta_audio.mkdir(parents=True, exist_ok=True)
        try:
            import edge_tts
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "edge-tts"], check=True)
            import edge_tts

        async def _go():
            try:
                com = edge_tts.Communicate(texto, voz, rate=taxa, pitch=tom, boundary="WordBoundary")
            except TypeError:
                com = edge_tts.Communicate(texto, voz, rate=taxa, pitch=tom)
            pal = []
            with open(mp3, "wb") as f:
                async for ch in com.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        pal.append((ch["offset"] / 1e7, ch["text"]))
            return pal
        for tent in range(4):
            try:
                pal = asyncio.run(_go())
                break
            except Exception as e:
                print("TTS falhou:", e)
                if tent == 3:
                    raise
        js.write_text(json.dumps(pal, ensure_ascii=False), encoding="utf-8")
    pal = [tuple(x) for x in json.loads(js.read_text(encoding="utf-8"))]
    raw = tmp / f"c{i:02d}.raw"
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", str(SR),
                    "-f", "s16le", str(raw)], check=True)
    return raw.read_bytes(), pal


def trilha(dur, destino):
    """Trilha de fundo discreta, sintetizada (acordes suaves + pulso leve), em loop de 8 compassos."""
    try:
        import numpy as np
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "numpy"], check=True)
        import numpy as np
    sr = 44100
    bpm = 92
    beat = 60 / bpm
    prog = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]  # Am F C G
    n = int(dur * sr) + sr
    t = np.arange(n) / sr
    out = np.zeros(n)
    comp = 4 * beat
    for k in range(int(dur / comp) + 2):
        acorde = prog[k % 4]
        i0 = int(k * comp * sr)
        i1 = min(n, int((k + 1) * comp * sr) + int(0.4 * sr))
        if i0 >= n:
            break
        tt = t[i0:i1] - k * comp
        env = np.minimum(1, tt / 0.8) * np.exp(-tt / 6)
        for nota in acorde:
            f = 440 * 2 ** ((nota - 69) / 12)
            out[i0:i1] += 0.10 * env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt))
        fb = 440 * 2 ** ((acorde[0] - 12 - 69) / 12)
        for b in range(4):
            j0 = i0 + int(b * beat * sr)
            j1 = min(n, j0 + int(0.5 * sr))
            if j0 >= n:
                break
            tb = t[j0:j1] - t[j0]
            out[j0:j1] += 0.12 * np.exp(-tb / 0.18) * np.sin(2 * np.pi * fb * tb)
            if b % 2 == 1:  # leve "tique"
                ruido = np.random.default_rng(k * 4 + b).standard_normal(min(j1 - j0, int(0.03 * sr)))
                out[j0:j0 + len(ruido)] += 0.015 * ruido * np.exp(-np.arange(len(ruido)) / 300)
    fade = int(3 * sr)
    out[:sr] *= np.linspace(0, 1, sr)
    out[int(dur * sr) - fade:int(dur * sr)] *= np.linspace(1, 0, fade)
    out[int(dur * sr):] = 0
    out = out / (np.max(np.abs(out)) or 1) * 0.6
    pcm = (out * 32767).astype(np.int16)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# ------------------------------------------------------------------ render

def gerar(pasta, modulo, so_short=False):
    pasta = Path(pasta)
    cfg = json.loads((pasta / "roteiro.json").read_text(encoding="utf-8"))
    mod = importlib.import_module(modulo)
    voz, taxa, tom = cfg["voz"], cfg.get("taxa", "+0%"), cfg.get("tom", "+0Hz")
    audio = pasta / "audio"
    tmp = pasta / "_tmp"
    tmp.mkdir(exist_ok=True)
    fake = str(bool(os.environ.get("LEGIS_FAKE_TTS"))).encode()
    fontes = b"".join(Path(m.__file__).read_bytes() for m in (mod, q, sys.modules[__name__]))
    ass = hashlib.sha256((pasta / "roteiro.json").read_bytes() + fontes + VERSAO.encode() + fake).hexdigest()
    marca = pasta / ".render"
    if not so_short and not (marca.exists() and marca.read_text().strip() == ass and (pasta / "video.mp4").exists()):
        longo(pasta, cfg, mod, voz, taxa, tom, audio, tmp)
        marca.write_text(ass + "\n")
    else:
        print("vídeo sem mudanças")
    if hasattr(mod, "SHORT"):
        ass2 = hashlib.sha256(ass.encode() + json.dumps(mod.SHORT, ensure_ascii=False).encode()).hexdigest()
        m2 = pasta / ".render_short"
        if not (m2.exists() and m2.read_text().strip() == ass2 and (pasta / "short.mp4").exists()):
            short(pasta, cfg, mod, voz, taxa, tom, audio, tmp)
            m2.write_text(ass2 + "\n")
    if hasattr(mod, "miniatura"):
        mod.miniatura().convert("RGB").save(pasta / "thumb.jpg", quality=92)
    shutil.rmtree(tmp, ignore_errors=True)


def mixar(narr_wav, dur, destino_m4a, tmp, vol_trilha=0.11):
    tr = tmp / "trilha.wav"
    trilha(dur + 1, tr)
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(narr_wav), "-i", str(tr), "-filter_complex",
                    f"[1:a]volume={vol_trilha}[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]",
                    "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(destino_m4a)], check=True)


def longo(pasta, cfg, mod, voz, taxa, tom, audio, tmp):
    cenas = []
    for i, c in enumerate(cfg["cenas"]):
        amostras, pal = tts(c["narracao"], voz, taxa, tom, audio, tmp, i)
        dur = len(amostras) / 2 / SR
        cenas.append(dict(c, amostras=amostras, pal=pal, voz_dur=dur, dur=dur + PAUSA))
        print(f"cena {i + 1}: {dur:.1f}s")
    wav = tmp / "narr.wav"
    sil = bytes(int(PAUSA * SR) * 2)
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(c["amostras"] + sil for c in cenas))
    total = sum(c["dur"] for c in cenas)
    m4a = tmp / "audio.m4a"
    mixar(wav, total, m4a, tmp)
    destino = pasta / "video.mp4"
    cmd = [vl.ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", str(m4a), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
           "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(destino)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    srt, caps, nsrt, tg, qg = [], [], 1, 0.0, 0
    anterior = None
    for i, c in enumerate(cenas):
        sc = mod.CENAS[i]()
        sc.preparar()
        n = len(sc.els)
        for k, e in enumerate(sc.els):
            e["t0"] = tempo_cue(e["cue"], c["pal"], c["voz_dur"], k, n)
        lts = []
        if sc.lupa:
            lts = [(tempo_cue(cu, c["pal"], c["voz_dur"], 0, 1), p) for cu, p in sc.lupa.get("poses", [])]
        legs = ta.legendas(c["pal"], c["voz_dur"], c["narracao"])
        for ini, txt, fim in legs:
            srt.append(f"{nsrt}\n{vl.srt_tempo(tg + ini)} --> {vl.srt_tempo(tg + fim)}\n{txt}\n")
            nsrt += 1
        caps.append((tg, c.get("capitulo") or c["titulo"]))
        cta = c.get("cta")
        mk = cta_meio.marcos(c["pal"], c["voz_dur"]) if cta else None
        nq = int(round(c["dur"] * FPS))
        moldura = Image.new("RGBA", (W, H), sc.fundo.getpixel((W // 2, H - 4)) + (255,))
        moldura.paste(sc.fundo.crop((0, 0, W, 14)), (0, 0))
        cache_t, cache_img = None, None
        leg_cache = {}
        for f in range(nq):
            t = f / FPS
            chave = tuple(round(min(1.0, (t - e["t0"]) / T_EL), 2) if t >= e["t0"] else -1 for e in sc.els)
            if chave != cache_t:
                cache_img = quadro_cena(sc, t)
                cache_t = chave
            img = cache_img.copy()
            if mk:
                bar = cta_meio.barra(t, mk, fonte_bd=vl.BD(88), fonte_bk=vl.BK(84))
                ent = suave(t / 0.4) * suave((c["voz_dur"] - t + 0.2) / 0.4)
                if ent > 0.02:
                    bar = bar.copy()
                    bar.putalpha(bar.getchannel("A").point(lambda v, a=ent: int(v * a)))
                    cx, cy = cta if isinstance(cta, list) else (370, 700)
                    img.alpha_composite(bar, (cx, int(cy + 60 * (1 - ent))))
            lupa_em(img, sc.lupa, t, qg / FPS, lts)
            img = enquadrar(img, moldura)
            atual = next((txt for ini, txt, fim in legs if ini <= t < fim), "")
            if atual:
                if atual not in leg_cache:
                    leg_cache[atual] = legenda_rgba(atual)
                li = leg_cache[atual]
                img.alpha_composite(li, (0, H - 16 - li.height))
            if anterior is not None and t < T_CENA:
                img = Image.blend(anterior, img, suave(t / T_CENA))
            fr = img.convert("RGB")
            proc.stdin.write(fr.tobytes())
            qg += 1
        anterior = img.copy()
        tg += c["dur"]
        print(f"vídeo: cena {i + 1}/{len(cenas)} ({tg / 60:.1f} min)")
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError("ffmpeg falhou")
    (pasta / "legendas.srt").write_text("\n".join(srt), encoding="utf-8")
    linhas, ult = [], -99
    for t0, nome in caps:
        if t0 - ult >= 20 or not linhas:
            m, s = divmod(int(t0), 60)
            linhas.append(f"{m:02d}:{s:02d} {nome}")
            ult = t0
    (pasta / "capitulos.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"ok {destino} ({tg / 60:.1f} min)")


ESC = 0.9  # o quadro encolhe um pouco para a legenda ficar numa faixa própria, sem cobrir nada


def enquadrar(img, moldura):
    w, h = int(W * ESC), int(H * ESC)
    out = moldura.copy()
    out.alpha_composite(img.resize((w, h), Image.BILINEAR), ((W - w) // 2, 0))
    return out


def legenda_rgba(txt):
    lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = vl.BD(36)
    linhas = vl.wrap(d, txt, f, 1760)[:2]
    hh = len(linhas) * 46 + 24
    larg = max(d.textlength(l, font=f) for l in linhas) + 70
    x0 = (W - larg) / 2
    d.rounded_rectangle([x0, 0, x0 + larg, hh], radius=18, fill=(16, 37, 26, 235))
    for k, l in enumerate(linhas):
        d.text((W / 2, 12 + k * 46), l, font=f, fill=(255, 255, 255), anchor="mt")
    return lay.crop((0, 0, W, hh))


# ------------------------------------------------------------------ Short (1080x1920): quadros da série em moldura vertical

def short(pasta, cfg, mod, voz, taxa, tom, audio, tmp):
    VW, VH = 1080, 1920
    itens = mod.SHORT["cenas"]
    cenas = []
    for i, c in enumerate(itens):
        amostras, pal = tts(c["narracao"], voz, taxa, tom, audio, tmp, 200 + i)
        dur = len(amostras) / 2 / SR
        cenas.append(dict(c, amostras=amostras, pal=pal, voz_dur=dur, dur=dur + 0.3))
    wav = tmp / "narr_s.wav"
    sil = bytes(int(0.3 * SR) * 2)
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(c["amostras"] + sil for c in cenas))
    total = sum(c["dur"] for c in cenas)
    m4a = tmp / "audio_s.m4a"
    mixar(wav, total, m4a, tmp)
    destino = pasta / "short.mp4"
    cmd = [vl.ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
           "-r", str(FPS), "-i", "-", "-i", str(m4a), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
           "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(destino)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fundo = Image.new("RGB", (VW, VH), q.FUNDO)
    d = ImageDraw.Draw(fundo)
    for k, c in enumerate((q.UNI, q.EST, q.MUN)):
        d.rectangle([k * VW / 3, 0, (k + 1) * VW / 3, 14], fill=c)
    d.text((VW / 2, 150), "QUEM FAZ O QUÊ?", font=q.BK(72), fill=q.VERDE, anchor="mm")
    d.text((VW / 2, 230), mod.SHORT.get("selo", ""), font=q.BD(40), fill=q.TINTA, anchor="mm")
    lg = vl.logo(70)
    if lg:
        fundo.paste(lg, ((VW - lg.width) // 2, 1640), lg)
    d.text((VW / 2, 1760), "Episódio completo no canal", font=q.BD(36), fill=q.TINTA, anchor="mm")
    qg = 0
    for c in cenas:
        sc = mod.CENAS[c["cena"] - 1]()
        sc.preparar()
        n = len(sc.els)
        for k, e in enumerate(sc.els):
            e["t0"] = tempo_cue(None, c["pal"], c["voz_dur"], k, n) * 0.6
        legs = ta.legendas(c["pal"], c["voz_dur"], c["narracao"])
        nq = int(round(c["dur"] * FPS))
        cache_t = None
        for f in range(nq):
            t = f / FPS
            chave = tuple(round(min(1.0, (t - e["t0"]) / T_EL), 2) if t >= e["t0"] else -1 for e in sc.els)
            if chave != cache_t:
                fr = quadro_cena(sc, t).convert("RGB").resize((VW, int(VW * H / W)), Image.LANCZOS)
                cache_t = chave
            img = fundo.copy()
            img.paste(fr, (0, 330))
            atual = next((txt for ini, txt, fim in legs if ini <= t < fim), "")
            if atual:
                lay = Image.new("RGBA", (VW, 260), (0, 0, 0, 0))
                dd = ImageDraw.Draw(lay)
                ff = vl.BD(52)
                ls = vl.wrap(dd, atual, ff, 940)[:2]
                hh = len(ls) * 66 + 36
                lw = max(dd.textlength(x, font=ff) for x in ls) + 60
                dd.rounded_rectangle([(VW - lw) / 2, 0, (VW + lw) / 2, hh], radius=22, fill=(16, 37, 26, 240))
                for k, x in enumerate(ls):
                    dd.text((VW / 2, 18 + k * 66), x, font=ff, fill=(255, 255, 255), anchor="mt")
                img.paste(lay, (0, 1000), lay)
            sp = personagem.pose("explicando", "fechada", "fechados" if qg % (FPS * 4) < 3 else "abertos",
                                 380, qg / FPS, 0)
            img.paste(sp, (VW - sp.width + 30, 1240), sp)
            proc.stdin.write(img.tobytes())
            qg += 1
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError("ffmpeg falhou")
    print(f"ok {destino} ({total:.1f}s)")


if __name__ == "__main__":
    gerar(sys.argv[1], sys.argv[2], so_short="--so-short" in sys.argv)

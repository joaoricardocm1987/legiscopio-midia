"""Editor de vídeos com o rosto do João (Legiscópio). Fora da rotina diária.

Pasta do vídeo: videos/rosto/<nome>/config.json
  {"drive": "<link da pasta ou do arquivo no Google Drive>",
   "roteiro": "texto que o João leu (ajuda a transcrição e a grafia das legendas)",
   "insercoes": [{"gatilho": "palavra ou expressão dita", "tipo": "titulo|chips|tela|placar|logo",
                  "dur": 3.5, "atras": false, ...campos do tipo}],
   "final": {"titulo": "...", "link": "legiscopio.com.br/baixar"}}
Etapas: baixa o bruto do Drive -> normaliza (1080x1920, 30 fps, áudio e vídeo alinhados) -> transcreve
(faster-whisper, tempos por palavra) -> corta silêncios e tomadas repetidas -> monta: zoom alternado, inserções
(na frente; com "atras": true ficam atrás da cabeça, via recorte MediaPipe), legenda palavra a palavra,
voz tratada (EQ, redução de ruído, compressão, -14 LUFS), cartão final -> video.mp4 + legendas.srt.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import personagem  # noqa: E402
import video_longo as vl  # noqa: E402

VERSAO = "3"
W, H, FPS = 1080, 1920, 30
VERDE, VESC, LIMA, BR = vl.VERDE, (3, 60, 32), vl.LIMA, (255, 255, 255)
AMAR = (255, 214, 64)
BK, BD, RG = vl.BK, vl.BD, vl.RG
GAP = 0.45      # pausa que separa trechos
MARGEM = 0.10   # folga antes/depois de cada trecho mantido
FIM = 3.2       # duração do cartão final
# tratamento da voz: tira ronco grave, reduz ruído de fundo, corta o "embolado" dos médios-graves, dá presença,
# comprime de leve e nivela no padrão das redes (-14 LUFS)
VOZ = ("aformat=channel_layouts=mono,highpass=f=85,afftdn=nf=-28:tn=1,"
       "equalizer=f=250:t=q:w=1.2:g=-3,equalizer=f=3200:t=q:w=1.5:g=3,equalizer=f=8000:t=q:w=2:g=1.5,"
       "acompressor=threshold=-21dB:ratio=3:attack=8:release=120:makeup=2,"
       "alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=7")


LOG = []


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg)
    LOG.append(msg)


def pip(*pacotes):
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *pacotes], check=True)


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return "".join(c for c in w if c.isalnum())


# ------------------------------------------------------------------ 1. baixar e normalizar

def baixar(cfg, pasta):
    bruto = pasta / "bruto"
    vids = [p for p in bruto.glob("*") if p.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm", ".mkv")] if bruto.exists() else []
    if vids:
        return sorted(vids)[0], bruto
    bruto.mkdir(parents=True, exist_ok=True)
    try:
        import gdown
    except ImportError:
        pip("gdown")
        import gdown
    url = cfg["drive"]
    if "/folders/" in url:
        gdown.download_folder(url=url, output=str(bruto), quiet=False, use_cookies=False)
    else:
        gdown.download(url=url, output=str(bruto / "bruto.mp4"), quiet=False, fuzzy=True)
    vids = [p for p in bruto.rglob("*") if p.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm", ".mkv")]
    if not vids:
        raise RuntimeError("nenhum vídeo encontrado no Drive (o link está como 'qualquer pessoa com o link'?)")
    return sorted(vids, key=lambda p: -p.stat().st_size)[0], bruto


def normalizar(src, tmp):
    """1080x1920, 30 fps constante, rotação aplicada; áudio mono 16 kHz para a transcrição."""
    base = tmp / "base.mp4"
    info = subprocess.run([vl.ffmpeg(), "-hide_banner", "-i", str(src)], capture_output=True, text=True).stderr
    log("bruto:", " | ".join(l.strip() for l in info.splitlines() if "Stream" in l or "rotate" in l or "Duration" in l))
    # remove faixas pretas (letterbox) antes de enquadrar
    det = subprocess.run([vl.ffmpeg(), "-hide_banner", "-ss", "1", "-i", str(src), "-t", "6", "-vf", "cropdetect=24:2:0",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    crops = re.findall(r"crop=(\d+:\d+:\d+:\d+)", det)
    corte = f"crop={max(set(crops), key=crops.count)}," if crops else ""
    log("corte de bordas:", corte or "nenhum")
    dur_a = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    dur_a = int(dur_a[1]) * 3600 + int(dur_a[2]) * 60 + float(dur_a[3]) if dur_a else None
    # fps com start_time=0 + tpad: vídeo em ritmo constante, começando junto com o áudio e cobrindo toda a fala
    vf = (f"{corte}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"fps={FPS}:start_time=0,tpad=stop_mode=clone:stop_duration=30,format=yuv420p")
    af = "aresample=async=1000:first_pts=0"
    cmd = [vl.ffmpeg(), "-y", "-loglevel", "error", "-fflags", "+genpts", "-i", str(src), "-vf", vf, "-af", af,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    if dur_a:
        cmd += ["-t", f"{dur_a:.3f}"]
    subprocess.run(cmd + [str(base)], check=True)
    wav = tmp / "fala.wav"
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(base), "-ac", "1", "-ar", "16000", str(wav)],
                   check=True)
    return base, wav


# ------------------------------------------------------------------ 2. transcrição

def transcrever(wav, roteiro, cache):
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        pip("faster-whisper")
        from faster_whisper import WhisperModel
    import wave
    with wave.open(str(wav)) as w:  # passa o áudio já decodificado (evita incompatibilidade com o PyAV)
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    modelo = WhisperModel("medium", device="cpu", compute_type="int8")
    segs, _ = modelo.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False,
                                initial_prompt=(roteiro or "")[:800], beam_size=5)
    pal = []
    for s in segs:
        for w in s.words or []:
            t = w.word.strip()
            if t:
                pal.append([round(w.start, 3), round(w.end, 3), t])
    cache.write_text(json.dumps(pal, ensure_ascii=False), encoding="utf-8")
    return pal


def grafia_do_roteiro(pal, roteiro):
    """Troca a grafia das palavras transcritas pela do roteiro quando elas casam (nomes, acentos, siglas)."""
    if not roteiro:
        return pal
    toks = re.findall(r"\S+", roteiro)
    a = [norm(p[2]) for p in pal]
    b = [norm(t) for t in toks]
    sm = SequenceMatcher(None, a, b, autojunk=False)
    out = [list(p) for p in pal]
    for i, j, n in sm.get_matching_blocks():
        for k in range(n):
            out[i + k][2] = toks[j + k]
    return out


# ------------------------------------------------------------------ 3. cortes

def sem_retomadas(pal, n=4, janela=45):
    """Se uma sequência de n palavras se repete logo adiante, a primeira tentativa (e o que veio até a
    repetição) é descartada: é o João recomeçando a frase depois de errar."""
    nk = [norm(p[2]) for p in pal]
    i, out = 0, []
    while i < len(pal):
        alvo = nk[i:i + n]
        k_rep = None
        if len(alvo) == n:
            for k in range(i + 1, min(len(pal) - n + 1, i + janela)):
                if nk[k:k + n] == alvo:
                    k_rep = k
        if k_rep is not None:
            log("retomada descartada:", " ".join(p[2] for p in pal[i:k_rep]))
            i = k_rep
            continue
        out.append(pal[i])
        i += 1
    return out


def trechos(pal):
    """Agrupa as palavras em trechos separados por pausas e descarta tomadas que foram refeitas."""
    pal = sem_retomadas(pal)
    grupos, atual = [], []
    for p in pal:
        if atual and p[0] - atual[-1][1] > GAP:
            grupos.append(atual)
            atual = []
        atual.append(p)
    if atual:
        grupos.append(atual)

    def ini(g, n=3):
        return [norm(x[2]) for x in g[:n]]

    manter = []
    for k, g in enumerate(grupos):
        # se um trecho posterior (até 3 à frente) recomeça com as mesmas palavras, este foi uma tomada errada
        refeito = any(ini(g) == ini(h) and len(ini(g)) >= 2 for h in grupos[k + 1:k + 4])
        if not refeito:
            manter.append(g)
    return manter


def cortar(base, grupos, tmp):
    """Junta os trechos mantidos (vídeo + áudio) e devolve as palavras no novo tempo."""
    partes, novas, t_novo, bordas = [], [], 0.0, []
    for g in grupos:
        a = max(0.0, g[0][0] - MARGEM)
        b = g[-1][1] + MARGEM
        partes.append((a, b))
    # funde trechos que se encostam
    fund = []
    for a, b in partes:
        if fund and a <= fund[-1][1]:
            fund[-1] = (fund[-1][0], max(b, fund[-1][1]))
        else:
            fund.append((a, b))
    filtro, ins = [], []
    for i, (a, b) in enumerate(fund):
        filtro.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];"
                      f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,"
                      f"afade=t=out:st={max(0, b - a - 0.03):.3f}:d=0.03[a{i}]")
        ins.append(f"[v{i}][a{i}]")
    fc = ";".join(filtro) + ";" + "".join(ins) + f"concat=n={len(fund)}:v=1:a=1[v][a]"
    out = tmp / "cortado.mp4"
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(base), "-filter_complex", fc, "-map", "[v]",
                    "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "aac",
                    "-b:a", "192k", str(out)], check=True)
    for a, b in fund:
        bordas.append(t_novo)
        for g in grupos:
            for p in g:
                if a <= p[0] < b:
                    novas.append([p[0] - a + t_novo, min(p[1], b) - a + t_novo, p[2]])
        t_novo += b - a
    return out, novas, bordas, t_novo


# ------------------------------------------------------------------ 4. recorte da pessoa

class Recorte:
    def __init__(self):
        self.seg = None
        self.ok = False
        self.ema = None
        try:
            try:
                import mediapipe as mp
            except ImportError:
                pip("mediapipe")
                import mediapipe as mp
            try:
                self.seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0)
                self.modo = "solutions"
            except Exception:
                import urllib.request
                from mediapipe.tasks import python as mpt
                from mediapipe.tasks.python import vision
                mod = Path("/tmp/selfie_segmenter.tflite")
                if not mod.exists():
                    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/image_segmenter/"
                                               "selfie_segmenter/float16/latest/selfie_segmenter.tflite", mod)
                op = vision.ImageSegmenterOptions(base_options=mpt.BaseOptions(model_asset_path=str(mod)),
                                                  output_confidence_masks=True)
                self.seg = vision.ImageSegmenter.create_from_options(op)
                self.mp = mp
                self.modo = "tasks"
            self.ok = True
            log("recorte: mediapipe", getattr(mp, "__version__", "?"), self.modo)
        except Exception as e:  # sem recorte: as inserções ficam na frente, sem efeito de profundidade
            log("recorte indisponível:", repr(e))

    def mascara(self, rgb):
        if not self.ok:
            return None
        import cv2
        peq = cv2.resize(rgb, (288, 512))
        if self.modo == "solutions":
            m = self.seg.process(peq).segmentation_mask
        else:
            r = self.seg.segment(self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=np.ascontiguousarray(peq)))
            m = r.confidence_masks[0].numpy_view().astype(np.float32)
            if m.ndim == 3:
                m = m[..., 0]
        m = cv2.resize(m, (W, H))
        self.ema = m if self.ema is None else 0.6 * m + 0.4 * self.ema
        m = np.clip((self.ema - 0.35) / 0.3, 0, 1)
        m = cv2.GaussianBlur(m, (0, 0), 3)
        return Image.fromarray((m * 255).astype(np.uint8))


# ------------------------------------------------------------------ 5. inserções

def caixa_txt(d, txt, x, y, f, bg, fg, pad=26, r=24):
    bb = d.textbbox((0, 0), txt, font=f)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=bg)
    d.text((x + pad, y + pad - bb[1]), txt, font=f, fill=fg)
    return w, h


def sombra_rgba(img, blur=24, alpha=110):
    a = img.getchannel("A").point(lambda v: min(alpha, v)).filter(ImageFilter.GaussianBlur(blur))
    s = Image.new("RGBA", img.size, (0, 30, 15, 0))
    s.putalpha(a)
    return s


def celular_rgba(tela_png, largura):
    s = largura / 500
    bz = int(16 * s)
    sw = largura - 2 * bz
    tela = Image.open(tela_png).convert("RGBA")
    tela = tela.resize((sw, int(sw * tela.height / tela.width)), Image.LANCZOS)
    h = tela.height + 2 * bz
    ph = Image.new("RGBA", (largura, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ph)
    d.rounded_rectangle([0, 0, largura - 1, h - 1], radius=int(60 * s), fill=(20, 24, 22))
    m = Image.new("L", tela.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, tela.width - 1, tela.height - 1], radius=int(46 * s), fill=255)
    ph.paste(tela, (bz, bz), m)
    return ph


def insercao_rgba(ins, telas):
    """Camada RGBA 1080x1920 da inserção (desenhada na metade de cima do quadro)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tipo = ins.get("tipo", "titulo")
    if tipo == "titulo":
        linhas = ins["texto"].upper().split("|")
        tam = ins.get("tam", 132)
        while tam > 60 and max(d.textlength(l, font=BK(tam)) for l in linhas) > W - 100:
            tam -= 4
        f = BK(tam)
        y = ins.get("y", 150)
        for k, l in enumerate(linhas):
            cor = AMAR if k == len(linhas) - 1 and len(linhas) > 1 else BR
            w = d.textlength(l, font=f)
            d.text(((W - w) / 2 + 5, y + 6), l, font=f, fill=(0, 0, 0, 120))
            d.text(((W - w) / 2, y), l, font=f, fill=cor)
            y += int(f.size * 1.05)
    elif tipo == "chips":
        y = ins.get("y", 220)
        f = BK(ins.get("tam", 64))
        for k, t in enumerate(ins["itens"]):
            w = d.textbbox((0, 0), t, font=f)[2] + 60
            x = (W - w) / 2 + (-90, 90, 0, -60, 60)[k % 5]
            caixa_txt(d, t, x, y, f, (BR, LIMA, AMAR)[k % 3] + (245,), VESC, pad=30, r=40)
            y += int(f.size * 1.9)
    elif tipo == "placar":
        f1, f2 = BK(150), BD(46)
        d.rounded_rectangle([110, 170, W - 110, 690], radius=48, fill=(255, 255, 255, 240))
        d.text((W / 2, 230), ins.get("rotulo", "VOTAÇÃO"), font=BD(44), fill=VERDE, anchor="mt")
        d.text((W / 2 - 230, 330), str(ins["sim"]), font=f1, fill=(46, 160, 90), anchor="mt")
        d.text((W / 2 + 230, 330), str(ins["nao"]), font=f1, fill=(214, 90, 80), anchor="mt")
        d.text((W / 2 - 230, 510), "SIM", font=f2, fill=(46, 160, 90), anchor="mt")
        d.text((W / 2 + 230, 510), "NÃO", font=f2, fill=(214, 90, 80), anchor="mt")
        d.text((W / 2, 600), ins.get("nota", ""), font=RG(34), fill=(70, 90, 80), anchor="mt")
    elif tipo == "logo":
        lg = vl.logo(ins.get("alt", 300))
        if lg:
            pl = Image.new("RGBA", (lg.width + 120, lg.height + 90), (0, 0, 0, 0))
            ImageDraw.Draw(pl).rounded_rectangle([0, 0, pl.width - 1, pl.height - 1], radius=50, fill=(255, 255, 255, 245))
            pl.alpha_composite(lg, (60, 45))
            x, y = (W - pl.width) // 2, ins.get("y", 220)
            lay.alpha_composite(sombra_rgba(pl), (x + 10, y + 20))
            lay.alpha_composite(pl, (x, y))
    elif tipo == "tela":
        arq = telas.get(ins["tela"])
        if arq:
            ph = celular_rgba(arq, ins.get("largura", 520)).rotate(ins.get("giro", -6), resample=Image.BICUBIC, expand=True)
            x = ins.get("x", (W - ph.width) // 2)
            y = ins.get("y", 60)
            lay.alpha_composite(sombra_rgba(ph), (x + 14, y + 30))
            lay.alpha_composite(ph, (x, y))
        elif ins.get("reserva"):
            return insercao_rgba(ins["reserva"], telas)
    if ins.get("legenda_topo"):
        caixa_txt(d, ins["legenda_topo"], 60, 70, BK(44), VERDE + (240,), BR, pad=22)
    return lay


def tempo_gatilho(pal, gatilho, depois=0.0):
    alvo = [norm(x) for x in gatilho.split()]
    for i in range(len(pal)):
        if pal[i][0] < depois:
            continue
        if all(i + k < len(pal) and norm(pal[i + k][2]).startswith(alvo[k][:6]) for k in range(len(alvo))):
            return pal[i][0]
    return None


# ------------------------------------------------------------------ 6. legendas

TROCAS = [("legiscopio ponto com ponto br barra baixar", "legiscopio.com.br/baixar"),
          ("legiscopio ponto com ponto br", "legiscopio.com.br"),
          ("apoia ponto se barra legiscopio", "apoia.se/legiscopio")]


def palavras_legenda(pal):
    """Junta endereços falados ('ponto com ponto br') num token só."""
    out, i = [], 0
    while i < len(pal):
        feito = False
        for falado, escrito in TROCAS:
            n = len(falado.split())
            jan = " ".join(norm(p[2]) for p in pal[i:i + n])
            if jan == " ".join(norm(x) for x in falado.split()):
                out.append([pal[i][0], pal[i + n - 1][1], escrito])
                i += n
                feito = True
                break
        if not feito:
            out.append(pal[i])
            i += 1
    return out


def blocos(pal, maxc=22):
    bl, atual = [], []
    for p in pal:
        txt = " ".join(x[2] for x in atual + [p])
        if atual and (len(txt) > maxc or p[0] - atual[-1][1] > 0.35 or re.search(r"[.?!:]$", atual[-1][2])):
            bl.append(atual)
            atual = []
        atual.append(p)
    if atual:
        bl.append(atual)
    return bl


def legenda_rgba(bloco, ativa):
    f = BK(76)
    lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pals = [p[2] for p in bloco]
    esp = d.textlength(" ", font=f)
    larg = [d.textlength(p, font=f) for p in pals]
    linhas, atual, w = [], [], 0
    for k, lw in enumerate(larg):
        if atual and w + esp + lw > W - 140:
            linhas.append(atual)
            atual, w = [], 0
        atual.append(k)
        w += (esp if w else 0) + lw
    linhas.append(atual)
    y = 10
    for ln in linhas[:2]:
        tot = sum(larg[k] for k in ln) + esp * (len(ln) - 1)
        x = (W - tot) / 2
        for k in ln:
            cor = LIMA if k == ativa else BR
            d.text((x, y), pals[k], font=f, fill=cor, stroke_width=9, stroke_fill=(0, 0, 0))
            x += larg[k] + esp
        y += 100
    return lay


# ------------------------------------------------------------------ 7. montagem

def cartao_final(fundo_rgb, cfg_final):
    img = fundo_rgb.filter(ImageFilter.GaussianBlur(28)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (3, 60, 32, 200))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    lg = vl.logo(170)
    if lg:
        pl = Image.new("RGBA", (lg.width + 80, lg.height + 60), (255, 255, 255, 255))
        pl.alpha_composite(lg, (40, 30))
        m = Image.new("L", pl.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, pl.width - 1, pl.height - 1], radius=36, fill=255)
        img.paste(pl, ((W - pl.width) // 2, 260), m)
    d.text((W / 2, 560), cfg_final.get("titulo", "Baixe grátis"), font=BK(96), fill=BR, anchor="mt")
    caixa_txt(d, "ANDROID", (W - d.textbbox((0, 0), "ANDROID", font=BK(90))[2] - 60) / 2, 690, BK(90), LIMA, VESC, pad=30, r=50)
    d.text((W / 2, 900), cfg_final.get("link", "legiscopio.com.br/baixar"), font=BK(64), fill=AMAR, anchor="mt")
    d.text((W / 2, 1000), "iOS em breve · grátis e sem anúncios", font=BD(42), fill=(220, 242, 228), anchor="mt")
    d.text((W / 2, 1090), "Apoie: apoia.se/legiscopio", font=BD(40), fill=(220, 242, 228), anchor="mt")
    lu = personagem.pose("acenando", "sorriso", "abertos", 520, 0.3, 1)
    img.alpha_composite(lu, ((W - lu.width) // 2, H - lu.height - 60))
    return img.convert("RGB")


def montar(cortado, pal, bordas, dur, cfg, telas, destino, tmp):
    try:
        import cv2
    except ImportError:
        pip("opencv-python-headless")
        import cv2
    ins = []
    depois = 0.0
    for it in cfg.get("insercoes", []):
        t0 = tempo_gatilho(pal, it["gatilho"], depois) if it.get("gatilho") else it.get("t", 0.0)
        if t0 is None:
            log("gatilho não encontrado:", it["gatilho"])
            continue
        log(f"inserção {it.get('tipo')} em {t0:.1f}s ({it['gatilho']})")
        depois = t0
        ins.append(dict(it, t0=max(0.0, t0 - 0.15), t1=min(dur, t0 + it.get("dur", 3.5)), lay=insercao_rgba(it, telas)))
    for a, b in zip(ins, ins[1:]):  # uma inserção sai quando a próxima entra
        a["t1"] = min(a["t1"], b["t0"])
    leg = palavras_legenda(pal)
    bls = blocos(leg)
    rec = Recorte() if any(it.get("atras") for it in ins) else type("SemRecorte", (), {"ema": None})()
    cap = cv2.VideoCapture(str(cortado))
    audio = tmp / "audio.m4a"
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(cortado), "-af",
                    VOZ + f",apad=pad_dur={FIM + 0.5}", "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k",
                    str(audio)], check=True)
    cmd = [vl.ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", str(audio), "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(destino)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nq = int(dur * FPS)
    leg_cache = {}
    ultimo = None
    for f in range(nq):
        ok, bgr = cap.read()
        if not ok:
            break
        t = f / FPS
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        # zoom alternado por trecho (disfarça os cortes) com leve aproximação contínua
        k = max(i for i, b in enumerate(bordas) if b <= t + 1e-6) if bordas else 0
        t_ini = bordas[k] if bordas else 0
        z = (1.0, 1.12)[k % 2] + 0.012 * min(1.0, (t - t_ini) / 4)
        if z > 1.001:
            cw, ch = int(W / z), int(H / z)
            x0, y0 = (W - cw) // 2, int((H - ch) * 0.35)
            rgb = cv2.resize(rgb[y0:y0 + ch, x0:x0 + cw], (W, H), interpolation=cv2.INTER_LINEAR)
        quadro = Image.fromarray(rgb)
        ativos = [it for it in ins if it["t0"] <= t < it["t1"]]
        if ativos:
            m = rec.mascara(rgb) if any(it.get("atras") for it in ativos) else None
            if m is not None and f % 60 == 0:
                log(f"máscara t={t:.1f}s: {np.asarray(m).mean() / 255:.0%} do quadro é pessoa")
            img = quadro.convert("RGBA")
            for it in ativos:
                a = min(1.0, (t - it["t0"]) / 0.25, (it["t1"] - t) / 0.25)
                lay = it["lay"]
                if a < 0.999:
                    lay = lay.copy()
                    lay.putalpha(lay.getchannel("A").point(lambda v, a=a: int(v * a)))
                dy = int(40 * (1 - min(1.0, (t - it["t0"]) / 0.3)))
                img.alpha_composite(lay, (0, dy))
            if m is not None and any(it.get("atras") for it in ativos):
                img.paste(quadro, (0, 0), m)  # a pessoa volta para a frente das inserções
            quadro = img.convert("RGB")
        else:
            rec.ema = None
        # legenda
        for bi, b in enumerate(bls):
            if b[0][0] - 0.05 <= t < (bls[bi + 1][0][0] if bi + 1 < len(bls) else b[-1][1] + 0.4):
                ativa = max((j for j, p in enumerate(b) if p[0] <= t), default=0)
                chave = (bi, ativa)
                if chave not in leg_cache:
                    leg_cache.clear()
                    leg_cache[chave] = legenda_rgba(b, ativa)
                q = quadro.convert("RGBA")
                q.alpha_composite(leg_cache[chave], (0, int(H * 0.66)))
                quadro = q.convert("RGB")
                break
        proc.stdin.write(quadro.tobytes())
        ultimo = quadro
    # cartão final
    if ultimo is not None:
        fim = cartao_final(ultimo, cfg.get("final", {}))
        for f in range(int(FIM * FPS)):
            a = min(1.0, f / (0.35 * FPS))
            proc.stdin.write((Image.blend(ultimo, fim, a) if a < 1 else fim).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError("ffmpeg falhou")
    cap.release()


def srt(pal, destino):
    def tf(t):
        h, r = divmod(t, 3600)
        m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    linhas = []
    for i, b in enumerate(blocos(palavras_legenda(pal), maxc=42), 1):
        linhas.append(f"{i}\n{tf(b[0][0])} --> {tf(b[-1][1])}\n{' '.join(p[2] for p in b)}\n")
    destino.write_text("\n".join(linhas), encoding="utf-8")


def gerar(pasta):
    pasta = Path(pasta)
    cfg = json.loads((pasta / "config.json").read_text(encoding="utf-8"))
    tmp = pasta / "_tmp"
    tmp.mkdir(exist_ok=True)
    fontes = Path(__file__).read_bytes() + json.dumps(cfg, ensure_ascii=False).encode() + VERSAO.encode()
    ass = hashlib.sha256(fontes).hexdigest()
    marca = pasta / ".render"
    if marca.exists() and marca.read_text().strip() == ass and (pasta / "video.mp4").exists():
        print("sem mudanças")
        return
    src, bruto = baixar(cfg, pasta)
    telas = {p.name: p for p in bruto.rglob("*.png")}
    raiz_telas = Path(__file__).resolve().parents[1] / "videos" / "tutorial-app" / "telas"
    for p in raiz_telas.glob("*.png") if raiz_telas.exists() else []:
        telas.setdefault(p.name, p)
    base, wav = normalizar(src, tmp)
    pal = transcrever(wav, cfg.get("roteiro", ""), pasta / "transcricao.json")
    pal = grafia_do_roteiro(pal, cfg.get("roteiro", ""))
    grupos = trechos(pal)
    cortado, novas, bordas, dur = cortar(base, grupos, tmp)
    log(f"bruto {len(pal)} palavras · {len(grupos)} trechos · {dur:.1f}s depois dos cortes")
    montar(cortado, novas, bordas, dur, cfg, telas, pasta / "video.mp4", tmp)
    srt(novas, pasta / "legendas.srt")
    (pasta / "log.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    marca.write_text(ass + "\n")
    shutil.rmtree(tmp, ignore_errors=True)
    if not os.environ.get("ROSTO_MANTER_BRUTO"):
        shutil.rmtree(pasta / "bruto", ignore_errors=True)  # o bruto fica só no Drive (arquivo grande demais para o git)


if __name__ == "__main__":
    gerar(sys.argv[1])

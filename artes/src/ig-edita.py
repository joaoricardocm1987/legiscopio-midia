# Único (apaga a si mesmo): monta o Reel do Instagram de 08/11 (app no iOS + emendas por cidade) com os melhores
# trechos dos 2 vídeos do Drive. Usa scripts/rosto_editor.py (voz tratada, zoom nos cortes, legenda palavra a
# palavra, inserções e cartão final "Android e iOS"). Saída: videos/rosto/ig-2026-11-08/video.mp4
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
PASTA = ROOT / "videos" / "rosto" / "ig-2026-11-08"
AN = PASTA / "analise"
IDS = {"A": "1Q_72x8r4UzRokOZbxjtMmwXUAv-hFTKY", "B": "1QdD4kPZaGk_uk281k_jUUPeGRF_6hg0f"}
# (vídeo, início, fim) em segundos no vídeo normalizado
TRECHOS = [
    ("A", 0.85, 4.40),    # Fala pessoal, voltei agora nesse final de domingo
    ("B", 12.45, 19.30),  # Temos uma novidade no app: agora ele tá liberado pro iOS, então Android e iOS
    ("B", 19.55, 24.52),  # Só ir lá na Play Store, na Apple Store e baixar
    ("B", 24.40, 34.10),  # E agora temos a tabela também sobre as emendas parlamentares... pra onde tá sendo enviado
    ("A", 34.18, 39.66),  # e o que cada deputado mandou, tanto a bancada quanto o deputado mandaram
    ("A", 41.28, 42.85),  # para a cidade
    ("B", 34.55, 37.55),  # Vá lá, confere lá, Legiscópio!
]
CFG = {
    "insercoes": [
        {"gatilho": "liberado pro", "tipo": "titulo", "texto": "AGORA TAMBÉM|NO iOS", "dur": 3.0, "atras": True},
        {"gatilho": "Play Store", "tipo": "chips", "itens": ["Google Play", "App Store"], "dur": 3.4, "y": 200},
        {"gatilho": "emendas parlamentares", "tipo": "titulo", "texto": "EMENDAS|POR CIDADE", "dur": 3.6,
         "atras": True},
        {"gatilho": "cada deputado", "tipo": "chips", "itens": ["Por deputado", "Por bancada"], "dur": 3.6, "y": 200},
    ],
    "final": {"titulo": "Baixe grátis", "link": "www.legiscopio.com.br/baixar"},
}
log = []
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "numpy", "gdown", "opencv-python-headless"], check=True)
    import rosto_editor as re_
    import video_longo as vl
    import gdown
    tmp = Path("/tmp/ig")
    tmp.mkdir(exist_ok=True)
    bases, pals = {}, {}
    for k, fid in IDS.items():
        dst = tmp / f"{k}.mp4"
        if not dst.exists():
            gdown.download(id=fid, output=str(dst), quiet=True)
        sub = tmp / k
        sub.mkdir(exist_ok=True)
        bases[k], _ = re_.normalizar(dst, sub)
        pals[k] = json.loads((AN / f"transcricao_{k}.json").read_text(encoding="utf-8"))

    # correções de grafia da transcrição
    def corrige(k, p):
        w = p[2]
        if k == "B" and w == "OS" and 18 < p[0] < 20:
            return "e iOS."
        if k == "B" and w == "Apple":
            return "Apple"
        if k == "B" and w == "iOS,":
            return "iOS,"
        return w

    # junta os trechos (vídeo + áudio) e recalcula os tempos das palavras
    filtro, ins_, novas, bordas, t = [], [], [], [], 0.0
    entradas = {"A": 0, "B": 1}
    for i, (k, a, b) in enumerate(TRECHOS):
        n = entradas[k]
        filtro.append(f"[{n}:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];"
                      f"[{n}:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,"
                      f"afade=t=out:st={max(0, b - a - 0.05):.3f}:d=0.05[a{i}]")
        ins_.append(f"[v{i}][a{i}]")
        bordas.append(t)
        trecho = [p for p in pals[k] if p[0] >= a - 0.05 and p[1] <= b + 0.05]
        # "lê esse copo" = Legiscópio
        if k == "B" and a > 34:
            fim = [p for p in trecho if p[2] in ("lê", "esse", "copo")]
            trecho = [p for p in trecho if p[2] not in ("lê", "esse", "copo")]
            if fim:
                trecho.append([fim[0][0], fim[-1][1], "Legiscópio!"])
        for p in trecho:
            novas.append([round(p[0] - a + t, 3), round(min(p[1], b) - a + t, 3), corrige(k, p)])
        t += b - a
    fc = ";".join(filtro) + ";" + "".join(ins_) + f"concat=n={len(TRECHOS)}:v=1:a=1[v][a]"
    cortado = tmp / "cortado.mp4"
    subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(bases["A"]), "-i", str(bases["B"]),
                    "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "16", "-c:a", "aac", "-b:a", "192k", str(cortado)], check=True)
    if novas:
        novas[0][2] = novas[0][2][:1].upper() + novas[0][2][1:]
    log.append(f"trechos: {len(TRECHOS)} · {t:.1f}s de fala")
    log.append("texto: " + " ".join(p[2] for p in novas))
    destino = PASTA / "video.mp4"
    re_.montar(cortado, novas, bordas, t, CFG, {}, destino, tmp)
    re_.srt(novas, PASTA / "legendas.srt")
    (PASTA / "config.json").write_text(json.dumps({"trechos": TRECHOS, **CFG}, ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8")
    if destino.exists():
        subprocess.run([vl.ffmpeg(), "-y", "-loglevel", "error", "-i", str(destino), "-vf",
                        "fps=1/3,scale=270:480,tile=7x2", "-frames:v", "1", str(PASTA / "previa.jpg")], check=False)
        log.append(f"video.mp4: {destino.stat().st_size} bytes")
    log.extend(re_.LOG)
except Exception:
    log.append(traceback.format_exc())
(PASTA / "log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(Path(__file__))], check=False, cwd=ROOT)

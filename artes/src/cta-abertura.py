# Único (apaga a si mesmo): a chamada animada (joinha, Inscrever-se e sininho) pode entrar logo depois do
# resumão de abertura ("cta_pos": "abertura" no video.json), em vez de no meio. Aplica em scripts/video_longo.py,
# ajusta o roteiro de 2026-11-07 (Semana no Congresso) e refaz esse vídeo e os capítulos.
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARQ = ROOT / "scripts" / "video_longo.py"
PASTA = ROOT / "videos" / "2026-11-07"
LOG = PASTA / "cta_abertura_log.txt"
log = []

TROCAS = [
    ('Opcional no video.json: "cta_meio": false (desliga) ou "cta_meio_fala": "texto próprio".\n',
     'Opcional no video.json: "cta_meio": false (desliga) ou "cta_meio_fala": "texto próprio".\n'
     '"cta_pos": "abertura" põe a mesma chamada logo depois da 1ª cena (o resumão), em vez do meio.\n'),
    ('        if melhor:\n            fala = cfg.get("cta_meio_fala") or cta_meio.FALA_PADRAO\n',
     '        abertura = cfg.get("cta_pos") == "abertura"\n'
     '        if abertura:\n'
     '            melhor = 1\n'
     '        if melhor:\n'
     '            fala = cfg.get("cta_meio_fala") or (FALA_ABERTURA if abertura else cta_meio.FALA_PADRAO)\n'),
    ('            print(f"chamada do meio (like/inscrição/sino) antes da cena {melhor + 1}: {dur:.1f}s")\n',
     '            print(f"chamada (like/inscrição/sino) antes da cena {melhor + 1}: {dur:.1f}s")\n'),
    ('# ------------------------------------------------------------------ principal\n',
     'FALA_ABERTURA = ("Antes de começar: se esse assunto te interessa, deixa o seu like, se inscreve no canal "\n'
     '                 "e ativa o sininho pra não perder os próximos. Agora, vamos lá!")\n\n\n'
     '# ------------------------------------------------------------------ principal\n'),
]

try:
    s = ARQ.read_text(encoding="utf-8")
    if 'cfg.get("cta_pos") == "abertura"' not in s:
        for velho, novo in TROCAS:
            assert s.count(velho) == 1, f"trecho não encontrado: {velho[:60]!r}"
            s = s.replace(velho, novo)
        ARQ.write_text(s, encoding="utf-8")
        log.append("video_longo.py: cta_pos abertura adicionado")
    subprocess.run(["git", "add", str(ARQ)], check=True, cwd=ROOT)

    # roteiro de hoje: tira a frase falada de inscrição do resumão (a chamada animada fala por ela)
    vj = PASTA / "video.json"
    cfg = json.loads(vj.read_text(encoding="utf-8"))
    cfg.pop("cta_meio", None)
    novo = {}
    for k, v in cfg.items():
        novo[k] = v
        if k == "velocidade":
            novo["cta_pos"] = "abertura"
    cfg = novo
    f0 = cfg["cenas"][0]["fala"]
    corte = " Se esse assunto te interessa, se inscreve no canal: toda semana tem um resumo assim."
    if corte in f0:
        cfg["cenas"][0]["fala"] = f0.replace(corte, "")
        log.append("cena 1: frase de inscrição falada removida")
    vj.write_text(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    for nome in (".video_render", "video.mp4", "legendas.srt", "capitulos.txt"):
        (PASTA / nome).unlink(missing_ok=True)
    sys.path.insert(0, str(ROOT / "scripts"))
    import video_longo  # noqa: E402
    import capitulos  # noqa: E402
    video_longo.gerar(vj)
    capitulos.gerar(vj)
    mp4 = PASTA / "video.mp4"
    if mp4.exists():
        subprocess.run([video_longo.ffmpeg(), "-y", "-loglevel", "error", "-ss", "14", "-t", "24", "-i", str(mp4),
                        "-vf", "fps=1/3,scale=480:270,tile=4x2", "-frames:v", "1",
                        str(PASTA / "cta_abertura_previa.png")], check=True)
        log.append(f"video.mp4 refeito: {mp4.stat().st_size} bytes")
except Exception:
    log.append(traceback.format_exc())
LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(Path(__file__))], check=False, cwd=ROOT)

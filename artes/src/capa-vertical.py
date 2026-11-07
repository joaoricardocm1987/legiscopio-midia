# Único (apaga a si mesmo): nos sábados, o Short e o Resumo de 2 min (Reels/TikTok) também abrem com a capa
# "Resumão da semana na Câmara e no Senado". Aplica em scripts/short_video.py e refaz os verticais de 2026-11-07.
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SV = ROOT / "scripts" / "short_video.py"
PASTA = ROOT / "videos" / "2026-11-07"
LOG = PASTA / "capa_vertical_log.txt"
log = []

TROCAS = [
    ('Por padrão o botão diz "Vídeo completo / no canal"; nos dias sem vídeo longo use, por exemplo,\n',
     'Nos sábados (video.json com a 1ª cena em "capa_semana"), o short e o resumo ganham automaticamente uma\n'
     'cena de abertura com a mesma capa ("Resumão da semana na Câmara e no Senado").\n'
     'Por padrão o botão diz "Vídeo completo / no canal"; nos dias sem vídeo longo use, por exemplo,\n'),
    ('\n\n@contextmanager\ndef painel_vertical():',
     '\nFALA_CAPA_SEMANA = "Esse é o resumão da semana na Câmara e no Senado."\n\n\n'
     '@contextmanager\ndef painel_vertical():'),
    ('        print(f"sem {saida}.json em", pasta)\n        return\n',
     '        print(f"sem {saida}.json em", pasta)\n        return\n'
     '    # sábado: abre com a capa "Resumão da semana" do vídeo longo\n'
     '    capa = next((c.get("visual") for c in cfg.get("cenas", [])[:1]\n'
     '                 if (c.get("visual") or {}).get("tipo") == "capa_semana"), None)\n'
     '    if capa and (sh["cenas"][0].get("visual") or {}).get("tipo") != "capa_semana":\n'
     '        sh = dict(sh, cenas=[{"fala": FALA_CAPA_SEMANA, "visual": capa}] + list(sh["cenas"]))\n'),
]

try:
    s = SV.read_text(encoding="utf-8")
    if "FALA_CAPA_SEMANA" not in s:
        for velho, novo in TROCAS:
            assert s.count(velho) == 1, f"trecho não encontrado: {velho[:60]!r}"
            s = s.replace(velho, novo)
        SV.write_text(s, encoding="utf-8")
        log.append("short_video.py: capa_semana na abertura dos verticais de sábado")
    subprocess.run(["git", "add", str(SV)], check=True, cwd=ROOT)

    # o short de hoje abria com "A semana no Congresso em um minuto!": a capa já faz essa abertura
    sj = PASTA / "short.json"
    sh = json.loads(sj.read_text(encoding="utf-8"))
    f0 = sh["cenas"][0]["fala"]
    corte = "A semana no Congresso em um minuto! "
    if f0.startswith(corte):
        sh["cenas"][0]["fala"] = f0[len(corte):]
        sj.write_text(json.dumps(sh, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        log.append("short.json: abertura falada repetida removida")

    for nome in (".resumo_render", ".short_render", "resumo.mp4", "short.mp4"):
        (PASTA / nome).unlink(missing_ok=True)
    sys.path.insert(0, str(ROOT / "scripts"))
    import short_video  # noqa: E402
    import video_longo  # noqa: E402
    for nome in ("resumo", "short"):
        short_video.gerar(PASTA / f"{nome}.json")
        mp4 = PASTA / f"{nome}.mp4"
        if mp4.exists():
            subprocess.run([video_longo.ffmpeg(), "-y", "-loglevel", "error", "-ss", "0.5", "-t", "12", "-i", str(mp4),
                            "-vf", "fps=1/2,scale=270:480,tile=6x1", "-frames:v", "1",
                            str(PASTA / f"capa_vertical_{nome}_previa.png")], check=True)
            dur = subprocess.run([video_longo.ffmpeg(), "-i", str(mp4)], capture_output=True, text=True).stderr
            dur = next((l.strip() for l in dur.splitlines() if "Duration" in l), "")
            log.append(f"{nome}.mp4 refeito: {mp4.stat().st_size} bytes {dur}")
        else:
            log.append(f"{nome}.mp4 NÃO gerado")
except Exception:
    log.append(traceback.format_exc())
LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(PASTA), str(Path(__file__))], check=False, cwd=ROOT)

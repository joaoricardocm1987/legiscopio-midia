# Série "Quem Faz o Quê?": gera amostras de voz (pt-BR) para escolher o narrador. Avulso, fora da rotina diária.
# Saída: videos/quem-faz-o-que/amostras/<voz>_<ajuste>.mp3 + vozes.txt (lista de vozes pt-BR disponíveis)
import asyncio
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "quem-faz-o-que" / "amostras"
PASTA.mkdir(parents=True, exist_ok=True)

try:
    import edge_tts
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "edge-tts"], check=True)
    import edge_tts

TEXTO = ("O poste da sua rua apagou. Já faz uma semana. Você reclama com quem: prefeito, vereador ou "
         "companhia de energia? Quem Faz o Quê? Uma série do Legiscópio e do Diário do Mandato. "
         "Episódio 1: Município. O Brasil é uma federação. A Constituição diz que a organização do país "
         "compreende a União, os estados, o Distrito Federal e os municípios, todos autônomos.")

AJUSTES = {"normal": ("+0%", "+0Hz"), "ritmo-telejornal": ("+6%", "-2Hz"), "grave-pausado": ("-4%", "-6Hz")}


async def principal():
    vozes = [v for v in await edge_tts.list_voices() if v["Locale"] == "pt-BR"]
    (PASTA / "vozes.txt").write_text("\n".join(f"{v['ShortName']}\t{v['Gender']}" for v in vozes) + "\n",
                                     encoding="utf-8")
    for v in vozes:
        nome = v["ShortName"]
        for rot, (taxa, tom) in AJUSTES.items():
            mp3 = PASTA / f"{nome}_{rot}.mp3"
            if mp3.exists():
                continue
            for tentativa in range(3):
                try:
                    await edge_tts.Communicate(TEXTO, nome, rate=taxa, pitch=tom).save(str(mp3))
                    print("ok", mp3.name)
                    break
                except Exception as e:
                    print("falhou", nome, rot, e)


asyncio.run(principal())
subprocess.run(["git", "add", str(PASTA)], check=True, cwd=ROOT)

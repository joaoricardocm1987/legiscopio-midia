# Ajuste único (apaga a si mesmo): no Ep. 5, a voz multilíngue lia "Encontrou algo errado?" com pronúncia de espanhol.
# Troca o começo da cena 16 por uma frase mais longa e claramente em português; o qfq-ep5.py (roda depois, em ordem
# alfabética) refaz só o áudio dessa cena e renderiza o vídeo de novo.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
rot = ROOT / "videos" / "quem-faz-o-que" / "ep5" / "roteiro.json"
txt = rot.read_text(encoding="utf-8")
velho = "Encontrou algo errado? Você pode registrar a denúncia"
novo = "Se você encontrar alguma irregularidade, pode registrar a denúncia"
if velho in txt:
    rot.write_text(txt.replace(velho, novo), encoding="utf-8")
    print("cena 16 ajustada")
else:
    print("trecho não encontrado (já ajustado?)")
Path(__file__).unlink()

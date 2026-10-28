# Ajuste único (28/10/2026): o app já está disponível para Android.
# Troca "nos próximos dias" por "já disponível" nos modelos e no tutorial e depois se apaga.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TROCAS = {
    "scripts/video_longo.py": [
        ('"Android nos próximos dias · iOS em breve"', '"Já no Android · iOS em breve"'),
    ],
    "scripts/tutorial_app.py": [
        ('"Android: nos próximos dias · iOS: em breve"', '"Android: já disponível · iOS: em breve"'),
    ],
    "videos/tutorial-app/tutorial.json": [
        ("Os avisos no celular vão chegar pelo aplicativo. Fique ligado: nos próximos dias ele estará disponível para Android, e o iOS chega em breve.",
         "Os avisos no celular chegam pelo aplicativo, que já está disponível para Android. O iOS chega em breve."),
        ('"Avisos no app: Android em breve"', '"Avisos no app: já no Android"'),
        ("(fique ligado: nos próximos dias no Android; iOS em breve)", "(já disponível para Android; iOS em breve)"),
    ],
    "videos/tutorial-app/short.json": [
        ("(fique ligado: nos próximos dias no Android; iOS em breve)", "(já disponível para Android; iOS em breve)"),
    ],
    "artes/src/tutorial-app.py": [
        ("# Revisão 5: Android nos próximos dias e iOS em breve;", "# Revisão 6: já disponível no Android e iOS em breve;"),
    ],
}
for rel, pares in TROCAS.items():
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for a, b in pares:
        if a in s:
            s = s.replace(a, b)
            print("ok:", rel, "|", b[:60])
        else:
            print("não encontrado:", rel, "|", a[:60])
    p.write_text(s, encoding="utf-8")
Path(__file__).unlink()

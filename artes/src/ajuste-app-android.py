# Ajuste único (23/10/2026): o app ainda está em análise na loja do Android.
# Troca a data fixa "23/10" por "nos próximos dias" nos modelos e no tutorial e depois se apaga.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TROCAS = {
    "scripts/video_longo.py": [
        ('"Android a partir de 23/10 · iOS em breve"', '"Android nos próximos dias · iOS em breve"'),
    ],
    "scripts/tutorial_app.py": [
        ('"Android: 23/10/2026 · iOS: em breve"', '"Android: nos próximos dias · iOS: em breve"'),
    ],
    "videos/tutorial-app/tutorial.json": [
        ("Os avisos no celular vão chegar pelo aplicativo, que será liberado para Android no dia 23 de outubro e para iOS em breve.",
         "Os avisos no celular vão chegar pelo aplicativo. Fique ligado: nos próximos dias ele estará disponível para Android, e o iOS chega em breve."),
        ('"Avisos no app: Android em 23/10"', '"Avisos no app: Android em breve"'),
        ("(Android a partir de 23/10/2026; iOS em breve)", "(fique ligado: nos próximos dias no Android; iOS em breve)"),
    ],
    "videos/tutorial-app/short.json": [
        ("(Android a partir de 23/10/2026; iOS em breve)", "(fique ligado: nos próximos dias no Android; iOS em breve)"),
    ],
    "artes/src/tutorial-app.py": [
        ("# Revisão 4: Android em 23/10/2026 e iOS em breve;", "# Revisão 5: Android nos próximos dias e iOS em breve;"),
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

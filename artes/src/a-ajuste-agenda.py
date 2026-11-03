# Ajuste único (apaga a si mesmo): agenda.py tira requerimentos/indicações da pauta e ajusta o carrossel ao espaço
# da página; remove a pasta de testes videos/_teste-agenda.
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "scripts" / "agenda.py"
s = p.read_text(encoding="utf-8")
TROCAS = [
    ('FIXTURES = None  # testes',
     'FORA_PAUTA = {"REQ", "RIC", "INC", "RQS", "RQN"}  # requerimentos e indicações: fora da lista da pauta\nFIXTURES = None  # testes'),
    ('if not ident or ident in [i["id"] for i in itens]:',
     'if not ident or ident in [i["id"] for i in itens] or (sig or ident.split(" ")[0]) in FORA_PAUTA:'),
    ('if ident and ident not in [x["id"] for x in mats]:',
     'if ident and ident not in [x["id"] for x in mats] and ident.split(" ")[0] not in FORA_PAUTA:'),
    ('''        lim = 4 if nome == "CÂMARA" else 3
        for it in itens[:lim]:
            linha = vl.wrap(dd, f"{it['id']}: {resumo(it, resumos)}", RG(32), WC - 200)
            for j, l in enumerate(linha[:2]):
                if j == 0:
                    dd.ellipse([84, y + 14, 98, y + 28], fill=cor)
                dd.text((120, y), l, font=RG(32), fill=TEXTO)
                y += 42
            y += 10
        if len(itens) > lim:
            dd.text((120, y), f"+ {len(itens) - lim} itens", font=BD(32), fill=OLIVA)
            y += 50''',
     '''        limite_y = (HC - 470) if nome == "CÂMARA" else (HC - 190)  # a Câmara deixa lugar para o Senado
        mostrados = 0
        for it in itens:
            linha = vl.wrap(dd, f"{it['id']}: {resumo(it, resumos)}", RG(32), WC - 200)[:2]
            if y + 42 * len(linha) + 10 > limite_y - 50:
                break
            for j, l in enumerate(linha):
                if j == 0:
                    dd.ellipse([84, y + 14, 98, y + 28], fill=cor)
                dd.text((120, y), l, font=RG(32), fill=TEXTO)
                y += 42
            y += 10
            mostrados += 1
        if len(itens) > mostrados:
            k = len(itens) - mostrados
            dd.text((120, y), f"+ {k} {'item' if k == 1 else 'itens'}", font=BD(32), fill=OLIVA)
            y += 50'''),
]
for velho, novo in TROCAS:
    assert s.count(velho) == 1, velho[:60]
    s = s.replace(velho, novo)
p.write_text(s, encoding="utf-8")
shutil.rmtree(ROOT / "videos" / "_teste-agenda", ignore_errors=True)
Path(__file__).unlink()

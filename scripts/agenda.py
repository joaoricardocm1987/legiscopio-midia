"""Agenda do Congresso em imagens (Legiscópio).

gerar("AAAA-MM-DD") busca nas APIs oficiais da Câmara e do Senado a agenda do dia e grava em posts/AAAA-MM-DD/:
  agenda_1.png ... agenda_N.png   stories 1080x1920 (capa, Plenário da Câmara, Plenário do Senado e Congresso,
                                  comissões da Câmara, comissões do Senado; telas sem nada são puladas)
  semana_1.png ... semana_K.png   SÓ às segundas: carrossel 1080x1350 com a agenda da semana (segunda a sexta)
  agenda.json                     dados usados + lista de arquivos, para a rotina montar os posts no Metricool
Resumos curtos opcionais das matérias (escritos pela rotina) em posts/AAAA-MM-DD/agenda_resumos.json:
  {"PEC 18/2025": "PEC da Segurança Pública", ...}  (chave = sigla número/ano)
Fim de semana ou dia sem nenhum evento: não gera imagens (agenda.json com "arquivos": []).
"""
import datetime as dt
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import video_longo as vl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
W, H = 1080, 1920
WC, HC = 1080, 1350
FUNDO, VERDE, VESC, TEXTO, OLIVA, BR, LIMA = vl.FUNDO, vl.VERDE, vl.VERDE_ESC, vl.TEXTO, vl.OLIVA, vl.BRANCO, vl.LIMA
BORDA, TAG = vl.BORDA, vl.TAG
CINZA = (110, 122, 114)
BK, BD, RG, MO = vl.BK, vl.BD, vl.RG, vl.MO
CAMARA_COR, SENADO_COR = (5, 87, 47), (31, 78, 140)
DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]
FORA_PAUTA = {"REQ", "RIC", "INC", "RQS", "RQN"}  # requerimentos e indicações: fora da lista da pauta
FIXTURES = None  # testes: dict url -> caminho de arquivo


# ------------------------------------------------------------------ dados

def baixar(url, tentativas=3):
    if FIXTURES is not None:
        p = FIXTURES.get(url)
        return json.loads(Path(p).read_text(encoding="utf-8")) if p else None
    for k in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "legiscopio-midia"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print("falhou", url, repr(e))
            time.sleep(3 * (k + 1))
    return None


def lista(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def camara_eventos(d0, d1):
    url = (f"https://dadosabertos.camara.leg.br/api/v2/eventos?dataInicio={d0}&dataFim={d1}"
           f"&ordem=ASC&ordenarPor=dataHoraInicio&itens=200")
    j = baixar(url) or {}
    evs = [e for e in j.get("dados", []) if (e.get("situacao") or "") != "Cancelada"]
    return evs


def camara_pauta(ev_id):
    j = baixar(f"https://dadosabertos.camara.leg.br/api/v2/eventos/{ev_id}/pauta") or {}
    itens = []
    for it in j.get("dados", []):
        p = it.get("proposicao_") or {}
        sig = p.get("siglaTipo")
        ident = f"{sig} {p.get('numero')}/{p.get('ano')}" if sig else (it.get("titulo") or "").strip()
        if not ident or ident in [i["id"] for i in itens] or (sig or ident.split(" ")[0]) in FORA_PAUTA:
            continue
        itens.append({"id": ident, "ementa": (p.get("ementa") or it.get("titulo") or "").strip()})
    return itens


def senado_plenario(dia):
    j = baixar(f"https://legis.senado.leg.br/dadosabertos/plenario/agenda/dia/{dia.replace('-', '')}.json") or {}
    sess = lista(((j.get("AgendaPlenario") or {}).get("Sessoes") or {}).get("Sessao"))
    out = []
    for s in sess:
        if (s.get("SituacaoSessao") or "").lower().startswith("cancel"):
            continue
        mats = []
        for m in lista((s.get("Materias") or {}).get("Materia")):
            ident = (m.get("DescricaoIdentificacaoMateria") or "").strip()
            if ident and ident not in [x["id"] for x in mats] and ident.split(" ")[0] not in FORA_PAUTA:
                mats.append({"id": ident, "ementa": (m.get("Ementa") or "").strip()})
        out.append({"hora": (s.get("Hora") or "").strip(), "tipo": (s.get("TipoSessao") or "").strip().capitalize(),
                    "casa": s.get("Casa"), "itens": mats})
    return out


def senado_comissoes(dia):
    j = baixar(f"https://legis.senado.leg.br/dadosabertos/comissao/agenda/{dia.replace('-', '')}.json") or {}
    rs = lista((((j.get("AgendaReuniao") or {}).get("reunioes")) or {}).get("reuniao"))
    out = []
    for r in rs:
        if (r.get("situacao") or "").lower().startswith("cancel") or r.get("isExibirNoPortal") == "false":
            continue
        col = r.get("colegiadoCriador") or {}
        tipos = {(p.get("descricaoTipo") or "") for p in lista(r.get("partes"))}
        n_itens = sum(len(lista(p.get("itens"))) for p in lista(r.get("partes")))
        if any("Audiência" in t for t in tipos):
            tipo = "Audiência pública"
        elif any("Deliberativa" in t for t in tipos):
            tipo = "Votações" + (f" ({n_itens} itens)" if n_itens else "")
        else:
            tipo = (r.get("tipo") or {}).get("descricao") or "Reunião"
        out.append({"hora": (r.get("dataInicio") or "")[11:16], "sigla": col.get("sigla", ""),
                    "nome": _nome_comissao(col.get("nome", "")), "tipo": tipo})
    out.sort(key=lambda x: x["hora"])
    return out


def _nome_comissao(n):
    n = re.sub(r"^Comissão (Permanente )?(de |do |da |dos |das )?", "", n or "").strip()
    return n[:1].upper() + n[1:]


def camara_dia(evs, dia):
    plen, com = [], []
    for e in evs:
        if not (e.get("dataHoraInicio") or "").startswith(dia):
            continue
        siglas = [o.get("sigla") for o in e.get("orgaos", [])]
        hora = e["dataHoraInicio"][11:16]
        tipo = e.get("descricaoTipo") or ""
        if "PLEN" in siglas:
            if "Solene" in tipo:
                continue  # homenagens: fora da agenda de votações
            plen.append({"id_evento": e["id"], "hora": hora, "tipo": tipo, "itens": []})
        else:
            o = (e.get("orgaos") or [{}])[0]
            nome = o.get("apelido") or o.get("nomeResumido") or o.get("nome") or o.get("sigla", "")
            if o.get("tipoOrgao", "").startswith("Comissão Especial") or len(nome) > 48:
                nome = (o.get("nomeResumido") or nome)
            desc = re.sub(r"\s+", " ", e.get("descricao") or "").strip()
            if "Audiência" in tipo or "Seminário" in tipo or "Mesa" in tipo:
                t = tipo
                tema = re.sub(r"^(Debate sobre|Debater|Tema:)\s*", "", desc, flags=re.I)
                if tema and "Discussão" not in tema[:12]:
                    t = f"{tipo}: {tema}"
            else:
                t = "Votações" if "Deliberativa" in tipo else tipo
            com.append({"hora": hora, "sigla": ",".join(s for s in siglas if s), "nome": _limpa(nome), "tipo": t})
    for p in plen:
        p["itens"] = camara_pauta(p["id_evento"])
    com.sort(key=lambda x: x["hora"])
    return plen, com


def _limpa(s):
    return re.sub(r"\s+", " ", s or "").strip()


def resumo(item, resumos):
    if item["id"] in resumos:
        return resumos[item["id"]]
    e = _limpa(item["ementa"])
    m = re.search(r",\s*para\s+(.*)", e)
    if e.startswith(("Altera", "Acrescenta", "Dá nova redação", "Modifica")) and m:
        e = "Muda a lei para " + m.group(1)
    e = re.sub(r"\s*,?\s*e dá outras providências\.?$", "", e)
    return e


# ------------------------------------------------------------------ desenho

def data_extenso(d):
    return f"{DIAS[d.weekday()]}, {d.day} de {MESES[d.month - 1]}"


def cabecalho(img, d, rotulo, cor=VERDE, larg=W):
    dd = ImageDraw.Draw(img)
    lg = vl.logo(110)
    if lg:
        img.paste(lg, (80, 90), lg)
    dd.text((larg - 80, 150), rotulo.upper(), font=MO(32), fill=OLIVA, anchor="rm")
    return dd


def rodape(dd, y, larg=W, fonte="Fonte: Câmara dos Deputados e Senado Federal"):
    dd.line([(80, y - 30), (larg - 80, y - 30)], fill=BORDA, width=2)
    dd.text((80, y), fonte + " · pauta sujeita a alteração", font=MO(22), fill=CINZA)
    dd.text((80, y + 50), "App: legiscopio.com.br/baixar", font=MO(30), fill=VERDE)
    dd.text((80, y + 95), "Apoie: apoia.se/legiscopio", font=MO(26), fill=OLIVA)


def caixa_lista(dd, x0, y, x1, linhas, cor, ymax, recuo=190, max_sub=3):
    """linhas: [(hora, titulo, subtitulo)]. Desenha cartões até ymax; devolve (y, quantos couberam)."""
    n = 0
    for hora, tit, sub in linhas:
        tl = vl.wrap(dd, tit, BD(40), x1 - x0 - recuo - 40)[:2]
        sl = vl.wrap(dd, sub, RG(32), x1 - x0 - recuo - 40)[:max_sub] if sub else []
        alt = 34 + 50 * len(tl) + 42 * len(sl) + 26
        if y + alt > ymax:
            break
        dd.rounded_rectangle([x0, y, x1, y + alt], radius=22, fill=BR, outline=BORDA, width=2)
        dd.rectangle([x0, y + 14, x0 + 8, y + alt - 14], fill=cor)
        if hora:
            dd.text((x0 + 40, y + 30), hora, font=BK(40), fill=cor)
        yy = y + 30
        for l in tl:
            dd.text((x0 + recuo, yy), l, font=BD(40), fill=TEXTO)
            yy += 50
        for l in sl:
            dd.text((x0 + recuo, yy + 4), l, font=RG(32), fill=CINZA)
            yy += 42
        y += alt + 20
        n += 1
    return y, n


def story_capa(d, info):
    img = Image.new("RGB", (W, H), FUNDO)
    dd = cabecalho(img, d, "Agenda do dia")
    dd.text((80, 330), "Agenda do", font=BK(110), fill=VERDE)
    dd.text((80, 455), "Congresso", font=BK(110), fill=VERDE)
    dd.text((80, 610), data_extenso(d).capitalize(), font=BD(52), fill=TEXTO)
    y = 760
    blocos = [("CÂMARA", CAMARA_COR, info["camara_plen"], len(info["camara_com"])),
              ("SENADO", SENADO_COR, [s for s in info["senado_plen"] if s["casa"] != "CN"], len(info["senado_com"]))]
    for nome, cor, plen, ncom in blocos:
        dd.rounded_rectangle([80, y, W - 80, y + 300], radius=28, fill=BR, outline=BORDA, width=2)
        dd.rectangle([80, y + 20, 92, y + 280], fill=cor)
        dd.text((130, y + 40), nome, font=BK(52), fill=cor)
        if plen:
            hs = " e ".join(p["hora"] for p in plen[:2])
            n = sum(len(p["itens"]) for p in plen)
            dd.text((130, y + 120), f"Plenário: sessão às {hs}", font=BD(42), fill=TEXTO)
            dd.text((130, y + 175), f"{n} {'item' if n == 1 else 'itens'} na pauta" if n else "pauta a divulgar",
                    font=RG(36), fill=CINZA)
        else:
            dd.text((130, y + 120), "Sem sessão de votação no Plenário", font=BD(42), fill=TEXTO)
        dd.text((130, y + 230), f"{ncom} {'reunião' if ncom == 1 else 'reuniões'} de comissões", font=RG(36),
                fill=CINZA)
        y += 340
    cn = [s for s in info["senado_plen"] if s["casa"] == "CN"]
    if cn:
        dd.text((80, y + 10), f"Congresso Nacional (sessão conjunta): {cn[0]['hora']}", font=BD(38), fill=TEXTO)
        y += 70
    dd.text((80, y + 40), "Deslize para ver os detalhes →", font=BD(40), fill=OLIVA)
    rodape(dd, H - 260)
    return img


def story_plenario(d, titulo, cor, sessoes, resumos):
    img = Image.new("RGB", (W, H), FUNDO)
    dd = cabecalho(img, d, data_extenso(d))
    dd.text((80, 300), titulo, font=BK(78), fill=cor)
    y = 420
    for s in sessoes:
        dd.text((80, y), f"{s['hora']} · {s['tipo']}", font=BD(42), fill=TEXTO)
        y += 80
        linhas = [(it["id"].split(" ")[0], it["id"], resumo(it, resumos)) for it in s["itens"]]
        if not linhas:
            dd.text((80, y), "Pauta ainda não divulgada.", font=RG(38), fill=CINZA)
            y += 80
            continue
        y, n = caixa_lista(dd, 80, y, W - 80, [("", f"{a}", c) for _, a, c in linhas], cor, H - 420, recuo=44)
        if n < len(linhas):
            dd.text((80, y), f"+ {len(linhas) - n} {'item' if len(linhas) - n == 1 else 'itens'} na pauta",
                    font=BD(38), fill=OLIVA)
            y += 70
        y += 20
    rodape(dd, H - 260)
    return img


def story_comissoes(d, titulo, cor, reunioes, max_telas=3):
    """Uma ou mais telas (até max_telas) com as reuniões das comissões."""
    telas, resto, k = [], [(r["hora"], r["nome"], r["tipo"]) for r in reunioes], 0
    while resto and len(telas) < max_telas:
        img = Image.new("RGB", (W, H), FUNDO)
        dd = cabecalho(img, d, data_extenso(d))
        tt = titulo if not telas else titulo + " (cont.)"
        dd.text((80, 300), tt, font=BK(78 if not telas else 66), fill=cor)
        if not telas:
            dd.text((80, 400), f"{len(reunioes)} {'reunião' if len(reunioes) == 1 else 'reuniões'} marcadas",
                    font=BD(42), fill=TEXTO)
        y, n = caixa_lista(dd, 80, 490 if not telas else 420, W - 80, resto, cor, H - 420, max_sub=2)
        resto = resto[max(n, 1):]
        if resto and len(telas) == max_telas - 1:
            k = len(resto)
            dd.text((80, y + 6), f"+ {k} {'reunião' if k == 1 else 'reuniões'} · veja todas no app", font=BD(38),
                    fill=OLIVA)
        rodape(dd, H - 260)
        telas.append(img)
    return telas


# ------------------------------------------------------------------ carrossel da semana

def slide_capa(seg, sex):
    img = Image.new("RGB", (WC, HC), VERDE)
    dd = ImageDraw.Draw(img)
    lg = vl.logo(120)
    if lg:
        box = Image.new("RGB", (lg.width + 50, lg.height + 36), BR)
        img.paste(box, (80, 80))
        img.paste(lg, (105, 98), lg)
    dd.text((80, 380), "Agenda da", font=BK(120), fill=BR)
    dd.text((80, 515), "semana no", font=BK(120), fill=BR)
    dd.text((80, 650), "Congresso", font=BK(120), fill=LIMA)
    per = f"{seg.day} a {sex.day} de {MESES[sex.month - 1]}" if seg.month == sex.month else \
        f"{seg.day}/{seg.month:02d} a {sex.day}/{sex.month:02d}"
    dd.text((80, 830), per, font=BD(56), fill=BR)
    dd.text((80, 940), "Plenários da Câmara e do Senado, dia a dia", font=RG(40), fill=LIMA)
    dd.text((80, HC - 140), "Arraste para o lado →", font=BD(44), fill=BR)
    return img


def slide_dia(d, cam_plen, cam_ncom, sen_plen, sen_ncom, resumos):
    img = Image.new("RGB", (WC, HC), FUNDO)
    dd = cabecalho(img, d, "Agenda da semana", larg=WC)
    dd.text((80, 260), data_extenso(d).capitalize(), font=BK(64), fill=VERDE)
    y = 370
    for nome, cor, plen, ncom in (("CÂMARA", CAMARA_COR, cam_plen, cam_ncom),
                                  ("SENADO", SENADO_COR, [s for s in sen_plen if s["casa"] != "CN"], sen_ncom)):
        dd.text((80, y), nome, font=BK(44), fill=cor)
        dd.text((WC - 80, y + 8), f"{ncom} reuniões de comissões", font=RG(32), fill=CINZA, anchor="ra")
        y += 70
        if not plen:
            dd.text((80, y), "Sem sessão de votação no Plenário", font=RG(36), fill=TEXTO)
            y += 80
            continue
        itens = []
        for s in plen:
            itens += s["itens"]
        horas = " e ".join(s["hora"] for s in plen[:2])
        dd.text((80, y), f"Plenário às {horas}", font=BD(38), fill=TEXTO)
        y += 60
        if not itens:
            dd.text((80, y), "Pauta ainda não divulgada", font=RG(34), fill=CINZA)
            y += 70
            continue
        limite_y = (HC - 470) if nome == "CÂMARA" else (HC - 190)  # a Câmara deixa lugar para o Senado
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
            y += 50
        y += 30
    cn = [s for s in sen_plen if s["casa"] == "CN"]
    if cn and y < HC - 230:
        dd.text((80, y), f"Congresso Nacional (sessão conjunta): {cn[0]['hora']}", font=BD(34), fill=TEXTO)
    dd.text((80, HC - 100), "Fonte: Câmara dos Deputados e Senado Federal · pauta sujeita a alteração", font=MO(22),
            fill=CINZA)
    dd.text((80, HC - 60), "App: legiscopio.com.br/baixar", font=MO(26), fill=VERDE)
    return img


def slide_fim():
    img = Image.new("RGB", (WC, HC), VERDE)
    dd = ImageDraw.Draw(img)
    dd.text((80, 300), "Acompanhe tudo", font=BK(96), fill=BR)
    dd.text((80, 420), "no app do", font=BK(96), fill=BR)
    dd.text((80, 540), "Legiscópio", font=BK(96), fill=LIMA)
    for k, t in enumerate(("Agenda da Câmara e do Senado", "Votações e como cada um votou",
                           "Notificações dos seus favoritos")):
        dd.text((80, 720 + k * 70), "✓ " + t, font=BD(42), fill=BR)
    dd.text((80, 1000), "Android: legiscopio.com.br/baixar", font=BK(52), fill=BR)
    dd.text((80, 1080), "iOS em breve · grátis e sem anúncios", font=RG(40), fill=LIMA)
    dd.text((80, 1160), "Apoie: apoia.se/legiscopio", font=BD(40), fill=LIMA)
    return img


# ------------------------------------------------------------------ principal

def gerar(data, pasta=None, forcar_semana=False):
    d = dt.date.fromisoformat(data)
    pasta = Path(pasta) if pasta else ROOT / "posts" / data
    pasta.mkdir(parents=True, exist_ok=True)
    for p in list(pasta.glob("agenda_*.png")) + list(pasta.glob("semana_*.png")):
        p.unlink()
    rp = pasta / "agenda_resumos.json"
    resumos = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}
    arquivos, semana = [], []
    info = {"data": data}
    if d.weekday() < 5:
        evs = camara_eventos(data, data)
        info["camara_plen"], info["camara_com"] = camara_dia(evs, data)
        info["senado_plen"] = senado_plenario(data)
        info["senado_com"] = senado_comissoes(data)
        total = len(info["camara_plen"]) + len(info["camara_com"]) + len(info["senado_plen"]) + len(info["senado_com"])
        if total:
            telas = [story_capa(d, info)]
            if info["camara_plen"]:
                telas.append(story_plenario(d, "Plenário da Câmara", CAMARA_COR, info["camara_plen"], resumos))
            sp = info["senado_plen"]
            if sp:
                titulo = "Plenário do Senado" if all(s["casa"] != "CN" for s in sp) else "Senado e Congresso"
                telas.append(story_plenario(d, titulo, SENADO_COR, sp, resumos))
            if info["camara_com"]:
                telas += story_comissoes(d, "Comissões da Câmara", CAMARA_COR, info["camara_com"])
            if info["senado_com"]:
                telas += story_comissoes(d, "Comissões do Senado", SENADO_COR, info["senado_com"])
            for k, im in enumerate(telas, 1):
                nome = f"agenda_{k}.png"
                im.save(pasta / nome)
                arquivos.append(nome)
    if d.weekday() == 0 or forcar_semana:
        sex = d + dt.timedelta(days=4)
        evs = camara_eventos(data, sex.isoformat())
        slides = [slide_capa(d, sex)]
        dias = []
        for k in range(5):
            dk = d + dt.timedelta(days=k)
            cp, cc = camara_dia(evs, dk.isoformat()) if k else (info.get("camara_plen", []), info.get("camara_com", []))
            sp = senado_plenario(dk.isoformat()) if k else info.get("senado_plen", [])
            sc = senado_comissoes(dk.isoformat()) if k else info.get("senado_com", [])
            dias.append({"data": dk.isoformat(), "camara_plen": cp, "n_camara_com": len(cc), "senado_plen": sp,
                         "n_senado_com": len(sc)})
            if cp or cc or sp or sc:
                slides.append(slide_dia(dk, cp, len(cc), sp, len(sc), resumos))
        slides.append(slide_fim())
        info["semana"] = dias
        if len(slides) > 2:
            for k, im in enumerate(slides, 1):
                nome = f"semana_{k}.png"
                im.save(pasta / nome)
                semana.append(nome)
    info["arquivos"] = arquivos
    info["semana_arquivos"] = semana
    (pasta / "agenda.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print("agenda:", arquivos, semana)
    return arquivos, semana


if __name__ == "__main__":
    gerar(sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat())

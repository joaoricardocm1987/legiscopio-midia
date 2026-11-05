# Único (apaga a si mesmo): tenta baixar pela API do Meshy (só consultas GET, sem gastar crédito) o modelo da Lupa
# feito no site (tarefa 01a1a900-...) e lista as tarefas recentes de modelo/esqueleto/animação da conta.
# Saída: artes/3d/lupa/ (arquivos .glb/.fbx/.png baixados) + log_api.txt
import json
import os
import subprocess
import traceback
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artes" / "3d" / "lupa"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://api.meshy.ai/openapi"
TAREFA = "01a1a900-5701-703f-b7c3-5af8ced3eef1"
log = []


def get(caminho):
    r = urllib.request.Request(BASE + caminho, headers={"Authorization": "Bearer " + os.environ["MESHY_API_KEY"]})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def urls(obj, prefixo=""):
    """Acha todas as URLs de arquivo (glb, fbx, usdz, obj, png...) dentro da resposta."""
    achados = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            achados += urls(v, f"{prefixo}{k}.")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            achados += urls(v, f"{prefixo}{i}.")
    elif isinstance(obj, str) and obj.startswith("http"):
        achados.append((prefixo.rstrip("."), obj))
    return achados


def resumo(d):
    if not isinstance(d, dict):
        return str(d)[:300]
    return json.dumps({k: d.get(k) for k in ("id", "status", "mode", "progress", "task_error", "created_at",
                                              "input_task_id", "rig_task_id", "action_id") if k in d},
                      ensure_ascii=False)


def baixar(nome, u):
    ext = u.split("?")[0].rsplit(".", 1)[-1].lower()
    if ext not in ("glb", "fbx", "usdz", "obj", "mtl", "png", "jpg", "blend", "stl"):
        return
    destino = OUT / f"{nome.replace('.', '_')}.{ext}"
    try:
        with urllib.request.urlopen(u, timeout=300) as resp:
            dados = resp.read()
        if len(dados) > 95 * 1024 * 1024:
            log.append(f"  PULADO (muito grande para o GitHub, {len(dados)//1048576} MB): {destino.name}")
            return
        destino.write_bytes(dados)
        log.append(f"  baixado {destino.name} ({len(dados)//1024} KB)")
    except Exception as e:
        log.append(f"  falha ao baixar {destino.name}: {e}")


try:
    if not os.environ.get("MESHY_API_KEY"):
        raise RuntimeError("MESHY_API_KEY não está disponível no workflow")
    # 1) a tarefa do link, testando cada tipo de endpoint
    for ep in ("/v1/image-to-3d", "/v2/text-to-3d", "/v1/multi-image-to-3d", "/v1/rigging", "/v1/animations",
               "/v1/image-to-image", "/v1/text-to-image", "/v1/retexture", "/v1/remesh"):
        st, d = get(f"{ep}/{TAREFA}")
        log.append(f"{ep}/{TAREFA}: {st} {resumo(d)}")
        if st == 200 and isinstance(d, dict):
            for nome, u in urls(d):
                log.append(f"  url em {nome}")
                baixar(f"tarefa_{ep.split('/')[-1]}_{nome}", u)
    # 2) listas recentes da conta (para achar esqueleto e animações feitos no site)
    for ep in ("/v1/image-to-3d", "/v1/rigging", "/v1/animations"):
        st, d = get(f"{ep}?page_size=20&sort_by=-created_at")
        if st != 200:
            log.append(f"LISTA {ep}: {st} {str(d)[:200]}")
            continue
        itens = d if isinstance(d, list) else d.get("result", d.get("data", []))
        log.append(f"LISTA {ep}: {len(itens)} tarefas")
        for it in itens:
            log.append(f"  - {resumo(it)}")
            if ep != "/v1/image-to-3d" and it.get("status") == "SUCCEEDED":
                for nome, u in urls(it):
                    log.append(f"    url em {nome}")
                    baixar(f"{ep.split('/')[-1]}_{it.get('id', '')[:8]}_{nome}", u)
except Exception:
    log.append(traceback.format_exc())
(OUT / "log_api.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(OUT)], check=True, cwd=ROOT)

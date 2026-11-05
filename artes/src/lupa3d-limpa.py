# Único (apaga a si mesmo): organiza artes/3d/lupa — mantém um arquivo de cada e apaga as cópias repetidas.
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "artes" / "3d" / "lupa"
MANTER = {
    "tarefa_rigging_result_rigged_character_glb_url.glb": "lupa_rig.glb",
    "tarefa_rigging_result_rigged_character_fbx_url.fbx": "lupa_rig.fbx",
    "tarefa_rigging_result_basic_animations_walking_armature_glb_url.glb": "lupa_andando.glb",
    "tarefa_rigging_result_basic_animations_running_armature_glb_url.glb": "lupa_correndo.glb",
    "tarefa_rigging_result_basic_animations_walking_glb_url.glb": "anim_andando_so_ossos.glb",
    "tarefa_rigging_result_basic_animations_running_glb_url.glb": "anim_correndo_so_ossos.glb",
    "tarefa_image-to-3d_model_url.glb": "lupa_modelo.glb",
    "tarefa_image-to-3d_thumbnail_url.png": "lupa_miniatura.png",
    "tarefa_image-to-3d_texture_urls_0_base_color.png": "textura_cor.png",
    "tarefa_image-to-3d_texture_urls_0_normal.png": "textura_normal.png",
    "tarefa_image-to-3d_texture_urls_0_roughness.png": "textura_rugosidade.png",
    "tarefa_image-to-3d_texture_urls_0_metallic.png": "textura_metal.png",
}
log = []
for f in sorted(D.iterdir()):
    if f.name == "log_api.txt":
        continue
    if f.name in MANTER:
        f.rename(D / MANTER[f.name])
        log.append(f"{f.name} -> {MANTER[f.name]}")
    elif f.name.startswith("tarefa_"):
        f.unlink()
        log.append(f"apagado {f.name}")
(D / "log_limpeza.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
Path(__file__).unlink()
subprocess.run(["git", "add", "-A", str(D)], check=True, cwd=ROOT)

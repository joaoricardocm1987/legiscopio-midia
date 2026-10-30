# Vídeo com o rosto do João — teste 01 (editor automático, fora da rotina diária). Revisão 6.
# Baixa o bruto do Google Drive, transcreve, corta, insere títulos/placares, legenda, trata a voz e faz o cartão final.
# Saída: videos/rosto/teste-01/video.mp4 + legendas.srt (o bruto não vai para o git).
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "rosto" / "teste-01"
REVISAO = "6"
sys.path.insert(0, str(ROOT / "scripts"))
try:
    try:
        import numpy  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "numpy"], check=True)
    # bibliotecas gráficas que o MediaPipe (recorte da pessoa) precisa no runner
    subprocess.run("sudo apt-get install -y -q libegl1 libgles2 libgl1 libglib2.0-0", shell=True, check=False)
    rev = PASTA / ".revisao"
    if not rev.exists() or rev.read_text().strip() != REVISAO:  # força um novo render nesta revisão
        (PASTA / ".render").unlink(missing_ok=True)
        rev.write_text(REVISAO + "\n")
    import rosto_editor  # noqa: E402
    rosto_editor.gerar(PASTA)
    (PASTA / "erro.txt").unlink(missing_ok=True)
except Exception:
    traceback.print_exc()
    (PASTA / "erro.txt").write_text(traceback.format_exc(), encoding="utf-8")
finally:
    shutil.rmtree(PASTA / "bruto", ignore_errors=True)
    shutil.rmtree(PASTA / "_tmp", ignore_errors=True)
subprocess.run(["git", "add", str(PASTA)], check=True, cwd=ROOT)

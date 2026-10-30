# Vídeo com o rosto do João — teste 01 (editor automático, fora da rotina diária). Revisão 3.
# Baixa o bruto do Google Drive, transcreve, corta, insere telas/placares atrás da cabeça, legenda e cartão final.
# Saída: videos/rosto/teste-01/video.mp4 + legendas.srt (o bruto não vai para o git).
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "videos" / "rosto" / "teste-01"
sys.path.insert(0, str(ROOT / "scripts"))
try:
    try:
        import numpy  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "numpy"], check=True)
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

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POST = ROOT / "posts" / "2026-10-10" / "post.json"

sys.path.insert(0, str(ROOT / "scripts"))
import render  # noqa: E402

render.main([POST])
subprocess.run(["git", "add", str(POST.parent)], check=True, cwd=ROOT)

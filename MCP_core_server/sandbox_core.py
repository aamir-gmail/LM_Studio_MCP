# sandbox_core.py
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from uuid import uuid4

# Root where all runs are stored and served
TEMP_DIR = Path(os.getenv("SANDBOX_TEMP_DIR", "/app/temp")).resolve()
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# What we consider "images" to auto-expose (viewer will handle non-images too)
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".tiff", ".tif", ".pdf"}

# Execution guardrails
EXEC_TIMEOUT = int(os.getenv("EXEC_TIMEOUT_SECONDS", "30"))

# Toggle autosave of Matplotlib figures at process exit (default on for LM Studio UX)
AUTO_SAVE_MPL = os.getenv("AUTO_SAVE_MPL", "1") not in {"0", "false", "False"}


def _guess_mime(path: Path) -> str:
    import mimetypes
    ctype, _ = mimetypes.guess_type(path.as_posix())
    return ctype or "application/octet-stream"


def _new_run_dir() -> Path:
    """
    Create a unique per-run directory under TEMP_DIR, e.g.:
      /app/temp/20250921-123456-abc123
    """
    run_id = f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:6]}"
    run_dir = TEMP_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def _list_new_images(run_dir: Path) -> List[Dict[str, str]]:
    """
    Recursively list image-like files created within run_dir.
    Return paths relative to TEMP_DIR so /files/<relpath> works.
    """
    out: List[Dict[str, str]] = []
    for p in sorted(run_dir.rglob("*")):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in IMAGE_EXTS:
            rel = p.relative_to(TEMP_DIR).as_posix()  # e.g. "20250921-.../sine.png"
            out.append({"filename": rel, "content_type": _guess_mime(p)})
    return out


def _wrap_with_mpl_autosave(user_code: str) -> str:
    """
    Prepend a small shim that:
      - Forces a non-interactive backend.
      - Registers an atexit handler to save any open figures as figure_N.png
        if the user didn't explicitly save them.
    """
    if not AUTO_SAVE_MPL:
        return user_code

    prelude = r"""
# --- sandbox autosave shim (matplotlib) ---
try:
    import os, atexit
    import matplotlib
    try:
        matplotlib.use("Agg")  # ensure headless backend
    except Exception:
        pass
    try:
        import matplotlib.pyplot as plt
    except Exception:
        plt = None

    def _sandbox_autosave_figs():
        try:
            if plt is None:
                return
            # Gather current figures and save any that aren't saved yet.
            figs = []
            try:
                figs = [plt.figure(num) for num in plt.get_fignums()]
            except Exception:
                pass
            for idx, fig in enumerate(figs, 1):
                path = f"figure_{idx}.png"
                try:
                    fig.savefig(path, bbox_inches="tight")
                except Exception:
                    # ignore individual save errors, keep going
                    pass
        except Exception:
            pass

    atexit.register(_sandbox_autosave_figs)
except Exception:
    # Never let the shim break user code
    pass
# --- end autosave shim ---
"""
    return prelude + "\n" + user_code


def execute_python(code: str) -> Dict[str, object]:
    """
    Run 'code' in a sandboxed subprocess with a fresh per-run CWD = <TEMP_DIR>/<run_id>.
    Collects any image-like files created during execution (recursively).
    Returns:
      {
        "stdout": str,
        "stderr": str,
        "returncode": int,
        "images": [ { "filename": str, "content_type": str }, ... ]
      }
    """
    run_dir = _new_run_dir()

    # Prepare environment (force non-interactive MPL backend)
    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")

    # Inject autosave shim so figures are persisted even if user forgets to savefig()
    wrapped = _wrap_with_mpl_autosave(code)

    cmd = [sys.executable, "-c", wrapped]

    try:
        proc = subprocess.run(
            cmd,
            cwd=run_dir,            # isolate writes into this unique folder
            env=env,
            capture_output=True,
            text=True,
            timeout=EXEC_TIMEOUT,
        )
        stdout = proc.stdout
        stderr = proc.stderr
        returncode = proc.returncode
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ""
        stderr = (e.stderr or "") + f"\n[timeout] Execution exceeded {EXEC_TIMEOUT}s"
        returncode = 124
    except Exception as e:
        stdout, stderr, returncode = "", f"[runner error] {e}", 1

    images = _list_new_images(run_dir)

    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
        "images": images,
    }


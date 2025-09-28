from __future__ import annotations

import html
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sandbox_core import TEMP_DIR, execute_python

app = FastAPI(title="Python Sandbox REST")

# Serve raw generated files (including per-run subfolders)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=TEMP_DIR), name="files")


class ImageRecord(BaseModel):
    filename: str        # may include subfolders, e.g. run-id/sine.png
    content_type: str
    note: Optional[str] = None


class ExecRequest(BaseModel):
    code: str


class ExecResponse(BaseModel):
    stdout: str
    stderr: str
    returncode: int
    images: List[ImageRecord]


@app.post("/execute", response_model=ExecResponse, response_model_exclude_none=True)
def execute(req: ExecRequest):
    """
    Execute Python source in a subprocess with CWD=<TEMP_DIR>/<run_id>
    and return stdout/stderr/returncode plus any new image files.
    """
    result = execute_python(req.code)
    return ExecResponse(**result)


def _resolve_safe(relpath: str) -> Path:
    """
    Safely resolve a relative path under TEMP_DIR, allowing subfolders,
    and prevent directory traversal.
    """
    base = TEMP_DIR.resolve()
    candidate = (base / relpath).resolve()
    if not candidate.is_file() or not candidate.is_relative_to(base):
        raise HTTPException(status_code=404, detail="File not found")
    return candidate


@app.get("/view/{relpath:path}", response_class=HTMLResponse)
def view_file(relpath: str):
    """Simple HTML viewer for images/PDF/SVG/etc under TEMP_DIR (with subfolders)."""
    file_path = _resolve_safe(relpath)
    rel_display = file_path.relative_to(TEMP_DIR).as_posix()

    file_url = f"/files/{html.escape(rel_display)}"
    ctype = "application/octet-stream"
    try:
        import mimetypes
        ctype = mimetypes.guess_type(file_path.as_posix())[0] or ctype
    except Exception:
        pass

    if ctype.startswith("image/"):
        body = f'<img src="{file_url}" alt="{html.escape(rel_display)}" style="max-width:100%;height:auto" />'
    else:
        body = (
            f'<object data="{file_url}" type="{ctype}" width="100%" height="90vh">'
            f'<a href="{file_url}">Open file</a></object>'
        )

    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>View: {html.escape(rel_display)}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>body {{ font-family: system-ui, sans-serif; margin: 16px; }}</style>
  </head>
  <body>
    <h3>{html.escape(rel_display)}</h3>
    {body}
  </body>
</html>"""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
    return """<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Python Sandbox REST</title></head>
  <body style="font-family: system-ui, sans-serif; margin:16px">
    <h2>Python Sandbox REST</h2>
    <p>Use the <code>/execute</code> POST endpoint to run code. Generated files (per-run folders) are under <code>/files</code>.</p>
    <ul>
      <li><a href="/docs">OpenAPI docs</a></li>
      <li><a href="/health">Health</a></li>
    </ul>
  </body>
</html>"""


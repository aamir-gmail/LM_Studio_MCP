from __future__ import annotations

import os
import re
import html
import threading
from typing import Dict, List

# FastMCP import: support multiple versions
try:
    from fastmcp import FastMCP  # modern versions
except Exception:  # fallback for older releases
    from fastmcp import MCP as FastMCP

import uvicorn

from sandbox_core import execute_python
from rest_app import app as rest_app  # reuse the same FastAPI app

# Prefer runtime-provided value; fallback is only for local dev
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
PUBLIC_BASE_URL_MODE = os.getenv("PUBLIC_BASE_URL_MODE", "rest")  # "rest" | "plain"

server = FastMCP("Python Sandbox (Single Image)")


def _without_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def _escape_toolish_tags(s: str) -> str:
    """
    Escape only the bits that LM Studio might mistake for tool calls,
    while leaving normal text, markdown, and JSON unchanged.
    """
    if not s:
        return s
    # Escape common "tool-like" tags
    patterns = [
        r"</?\s*tool_call\b[^>]*>",
        r"</?\s*tool_result\b[^>]*>",
        r"</?\s*thinking\b[^>]*>",
        r"</?\s*think\b[^>]*>",
    ]
    for pat in patterns:
        s = re.sub(pat, lambda m: html.escape(m.group(0)), s, flags=re.IGNORECASE)
    # Escape angle-bracketed URLs like <http://...>
    s = re.sub(r"<\s*https?://[^>]+>", lambda m: html.escape(m.group(0)), s, flags=re.IGNORECASE)
    return s


# Strip base64 data-URI images from text output (LM Studio doesn't use them)
_DATA_URI_RE = re.compile(
    r"data:image/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=\s]+",
    re.IGNORECASE,
)

def _strip_data_uris(s: str) -> str:
    if not s:
        return s
    s = _DATA_URI_RE.sub("", s)
    # tidy up whitespace after removals
    s = re.sub(r"[ \t]+(\r?\n)", r"\1", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s


def _with_links(image_record: Dict[str, object]) -> Dict[str, object]:
    """
    Augment a sandbox_core image record with absolute links.

    Modes:
      - rest  : base + /files/<relpath> (served by the sandbox FastAPI)
      - plain : base + /<relpath>       (served by the external static server)
    """
    filename = str(image_record.get("filename", ""))
    base = PUBLIC_BASE_URL.rstrip("/")

    if PUBLIC_BASE_URL_MODE.lower() == "plain":
        rec = {
            **image_record,
            "url": f"{base}/{filename}",
            # no iframe viewer on the static server
        }
    else:
        rec = {
            **image_record,
            "url": f"{base}/files/{filename}",
            "iframe_url": f"{base}/view/{filename}",
        }
    return _without_none(rec)


def _start_rest_background():
    """Launch the REST app (files + /execute + /view) in a background thread."""
    def _run():
        uvicorn.run(rest_app, host="0.0.0.0", port=8000, log_level="info")
    t = threading.Thread(target=_run, name="rest-uvicorn", daemon=True)
    t.start()


@server.tool()
def execute_python_code(code: str) -> Dict[str, object]:
    """
    Executes Python code in a sandboxed subprocess and returns:
      - stdout (str)
      - stderr (str)
      - returncode (int)
      - images (list[{filename, content_type, note?, url, iframe_url}])
        * filename may include subfolders (per-run isolation)
    """
    result = execute_python(code)

    # Make sure the keys exist and are of expected types
    stdout = result.get("stdout", "") or ""
    stderr = result.get("stderr", "") or ""
    images: List[Dict[str, object]] = result.get("images") or []
    if not isinstance(images, list):
        images = []

    # 1) Prevent LM Studio from mis-parsing output as a tool call
    stdout = _escape_toolish_tags(stdout)
    stderr = _escape_toolish_tags(stderr)

    # 2) Remove base64 data-URI images from text output
    stdout = _strip_data_uris(stdout)
    stderr = _strip_data_uris(stderr)

    # 3) Build absolute links for images (persisted URLs)
    images = [_with_links(img) for img in images]

    # 4) Optional: if there are images but stdout is empty, provide a helpful note
    if not stdout.strip() and images:
        first = images[0].get("url") or images[0].get("iframe_url") or ""
        hint = f"Generated image(s). Example: {first}" if first else "Generated image(s)."
        stdout = hint

    # 5) Graceful no-image scenario: do nothing special — keep text output as-is.
    #    (stdout/stderr already sanitized; images is an empty list.)

    result["stdout"] = stdout
    result["stderr"] = stderr
    result["images"] = images

    return {"result": result}


def run_stdio_compat():
    """Start the MCP server in stdio mode across fastmcp versions."""
    try:
        server.run(transport="stdio")
    except TypeError:
        server.run_stdio()


def run_http_compat():
    """Optional HTTP transport (unused by mcp.json here)."""
    server.run(transport="http")


if __name__ == "__main__":
    _start_rest_background()
    run_stdio_compat()


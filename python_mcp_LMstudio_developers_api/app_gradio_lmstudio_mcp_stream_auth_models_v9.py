# app_gradio_lmstudio_mcp_stream_auth_models_v7.py
# Max instrumentation + guaranteed Artifacts links + tool-call popup

import os
import re
import json
import time
import hashlib
import requests
import gradio as gr
from typing import Dict, Any, List, Iterable, Optional, Tuple
from urllib.parse import urlparse
from pathlib import Path
from ui_logging import configure_logging, make_rid
from sys_prompt import SYSTEM_PROMPT

# -------------------- Config --------------------
LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://192.168.1.133:1234")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen.qwen3-coder-30b-a3b-instruct")
SANDBOX_BASE_URL = os.getenv("SANDBOX_BASE_URL", "http://192.168.1.133:8000")
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", "/app/artifacts")).resolve()
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACTS_EXTERNAL_BASE = os.getenv("ARTIFACTS_EXTERNAL_BASE", "").rstrip("/")

UI_LOG_ENABLED = os.getenv("UI_LOG_ENABLED", "1") in ("1", "true", "TRUE", "yes", "on")
UI_LOG_LEVEL = os.getenv("UI_LOG_LEVEL", "DEBUG")
UI_LOG_DIR = os.getenv("UI_LOG_DIR", "/app/logs")
UI_LOG_FORMAT = os.getenv("UI_LOG_FORMAT", "json")

# Tracing controls
UI_TRACE_VERBOSE = os.getenv("UI_TRACE_VERBOSE", "1") in ("1", "true", "TRUE", "yes", "on")
UI_TRACE_MAXLEN = int(os.getenv("UI_TRACE_MAXLEN", "4000"))
UI_TRACE_SAVE_BLOBS = os.getenv("UI_TRACE_SAVE_BLOBS", "0") in ("1", "true", "TRUE", "yes", "on")
UI_TRACE_INCLUDE_CODE = os.getenv("UI_TRACE_INCLUDE_CODE", "1") in ("1", "true", "TRUE", "yes", "on")

# Optional basic auth
UI_USER = os.getenv("UI_USER", "")
UI_PASS = os.getenv("UI_PASS", "")

# Logger
log = configure_logging(
    enabled=UI_LOG_ENABLED,
    level=UI_LOG_LEVEL,
    log_dir=UI_LOG_DIR,
    name="ui",
    fmt=UI_LOG_FORMAT,
)

# Prepare blob dir if needed
BLOB_DIR = Path(UI_LOG_DIR) / "blobs"
if UI_TRACE_SAVE_BLOBS:
    BLOB_DIR.mkdir(parents=True, exist_ok=True)

# -------------------- Trace helpers --------------------
def _clip_str(s: str, n: Optional[int] = None) -> str:
    if not isinstance(s, str):
        try:
            s = json.dumps(s, ensure_ascii=False)
        except Exception:
            s = str(s)
    n = n or UI_TRACE_MAXLEN
    return s if len(s) <= n else (s[:n] + f"...[{len(s)-n} more]")

def _sha(text: str) -> str:
    try:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    except Exception:
        return "NA"

def dump_blob(kind: str, rid: str, body: Any, suffix: str = "json") -> Optional[str]:
    if not UI_TRACE_SAVE_BLOBS:
        return None
    try:
        fn = BLOB_DIR / f"{int(time.time()*1000)}_{rid}_{kind}.{suffix}"
        if isinstance(body, (dict, list)):
            fn.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            fn.write_text(str(body), encoding="utf-8")
        return str(fn)
    except Exception:
        log.exception("blob_dump_error", extra={"marker": "BLOB_DUMP_ERROR", "rid": rid, "kind": kind})
        return None

def trace(marker: str, rid: Optional[str] = None, **fields):
    if not UI_LOG_ENABLED:
        return
    if not UI_TRACE_VERBOSE:
        compact = {}
        for k, v in fields.items():
            if isinstance(v, str):
                compact[k] = len(v)
            elif isinstance(v, (dict, list)):
                compact[k] = f"type={type(v).__name__} size≈{len(str(v))}"
            else:
                compact[k] = v
        fields = compact
    else:
        for k, v in list(fields.items()):
            if isinstance(v, str):
                fields[k] = _clip_str(v)
    payload = {"marker": marker}
    if rid:
        payload["rid"] = rid
    payload.update(fields)
    log.info("trace", extra=payload)

def _join_url(base: str, path: str) -> str:
    base = base.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path

def _time_ms() -> int:
    return int(time.time() * 1000)

# -------------------- Endpoints controls --------------------
def set_endpoints(lm_url: str, model: str, sbx_url: str) -> str:
    global LMSTUDIO_BASE_URL, MODEL_NAME, SANDBOX_BASE_URL
    LMSTUDIO_BASE_URL = lm_url.strip().rstrip("/") or LMSTUDIO_BASE_URL
    MODEL_NAME = model.strip() or MODEL_NAME
    SANDBOX_BASE_URL = sbx_url.strip().rstrip("/") or SANDBOX_BASE_URL
    trace("SET_ENDPOINTS", lm=LMSTUDIO_BASE_URL, model=MODEL_NAME, sbx=SANDBOX_BASE_URL)
    return f"LM Studio: {LMSTUDIO_BASE_URL}, Model: {MODEL_NAME}, Sandbox: {SANDBOX_BASE_URL}"

# -------------------- Models dropdown --------------------
def list_models() -> List[str]:
    rid = make_rid()
    url = _join_url(LMSTUDIO_BASE_URL, "/v1/models")
    t0 = _time_ms()
    try:
        trace("MODELS_BEGIN", rid=rid, url=url)
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        ids = [item.get("id") for item in data.get("data", []) if item.get("id")]
        dt = _time_ms() - t0
        trace("MODELS_OK", rid=rid, count=len(ids), ms=dt)
        dump_blob("models_resp", rid, data)
        return ids or [MODEL_NAME]
    except Exception as e:
        dt = _time_ms() - t0
        trace("MODELS_ERR", rid=rid, ms=dt, error=str(e))
        return [MODEL_NAME]

def refresh_models() -> gr.Dropdown:
    ids = list_models()
    value = MODEL_NAME if MODEL_NAME in ids else (ids[0] if ids else MODEL_NAME)
    return gr.Dropdown.update(choices=ids, value=value)

def set_model(selected: str) -> str:
    global MODEL_NAME
    if selected:
        MODEL_NAME = selected
        trace("MODEL_SET", model=MODEL_NAME)
    return f"Using model: {MODEL_NAME}"

# -------------------- Streaming helpers --------------------
def _iter_sse_lines(resp, rid: str):
    total = 0
    for raw in resp.iter_lines(decode_unicode=True):
        if not raw:
            continue
        if raw.startswith("data:"):
            raw = raw[len("data:"):].strip()
        if raw == "[DONE]":
            trace("STREAM_DONE", rid=rid, total=total)
            break
        try:
            total += 1
            if UI_TRACE_VERBOSE:
                trace("STREAM_LINE", rid=rid, line=_clip_str(raw, 512))
        except Exception:
            pass
        yield raw

# -------------------- Cutoff detection --------------------
_CUTOFF_SNIPPETS = (
    "Let me fix", "I see the issue", "Here's the fixed", "Let me update",
    "The corrected code", "I'll rewrite", "We can fix this by", "To fix this",
    "The solution is", "Here is the code", "Fixed code", "Updated code",
)

def looks_cut_off(txt: str) -> bool:
    if not txt:
        return False
    t = txt.strip()
    if t.count("```") % 2 == 1:
        return True
    if re.search(r"[\w\)\]]\s*$", t) and not re.search(r"[\.!\?]$", t):
        return True
    if t.endswith((":", ";", "—", "-", "…")):
        return True
    if any(snip.lower() in t.lower() for snip in _CUTOFF_SNIPPETS) and not re.search(r"```[a-zA-Z]*\s", t):
        return True
    return False

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
def strip_code_blocks(s: str) -> str:
    return CODE_FENCE_RE.sub("[code hidden – ask to see it]", s or "")

# -------------------- Sandbox helpers --------------------
def sandbox_execute_raw(code: str, rid: Optional[str] = None) -> Dict[str, Any]:
    exec_url = _join_url(SANDBOX_BASE_URL, "/execute")
    t0 = _time_ms()
    try:
        trace("SANDBOX_EXEC_BEGIN", rid=rid, url=exec_url, len_code=len(code), code_hash=_sha(code))
        if UI_TRACE_INCLUDE_CODE:
            dump_blob("sandbox_req_code", rid or make_rid(), code, suffix="py")
        r = requests.post(exec_url, json={"code": code}, timeout=600)
        r.raise_for_status()
        data = r.json()
        dt = _time_ms() - t0
        trace("SANDBOX_EXEC_RESULT",
              rid=rid,
              ms=dt,
              rc=data.get("returncode", None),
              stdout_len=len(data.get("stdout", "") or ""),
              stderr_len=len(data.get("stderr", "") or ""),
              images=len((data.get("images") or [])))
        dump_blob("sandbox_resp", rid or make_rid(), data)
        return data
    except Exception as e:
        dt = _time_ms() - t0
        trace("SANDBOX_EXEC_ERROR", rid=rid, ms=dt, error=str(e))
        return {"error": str(e)}

def sandbox_execute(code: str):
    rid = make_rid()
    trace("SANDBOX_UI_RUN", rid=rid, len_code=len(code), code_hash=_sha(code))
    data = sandbox_execute_raw(code, rid=rid)
    if "error" in data:
        return "", f"[client-error] {data['error']}", -1, [], [], []
    stdout = data.get("stdout", "")
    stderr = data.get("stderr", "")
    rc = int(data.get("returncode", -1))
    images = data.get("images") or []
    links = []
    gallery_urls = []
    for rec in images:
        filename = rec.get("filename") or ""
        url = rec.get("url") or ""
        iframe = rec.get("iframe_url") or ""
        if ARTIFACTS_EXTERNAL_BASE and filename:
            url = f"{ARTIFACTS_EXTERNAL_BASE}/{filename}"
            iframe = url
        elif not url and filename:
            url = _join_url(SANDBOX_BASE_URL, f"/files/{filename}")
            iframe = _join_url(SANDBOX_BASE_URL, f"/view/{filename}")
        links.append([filename, url, iframe])
        if url:
            gallery_urls.append(url)
    trace("SANDBOX_UI_PARSED", rid=rid, images=len(images), links=len(links), gallery=len(gallery_urls))
    return stdout, stderr, rc, images, links, gallery_urls

# -------------------- Tool schema --------------------
PY_SANDBOX_TOOL = {
    "type": "function",
    "function": {
        "name": "python_sandbox_execute",
        "description": (
            "Run Python code inside the provided sandbox and return its results. "
            "When generating files or figures, ALWAYS save to the CURRENT WORKING DIRECTORY (CWD) "
            "(use relative paths like 'plot.png' or './images/plot.png'). "
            "Do NOT use absolute paths like '/app/temp' directly. The sandbox runs each call in a fresh "
            "per-run CWD under '/app/temp/<run_id>' and automatically exposes anything saved there. "
            "Use the installed scientific stack. Preserve aspect ratio for images."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The exact Python code to execute in the sandbox."
                }
            },
            "required": ["code"],
        },
    },
}

# -------------------- Chat passes --------------------
def _first_chat_pass(
    messages: List[Dict[str, Any]],
    temperature: float,
    max_tokens: int,
    tools: Optional[List[Dict[str, Any]]],
    rid: str,
):
    url = _join_url(LMSTUDIO_BASE_URL, "/v1/chat/completions")
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens if max_tokens > 0 else None,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    payload = {k: v for k, v in payload.items() if v is not None}
    t0 = _time_ms()
    trace("FIRST_PASS_BEGIN", rid=rid, url=url, temp=temperature, max_tokens=payload.get("max_tokens"), tools=bool(tools))
    dump_blob("chat_first_req", rid, payload)
    r = requests.post(url, json=payload, timeout=600)
    r.raise_for_status()
    data = r.json()
    dt = _time_ms() - t0
    try:
        calls = (data.get("choices") or [{}])[0].get("message", {}).get("tool_calls") or []
        trace("FIRST_PASS_RESULT", rid=rid, ms=dt, tool_calls=len(calls))
    finally:
        dump_blob("chat_first_resp", rid, data)
    return data

def _final_chat_stream(
    messages: List[Dict[str, Any]],
    temperature: float,
    max_tokens: int,
    rid: str,
) -> Iterable[str]:
    url = _join_url(LMSTUDIO_BASE_URL, "/v1/chat/completions")
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens if max_tokens > 0 else None,
        "stream": True,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    dump_blob("chat_final_stream_req", rid, payload)
    t0 = _time_ms()
    with requests.post(url, json=payload, stream=True, timeout=600) as resp:
        resp.raise_for_status()
        full = ""
        n_chunks = 0
        for line in _iter_sse_lines(resp, rid=rid):
            try:
                obj = json.loads(line)
                delta = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if delta:
                    n_chunks += 1
                    full += delta
                    if UI_TRACE_VERBOSE:
                        trace("STREAM_CHUNK", rid=rid, add=len(delta), total=len(full), chunks=n_chunks)
                    yield full
            except Exception:
                continue
        dt = _time_ms() - t0
        trace("FINAL_STREAM_DONE", rid=rid, ms=dt, chunks=n_chunks, total=len(full))
        dump_blob("chat_final_stream_result", rid, {"text": full})
        yield full

def _final_chat_once(
    messages: List[Dict[str, Any]],
    temperature: float,
    max_tokens: int,
    rid: str,
) -> str:
    url = _join_url(LMSTUDIO_BASE_URL, "/v1/chat/completions")
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens if max_tokens > 0 else None,
        "stream": False,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    dump_blob("chat_final_req", rid, payload)
    t0 = _time_ms()
    resp = requests.post(url, json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    dt = _time_ms() - t0
    text = data["choices"][0]["message"]["content"]
    trace("FINAL_ONCE_OK", rid=rid, ms=dt, chars=len(text))
    dump_blob("chat_final_resp", rid, data)
    return text

def _auto_continue_loop(
    history: List[Dict[str, str]],
    api_messages: List[Dict[str, Any]],
    temperature: float,
    max_tokens: int,
    stream_final: bool,
    auto_continue: bool,
    max_cont: int,
    strip_code: bool,
    rid: str,
):
    if not history or history[-1].get("role") != "assistant":
        history.append({"role": "assistant", "content": ""})

    def _run_one_pass_and_yield():
        if stream_final:
            for text in _final_chat_stream(api_messages, temperature, max_tokens, rid=rid):
                history[-1] = {"role": "assistant", "content": text}
                yield history, ""
            return history[-1]["content"]
        else:
            text = _final_chat_once(api_messages, temperature, max_tokens, rid=rid)
            history[-1] = {"role": "assistant", "content": text}
            yield history, ""
            return text

    for out in _run_one_pass_and_yield():
        yield out
    final_text = history[-1]["content"]
    trace("FINAL_PASS_RESULT", rid=rid, chars=len(final_text))

    if not auto_continue:
        if strip_code and final_text:
            final_text = strip_code_blocks(final_text)
            history[-1]["content"] = final_text
            trace("SANITIZE_CODE", rid=rid, applied=True, final_len=len(final_text))
            yield history, ""
        return

    for i in range(int(max_cont)):
        if not looks_cut_off(final_text):
            break
        trace("AUTO_CONTINUE_TRIGGER", rid=rid, iter=i + 1, current_len=len(final_text))
        api_messages.append({"role": "assistant", "content": final_text})
        api_messages.append({"role": "user", "content": "Continue exactly where you left off. If you were writing code, finish it inside a single fenced block."})

        if stream_final:
            for text in _final_chat_stream(api_messages, temperature, max_tokens, rid=rid):
                history[-1] = {"role": "assistant", "content": final_text + ("\n" if text else "") + text}
                yield history, ""
            final_text = history[-1]["content"]
        else:
            more = _final_chat_once(api_messages, temperature, max_tokens, rid=rid)
            final_text = final_text + ("\n" if more else "") + more
            history[-1] = {"role": "assistant", "content": final_text}
            yield history, ""

    trace("AUTO_CONTINUE_DONE", rid=rid, total_len=len(final_text))
    if strip_code and final_text:
        final_text = strip_code_blocks(final_text)
        history[-1]["content"] = final_text
        trace("SANITIZE_CODE", rid=rid, applied=True, final_len=len(final_text))
        yield history, ""

# -------------------- Links helper --------------------
def _links_from_images(images):
    links = []
    for rec in images or []:
        fname = rec.get("filename") or ""
        url = rec.get("url") or ""
        if not url and fname:
            url = _join_url(SANDBOX_BASE_URL, f"/files/{fname}")  # fallback
        if fname and url:
            links.append((fname, url))
    return links

# -------------------- Download/persist helpers --------------------
def _download(url: str, dest: Path, rid: Optional[str] = None):
    t0 = _time_ms()
    try:
        trace("DOWNLOAD_BEGIN", rid=rid, url=url, dest=str(dest))
        with requests.get(url, stream=True, timeout=600) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        dt = _time_ms() - t0
        trace("DOWNLOAD_OK", rid=rid, bytes=dest.stat().st_size, ms=dt)
    except Exception as e:
        dt = _time_ms() - t0
        trace("DOWNLOAD_ERR", rid=rid, ms=dt, error=str(e))
        raise

def persist_images(images: List[Dict[str, Any]]):
    rid = make_rid()
    if not images:
        trace("PERSIST_NO_IMAGES", rid=rid)
        return "No images to download.", []
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_dir = ARTIFACTS_DIR / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for rec in images:
        url = rec.get("url") or ""
        filename = rec.get("filename") or ""
        if ARTIFACTS_EXTERNAL_BASE and filename:
            url = f"{ARTIFACTS_EXTERNAL_BASE}/{filename}"
        if not url and filename:
            url = _join_url(SANDBOX_BASE_URL, f"/files/{filename}")
        if not url:
            continue
        name = filename or Path(urlparse(url).path).name or f"file_{len(saved)+1}"
        dest = out_dir / name
        try:
            _download(url, dest, rid=rid)
            saved.append(str(dest))
        except Exception as e:
            (out_dir / f"ERROR_{name}.txt").write_text(str(e), encoding="utf-8")
    msg = f"Saved {len(saved)} file(s) to {out_dir}"
    trace("PERSIST_DONE", rid=rid, dir=str(out_dir), count=len(saved))
    return msg, [Path(p) for p in saved]

# -------------------- UI --------------------
def _init_models() -> Tuple[List[str], str]:
    ids = list_models()
    value = MODEL_NAME if MODEL_NAME in ids else (ids[0] if ids else MODEL_NAME)
    return ids, value

INIT_MODELS, INIT_VALUE = _init_models()

with gr.Blocks(title="LM Studio + MCP (max logging)") as demo:
    gr.Markdown("## LM Studio + MCP — max logging build (tools, auto-continue, payload tracing)")

    with gr.Accordion("Endpoints & Model", open=False):
        lm_url = gr.Textbox(label="LM Studio Base URL", value=LMSTUDIO_BASE_URL)
        models_dd = gr.Dropdown(label="Model", choices=INIT_MODELS, value=INIT_VALUE, allow_custom_value=True)
        refresh = gr.Button("Refresh models")
        apply_model = gr.Button("Set selected model")
        model_status = gr.Markdown()
        sbx_url = gr.Textbox(label="Sandbox Base URL", value=SANDBOX_BASE_URL)
        set_btn = gr.Button("Apply URLs")
        status = gr.Markdown()
        refresh.click(refresh_models, outputs=models_dd)
        apply_model.click(set_model, inputs=models_dd, outputs=model_status)
        set_btn.click(set_endpoints, inputs=[lm_url, models_dd, sbx_url], outputs=status)

    with gr.Tab("Chat"):
        sys_prompt = gr.Textbox(
            label="System prompt",
            lines=9,
            value=(SYSTEM_PROMPT
            ),
        )
        stream_toggle = gr.Checkbox(label="Stream final answer", value=True)
        allow_tools = gr.Checkbox(label="Allow tool calls (python_sandbox_execute)", value=True)
        auto_continue = gr.Checkbox(label="Auto-continue on cutoff", value=True)
        max_continues = gr.Slider(0, 3, value=1, step=1, label="Max continues")
        chat = gr.Chatbot(type="messages", height=420)
        user_in = gr.Textbox(label="Your message")
        with gr.Row():
            temp = gr.Slider(0.0, 2.0, value=0.7, step=0.1, label="temperature")
            max_toks = gr.Slider(0, 4096, value=1024, step=16, label="max_tokens (0 = provider default)")
        send = gr.Button("Send", variant="primary")

        def chat_send(history, user_message, temperature, max_tokens, sys_prompt,
                      stream_final, tools_enabled, auto_cont, max_cont):
            rid = make_rid()
            try:
                trace("CHAT_INPUT", rid=rid,
                      msg_len=len(user_message or ""),
                      temp=float(temperature),
                      max_tokens=int(max_tokens),
                      stream=bool(stream_final),
                      tools=bool(tools_enabled),
                      auto=bool(auto_cont),
                      max_cont=int(max_cont))

                history = history or []
                history.append({"role": "user", "content": user_message or ""})

                api_messages: List[Dict[str, Any]] = []
                if sys_prompt and sys_prompt.strip():
                    api_messages.append({"role": "system", "content": sys_prompt})
                api_messages.extend(history)

                tools = [PY_SANDBOX_TOOL] if tools_enabled else None
                first = _first_chat_pass(api_messages, float(temperature), int(max_tokens), tools, rid=rid)

                msg0 = first["choices"][0]["message"]
                tool_calls = msg0.get("tool_calls") or []
                trace("TOOL_DETECTED", rid=rid, count=len(tool_calls))

                # ------------------------- TOOL PATH -------------------------
                if tool_calls:
                    # Popup toast + inline status message
                    gr.Info("Calling Python sandbox…")
                    history.append({"role": "assistant", "content": "🔧 Executing in Python sandbox…"})

                    accum_images: List[Dict[str, Any]] = []

                    api_messages.append({
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tc.get("id"),
                                "type": tc.get("type"),
                                "function": tc.get("function"),
                            } for tc in tool_calls
                        ],
                    })

                    for idx, tc in enumerate(tool_calls, start=1):
                        fn = (tc.get("function") or {}).get("name", "") or ""
                        args_str = (tc.get("function") or {}).get("arguments", "{}")
                        try:
                            args = json.loads(args_str) if isinstance(args_str, str) else (args_str or {})
                        except Exception:
                            args = {}

                        result_payload: Dict[str, Any] = {"error": f"Unsupported tool: {fn}"}
                        if fn == "python_sandbox_execute":
                            code_to_run = args.get("code", "") or ""
                            trace("TOOL_CALL_BEGIN", rid=rid, idx=idx, tool=fn,
                                  len_code=len(code_to_run), code_hash=_sha(code_to_run))
                            if UI_TRACE_INCLUDE_CODE:
                                dump_blob("tool_code", rid, code_to_run, suffix="py")

                            data = sandbox_execute_raw(code_to_run, rid=rid)

                            imgs = data.get("images") or []
                            for rec in imgs:
                                fnm = rec.get("filename") or ""
                                if ARTIFACTS_EXTERNAL_BASE and fnm:
                                    rec["url"] = f"{ARTIFACTS_EXTERNAL_BASE}/{fnm}"
                                    rec["iframe_url"] = rec["url"]
                            result_payload = data
                            accum_images.extend(result_payload.get("images") or [])

                            trace("TOOL_CALL_RESULT", rid=rid, idx=idx,
                                  rc=result_payload.get("returncode", None),
                                  stdout_len=len(result_payload.get("stdout", "") or ""),
                                  stderr_len=len(result_payload.get("stderr", "") or ""),
                                  images=len((result_payload.get("images") or [])))

                        api_messages.append({
                            "role": "tool",
                            "content": json.dumps(result_payload),
                            "tool_call_id": tc.get("id"),
                        })

                    # Final assistant message after tool: non-stream + strip code
                    history[-1] = {"role": "assistant", "content": ""}
                    for pair in _auto_continue_loop(
                        history,
                        api_messages,
                        float(temperature),
                        int(max_tokens),
                        False,                 # non-streamed when a tool ran
                        bool(auto_cont),
                        int(max_cont),
                        True,                  # strip fenced code
                        rid=rid,
                    ):
                        yield pair

                    # Always append visible Artifacts links (independent of model prose)
                    link_pairs = _links_from_images(accum_images)
                    if link_pairs:
                        appendix = "\n\n**Artifacts**:\n" + "\n".join([f"- [{n}]({u})" for n, u in link_pairs])
                        last = history[-1].get("content", "") or ""
                        history[-1]["content"] = last + appendix
                        # Emit one more update to refresh the Chat UI with the appended links
                        yield history, ""

                    return

                # ---------------------- NO-TOOL PATH ------------------------
                history.append({"role": "assistant", "content": ""})
                api_messages.append({"role": "assistant", "content": ""})
                for pair in _auto_continue_loop(
                    history,
                    api_messages,
                    float(temperature),
                    int(max_tokens),
                    bool(stream_final),
                    bool(auto_cont),
                    int(max_cont),
                    False,    # do not strip code when no tool ran
                    rid=rid,
                ):
                    yield pair
                return

            except Exception as e:
                trace("CHAT_ERROR", rid=rid, error=str(e))
                history = history or []
                history.append({"role": "assistant", "content": f"[UI error] {e}"})
                return history, ""

        send.click(
            chat_send,
            inputs=[chat, user_in, temp, max_toks, sys_prompt, stream_toggle, allow_tools, auto_continue, max_continues],
            outputs=[chat, user_in],
        )

    with gr.Tab("Completions"):
        prompt = gr.Textbox(label="Prompt", lines=8, value="Write a haiku about code.")
        stream_c = gr.Checkbox(label="Stream", value=True)
        with gr.Row():
            temp2 = gr.Slider(0.0, 2.0, value=0.7, step=0.1, label="temperature")
            max_toks2 = gr.Slider(0, 4096, value=256, step=16, label="max_tokens (0 = provider default)")
        out_text = gr.Textbox(label="Output", lines=12)
        run_comp = gr.Button("Complete", variant="primary")

        def complete_run(p, t, m, stream):
            rid = make_rid()
            try:
                url = _join_url(LMSTUDIO_BASE_URL, "/v1/completions")
                payload = {"model": MODEL_NAME, "prompt": p, "temperature": t,
                           "max_tokens": int(m) if int(m) > 0 else None, "stream": stream}
                payload = {k: v for k, v in payload.items() if v is not None}
                trace("COMP_BEGIN", rid=rid, stream=bool(stream))
                dump_blob("comp_req", rid, payload)
                if stream:
                    with requests.post(url, json=payload, stream=True, timeout=600) as r:
                        r.raise_for_status()
                        full = ""
                        for line in _iter_sse_lines(r, rid=rid):
                            try:
                                obj = json.loads(line)
                                delta = obj.get("choices", [{}])[0].get("text", "")
                                if delta:
                                    full += delta
                                    if UI_TRACE_VERBOSE:
                                        trace("COMP_CHUNK", rid=rid, add=len(delta), total=len(full))
                                    yield full
                            except Exception:
                                continue
                    dump_blob("comp_resp_stream", rid, {"text": full})
                    yield full
                else:
                    r = requests.post(url, json=payload, timeout=600)
                    r.raise_for_status()
                    data = r.json()
                    dump_blob("comp_resp", rid, data)
                    text = data["choices"][0]["text"]
                    trace("COMP_OK", rid=rid, chars=len(text))
                    yield text
            except Exception as e:
                trace("COMP_ERR", rid=rid, error=str(e))
                yield f"[Error] {e}"

        run_comp.click(complete_run, inputs=[prompt, temp2, max_toks2, stream_c], outputs=out_text)

    with gr.Tab("Embeddings"):
        multi = gr.Textbox(label="One text per line", lines=6, value="Hello world\nLM Studio\nEmbeddings")
        result = gr.JSON(label="Response JSON")
        go = gr.Button("Embed", variant="primary")

        def do_embed(s: str):
            rid = make_rid()
            try:
                url = _join_url(LMSTUDIO_BASE_URL, "/v1/embeddings")
                payload = {"model": MODEL_NAME, "input": [x for x in (s or "").splitlines() if x.strip()]}
                trace("EMB_BEGIN", rid=rid, n=len(payload["input"]))
                dump_blob("emb_req", rid, payload)
                r = requests.post(url, json=payload, timeout=180)
                r.raise_for_status()
                data = r.json()
                dump_blob("emb_resp", rid, data)
                dims = len(data.get("data", [])[0].get("embedding", [])) if data.get("data") else 0
                trace("EMB_OK", rid=rid, dims=dims)
                return data
            except Exception as e:
                trace("EMB_ERR", rid=rid, error=str(e))
                return {"error": str(e)}

        go.click(lambda s: do_embed(s), inputs=multi, outputs=result)

    with gr.Tab("Sandbox (/execute)"):
        code = gr.Code(language="python", label="Python", value="print('Aamir')")
        run = gr.Button("Run", variant="primary")
        with gr.Row():
            stdout = gr.Textbox(label="stdout", lines=8)
            stderr = gr.Textbox(label="stderr", lines=8)
        rc = gr.Number(label="return code", precision=0)
        imgs_json = gr.JSON(label="images (raw)")
        links_table = gr.Dataframe(headers=["filename", "url", "viewer"], label="Resolved Links", row_count=(0, "dynamic"))
        gallery = gr.Gallery(label="Embedded previews", columns=3, allow_preview=True, preview=True, height=320)
        persist_btn = gr.Button("Download & Persist")
        persist_msg = gr.Textbox(label="Persist result", lines=2)
        persisted_files = gr.Files(label="Saved files")

        run.click(lambda c: sandbox_execute(c), inputs=code, outputs=[stdout, stderr, rc, imgs_json, links_table, gallery])
        persist_btn.click(lambda imgs: persist_images(imgs), inputs=imgs_json, outputs=[persist_msg, persisted_files])

# -------------- Auth + launch --------------
auth_arg = None
if UI_USER and UI_PASS:
    auth_arg = [(UI_USER, UI_PASS)]

if __name__ == "__main__":
    trace("UI_STARTUP", lmstudio=LMSTUDIO_BASE_URL, sandbox=SANDBOX_BASE_URL, model=MODEL_NAME)
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
        auth=auth_arg,
    )


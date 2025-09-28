# ui_logging.py
import os, json, logging, uuid, time
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional

DEFAULT_MAX_BYTES = 5 * 1024 * 1024   # 5 MB
DEFAULT_BACKUPS = 10

def _ensure_dir(p: str) -> Path:
    path = Path(p).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }
        for key, val in getattr(record, "__dict__", {}).items():
            if key.startswith("_") or key in ("msg","args","levelname","levelno","pathname","filename","module","exc_info","exc_text","stack_info","lineno","funcName","created","msecs","relativeCreated","thread","threadName","processName","process"):
                continue
            payload[key] = val
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def configure_logging(
    enabled: bool = True,
    level: str = "INFO",
    log_dir: str = "./logs",
    name: str = "ui",
    fmt: str = "json",
    max_bytes: int = DEFAULT_MAX_BYTES,
    backups: int = DEFAULT_BACKUPS,
) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not enabled:
        logger.addHandler(logging.NullHandler())
        return logger
    d = _ensure_dir(log_dir)
    fp = d / f"{name}.log"
    handler = RotatingFileHandler(fp, maxBytes=max_bytes, backupCount=backups, encoding="utf-8")
    if fmt.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    logger.info("logging_initialized", extra={"log_path": str(fp), "level": level.upper(), "format": fmt})
    return logger

def make_rid() -> str:
    return f"{int(time.time())}-{uuid.uuid4().hex[:8]}"

def redacted_headers(h: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not h: return {}
    out = {}
    for k, v in h.items():
        if k.lower() in ("authorization","x-api-key","api-key","proxy-authorization"):
            out[k] = "***redacted***"
        else:
            out[k] = v
    return out

from __future__ import annotations

import uvicorn

# Reuse the exact same FastAPI app (files + /execute + /view) defined in rest_app.py
from rest_app import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


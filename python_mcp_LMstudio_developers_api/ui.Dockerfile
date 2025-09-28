# ui.Dockerfile (logging-enabled build)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && rm -rf /var/lib/apt/lists/*

COPY requirements.ui.txt /app/requirements.ui.txt
RUN pip install --no-cache-dir -r requirements.ui.txt

COPY ui_logging.py /app/ui_logging.py
COPY app_gradio_lmstudio_mcp_stream_auth_models_v9.py /app/app_gradio_lmstudio_mcp_stream_auth_models_v9.py
COPY sys_prompt.py /app/sys_prompt.py

VOLUME ["/app/artifacts", "/app/logs"]
EXPOSE 7860

ENV ARTIFACTS_DIR=/app/artifacts \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

CMD ["python", "-u", "app_gradio_lmstudio_mcp_stream_auth_models_v9.py"]

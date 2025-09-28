# syntax=docker/dockerfile:1
FROM continuumio/miniconda3:latest

# --- Runtime config (no hard-coded PUBLIC_BASE_URL) ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    EXEC_TIMEOUT_SECONDS=30 \
    MAX_IMAGE_BYTES=5242880 \
    MAX_IMAGE_COUNT=8 \
    SANDBOX_TEMP_DIR=/app/temp \
    PUBLIC_BASE_URL=""

# System packages: curl for healthcheck, Graphviz runtime & headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    graphviz \
    libgraphviz-dev \
    pkg-config \
 && rm -rf /var/lib/apt/lists/*

# --- Create a dedicated conda env (Python 3.11) ---
ARG ENV_NAME=app
RUN conda update -y -n base -c defaults conda && \
    conda create -y -n ${ENV_NAME} python=3.11 && \
    conda clean -afy
ENV PATH=/opt/conda/envs/${ENV_NAME}/bin:$PATH

# --- Data / ML / viz stack (conda-forge) ---
# - Use conda-forge to avoid compiling SciPy stack
# - graphviz binary comes from apt; python-graphviz provides Python bindings
RUN conda install -y -n ${ENV_NAME} -c conda-forge \
      numpy \
      scipy \
      pandas \
      scikit-learn \
      seaborn \
      matplotlib \
      python-graphviz \
      beautifulsoup4 \
      scrapy \
      networkx \
      pydot \
      xgboost \
 && conda clean -afy

# --- App/runtime libs (pip) ---
RUN /opt/conda/envs/${ENV_NAME}/bin/python -m pip install --no-cache-dir \
      fastmcp==0.4.1 \
      fastapi==0.115.0 \
      uvicorn[standard]==0.30.6 \
      pydantic==2.9.1

# --- App files ---
WORKDIR /app
COPY sandbox_core.py mcp_server.py rest_app.py server_rest.py ./

# Non-root user + writable temp dir
RUN useradd -m appuser && mkdir -p /app/temp && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck hits the REST sidecar
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s CMD curl -fsS http://127.0.0.1:8000/ || exit 1

# Start MCP server over stdio; REST sidecar is launched inside mcp_server.py on 0.0.0.0:8000
CMD ["python", "/app/mcp_server.py", "--stdio"]


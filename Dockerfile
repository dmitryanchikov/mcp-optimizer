# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

# Build-time dependencies - minimize layers and clean up in same RUN
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && pip install -U pip uv \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/*

WORKDIR /build
COPY pyproject.toml README.md ./
COPY ./src ./src

RUN python -m venv /build/venv
ENV PATH="/build/venv/bin:$PATH"

ARG ENV=production
ENV UV_CACHE_DIR=/build/.uv
RUN --mount=type=cache,target=/build/.uv \
    if [ "$ENV" = "production" ]; then \
      uv pip install --no-cache .; \
    else \
      uv pip install --no-cache ".[dev]"; \
    fi

# Conservative cleanup for smaller image
RUN find /build/venv -name "*.pyc" -delete \
    && find /build/venv -name "__pycache__" -type d -exec rm -rf {} + \
    && find /build/venv -name "*.pyo" -delete \
    && rm -rf /build/venv/lib/python*/site-packages/pip \
    && rm -rf /build/venv/lib/python*/site-packages/setuptools \
    && rm -rf /build/venv/lib/python*/site-packages/wheel

# Stage 2: Final image - use distroless-like approach
FROM python:3.12-slim

# Runtime dependencies and user creation in single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && groupadd -g 1000 mcp && useradd -u 1000 -g mcp -s /bin/bash -m mcp \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /usr/share/doc/* \
    && rm -rf /usr/share/man/* \
    && rm -rf /usr/share/locale/* \
    && rm -rf /usr/share/info/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy with correct ownership and set working directory
WORKDIR /code
COPY --from=builder --chown=mcp:mcp /build/venv /venv
COPY --chown=mcp:mcp ./src ./main.py ./

# Final cleanup and switch to non-root user
RUN find /venv -name "*.pyc" -delete \
    && find /venv -name "__pycache__" -type d -exec rm -rf {} + \
    && rm -rf /root/.cache \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

USER mcp

ENV PATH="/venv/bin:$PATH" \
    PYTHONPATH="/code" \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONOPTIMIZE=2 \
    MCP_OPTIMIZER_LOG_LEVEL=INFO \
    MCP_OPTIMIZER_MAX_SOLVE_TIME=300 \
    MCP_OPTIMIZER_MAX_MEMORY_MB=1024 \
    MCP_OPTIMIZER_MAX_CONCURRENT_REQUESTS=10

HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD python -c "from mcp_optimizer.mcp_server import create_mcp_server; create_mcp_server()" || exit 1

EXPOSE 8000

CMD ["python", "main.py"] 
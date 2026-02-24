FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv --quiet

# Install CPU-only torch first to avoid downloading CUDA packages
RUN uv pip install --system torch --extra-index-url https://download.pytorch.org/whl/cpu

# Install plyra-memory from local wheel (not on PyPI)
COPY plyra_memory_local/ ./plyra_memory_local/
RUN uv pip install --system ./plyra_memory_local/*.whl

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY memory_server/ ./memory_server/

# Install dependencies (plyra-memory already satisfied above)
RUN uv pip install --system ".[postgres]"

# Create data directory
RUN mkdir -p /data

# Default env
ENV PLYRA_STORE_URL=/data/memory.db
ENV PLYRA_VECTORS_URL=/data/memory.index
ENV PLYRA_KEY_STORE_URL=/data/keys.db
ENV PLYRA_HOST=0.0.0.0
ENV PLYRA_PORT=7700

EXPOSE 7700

CMD ["plyra-server"]

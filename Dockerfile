FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-install-project

COPY . .

RUN uv pip install --system --no-cache-dir -e .

ENTRYPOINT ["python", "-m", "src.interface.cli"]
CMD ["--problem", "P0"]

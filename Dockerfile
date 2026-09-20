# Use official lightweight Python image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy packaging metadata first for build caching
COPY pyproject.toml README.md ./
COPY ai_evaluation/ ./ai_evaluation/

RUN pip install --upgrade pip && \
    pip install ".[all]"

# Copy remaining source code
COPY . .

# Set permissions for output directories
RUN mkdir -p ai_evaluation/results && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

CMD ["run-evaluation", "--models", "simulated:default"]

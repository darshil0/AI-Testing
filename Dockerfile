# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
# 1. Prevent Python from writing .pyc files
# 2. Ensure logs are sent straight to terminal without buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# Install system dependencies if needed (e.g., git or build-essentials)
# Added 'curl' for potential health checks in dashboard mode
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only packaging files first to leverage Docker layer caching
COPY pyproject.toml .
# If you still use requirements.txt, uncomment the next line:
# COPY requirements.txt . 

# Install the package and its dependencies
# We install '.' to trigger the pyproject.toml installation
RUN pip install --upgrade pip && \
    pip install .

# Copy the rest of the project source
COPY . .

# Create persistent directories for results and ensure log file exists
RUN mkdir -p ai_evaluation/results && \
    touch evaluation.log && \
    chmod -R 777 ai_evaluation/results evaluation.log

# Expose Streamlit port for the dashboard
EXPOSE 8501

# Use the new console script as the entry point
# This allows users to override arguments easily
ENTRYPOINT ["run-evaluation"]

# Default arguments (can be overridden by user)
CMD ["--models", "simulated:default"]

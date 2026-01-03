# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for results and logs
RUN mkdir -p ai_evaluation/results && touch evaluation.log

# Command to run (defaults to simulated)
CMD ["python", "ai_evaluation/run_evaluation.py", "--models", "simulated"]

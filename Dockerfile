FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment inside Docker
RUN python -m venv /app/docker/venv

# Activate virtual environment
ENV PATH="/app/docker/venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/docker/venv"

# Upgrade pip in virtual environment
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies in virtual environment
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed data/embeddings logs

# Set Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Expose port for API (if needed)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "src.main"]

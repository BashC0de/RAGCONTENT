# Use Python 3.11 slim image
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Fix apt sources and install dependencies
RUN apt-get update --allow-releaseinfo-change && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        gcc \
        g++ \
        git \
        libomp-dev \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        python3-dev \
        ca-certificates \
        gnupg \
    && rm -rf /var/lib/apt/lists/*


# Install system dependencies
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        build-essential gcc g++ git curl libomp-dev libpq-dev libssl-dev libffi-dev python3-dev ca-certificates gnupg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*




# Copy requirements first
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

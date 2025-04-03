FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev libssl-dev libpq-dev curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy everything from api_icatu/app/ directly into /app
COPY ./api_icatu/app/ /app/

# Copy requirements file
COPY ./api_icatu/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Ensure /app is in PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Start FastAPI from main.py inside /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

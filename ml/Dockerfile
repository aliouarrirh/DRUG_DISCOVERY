FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY api/ ./api/
COPY data/processed/ ./data/processed/

ENV DATA_DIR=data/processed

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

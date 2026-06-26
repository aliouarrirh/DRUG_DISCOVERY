FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY ml/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ml/src/ ./src/
COPY ml/api/ ./api/
COPY ml/data/processed/descriptor_imputer.pkl ./data/processed/descriptor_imputer.pkl
COPY ml/data/processed/descriptor_scaler.pkl ./data/processed/descriptor_scaler.pkl
COPY ml/data/processed/variance_threshold.pkl ./data/processed/variance_threshold.pkl
COPY ml/models/best_model.pkl ./models/best_model.pkl

ENV DATA_DIR=data/processed
ENV MODEL_DIR=models

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

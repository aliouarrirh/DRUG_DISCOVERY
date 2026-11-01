# ToxiScan — Molecular Toxicity Classifier

Binary toxicity classification (TOXIC / NON-TOXIC) from molecular SMILES strings, combining Tox21 and ClinTox datasets with an XGBoost model, a FastAPI backend, and a React interface.

---

## Results

| Metric | Value |
|--------|-------|
| ROC-AUC (test) | **0.8191** |
| PR-AUC (test) | **0.7113** |
| F1-score | 0.6566 |
| Recall | 0.7036 |
| Precision | 0.6155 |
| CV ROC-AUC (3-fold, train) | 0.7918 |

---

## Dataset

- **Sources:** Tox21 (7 823 molecules) + ClinTox (1 461 molecules)
- **After deduplication:** 8 799 unique molecules
- **Label construction:**
  - ClinTox → `CT_TOX` binary label directly
  - Tox21 → logical OR over 12 assay endpoints (NaN treated as inactive)
  - Conflict rule → toxic-priority (label 1 wins)
- **Split:** stratified 80/20 → 7 039 train / 1 760 test
- **Class balance:** 33.4% toxic / 66.6% non-toxic

---

## Features

- **2 048-bit Morgan fingerprints** (ECFP4, radius=2) via RDKit
- **31 RDKit molecular descriptors** (MW, LogP, TPSA, HBD, HBA, …)
- **Total:** 2 079-dimensional feature vector

---

## Model

XGBoost champion, selected by 3-fold stratified CV on train set only:

```
learning_rate = 0.05
max_depth     = 6
n_estimators  = 200
reg_alpha     = 0.1
subsample     = 0.8
```

SMOTE applied on train set only. Tanimoto similarity analysis: 88.5% of test molecules have no training neighbor with similarity > 0.85.

---

## Project Structure

```
drug_discovery/
├── ml/
│   ├── api/               # FastAPI app
│   │   └── main.py
│   ├── data/
│   │   ├── raw/           # clintox.csv, tox21.csv
│   │   ├── interim/       # combined_labeled.csv
│   │   └── processed/     # X_train/test.npy, y_train/test.npy
│   ├── models/
│   │   ├── best_model.pkl
│   │   └── best_model_meta.json
│   ├── notebooks/
│   │   ├── 01_eda.ipynb
│   │   ├── 02_preprocessing.ipynb
│   │   ├── 03_feature_engineering.ipynb
│   │   ├── 04_modelling.ipynb
│   │   └── 05_shap.ipynb
│   ├── reports/figures/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # React ToxiScan UI
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── render.yaml
```

---

## Run Locally

**Requirements:** Docker + Docker Compose

```bash
git clone <repo-url>
cd drug_discovery
docker compose up --build
```

- API: [http://localhost:8000](http://localhost:8000)
- UI: [http://localhost:3000](http://localhost:3000)
- Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API

```bash
# Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles": "CCO"}'

# Batch prediction
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"smiles_list": ["CCO", "CC(=O)Oc1ccccc1C(=O)O"]}'
```

Response:
```json
{"smiles": "CCO", "prediction": "NON-TOXIC"}
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| ML | XGBoost, scikit-learn, RDKit, imbalanced-learn |
| Experiment tracking | MLflow |
| Data versioning | DVC |
| API | FastAPI + Uvicorn |
| Frontend | React + TypeScript + Vite + TailwindCSS + Framer Motion |
| Deployment | Docker, Render (API), Vercel (frontend) |

---

## Notebooks

| Notebook | Content |
|----------|---------|
| `01_eda.ipynb` | Exploratory data analysis |
| `02_preprocessing.ipynb` | Cleaning, deduplication, label construction |
| `03_feature_engineering.ipynb` | Morgan FP + descriptors, SMOTE, train/test split |
| `04_modelling.ipynb` | Baseline + GridSearchCV + MLflow tracking |
| `05_shap.ipynb` | SHAP interpretability + substructure visualization |

---

## Interpretability

SHAP TreeExplainer (exact, not approximate) on the XGBoost model. Morgan bit mapping via RDKit `bitInfo` links influential fingerprint bits to molecular substructures. Failure mode analysis covers TP / FP / FN cases with concrete SMILES examples.

import os
import joblib
import numpy as np
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.pyfunc
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rdkit import Chem
from rdkit.Chem import Descriptors, rdFingerprintGenerator

MORGAN_BITS = 2048
MORGAN_RADIUS = 2
MODEL_URI = "models:/drug-toxicity-xgboost@champion"
DATA_DIR = Path(os.getenv("DATA_DIR", "data/processed"))

DESCRIPTOR_FNS = [
    ("MolWt", Descriptors.MolWt),
    ("LogP", Descriptors.MolLogP),
    ("TPSA", Descriptors.TPSA),
    ("HBD", Descriptors.NumHDonors),
    ("HBA", Descriptors.NumHAcceptors),
    ("RotBonds", Descriptors.NumRotatableBonds),
    ("NumAromaticRings", Descriptors.NumAromaticRings),
    ("NumAliphaticRings", Descriptors.NumAliphaticRings),
    ("NumSaturatedRings", Descriptors.NumSaturatedRings),
    ("NumHeteroatoms", Descriptors.NumHeteroatoms),
    ("NumHeavyAtoms", Descriptors.HeavyAtomCount),
    ("NumValenceElectrons", Descriptors.NumValenceElectrons),
    ("FractionCSP3", Descriptors.FractionCSP3),
    ("MolMR", Descriptors.MolMR),
    ("BalabanJ", Descriptors.BalabanJ),
    ("BertzCT", Descriptors.BertzCT),
    ("Chi0", Descriptors.Chi0),
    ("Chi1", Descriptors.Chi1),
    ("Kappa1", Descriptors.Kappa1),
    ("Kappa2", Descriptors.Kappa2),
    ("Kappa3", Descriptors.Kappa3),
    ("LabuteASA", Descriptors.LabuteASA),
    ("PEOE_VSA1", Descriptors.PEOE_VSA1),
    ("PEOE_VSA2", Descriptors.PEOE_VSA2),
    ("SMR_VSA1", Descriptors.SMR_VSA1),
    ("SMR_VSA2", Descriptors.SMR_VSA2),
    ("SlogP_VSA1", Descriptors.SlogP_VSA1),
    ("EState_VSA1", Descriptors.EState_VSA1),
    ("MaxAbsEStateIndex", Descriptors.MaxAbsEStateIndex),
    ("MinAbsEStateIndex", Descriptors.MinAbsEStateIndex),
]

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)

    client = mlflow.tracking.MlflowClient()
    version_info = client.get_model_version_by_alias("drug-toxicity-xgboost", "champion")
    state["model_version"] = version_info.version

    pyfunc_model = mlflow.pyfunc.load_model(MODEL_URI)
    inner = pyfunc_model._model_impl
    if hasattr(inner, "xgb_model"):
        state["model"] = inner.xgb_model
    elif hasattr(inner, "sklearn_model"):
        state["model"] = inner.sklearn_model
    else:
        state["model"] = pyfunc_model
    state["imputer"] = joblib.load(DATA_DIR / "descriptor_imputer.pkl")
    state["var_thresh"] = joblib.load(DATA_DIR / "variance_threshold.pkl")
    state["scaler"] = joblib.load(DATA_DIR / "descriptor_scaler.pkl")

    yield
    state.clear()


app = FastAPI(title="Drug Toxicity API", version="1.0.0", lifespan=lifespan)


class PredictRequest(BaseModel):
    smiles: str


class PredictResponse(BaseModel):
    smiles: str
    prediction: str


class BatchRequest(BaseModel):
    smiles_list: List[str]


def featurize(smiles: str) -> np.ndarray:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    gen = rdFingerprintGenerator.GetMorganGenerator(radius=MORGAN_RADIUS, fpSize=MORGAN_BITS)
    morgan = np.array(list(gen.GetFingerprint(mol)), dtype=np.float32).reshape(1, -1)
    morgan = state["var_thresh"].transform(morgan).astype(np.float32)

    desc = np.array([[fn(mol) for _, fn in DESCRIPTOR_FNS]], dtype=np.float64)
    desc = state["imputer"].transform(desc)
    desc = state["scaler"].transform(desc).astype(np.float32)

    return np.hstack([morgan, desc]).reshape(1, -1)


def predict_one(smiles: str) -> PredictResponse:
    X = featurize(smiles)
    label_int = int(state["model"].predict(X)[0])
    label = "TOXIC" if label_int == 1 else "NON-TOXIC"
    return PredictResponse(smiles=smiles, prediction=label)


@app.get("/health")
def health():
    return {"status": "ok", "model_version": state.get("model_version", "unknown")}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        return predict_one(req.smiles)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/predict/batch", response_model=List[PredictResponse])
def predict_batch(req: BatchRequest):
    results = []
    for smi in req.smiles_list:
        try:
            results.append(predict_one(smi))
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
    return results

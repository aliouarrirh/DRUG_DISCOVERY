# -*- coding: utf-8 -*-
import click
import logging
import numpy as np
import joblib
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from rdkit import Chem
from rdkit.Chem import Descriptors, rdFingerprintGenerator
from sklearn.impute import SimpleImputer

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

MORGAN_BITS = 2048
MORGAN_RADIUS = 2


def featurize(smiles, imputer, var_thresh, scaler):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    gen = rdFingerprintGenerator.GetMorganGenerator(radius=MORGAN_RADIUS, fpSize=MORGAN_BITS)
    morgan = np.array(list(gen.GetFingerprint(mol)), dtype=np.float32)

    desc = np.array([[fn(mol) for _, fn in DESCRIPTOR_FNS]], dtype=np.float64)
    desc = imputer.transform(desc)
    desc = var_thresh.transform(desc)
    desc = scaler.transform(desc).astype(np.float32)

    return np.hstack([morgan, desc[0]]).reshape(1, -1)


@click.command()
@click.option("--smiles", required=True, help="SMILES string of the molecule to predict")
@click.option("--model-dir", default="models", show_default=True, help="Directory with best_model.pkl")
@click.option("--data-dir", default="data/processed", show_default=True, help="Directory with fitted transformers")
def main(smiles, model_dir, data_dir):
    """Predict toxicity probability for a given SMILES string."""
    logger = logging.getLogger(__name__)
    model_dir = Path(model_dir)
    data_dir = Path(data_dir)

    model = joblib.load(model_dir / "best_model.pkl")
    imputer = joblib.load(data_dir / "descriptor_imputer.pkl")
    var_thresh = joblib.load(data_dir / "variance_threshold.pkl")
    scaler = joblib.load(data_dir / "descriptor_scaler.pkl")

    X = featurize(smiles, imputer, var_thresh, scaler)
    prob = model.predict_proba(X)[0, 1]
    label = "TOXIC" if prob >= 0.5 else "NON-TOXIC"

    logger.info(f"SMILES: {smiles}")
    logger.info(f"Prediction: {label} (probability: {prob:.4f})")
    click.echo(f"\nSMILES:      {smiles}")
    click.echo(f"Prediction:  {label}")
    click.echo(f"Probability: {prob:.4f}")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    project_dir = Path(__file__).resolve().parents[2]
    load_dotenv(find_dotenv())
    main()

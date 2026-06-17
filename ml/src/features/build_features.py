# -*- coding: utf-8 -*-
import click
import logging
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from rdkit import Chem
from rdkit.Chem import Descriptors, rdFingerprintGenerator
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import StandardScaler

DESCRIPTOR_LIST = [
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


def compute_morgan(smiles_list):
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=MORGAN_RADIUS, fpSize=MORGAN_BITS)
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        fps.append(list(gen.GetFingerprint(mol)) if mol else [0] * MORGAN_BITS)
    return np.array(fps, dtype=np.float32)


def compute_descriptors(smiles_list):
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol:
            rows.append([fn(mol) for _, fn in DESCRIPTOR_LIST])
        else:
            rows.append([np.nan] * len(DESCRIPTOR_LIST))
    return np.array(rows, dtype=np.float64)


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath, output_filepath):
    """Compute Morgan FP + RDKit descriptors and split into train/test sets."""
    logger = logging.getLogger(__name__)
    in_dir = Path(input_filepath)
    out_dir = Path(output_filepath)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_dir / "combined_labeled.csv")
    logger.info(f"Loaded {len(df)} molecules")

    X_smiles = df["canonical_smiles"].tolist()
    y = df["is_toxic"].values

    X_train_smi, X_test_smi, y_train, y_test = train_test_split(
        X_smiles, y, test_size=0.2, stratify=y, random_state=42
    )
    logger.info(f"Train: {len(X_train_smi)}, Test: {len(X_test_smi)}")

    logger.info("Computing Morgan fingerprints...")
    morgan_train = compute_morgan(X_train_smi)
    morgan_test = compute_morgan(X_test_smi)
    morgan_names = [f"morgan_{i}" for i in range(MORGAN_BITS)]

    logger.info("Computing RDKit descriptors...")
    desc_train = compute_descriptors(X_train_smi)
    desc_test = compute_descriptors(X_test_smi)
    desc_names = [name for name, _ in DESCRIPTOR_LIST]

    imputer = SimpleImputer(strategy="median")
    desc_train = imputer.fit_transform(desc_train)
    desc_test = imputer.transform(desc_test)

    var_thresh = VarianceThreshold(threshold=0.0)
    desc_train = var_thresh.fit_transform(desc_train)
    desc_test = var_thresh.transform(desc_test)
    selected_desc_names = [desc_names[i] for i in var_thresh.get_support(indices=True)]

    scaler = StandardScaler()
    desc_train = scaler.fit_transform(desc_train)
    desc_test = scaler.transform(desc_test)

    X_train = np.hstack([morgan_train, desc_train]).astype(np.float32)
    X_test = np.hstack([morgan_test, desc_test]).astype(np.float32)
    feature_names = morgan_names + selected_desc_names

    np.save(out_dir / "X_train.npy", X_train)
    np.save(out_dir / "y_train.npy", y_train)
    np.save(out_dir / "X_test.npy", X_test)
    np.save(out_dir / "y_test.npy", y_test)
    pd.DataFrame({"feature": feature_names}).to_csv(out_dir / "feature_names.csv", index=False)

    joblib.dump(imputer, out_dir / "descriptor_imputer.pkl")
    joblib.dump(var_thresh, out_dir / "variance_threshold.pkl")
    joblib.dump(scaler, out_dir / "descriptor_scaler.pkl")

    # Save test SMILES for SHAP alignment
    pd.DataFrame({"smiles": X_test_smi}).to_csv(out_dir / "X_test_smiles.csv", index=False)

    logger.info(f"Features: {X_train.shape[1]} ({MORGAN_BITS} Morgan + {len(selected_desc_names)} descriptors)")
    logger.info(f"Saved processed data to {out_dir}")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    project_dir = Path(__file__).resolve().parents[2]
    load_dotenv(find_dotenv())
    main()

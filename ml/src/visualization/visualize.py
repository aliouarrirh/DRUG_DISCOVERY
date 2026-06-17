# -*- coding: utf-8 -*-
import click
import logging
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Draw import SimilarityMaps

MORGAN_BITS = 2048
MORGAN_RADIUS = 2


def shap_summary(explainer, shap_values, feature_names, out_dir):
    plt.figure()
    shap.summary_plot(shap_values, feature_names=feature_names, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig(out_dir / "shap_summary.png", dpi=150)
    plt.close()


def shap_waterfall(explainer, shap_values, X_sample, feature_names, out_dir):
    exp = shap.Explanation(
        values=shap_values[0],
        base_values=explainer.expected_value,
        data=X_sample[0],
        feature_names=feature_names,
    )
    plt.figure()
    shap.plots.waterfall(exp, show=False)
    plt.tight_layout()
    plt.savefig(out_dir / "shap_waterfall.png", dpi=150)
    plt.close()


def shap_force(explainer, shap_values, X_sample, feature_names, out_dir):
    shap.force_plot(
        explainer.expected_value,
        shap_values[0],
        X_sample[0],
        feature_names=feature_names,
        matplotlib=True,
        show=False,
    )
    plt.tight_layout()
    plt.savefig(out_dir / "shap_force.png", dpi=150)
    plt.close()


def shap_molecule(smiles, shap_vals, out_dir):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return

    gen = rdFingerprintGenerator.GetMorganGenerator(radius=MORGAN_RADIUS, fpSize=MORGAN_BITS)
    bit_info = {}
    gen.GetFingerprint(mol, additionalOutput=rdFingerprintGenerator.AdditionalOutput(bitInfoMap=bit_info))

    atom_weights = np.zeros(mol.GetNumAtoms())
    for bit_idx, contrib in enumerate(shap_vals[:MORGAN_BITS]):
        if bit_idx in bit_info:
            for atom_id, _ in bit_info[bit_idx]:
                atom_weights[atom_id] += contrib

    fig, ax = plt.subplots(figsize=(5, 5))
    SimilarityMaps.GetSimilarityMapFromWeights(mol, atom_weights.tolist(), colorMap="RdYlGn_r", ax=ax)
    plt.savefig(out_dir / "shap_molecule.png", dpi=150, bbox_inches="tight")
    plt.close()


@click.command()
@click.argument("data_filepath", type=click.Path(exists=True))
@click.argument("model_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
@click.option("--n-samples", default=100, show_default=True, help="Number of test samples for SHAP")
def main(data_filepath, model_filepath, output_filepath, n_samples):
    """Generate SHAP explanation plots for the best model."""
    logger = logging.getLogger(__name__)
    data_dir = Path(data_filepath)
    model_dir = Path(model_filepath)
    out_dir = Path(output_filepath)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = joblib.load(model_dir / "best_model.pkl")
    X_test = np.load(data_dir / "X_test.npy")
    feature_names = pd.read_csv(data_dir / "feature_names.csv")["feature"].tolist()
    test_smiles_path = data_dir / "X_test_smiles.csv"

    X_sample = X_test[:n_samples]
    logger.info(f"Computing SHAP values for {n_samples} samples...")

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    logger.info("Generating summary plot...")
    shap_summary(explainer, shap_values, feature_names, out_dir)

    logger.info("Generating waterfall plot...")
    shap_waterfall(explainer, shap_values, X_sample, feature_names, out_dir)

    logger.info("Generating force plot...")
    shap_force(explainer, shap_values, X_sample, feature_names, out_dir)

    if test_smiles_path.exists():
        smiles_list = pd.read_csv(test_smiles_path)["smiles"].tolist()
        logger.info("Generating molecule SHAP map...")
        shap_molecule(smiles_list[0], shap_values[0], out_dir)

    logger.info(f"All figures saved to {out_dir}")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    project_dir = Path(__file__).resolve().parents[2]
    load_dotenv(find_dotenv())
    main()

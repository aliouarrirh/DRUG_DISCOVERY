# -*- coding: utf-8 -*-
import click
import logging
import pandas as pd
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from rdkit import Chem


def validate_and_canonicalize(smiles_series):
    canonical = []
    for smi in smiles_series:
        try:
            mol = Chem.MolFromSmiles(str(smi))
            canonical.append(Chem.MolToSmiles(mol) if mol else None)
        except Exception:
            canonical.append(None)
    return canonical


def process_clintox(raw_dir):
    df = pd.read_csv(raw_dir / "clintox.csv")
    df["canonical_smiles"] = validate_and_canonicalize(df["smiles"])
    df = df.dropna(subset=["canonical_smiles"])
    df = df.drop_duplicates(subset=["canonical_smiles"])
    df["is_toxic"] = df["CT_TOX"].astype(int)
    df["source"] = "clintox"
    return df[["canonical_smiles", "is_toxic", "source"]]


TOX21_TARGETS = [
    "NR-AR", "NR-AR-LBD", "NR-AhR", "NR-Aromatase", "NR-ER", "NR-ER-LBD",
    "NR-PPAR-gamma", "SR-ARE", "SR-ATAD5", "SR-HSE", "SR-MMP", "SR-p53",
]


def process_tox21(raw_dir):
    df = pd.read_csv(raw_dir / "tox21.csv")
    df["canonical_smiles"] = validate_and_canonicalize(df["smiles"])
    df = df.dropna(subset=["canonical_smiles"])
    df = df.drop_duplicates(subset=["canonical_smiles"])
    existing_targets = [t for t in TOX21_TARGETS if t in df.columns]
    df[existing_targets] = df[existing_targets].fillna(0)
    df["is_toxic"] = (df[existing_targets].sum(axis=1) > 0).astype(int)
    df["source"] = "tox21"
    return df[["canonical_smiles", "is_toxic", "source"]]


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath, output_filepath):
    """Combine ClinTox + Tox21 into a single labeled dataset saved to output_filepath."""
    logger = logging.getLogger(__name__)
    raw_dir = Path(input_filepath)
    out_dir = Path(output_filepath)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Processing ClinTox...")
    clintox = process_clintox(raw_dir)
    logger.info(f"ClinTox: {len(clintox)} molecules")

    logger.info("Processing Tox21...")
    tox21 = process_tox21(raw_dir)
    logger.info(f"Tox21: {len(tox21)} molecules")

    combined = pd.concat([clintox, tox21], ignore_index=True)
    # Keep is_toxic=1 when duplicate SMILES across sources
    combined = combined.sort_values("is_toxic", ascending=False)
    combined = combined.drop_duplicates(subset=["canonical_smiles"], keep="first")
    combined = combined.reset_index(drop=True)

    out_path = out_dir / "combined_labeled.csv"
    combined.to_csv(out_path, index=False)
    logger.info(f"Saved {len(combined)} molecules to {out_path}")
    logger.info(f"Class distribution:\n{combined['is_toxic'].value_counts()}")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    project_dir = Path(__file__).resolve().parents[2]
    load_dotenv(find_dotenv())
    main()

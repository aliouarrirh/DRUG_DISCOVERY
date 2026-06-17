# src/data/download_data.py
import pandas as pd

# Tox21 (MoleculeNet)
url_tox21 = "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz"
df = pd.read_csv(url_tox21)
df.to_csv("data/raw/tox21.csv", index=False)

# ClinTox
url_clintox = "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/clintox.csv.gz"
df2 = pd.read_csv(url_clintox)
df2.to_csv("data/raw/clintox.csv", index=False)
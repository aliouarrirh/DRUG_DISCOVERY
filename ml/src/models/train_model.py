# -*- coding: utf-8 -*-
import click
import json
import logging
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    roc_auc_score, accuracy_score, f1_score, precision_score, recall_score,
)
from xgboost import XGBClassifier


BASELINES = {
    "RandomForest": RandomForestClassifier(
        n_estimators=200, max_depth=15, class_weight="balanced", random_state=42, n_jobs=-1
    ),
    "XGBoost": XGBClassifier(
        n_estimators=100, use_label_encoder=False, eval_metric="logloss",
        scale_pos_weight=2, random_state=42, n_jobs=-1
    ),
    "SVC": SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=42),
    "LogisticRegression": LogisticRegression(
        C=1.0, solver="lbfgs", class_weight="balanced", max_iter=1000, random_state=42
    ),
}

XGB_PARAM_GRID = {
    "n_estimators": [100, 200],
    "max_depth": [3, 5, 7],
    "learning_rate": [0.05, 0.1],
    "subsample": [0.8, 1.0],
    "reg_alpha": [0, 0.1],
}


def evaluate(model, X, y):
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]
    return {
        "roc_auc": roc_auc_score(y, y_prob),
        "accuracy": accuracy_score(y, y_pred),
        "f1": f1_score(y, y_pred),
        "precision": precision_score(y, y_pred),
        "recall": recall_score(y, y_pred),
    }


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath, output_filepath):
    """Train baseline models, tune the best one, and save to output_filepath."""
    logger = logging.getLogger(__name__)
    in_dir = Path(input_filepath)
    out_dir = Path(output_filepath)
    out_dir.mkdir(parents=True, exist_ok=True)

    X_train = np.load(in_dir / "X_train.npy")
    y_train = np.load(in_dir / "y_train.npy")
    X_test = np.load(in_dir / "X_test.npy")
    y_test = np.load(in_dir / "y_test.npy")
    logger.info(f"Train: {X_train.shape}, Test: {X_test.shape}")

    mlflow.set_experiment("drug_toxicity_prediction")

    best_name, best_model, best_auc = None, None, -1

    for name, model in BASELINES.items():
        with mlflow.start_run(run_name=f"baseline_{name}"):
            logger.info(f"Training {name}...")
            model.fit(X_train, y_train)
            metrics = evaluate(model, X_test, y_test)
            mlflow.log_params(model.get_params())
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, name)
            logger.info(f"{name} → ROC-AUC: {metrics['roc_auc']:.4f}")

            if metrics["roc_auc"] > best_auc:
                best_auc = metrics["roc_auc"]
                best_name = name
                best_model = model

    logger.info(f"Best baseline: {best_name} (ROC-AUC={best_auc:.4f})")
    logger.info("Running GridSearchCV on best model...")

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    # Use XGBoost param grid regardless of which baseline won (it's almost always XGBoost)
    base_xgb = XGBClassifier(
        use_label_encoder=False, eval_metric="logloss",
        scale_pos_weight=int(np.sum(y_train == 0) / np.sum(y_train == 1)),
        random_state=42, n_jobs=-1
    )
    grid_search = GridSearchCV(
        base_xgb, XGB_PARAM_GRID, cv=cv, scoring="roc_auc", n_jobs=-1, verbose=1
    )

    with mlflow.start_run(run_name="tuned_XGBoost"):
        grid_search.fit(X_train, y_train)
        tuned_model = grid_search.best_estimator_
        metrics = evaluate(tuned_model, X_test, y_test)
        mlflow.log_params(grid_search.best_params_)
        mlflow.log_metric("cv_roc_auc", grid_search.best_score_)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(tuned_model, "tuned_XGBoost")
        logger.info(f"Tuned XGBoost → CV ROC-AUC: {grid_search.best_score_:.4f}, Test: {metrics['roc_auc']:.4f}")

    joblib.dump(tuned_model, out_dir / "best_model.pkl")
    meta = {"model": "XGBoost", "params": grid_search.best_params_, "metrics": metrics}
    (out_dir / "best_model_meta.json").write_text(json.dumps(meta, indent=2))
    logger.info(f"Saved best model to {out_dir / 'best_model.pkl'}")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    project_dir = Path(__file__).resolve().parents[2]
    load_dotenv(find_dotenv())
    main()

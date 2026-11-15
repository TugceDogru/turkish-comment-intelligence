from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[2]
SPLIT_DIR = ROOT / "data" / "splits"
MODEL_DIR = ROOT / "models" / "baseline"
REPORT_DIR = ROOT / "reports" / "baseline"

TASKS = {
    "sentiment": ["POSITIVE", "NEUTRAL", "NEGATIVE", "MIXED"],
    "actionability": [
        "NOT_ACTIONABLE",
        "IMPLICITLY_ACTIONABLE",
        "EXPLICITLY_ACTIONABLE",
    ],
    "toxicity": ["NON_TOXIC", "TOXIC"],
    "question_type": [
        "NOT_QUESTION",
        "INFORMATION_SEEKING",
        "ACTION_REQUEST",
        "RHETORICAL",
    ],
}

WEIGHT_OPTIONS = {
    "unweighted": None,
    "balanced": "balanced",
}


def load_split(name: str) -> pd.DataFrame:
    path = SPLIT_DIR / f"{name}.csv"

    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype={
            "comment_id": "string",
            "video_id": "string",
        },
        keep_default_na=False,
    )

    required = {"comment_id", "video_id", "text", *TASKS}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"{name}: missing columns {sorted(missing)}")

    if df.empty:
        raise ValueError(f"{name} is empty")

    if df["text"].astype(str).str.strip().eq("").any():
        raise ValueError(f"{name}: empty text detected")

    for task, labels in TASKS.items():
        invalid = set(df[task]) - set(labels)
        if invalid:
            raise ValueError(f"{name}: invalid {task} labels: {invalid}")

    return df


def validate_train_val(
    train: pd.DataFrame,
    val: pd.DataFrame,
) -> None:
    if set(train["comment_id"]) & set(val["comment_id"]):
        raise ValueError("Train/validation comment overlap")

    if set(train["video_id"]) & set(val["video_id"]):
        raise ValueError("Train/validation video overlap")

    for task, labels in TASKS.items():
        if set(train[task]) != set(labels):
            raise ValueError(f"Training set lacks classes for {task}")


def make_pipeline(class_weight) -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.98,
                    sublinear_tf=True,
                    max_features=100_000,
                    token_pattern=r"(?u)\b\w+\b",
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    class_weight=class_weight,
                    max_iter=2000,
                    solver="lbfgs",
                    random_state=42,
                ),
            ),
        ]
    )


def evaluate(
    model: Pipeline,
    texts: pd.Series,
    labels: pd.Series,
    classes: list[str],
) -> dict:
    predictions = model.predict(texts)

    precision, recall, f1, support = precision_recall_fscore_support(
        labels,
        predictions,
        labels=classes,
        zero_division=0,
    )

    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "macro_f1": float(
            f1_score(
                labels,
                predictions,
                labels=classes,
                average="macro",
                zero_division=0,
            )
        ),
        "weighted_f1": float(
            f1_score(
                labels,
                predictions,
                labels=classes,
                average="weighted",
                zero_division=0,
            )
        ),
        "per_class": {
            label: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, label in enumerate(classes)
        },
        "confusion_matrix": confusion_matrix(
            labels,
            predictions,
            labels=classes,
        ).tolist(),
    }


def train_task(
    task: str,
    classes: list[str],
    train: pd.DataFrame,
    val: pd.DataFrame,
) -> dict:
    print(f"\n{'=' * 60}")
    print(f"TASK: {task.upper()}")
    print("=" * 60)

    x_train = train["text"].astype(str)
    y_train = train[task]

    x_val = val["text"].astype(str)
    y_val = val[task]

    candidates = []
    best_model = None
    best_name = None
    best_metrics = None
    best_score = -1.0

    for name, weight in WEIGHT_OPTIONS.items():
        print(f"\nTraining: {name}")

        model = make_pipeline(weight)
        model.fit(x_train, y_train)

        metrics = evaluate(model, x_val, y_val, classes)

        score = metrics["macro_f1"]

        print(f"  Accuracy: {metrics['accuracy']:.4f}")
        print(f"  Macro F1: {score:.4f}")
        print(f"  Weighted F1: {metrics['weighted_f1']:.4f}")

        candidates.append(
            {
                "name": name,
                "class_weight": weight,
                "metrics": metrics,
            }
        )

        if score > best_score:
            best_score = score
            best_model = model
            best_name = name
            best_metrics = metrics

    assert best_model is not None
    assert best_metrics is not None

    model_path = MODEL_DIR / f"{task}.joblib"

    joblib.dump(best_model, model_path)

    report = {
        "task": task,
        "selected_model": best_name,
        "selection_metric": "validation_macro_f1",
        "selected_score": best_score,
        "candidates": candidates,
        "selected_validation_metrics": best_metrics,
        "model_path": model_path.relative_to(ROOT).as_posix(),
    }

    report_path = REPORT_DIR / f"{task}_metrics.json"

    report_path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\nSelected: {best_name}")
    print(f"Best validation Macro F1: {best_score:.4f}")

    print("\nPer-class results:")

    print(
        classification_report(
            y_val,
            best_model.predict(x_val),
            labels=classes,
            zero_division=0,
        )
    )

    return {
        "task": task,
        "selected_model": best_name,
        "validation_accuracy": best_metrics["accuracy"],
        "validation_macro_f1": best_metrics["macro_f1"],
        "validation_weighted_f1": best_metrics["weighted_f1"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing existing baseline outputs",
    )
    args = parser.parse_args()

    train = load_split("train")
    val = load_split("val")

    # The test set is deliberately not loaded.
    validate_train_val(train, val)

    expected_outputs = (
        [MODEL_DIR / f"{task}.joblib" for task in TASKS]
        + [REPORT_DIR / f"{task}_metrics.json" for task in TASKS]
        + [REPORT_DIR / "baseline_comparison.csv"]
    )

    if not args.overwrite:
        existing = [path for path in expected_outputs if path.exists()]
        if existing:
            raise FileExistsError(
                "Existing outputs found. "
                "Use --overwrite only if intentional:\n" + "\n".join(map(str, existing))
            )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("TF-IDF + LOGISTIC REGRESSION BASELINE")
    print("=" * 60)
    print(f"Train comments: {len(train)}")
    print(f"Validation comments: {len(val)}")
    print("Test data: NOT USED")

    results = []

    for task, classes in TASKS.items():
        result = train_task(task, classes, train, val)
        results.append(result)

    comparison = pd.DataFrame(results)
    comparison.to_csv(
        REPORT_DIR / "baseline_comparison.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\n" + "=" * 60)
    print("BASELINE COMPARISON")
    print("=" * 60)
    print(comparison.to_string(index=False))
    print("\nTraining completed successfully.")


if __name__ == "__main__":
    main()

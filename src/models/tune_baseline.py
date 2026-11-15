from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "splits"
MODEL_DIR = ROOT / "models" / "baseline_tuned"
REPORT_DIR = ROOT / "reports" / "baseline_tuned"

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

VECTORIZERS = {
    "word_1_2": {
        "analyzer": "word",
        "ngram_range": (1, 2),
    },
    "char_2_5": {
        "analyzer": "char",
        "ngram_range": (2, 5),
    },
    "char_wb_3_5": {
        "analyzer": "char_wb",
        "ngram_range": (3, 5),
    },
}

WEIGHTS = {
    "unweighted": None,
    "balanced": "balanced",
}


def load_data(name: str) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.csv"

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

    if df["comment_id"].duplicated().any():
        raise ValueError(f"{name}: duplicate comment IDs")

    if df["text"].astype(str).str.strip().eq("").any():
        raise ValueError(f"{name}: empty comment texts")

    for task, labels in TASKS.items():
        invalid = set(df[task]) - set(labels)

        if invalid:
            raise ValueError(f"{name}: invalid {task} labels: {invalid}")

    return df


def make_model(
    vectorizer_config: dict,
    class_weight,
) -> Pipeline:
    config = {
        "lowercase": True,
        "min_df": 2,
        "max_df": 0.98,
        "sublinear_tf": True,
        "max_features": 100_000,
        **vectorizer_config,
    }

    if config["analyzer"] == "word":
        config["token_pattern"] = r"(?u)\b\w+\b"

    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(**config)),
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


def train_task(
    task: str,
    classes: list[str],
    train: pd.DataFrame,
    val: pd.DataFrame,
) -> tuple[list[dict], dict]:

    x_train = train["text"].astype(str)
    y_train = train[task]

    x_val = val["text"].astype(str)
    y_val = val[task]

    results = []
    best_model = None
    best_result = None
    best_predictions = None

    for vectorizer_name, config in VECTORIZERS.items():
        for weight_name, class_weight in WEIGHTS.items():
            experiment = f"{vectorizer_name}__{weight_name}"

            print(f"  Training {experiment} ...", flush=True)

            model = make_model(
                config,
                class_weight,
            )

            model.fit(x_train, y_train)
            predictions = model.predict(x_val)

            result = {
                "task": task,
                "experiment": experiment,
                "vectorizer": vectorizer_name,
                "class_weight": weight_name,
                "accuracy": float(accuracy_score(y_val, predictions)),
                "macro_f1": float(
                    f1_score(
                        y_val,
                        predictions,
                        labels=classes,
                        average="macro",
                        zero_division=0,
                    )
                ),
                "weighted_f1": float(
                    f1_score(
                        y_val,
                        predictions,
                        labels=classes,
                        average="weighted",
                        zero_division=0,
                    )
                ),
            }

            results.append(result)

            print(f"    Macro F1: {result['macro_f1']:.4f}")

            if best_result is None or result["macro_f1"] > best_result["macro_f1"]:
                best_result = result
                best_model = model
                best_predictions = predictions

    assert best_model is not None
    assert best_result is not None
    assert best_predictions is not None

    joblib.dump(
        best_model,
        MODEL_DIR / f"{task}.joblib",
    )

    report = classification_report(
        y_val,
        best_predictions,
        labels=classes,
        output_dict=True,
        zero_division=0,
    )

    report_path = REPORT_DIR / f"{task}_report.json"

    report_path.write_text(
        json.dumps(
            {
                "selected_experiment": best_result,
                "classification_report": report,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"\n  BEST: {best_result['experiment']}"
        f" | Macro F1: {best_result['macro_f1']:.4f}"
    )

    print(
        classification_report(
            y_val,
            best_predictions,
            labels=classes,
            zero_division=0,
        )
    )

    return results, best_result


def main() -> None:
    train = load_data("train")
    val = load_data("val")

    if set(train["comment_id"]) & set(val["comment_id"]):
        raise ValueError("Train/validation comment overlap")

    if set(train["video_id"]) & set(val["video_id"]):
        raise ValueError("Train/validation video overlap")

    for task, classes in TASKS.items():
        if set(train[task]) != set(classes):
            raise ValueError(f"Training classes missing for {task}")

    expected = (
        [MODEL_DIR / f"{task}.joblib" for task in TASKS]
        + [REPORT_DIR / f"{task}_report.json" for task in TASKS]
        + [
            REPORT_DIR / "all_experiments.csv",
            REPORT_DIR / "best_models.csv",
        ]
    )

    existing = [str(path) for path in expected if path.exists()]

    if existing:
        raise FileExistsError(
            "Tuned baseline outputs already exist:\n" + "\n".join(existing)
        )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("TF-IDF BASELINE TUNING")
    print("=" * 60)

    print(f"Train: {len(train)}")
    print(f"Validation: {len(val)}")
    print("Test: NOT USED")

    all_results = []
    best_results = []

    for task, classes in TASKS.items():
        print("\n" + "=" * 60)
        print(f"TASK: {task.upper()}")
        print("=" * 60)

        results, best = train_task(task, classes, train, val)

        all_results.extend(results)
        best_results.append(best)

    pd.DataFrame(all_results).to_csv(
        REPORT_DIR / "all_experiments.csv",
        index=False,
        encoding="utf-8-sig",
    )

    comparison = pd.DataFrame(best_results)

    comparison.to_csv(
        REPORT_DIR / "best_models.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\n" + "=" * 60)
    print("BEST MODELS")
    print("=" * 60)

    print(comparison[["task", "experiment", "macro_f1"]].to_string(index=False))

    print("\nBaseline tuning completed successfully.")


if __name__ == "__main__":
    main()

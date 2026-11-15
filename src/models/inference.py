from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models" / "baseline_tuned"

TASKS = (
    "sentiment",
    "actionability",
    "toxicity",
    "question_type",
)

EXPECTED_CLASSES = {
    "sentiment": {
        "POSITIVE",
        "NEGATIVE",
        "NEUTRAL",
        "MIXED",
    },
    "actionability": {
        "NOT_ACTIONABLE",
        "IMPLICITLY_ACTIONABLE",
        "EXPLICITLY_ACTIONABLE",
    },
    "toxicity": {
        "NON_TOXIC",
        "TOXIC",
    },
    "question_type": {
        "NOT_QUESTION",
        "INFORMATION_SEEKING",
        "ACTION_REQUEST",
        "RHETORICAL",
    },
}


class CommentClassifier:
    """Classify Turkish comments using trusted tuned baseline models."""

    def __init__(self, model_dir: Path | str = DEFAULT_MODEL_DIR):
        self.model_dir = Path(model_dir)
        self.models: dict[str, Any] = {}

        for task in TASKS:
            model_path = self.model_dir / f"{task}.joblib"

            if not model_path.is_file():
                raise FileNotFoundError(f"Missing model for '{task}': {model_path}")

            # joblib files must come from a trusted source.
            model = joblib.load(model_path)

            if not callable(getattr(model, "predict", None)):
                raise TypeError(f"Model '{task}' does not support predict().")

            if not callable(getattr(model, "predict_proba", None)):
                raise TypeError(f"Model '{task}' does not support predict_proba().")

            classes = getattr(model, "classes_", None)

            if classes is None:
                raise TypeError(f"Model '{task}' does not expose classes_.")

            actual_classes = {str(label) for label in classes}

            if actual_classes != EXPECTED_CLASSES[task]:
                raise ValueError(
                    f"Unexpected classes for '{task}': {sorted(actual_classes)}"
                )

            self.models[task] = model

    @staticmethod
    def _validate_text(text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("Comment text must be a string.")

        cleaned = text.strip()

        if not cleaned:
            raise ValueError("Comment text cannot be empty.")

        return cleaned

    def predict(self, text: str) -> dict[str, Any]:
        """Classify a single comment."""

        return self.predict_batch([text])[0]

    def predict_batch(
        self,
        texts: Sequence[str],
    ) -> list[dict[str, Any]]:
        """Classify multiple comments with one call per model."""

        if isinstance(texts, (str, bytes)) or not isinstance(texts, Sequence):
            raise TypeError("texts must be a sequence of strings.")

        cleaned_texts = [self._validate_text(text) for text in texts]

        if not cleaned_texts:
            return []

        results: list[dict[str, Any]] = [
            {
                "text": text,
                "model_family": "tuned_baseline",
                "predictions": {},
            }
            for text in cleaned_texts
        ]

        for task, model in self.models.items():
            labels = model.predict(cleaned_texts)
            probability_rows = model.predict_proba(cleaned_texts)
            class_names = [str(label) for label in model.classes_]

            if len(labels) != len(cleaned_texts) or len(probability_rows) != len(
                cleaned_texts
            ):
                raise RuntimeError(f"Unexpected prediction count for '{task}'.")

            for index, (label, probabilities) in enumerate(
                zip(labels, probability_rows, strict=True)
            ):
                if len(probabilities) != len(class_names):
                    raise RuntimeError(f"Unexpected probability count for '{task}'.")

                results[index]["predictions"][task] = {
                    "label": str(label),
                    "probabilities": {
                        class_name: round(float(probability), 6)
                        for class_name, probability in zip(
                            class_names,
                            probabilities,
                            strict=True,
                        )
                    },
                }

        return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description=("Classify Turkish comments using tuned baseline models.")
    )

    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument(
        "--text",
        help="A single Turkish comment.",
    )

    input_group.add_argument(
        "--texts",
        nargs="+",
        help="Multiple Turkish comments.",
    )

    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help="Directory containing trusted model artifacts.",
    )

    args = parser.parse_args()

    classifier = CommentClassifier(model_dir=args.model_dir)

    if args.text is not None:
        result = classifier.predict(args.text)
    else:
        result = classifier.predict_batch(args.texts)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

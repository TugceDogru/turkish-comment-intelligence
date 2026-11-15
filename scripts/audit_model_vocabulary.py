from __future__ import annotations

import re
from pathlib import Path

import joblib

MODEL_DIR = Path("models/baseline_tuned")

MODEL_FILES = (
    "sentiment.joblib",
    "actionability.joblib",
    "toxicity.joblib",
    "question_type.joblib",
)

PATTERNS = {
    "email_like": re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}"),
    "phone_like": re.compile(r"(?<!\d)(?:\+?90)?0?5\d{9}(?!\d)"),
    "long_numeric_identifier": re.compile(r"(?<!\d)\d{9,}(?!\d)"),
}


def audit_vocabulary(vocabulary: dict[str, int]) -> dict[str, int]:
    counts = {name: 0 for name in PATTERNS}

    for token in vocabulary:
        for name, pattern in PATTERNS.items():
            if pattern.search(token):
                counts[name] += 1

    return counts


def main() -> None:
    for filename in MODEL_FILES:
        path = MODEL_DIR / filename

        if not path.is_file():
            raise FileNotFoundError(f"Missing model: {path}")

        # Load only trusted, locally created artifacts.
        model = joblib.load(path)

        vectorizer = model.named_steps["tfidf"]
        vocabulary = vectorizer.vocabulary_

        counts = audit_vocabulary(vocabulary)

        print(f"\nModel: {filename}")
        print(f"Vocabulary size: {len(vocabulary)}")

        for category, count in counts.items():
            print(f"{category}: {count}")

    print(
        "\nNote: This heuristic scan cannot prove "
        "that a model contains no personal data."
    )


if __name__ == "__main__":
    main()

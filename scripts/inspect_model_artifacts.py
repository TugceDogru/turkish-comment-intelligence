from __future__ import annotations

from pathlib import Path

import joblib

MODEL_DIR = Path("models/baseline_tuned")

EXPECTED_FILES = (
    "sentiment.joblib",
    "actionability.joblib",
    "toxicity.joblib",
    "question_type.joblib",
)


def main() -> None:
    for filename in EXPECTED_FILES:
        path = MODEL_DIR / filename

        print(f"\n{'=' * 60}")
        print(f"MODEL: {filename}")
        print(f"{'=' * 60}")

        if not path.is_file():
            print("ERROR: Model file not found.")
            continue

        # Only load artifacts created locally or obtained from trusted sources.
        model = joblib.load(path)

        print("Object type:", type(model).__name__)
        print("Module:", type(model).__module__)

        if hasattr(model, "steps"):
            print("Pipeline steps:")

            for name, step in model.steps:
                print(f"  - {name}: {type(step).__name__}")

        if hasattr(model, "classes_"):
            print("Classes:", list(model.classes_))

        if hasattr(model, "named_steps"):
            vectorizer = model.named_steps.get("tfidf")

            if vectorizer is not None:
                vocabulary = getattr(vectorizer, "vocabulary_", None)

                if vocabulary is not None:
                    print("Vocabulary size:", len(vocabulary))
                    print(
                        "Contains learned vocabulary:",
                        "YES",
                    )

        print("Size (MB):", round(path.stat().st_size / (1024**2), 2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_REVIEW = PROJECT_ROOT / "reports" / "annotation_audit_high_medium_review.csv"

BACKUP_DIR = PROJECT_ROOT / "reports" / "backups"

LABEL_COLUMNS = [
    "sentiment",
    "actionability",
    "toxicity",
    "question_type",
]

# Final decisions explicitly approved by the reviewer.
FINAL_CORRECTIONS = {
    759: {
        "question_type": "INFORMATION_SEEKING",
    },
    2362: {
        "sentiment": "MIXED",
        "question_type": "INFORMATION_SEEKING",
    },
}

EXPECTED_ROWS = 53


def finalize_review(review_path: Path) -> tuple[Path, dict]:
    if not review_path.is_file():
        raise FileNotFoundError(f"Review file not found: {review_path}")

    df = pd.read_csv(
        review_path,
        encoding="utf-8-sig",
        dtype={"comment_id": "string"},
        keep_default_na=False,
    )

    required = {
        "row_number",
        "comment_id",
        "review_status",
        *LABEL_COLUMNS,
    }

    for column in LABEL_COLUMNS:
        required.add(f"suggested_{column}")

    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["row_number"] = pd.to_numeric(
        df["row_number"],
        errors="raise",
    ).astype(int)

    if len(df) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} review rows, found {len(df)}.")

    if df["row_number"].duplicated().any():
        raise ValueError("Duplicate row numbers found.")

    if df["comment_id"].duplicated().any():
        raise ValueError("Duplicate comment IDs found.")

    missing_corrections = set(FINAL_CORRECTIONS) - set(df["row_number"])

    if missing_corrections:
        raise ValueError(f"Correction rows not found: {sorted(missing_corrections)}")

    if not df["review_status"].eq("PENDING").all():
        raise ValueError(
            "Some review decisions are already finalized. No changes were made."
        )

    expected_originals = {
        759: {
            "question_type": "ACTION_REQUEST",
        },
        2362: {
            "sentiment": "POSITIVE",
            "question_type": "NOT_QUESTION",
        },
    }

    for row_number, expected in expected_originals.items():
        row = df.loc[df["row_number"] == row_number].iloc[0]

        for column, value in expected.items():
            if row[column] != value:
                raise ValueError(
                    f"Row {row_number}: expected original "
                    f"{column}={value}, found {row[column]}"
                )

    # Make a backup before modifying the review file.
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    backup_path = BACKUP_DIR / f"annotation_review_before_finalization_{timestamp}.csv"

    shutil.copy2(review_path, backup_path)

    # Clear all previous proposals.
    # Only the reviewer's final decisions will remain.
    for column in LABEL_COLUMNS:
        df[f"suggested_{column}"] = ""

    df["approved_correction"] = ""
    df["review_status"] = "APPROVED"

    if "reviewer_notes" not in df.columns:
        df["reviewer_notes"] = ""

    for index, row in df.iterrows():
        row_number = int(row["row_number"])

        if row_number in FINAL_CORRECTIONS:
            corrections = FINAL_CORRECTIONS[row_number]

            for column, new_value in corrections.items():
                df.at[index, f"suggested_{column}"] = new_value

            df.at[index, "review_status"] = "CORRECTED"
            df.at[index, "reviewer_notes"] = "Final correction approved by reviewer."
        else:
            df.at[index, "reviewer_notes"] = "Original labels retained by reviewer."

    df.to_csv(
        review_path,
        index=False,
        encoding="utf-8-sig",
    )

    stats = {
        "total_reviewed": len(df),
        "approved": int((df["review_status"] == "APPROVED").sum()),
        "corrected": int((df["review_status"] == "CORRECTED").sum()),
        "pending": int((df["review_status"] == "PENDING").sum()),
    }

    return backup_path, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize annotation review decisions")

    parser.add_argument(
        "--review",
        type=Path,
        default=DEFAULT_REVIEW,
    )

    args = parser.parse_args()

    backup_path, stats = finalize_review(args.review)

    print("=" * 60)
    print("ANNOTATION REVIEW FINALIZED")
    print("=" * 60)

    for key, value in stats.items():
        print(f"{key}: {value}")

    print(f"\nBackup:\n  {backup_path}")
    print(f"\nUpdated review:\n  {args.review}")
    print("\nOriginal annotation dataset was not modified.")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_REVIEW_PATH = (
    PROJECT_ROOT / "reports" / "annotation_audit_high_medium_review.csv"
)

BACKUP_DIR = PROJECT_ROOT / "reports" / "backups"

LABEL_COLUMNS = [
    "sentiment",
    "actionability",
    "toxicity",
    "question_type",
]

VALID_LABELS = {
    "sentiment": {"POSITIVE", "NEUTRAL", "NEGATIVE", "MIXED"},
    "actionability": {
        "NOT_ACTIONABLE",
        "IMPLICITLY_ACTIONABLE",
        "EXPLICITLY_ACTIONABLE",
    },
    "toxicity": {"NON_TOXIC", "TOXIC"},
    "question_type": {
        "NOT_QUESTION",
        "INFORMATION_SEEKING",
        "ACTION_REQUEST",
        "RHETORICAL",
    },
}


# Provisional suggestions from the manual review.
# These are NOT approved corrections.
#
# Format:
# row_number: {label_column: suggested_value}

PROPOSED_CHANGES = {
    199: {"question_type": "INFORMATION_SEEKING"},
    759: {"question_type": "INFORMATION_SEEKING"},
    1184: {"actionability": "EXPLICITLY_ACTIONABLE"},
    1193: {
        "actionability": "EXPLICITLY_ACTIONABLE",
        "question_type": "NOT_QUESTION",
    },
    214: {"question_type": "ACTION_REQUEST"},
    793: {"question_type": "ACTION_REQUEST"},
    956: {"toxicity": "NON_TOXIC"},
    1391: {"question_type": "RHETORICAL"},
    1473: {"question_type": "RHETORICAL"},
    1495: {"question_type": "RHETORICAL"},
    1793: {"question_type": "RHETORICAL"},
    2369: {"toxicity": "NON_TOXIC"},
    2374: {
        "toxicity": "NON_TOXIC",
        "sentiment": "NEUTRAL",
    },
    2386: {"toxicity": "NON_TOXIC"},
    2936: {"question_type": "RHETORICAL"},
    3021: {"toxicity": "NON_TOXIC"},
    3168: {"question_type": "RHETORICAL"},
    3199: {
        "sentiment": "NEGATIVE",
        "question_type": "RHETORICAL",
    },
    3222: {
        "toxicity": "TOXIC",
        "question_type": "RHETORICAL",
    },
    3269: {"question_type": "INFORMATION_SEEKING"},
    3401: {"toxicity": "NON_TOXIC"},
    3438: {"toxicity": "NON_TOXIC"},
    3577: {"question_type": "RHETORICAL"},
    3661: {"question_type": "INFORMATION_SEEKING"},
    3746: {"question_type": "RHETORICAL"},
    3763: {"question_type": "RHETORICAL"},
    3791: {"question_type": "RHETORICAL"},
    3937: {"question_type": "RHETORICAL"},
    4037: {"question_type": "RHETORICAL"},
    4407: {"question_type": "ACTION_REQUEST"},
    4968: {
        "sentiment": "NEUTRAL",
        "toxicity": "NON_TOXIC",
        "question_type": "INFORMATION_SEEKING",
    },
}

# These cases require additional human judgment.
UNCERTAIN_ROWS = {
    252,
    661,
    949,
    1034,
    1812,
    2362,
    3413,
    4191,
}

KEEP_ROWS = {
    7,
    1258,
    1507,
    1871,
    2204,
    2473,
    2536,
    2890,
    3228,
    3270,
    3572,
    3589,
    3636,
    4999,
}

REASONS = {
    199: "Personal report request, not a creator-content request.",
    759: "Product availability question.",
    1184: "Explicit request for a new camp with more questions.",
    1193: "Imperative expression; content intent needs confirmation.",
    214: "Asks for new educational video/PDF content.",
    793: "Requests a tablet review.",
    956: "Single ambiguous word; no clear targeted human insult.",
    1391: "Challenge to evidence; check rhetorical intent.",
    1473: "Review question function in its full context.",
    1495: "Challenges absent commentators rhetorically.",
    1793: "Expresses appreciation through a rhetorical question.",
    2369: "Short imperative; targeted toxicity is uncertain.",
    2374: "Ambiguous fragment; insufficient negative evidence.",
    2386: "Single ambiguous word; target is unclear.",
    2936: "Confrontational question; likely rhetorical.",
    3021: "Negative presenter criticism; toxicity needs review.",
    3168: "Humorous, exaggerated questions.",
    3199: "Critical rhetorical argument; sentiment needs review.",
    3222: "Direct personal insult and confrontational question.",
    3269: "Short information query.",
    3401: "Negative evaluation; human target not established.",
    3438: "Strong negative evaluation; target is unclear.",
    3577: "Positive surprise expressed as a question.",
    3661: "Short factual clarification question.",
    3746: "Rhetorical challenge.",
    3763: "Rhetorical challenge expressing dissatisfaction.",
    3791: "Speculative rhetorical question.",
    3937: "Rhetorical rejection of a claim.",
    4037: "Question intent requires contextual interpretation.",
    4407: "Asks whether a tutorial will be created.",
    4968: "Neutral information question, not an insult.",
}


def validate_review(df: pd.DataFrame) -> None:
    required = {
        "row_number",
        "comment_id",
        "text",
        "priority",
        "review_status",
        *LABEL_COLUMNS,
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if df["row_number"].duplicated().any():
        raise ValueError("Duplicate row_number values detected.")

    if df["comment_id"].duplicated().any():
        raise ValueError("Duplicate comment_id values detected.")

    if not df["priority"].isin({"HIGH", "MEDIUM"}).all():
        raise ValueError("Review file contains unexpected priorities.")

    for column in LABEL_COLUMNS:
        invalid = set(df[column]) - VALID_LABELS[column]

        if invalid:
            raise ValueError(f"Invalid labels in {column}: {invalid}")

    actual_rows = set(df["row_number"])

    expected_rows = set(PROPOSED_CHANGES) | UNCERTAIN_ROWS | KEEP_ROWS

    if actual_rows != expected_rows:
        raise ValueError(
            "Review rows do not match the expected "
            "53 candidates.\n"
            f"Missing: {sorted(expected_rows - actual_rows)}\n"
            f"Unexpected: {sorted(actual_rows - expected_rows)}"
        )

    for row_number, changes in PROPOSED_CHANGES.items():
        for column, value in changes.items():
            if value not in VALID_LABELS[column]:
                raise ValueError(
                    f"Invalid suggestion at row {row_number}: {column}={value}"
                )


def populate_review(
    review_path: Path,
) -> tuple[Path, dict]:

    if not review_path.is_file():
        raise FileNotFoundError(
            f"Review file not found: {review_path}\n"
            "Run: python -m src.annotation.prepare_review"
        )

    df = pd.read_csv(
        review_path,
        encoding="utf-8-sig",
        dtype={"comment_id": "string"},
        keep_default_na=False,
    )

    df["row_number"] = pd.to_numeric(
        df["row_number"],
        errors="raise",
    ).astype(int)

    validate_review(df)

    suggested_columns = [f"suggested_{column}" for column in LABEL_COLUMNS]

    for column in suggested_columns:
        if column not in df.columns:
            df[column] = ""

    if "reviewer_notes" not in df.columns:
        df["reviewer_notes"] = ""

    if "approved_correction" not in df.columns:
        df["approved_correction"] = ""

    # Do not overwrite existing review work.
    editable_columns = suggested_columns + ["reviewer_notes", "approved_correction"]

    if (
        df[editable_columns]
        .astype(str)
        .apply(lambda col: col.str.strip().ne(""))
        .any()
        .any()
        or df["review_status"].ne("PENDING").any()
    ):
        raise ValueError(
            "Review file already contains review work. No changes were made."
        )

    # Verify that each suggestion actually changes a label.
    for row_number, changes in PROPOSED_CHANGES.items():
        row = df.loc[df["row_number"] == row_number].iloc[0]

        for column, value in changes.items():
            if row[column] == value:
                raise ValueError(
                    f"Row {row_number}: suggested {column} "
                    "already matches the current label."
                )

    # Back up the original review file.
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    backup_path = BACKUP_DIR / f"annotation_review_before_population_{timestamp}.csv"

    shutil.copy2(review_path, backup_path)

    # Populate proposals, never approve them.
    for index, row in df.iterrows():
        row_number = int(row["row_number"])

        if row_number in PROPOSED_CHANGES:
            changes = PROPOSED_CHANGES[row_number]

            for column, value in changes.items():
                df.at[index, f"suggested_{column}"] = value

            df.at[index, "reviewer_notes"] = "PROPOSED CHANGE - " + REASONS.get(
                row_number,
                "Manual verification required.",
            )

        elif row_number in UNCERTAIN_ROWS:
            df.at[index, "reviewer_notes"] = (
                "UNCERTAIN - Review full comment using annotation guideline v1.3."
            )

        elif row_number in KEEP_ROWS:
            df.at[index, "reviewer_notes"] = (
                "PROPOSED KEEP - Existing labels appear acceptable; verify manually."
            )

        df.at[index, "review_status"] = "PENDING"

    df.to_csv(
        review_path,
        index=False,
        encoding="utf-8-sig",
    )

    stats = {
        "total": len(df),
        "proposed_changes": len(PROPOSED_CHANGES),
        "uncertain": len(UNCERTAIN_ROWS),
        "proposed_keep": len(KEEP_ROWS),
    }

    return backup_path, stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate annotation review suggestions"
    )

    parser.add_argument(
        "--review",
        type=Path,
        default=DEFAULT_REVIEW_PATH,
    )

    args = parser.parse_args()

    backup_path, stats = populate_review(args.review)

    print("=" * 60)
    print("ANNOTATION REVIEW POPULATION")
    print("=" * 60)

    print(f"Total review candidates: {stats['total']}")
    print(f"Proposed changes: {stats['proposed_changes']}")
    print(f"Uncertain: {stats['uncertain']}")
    print(f"Proposed keep: {stats['proposed_keep']}")

    print("\nAll review statuses remain PENDING.")
    print(f"\nBackup:\n  {backup_path}")
    print(f"\nUpdated review:\n  {args.review}")
    print("\nOriginal annotation dataset was not modified.")


if __name__ == "__main__":
    main()

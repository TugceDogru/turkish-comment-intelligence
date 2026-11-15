from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SOURCE = PROJECT_ROOT / "data" / "annotated" / "annotation_dataset_5000.csv"

DEFAULT_REVIEW = PROJECT_ROOT / "reports" / "annotation_audit_high_medium_review.csv"

DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "annotated" / "annotation_dataset_5000_reviewed.csv"
)

DEFAULT_CHANGELOG = PROJECT_ROOT / "reports" / "annotation_corrections_log.csv"

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

VALID_STATUSES = {
    "PENDING",
    "APPROVED",
    "CORRECTED",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    return pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype={"comment_id": "string"},
        keep_default_na=False,
    )


def validate_labels(
    df: pd.DataFrame,
    description: str,
) -> None:
    for column in LABEL_COLUMNS:
        if column not in df.columns:
            raise ValueError(f"{description}: missing column {column}")

        invalid = set(df[column]) - VALID_LABELS[column]

        if invalid:
            raise ValueError(
                f"{description}: invalid {column} labels: {sorted(invalid)}"
            )


def validate_source(df: pd.DataFrame) -> None:
    required = {"comment_id", "text", *LABEL_COLUMNS}

    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Source missing columns: {sorted(missing)}")

    if df["comment_id"].duplicated().any():
        raise ValueError("Source contains duplicate comment IDs.")

    if df["comment_id"].eq("").any():
        raise ValueError("Source contains empty comment IDs.")

    validate_labels(df, "Source dataset")


def validate_review(
    review: pd.DataFrame,
    source: pd.DataFrame,
) -> None:
    required = {
        "row_number",
        "comment_id",
        "text",
        "review_status",
        *LABEL_COLUMNS,
    }

    missing = required - set(review.columns)

    if missing:
        raise ValueError(f"Review missing columns: {sorted(missing)}")

    for column in LABEL_COLUMNS:
        suggested = f"suggested_{column}"

        if suggested not in review.columns:
            raise ValueError(f"Review missing column: {suggested}")

    review["row_number"] = pd.to_numeric(
        review["row_number"],
        errors="raise",
    ).astype(int)

    if review["row_number"].duplicated().any():
        raise ValueError("Duplicate row numbers in review.")

    if review["comment_id"].duplicated().any():
        raise ValueError("Duplicate comment IDs in review.")

    invalid_statuses = set(review["review_status"]) - VALID_STATUSES

    if invalid_statuses:
        raise ValueError(f"Invalid review statuses: {sorted(invalid_statuses)}")

    validate_labels(review, "Review dataset")

    source_by_id = source.set_index(
        "comment_id",
        drop=False,
    )

    for _, row in review.iterrows():
        row_number = int(row["row_number"])
        comment_id = row["comment_id"]

        if not 1 <= row_number <= len(source):
            raise ValueError(f"Invalid row number: {row_number}")

        if comment_id not in source_by_id.index:
            raise ValueError(f"Unknown comment ID: {comment_id}")

        original = source.iloc[row_number - 1]

        if original["comment_id"] != comment_id:
            raise ValueError(f"Row {row_number}: comment ID does not match source row.")

        if original["text"] != row["text"]:
            raise ValueError(f"Row {row_number}: comment text does not match source.")

        for column in LABEL_COLUMNS:
            if original[column] != row[column]:
                raise ValueError(f"Row {row_number}: original {column} label mismatch.")

            suggested = str(row[f"suggested_{column}"]).strip()

            if suggested and suggested not in VALID_LABELS[column]:
                raise ValueError(
                    f"Row {row_number}: invalid suggested {column}: {suggested}"
                )

        if row["review_status"] == "CORRECTED":
            changed_columns = [
                column
                for column in LABEL_COLUMNS
                if (
                    str(row[f"suggested_{column}"]).strip()
                    and str(row[f"suggested_{column}"]).strip() != row[column]
                )
            ]

            if not changed_columns:
                raise ValueError(
                    f"Row {row_number}: CORRECTED but no label changes specified."
                )


def apply_corrections(
    source: pd.DataFrame,
    review: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:

    result = source.copy(deep=True)
    result_index = {
        comment_id: index for index, comment_id in enumerate(result["comment_id"])
    }

    changes = []
    timestamp = datetime.now().isoformat(timespec="seconds")

    corrected = review.loc[review["review_status"] == "CORRECTED"]

    for _, row in corrected.iterrows():
        comment_id = row["comment_id"]
        index = result_index[comment_id]

        for column in LABEL_COLUMNS:
            new_value = str(row[f"suggested_{column}"]).strip()

            if not new_value:
                continue

            old_value = result.at[index, column]

            if new_value == old_value:
                continue

            result.at[index, column] = new_value

            changes.append(
                {
                    "timestamp": timestamp,
                    "row_number": int(row["row_number"]),
                    "comment_id": comment_id,
                    "column": column,
                    "old_label": old_value,
                    "new_label": new_value,
                    "reviewer_notes": row.get("reviewer_notes", ""),
                }
            )

    changelog = pd.DataFrame(
        changes,
        columns=[
            "timestamp",
            "row_number",
            "comment_id",
            "column",
            "old_label",
            "new_label",
            "reviewer_notes",
        ],
    )

    validate_labels(result, "Reviewed dataset")

    if len(result) != len(source):
        raise RuntimeError("Dataset row count changed unexpectedly.")

    if not result["comment_id"].equals(source["comment_id"]):
        raise RuntimeError("Comment IDs or row order changed.")

    non_label_columns = [
        column for column in source.columns if column not in LABEL_COLUMNS
    ]

    if not result[non_label_columns].equals(source[non_label_columns]):
        raise RuntimeError("Non-label data changed unexpectedly.")

    stats = {
        "total_comments": int(len(result)),
        "review_candidates": int(len(review)),
        "pending": int((review["review_status"] == "PENDING").sum()),
        "approved": int((review["review_status"] == "APPROVED").sum()),
        "corrected_comments": int(len(corrected)),
        "label_changes": int(len(changelog)),
    }

    return result, changelog, stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply approved annotation corrections"
    )

    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
    )

    parser.add_argument(
        "--review",
        type=Path,
        default=DEFAULT_REVIEW,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--changelog",
        type=Path,
        default=DEFAULT_CHANGELOG,
    )

    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help=(
            "Allow creating a provisional dataset while some reviews remain PENDING."
        ),
    )

    args = parser.parse_args()

    source = read_csv(args.source)
    review = read_csv(args.review)

    validate_source(source)
    validate_review(review, source)

    result, changelog, stats = apply_corrections(
        source,
        review,
    )

    if stats["pending"] and not args.allow_pending:
        raise ValueError(
            f"{stats['pending']} reviews are still "
            "PENDING. Resolve them before creating "
            "the final reviewed dataset. "
            "Use --allow-pending only for "
            "a provisional output."
        )

    summary_path = args.changelog.parent / "annotation_corrections_summary.json"

    output_paths = [
        args.output,
        args.changelog,
        summary_path,
    ]

    resolved_paths = [path.resolve() for path in output_paths]

    if len(set(resolved_paths)) != len(resolved_paths):
        raise ValueError("Output paths must be different.")

    protected_paths = {
        args.source.resolve(),
        args.review.resolve(),
    }

    for path in output_paths:
        if path.resolve() in protected_paths:
            raise ValueError(f"Cannot overwrite input file: {path}")

        if path.exists():
            raise FileExistsError(
                f"Output already exists: {path}\n"
                "Existing files will not be overwritten."
            )

    for path in output_paths:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    result.to_csv(
        args.output,
        index=False,
        encoding="utf-8-sig",
    )

    changelog.to_csv(
        args.changelog,
        index=False,
        encoding="utf-8-sig",
    )

    summary_path.write_text(
        json.dumps(
            stats,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 60)
    print("ANNOTATION CORRECTIONS")
    print("=" * 60)

    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\nGenerated files:")
    for path in output_paths:
        print(f"  {path}")

    print("\nOriginal dataset was not modified.")


if __name__ == "__main__":
    main()

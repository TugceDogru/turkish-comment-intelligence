from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_INPUT = PROJECT_ROOT / "data" / "annotated" / "annotation_dataset_5000.csv"

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports"

LABEL_COLUMNS = [
    "sentiment",
    "actionability",
    "toxicity",
    "question_type",
]

REQUIRED_COLUMNS = [
    "comment_id",
    "text",
    *LABEL_COLUMNS,
]

VALID_LABELS = {
    "sentiment": {
        "POSITIVE",
        "NEUTRAL",
        "NEGATIVE",
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

PRIORITY_ORDER = {
    "HIGH": 0,
    "MEDIUM": 1,
    "LOW": 2,
}

RULES = {
    "ACTION_REQUEST_vs_ACTIONABILITY": {
        "priority": "HIGH",
        "reason": (
            "ACTION_REQUEST normally refers to a "
            "content-related creator request. "
            "Check whether the request actually "
            "targets the creator's content."
        ),
        "review": "Review both dimensions",
    },
    "IMPLICIT_vs_ACTION_REQUEST": {
        "priority": "HIGH",
        "reason": (
            "A direct content-related request would normally be EXPLICITLY_ACTIONABLE."
        ),
        "review": "Review actionability",
    },
    "EXPLICIT_vs_INFORMATION": {
        "priority": "MEDIUM",
        "reason": (
            "Distinguish a request for new content "
            "from a genuine information or product "
            "advice question."
        ),
        "review": "Review question intent",
    },
    "VERY_SHORT_TOXIC": {
        "priority": "MEDIUM",
        "reason": (
            "Very short toxic comments require "
            "clear evidence of a targeted human insult, "
            "threat, or degrading expression."
        ),
        "review": "Review toxicity",
    },
    "QUESTION_MARK_NOT_QUESTION": {
        "priority": "MEDIUM",
        "reason": (
            "A question mark appears in a comment "
            "classified as NOT_QUESTION. "
            "It may be a quotation or punctuation "
            "rather than a meaningful question."
        ),
        "review": "Review question type",
    },
    "QUESTION_WITHOUT_MARKER": {
        "priority": "LOW",
        "reason": (
            "A question class is assigned, but no "
            "obvious question marker was found. "
            "Turkish questions may omit punctuation."
        ),
        "review": "Review question type",
    },
    "ANNOTATION_NOTE": {
        "priority": "LOW",
        "reason": (
            "The annotator left a note. Optional human follow-up may be useful."
        ),
        "review": "Review annotation note",
    },
}


def has_question_marker(text: str) -> bool:
    """
    Detect obvious question markers.

    This is deliberately conservative.
    Turkish questions may be written without
    punctuation or with attached particles.
    """
    if "?" in text or "？" in text:
        return True

    pattern = (
        r"\b("
        r"mı|mi|mu|mü|"
        r"mısın|misin|musun|müsün|"
        r"mıyım|miyim|muyum|müyüm|"
        r"mıyız|miyiz|muyuz|müyüz|"
        r"mısınız|misiniz|musunuz|müsünüz"
        r")\b"
    )

    return bool(re.search(pattern, text, re.IGNORECASE))


def validate_input(df: pd.DataFrame) -> None:
    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    for column, allowed in VALID_LABELS.items():
        invalid = df[column].dropna().astype(str).unique()
        invalid = [value for value in invalid if value not in allowed]

        if invalid:
            raise ValueError(f"Invalid labels in {column}: {invalid}")

    missing_labels = df[LABEL_COLUMNS].isna().sum()

    if missing_labels.any():
        raise ValueError("Incomplete annotations:\n" + missing_labels.to_string())


def detect_flags(row: pd.Series) -> list[str]:
    text = str(row["text"])
    actionability = row["actionability"]
    toxicity = row["toxicity"]
    question_type = row["question_type"]

    flags = []

    # Rule 1: A creator action request should
    # normally be explicitly actionable.
    if question_type == "ACTION_REQUEST" and actionability != "EXPLICITLY_ACTIONABLE":
        flags.append("ACTION_REQUEST_vs_ACTIONABILITY")

    # Rule 2: More specific subtype of rule 1.
    if question_type == "ACTION_REQUEST" and actionability == "IMPLICITLY_ACTIONABLE":
        flags.append("IMPLICIT_vs_ACTION_REQUEST")

    # Rule 3: Explicit content request or
    # ordinary information question?
    if (
        actionability == "EXPLICITLY_ACTIONABLE"
        and question_type == "INFORMATION_SEEKING"
    ):
        flags.append("EXPLICIT_vs_INFORMATION")

    # Rule 4: Very short toxic comments.
    # A short comment may still be toxic.
    if toxicity == "TOXIC" and len(text.split()) <= 2:
        flags.append("VERY_SHORT_TOXIC")

    # Rule 5: Question punctuation but
    # NOT_QUESTION label.
    if question_type == "NOT_QUESTION" and ("?" in text or "？" in text):
        flags.append("QUESTION_MARK_NOT_QUESTION")

    # Rule 6: Question label without an
    # obvious question marker.
    if question_type != "NOT_QUESTION" and not has_question_marker(text):
        flags.append("QUESTION_WITHOUT_MARKER")

    # Rule 7: Existing annotation note.
    note = row.get("annotation_notes", "")

    if pd.notna(note) and str(note).strip():
        flags.append("ANNOTATION_NOTE")

    return flags


def get_priority(flags: list[str]) -> str:
    return min(
        (RULES[flag]["priority"] for flag in flags),
        key=lambda value: PRIORITY_ORDER[value],
    )


def generate_audit(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    records = []
    rule_counts = Counter()

    for row_number, (_, row) in enumerate(
        df.iterrows(),
        start=1,
    ):
        flags = detect_flags(row)

        if not flags:
            continue

        rule_counts.update(flags)

        reasons = [RULES[flag]["reason"] for flag in flags]

        review_suggestions = list(
            dict.fromkeys(RULES[flag]["review"] for flag in flags)
        )

        records.append(
            {
                "row_number": row_number,
                "comment_id": row["comment_id"],
                "text": row["text"],
                "sentiment": row["sentiment"],
                "actionability": row["actionability"],
                "toxicity": row["toxicity"],
                "question_type": row["question_type"],
                "priority": get_priority(flags),
                "flags": " | ".join(flags),
                "audit_reason": " | ".join(reasons),
                "suggested_review": " | ".join(review_suggestions),
                "review_status": "PENDING",
                "approved_correction": "",
                "reviewer_notes": "",
            }
        )

    columns = [
        "row_number",
        "comment_id",
        "text",
        *LABEL_COLUMNS,
        "priority",
        "flags",
        "audit_reason",
        "suggested_review",
        "review_status",
        "approved_correction",
        "reviewer_notes",
    ]

    audit_df = pd.DataFrame(
        records,
        columns=columns,
    )

    if not audit_df.empty:
        audit_df["_priority_sort"] = audit_df["priority"].map(PRIORITY_ORDER)

        audit_df = (
            audit_df.sort_values(
                ["_priority_sort", "row_number"],
                kind="stable",
            )
            .drop(columns="_priority_sort")
            .reset_index(drop=True)
        )

    priority_counts = audit_df["priority"].value_counts()

    summary = {
        "total_rows": int(len(df)),
        "unique_comments_flagged": int(len(audit_df)),
        "flagged_by_priority": {
            priority: int(priority_counts.get(priority, 0))
            for priority in ["HIGH", "MEDIUM", "LOW"]
        },
        "rule_counts": {rule: int(rule_counts.get(rule, 0)) for rule in RULES},
        "method": (
            "Heuristic candidate generation; "
            "no labels were modified. "
            "Flagged rows are not confirmed errors."
        ),
        "source_file": "annotation_dataset_5000.csv",
    }

    return audit_df, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Turkish Comment Intelligence audit")

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )

    args = parser.parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(f"Dataset not found: {args.input}")

    df = pd.read_csv(
        args.input,
        encoding="utf-8-sig",
        dtype={"comment_id": "string"},
    )

    validate_input(df)

    audit_df, summary = generate_audit(df)

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    audit_path = args.output_dir / "annotation_audit.csv"

    summary_path = args.output_dir / "annotation_audit_summary.json"

    audit_df.to_csv(
        audit_path,
        index=False,
        encoding="utf-8-sig",
    )

    summary_path.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 60)
    print("ANNOTATION QUALITY AUDIT")
    print("=" * 60)
    print(f"Total comments: {len(df)}")
    print(f"Flagged comments: {len(audit_df)}")

    print("\nPriority distribution:")
    for priority, count in summary["flagged_by_priority"].items():
        print(f"  {priority}: {count}")

    print("\nRule counts:")
    for rule, count in summary["rule_counts"].items():
        print(f"  {rule}: {count}")

    print("\nGenerated files:")
    print(f"  {audit_path}")
    print(f"  {summary_path}")

    print("\nOriginal dataset was not modified.")


if __name__ == "__main__":
    main()

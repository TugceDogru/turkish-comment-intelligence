import atexit
import contextlib
from pathlib import Path

import pandas as pd

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ANNOTATION_FILE = PROJECT_ROOT / "data" / "annotated" / "annotation_dataset_5000.csv"


# ============================================================
# LABEL DEFINITIONS
# ============================================================

SENTIMENT_MAP = {
    "1": "POSITIVE",
    "2": "NEUTRAL",
    "3": "NEGATIVE",
    "4": "MIXED",
}

ACTIONABILITY_MAP = {
    "1": "NOT_ACTIONABLE",
    "2": "IMPLICITLY_ACTIONABLE",
    "3": "EXPLICITLY_ACTIONABLE",
}

TOXICITY_MAP = {
    "1": "NON_TOXIC",
    "2": "TOXIC",
}

QUESTION_TYPE_MAP = {
    "1": "NOT_QUESTION",
    "2": "INFORMATION_SEEKING",
    "3": "ACTION_REQUEST",
    "4": "RHETORICAL",
}


VALID_SENTIMENTS = set(SENTIMENT_MAP.values())
VALID_ACTIONABILITY = set(ACTIONABILITY_MAP.values())
VALID_TOXICITY = set(TOXICITY_MAP.values())
VALID_QUESTION_TYPES = set(QUESTION_TYPE_MAP.values())


REQUIRED_COLUMNS = {
    "comment_id",
    "video_id",
    "video_title",
    "text",
    "source_category",
    "sentiment",
    "actionability",
    "toxicity",
    "question_type",
    "annotation_notes",
}


# ============================================================
# GLOBAL STATE
# ============================================================

df = None
dirty = False


# ============================================================
# HELPERS
# ============================================================


def normalize_empty_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    label_columns = [
        "sentiment",
        "actionability",
        "toxicity",
        "question_type",
        "annotation_notes",
    ]

    for column in label_columns:
        dataframe[column] = dataframe[column].fillna("").astype(str).str.strip()

    return dataframe


def validate_dataset(dataframe: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    invalid_sentiment = (dataframe["sentiment"] != "") & (
        ~dataframe["sentiment"].isin(VALID_SENTIMENTS)
    )

    invalid_actionability = (dataframe["actionability"] != "") & (
        ~dataframe["actionability"].isin(VALID_ACTIONABILITY)
    )

    invalid_toxicity = (dataframe["toxicity"] != "") & (
        ~dataframe["toxicity"].isin(VALID_TOXICITY)
    )

    invalid_question_type = (dataframe["question_type"] != "") & (
        ~dataframe["question_type"].isin(VALID_QUESTION_TYPES)
    )

    if invalid_sentiment.any():
        bad_values = dataframe.loc[
            invalid_sentiment,
            "sentiment",
        ].unique()

        raise ValueError(f"Invalid sentiment labels found: {bad_values}")

    if invalid_actionability.any():
        bad_values = dataframe.loc[
            invalid_actionability,
            "actionability",
        ].unique()

        raise ValueError(f"Invalid actionability labels found: {bad_values}")

    if invalid_toxicity.any():
        bad_values = dataframe.loc[
            invalid_toxicity,
            "toxicity",
        ].unique()

        raise ValueError(f"Invalid toxicity labels found: {bad_values}")

    if invalid_question_type.any():
        bad_values = dataframe.loc[
            invalid_question_type,
            "question_type",
        ].unique()

        raise ValueError(f"Invalid question_type labels found: {bad_values}")


def has_original_labels(row: pd.Series) -> bool:
    """
    True when the original three annotation dimensions
    have already been completed.
    """
    return (
        row["sentiment"] in VALID_SENTIMENTS
        and row["actionability"] in VALID_ACTIONABILITY
        and row["toxicity"] in VALID_TOXICITY
    )


def is_completed(row: pd.Series) -> bool:
    """
    A comment is fully completed only when all four
    annotation dimensions have valid labels.
    """
    return has_original_labels(row) and row["question_type"] in VALID_QUESTION_TYPES


def completed_count() -> int:
    return int(df.apply(is_completed, axis=1).sum())


def original_labels_count() -> int:
    return int(df.apply(has_original_labels, axis=1).sum())


def question_type_count() -> int:
    return int(df["question_type"].isin(VALID_QUESTION_TYPES).sum())


def save_dataset(force_message: bool = True) -> None:
    global dirty

    if df is None:
        return

    df.to_csv(
        ANNOTATION_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    dirty = False

    if force_message:
        completed = completed_count()
        total = len(df)

        print(f"\n[SAVED] {completed:,} / {total:,} comments fully completed.")


def emergency_save() -> None:
    if df is not None and dirty:
        with contextlib.suppress(Exception):
            save_dataset(force_message=False)


def show_help() -> None:
    print(
        """
================================================================================
FAST ANNOTATION FORMAT
================================================================================

NORMAL MODE
-----------

Enter all 4 labels on ONE line:

    SENTIMENT ACTIONABILITY TOXICITY QUESTION_TYPE

Example:

    3 2 1 1

means:

    NEGATIVE
    IMPLICITLY_ACTIONABLE
    NON_TOXIC
    NOT_QUESTION


SENTIMENT
    1 = POSITIVE
    2 = NEUTRAL
    3 = NEGATIVE
    4 = MIXED


ACTIONABILITY
    1 = NOT_ACTIONABLE
    2 = IMPLICITLY_ACTIONABLE
    3 = EXPLICITLY_ACTIONABLE

TOXICITY
    1 = NON_TOXIC
    2 = TOXIC

QUESTION TYPE
    1 = NOT_QUESTION
    2 = INFORMATION_SEEKING
    3 = ACTION_REQUEST
    4 = RHETORICAL


QUESTION-TYPE-ONLY MODE
-----------------------

If Sentiment, Actionability and Toxicity already exist,
the tool preserves them.

Enter only the Question Type:

    1 / 2 / 3 / 4


COMMANDS
    n = Add annotation note
    s = Save
    q = Save and quit
    h = Show help


NORMAL MODE EXAMPLES
    1 1 1 1
    2 1 1 2
    2 3 1 3
    3 1 1 4
    3 1 2 1

================================================================================
"""
    )


def parse_labels(user_input: str):
    parts = user_input.strip().split()

    if len(parts) != 4:
        return None

    sentiment_choice = parts[0]
    actionability_choice = parts[1]
    toxicity_choice = parts[2]
    question_type_choice = parts[3]

    if sentiment_choice not in SENTIMENT_MAP:
        return None

    if actionability_choice not in ACTIONABILITY_MAP:
        return None

    if toxicity_choice not in TOXICITY_MAP:
        return None

    if question_type_choice not in QUESTION_TYPE_MAP:
        return None

    return (
        SENTIMENT_MAP[sentiment_choice],
        ACTIONABILITY_MAP[actionability_choice],
        TOXICITY_MAP[toxicity_choice],
        QUESTION_TYPE_MAP[question_type_choice],
    )


def parse_question_type(user_input: str):
    choice = user_input.strip()

    if choice not in QUESTION_TYPE_MAP:
        return None

    return QUESTION_TYPE_MAP[choice]


def print_comment(
    index: int,
    total: int,
    text: str,
    question_only: bool,
    row: pd.Series,
) -> None:

    print("\n" + "=" * 80)
    print(f"COMMENT {index + 1:,} / {total:,}")
    print(f"Dataset row: {index + 1:,}")
    print("=" * 80)

    print("\nCOMMENT:\n")
    print(text)

    print("\n" + "-" * 80)

    if question_only:
        print("MODE: QUESTION TYPE ONLY")

        print("\nExisting labels:")
        print(f"  Sentiment     : {row['sentiment']}")
        print(f"  Actionability : {row['actionability']}")
        print(f"  Toxicity      : {row['toxicity']}")

        print(
            "\nQUESTION TYPE:"
            "\n1 = NOT_QUESTION"
            "\n2 = INFORMATION_SEEKING"
            "\n3 = ACTION_REQUEST"
            "\n4 = RHETORICAL"
        )

    else:
        print("FORMAT: [Sentiment] [Actionability] [Toxicity] [Question Type]")

        print(
            "Example: 3 2 1 1 = "
            "NEGATIVE / IMPLICITLY_ACTIONABLE / "
            "NON_TOXIC / NOT_QUESTION"
        )

    print("-" * 80)


def print_selected_labels(
    sentiment: str,
    actionability: str,
    toxicity: str,
    question_type: str,
) -> None:

    print("\nSelected:")

    print(f"  Sentiment     : {sentiment}")
    print(f"  Actionability : {actionability}")
    print(f"  Toxicity      : {toxicity}")
    print(f"  Question Type : {question_type}")


# ============================================================
# MAIN
# ============================================================


def main():
    global df
    global dirty

    if not ANNOTATION_FILE.exists():
        raise FileNotFoundError(f"Annotation file not found:\n{ANNOTATION_FILE}")

    df = pd.read_csv(
        ANNOTATION_FILE,
        dtype=str,
        keep_default_na=False,
    )

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    df = normalize_empty_columns(df)

    validate_dataset(df)

    total = len(df)
    completed = completed_count()
    original_completed = original_labels_count()
    question_completed = question_type_count()

    print("\n" + "=" * 80)
    print("TURKISH COMMENT INTELLIGENCE")
    print("FAST MANUAL ANNOTATION TOOL - v1.2")
    print("=" * 80)

    print(f"\nDataset: {ANNOTATION_FILE}")
    print(f"Total comments          : {total:,}")
    print(f"Original 3 labels       : {original_completed:,}")
    print(f"Question Type completed : {question_completed:,}")
    print(f"Fully completed         : {completed:,}")
    print(f"Remaining               : {total - completed:,}")
    print(f"Progress                : {(completed / total) * 100:.2f}%")

    show_help()

    unfinished_indices = [
        index for index, row in df.iterrows() if not is_completed(row)
    ]

    if not unfinished_indices:
        print("\nAll comments are already annotated.")
        return

    annotations_since_save = 0

    for index in unfinished_indices:
        row = df.loc[index]

        # If the original three labels already exist,
        # preserve them and ask only for Question Type.
        question_only = has_original_labels(row)

        print_comment(
            index=index,
            total=total,
            text=row["text"],
            question_only=question_only,
            row=row,
        )

        pending_note = ""

        while True:
            if question_only:
                prompt = "\nQuestion Type (1/2/3/4) [n/s/q/h]: "
            else:
                prompt = "\nLabels (e.g. 3 2 1 1) [n/s/q/h]: "

            user_input = input(prompt).strip().lower()

            if user_input == "q":
                save_dataset()
                print("\nAnnotation session ended.")
                return

            if user_input == "s":
                save_dataset()
                continue

            if user_input == "h":
                show_help()
                continue

            if user_input == "n":
                pending_note = input("\nAnnotation note: ").strip()

                if pending_note:
                    print("[NOTE ADDED]")
                else:
                    print("[NOTE CLEARED]")

                continue

            # ====================================================
            # QUESTION-TYPE-ONLY MODE
            # ====================================================

            if question_only:
                question_type = parse_question_type(user_input)

                if question_type is None:
                    print(
                        "\n[INVALID INPUT]"
                        "\nUse Question Type: 1 / 2 / 3 / 4"
                        "\nOr use n / s / q / h."
                    )
                    continue

                sentiment = row["sentiment"]
                actionability = row["actionability"]
                toxicity = row["toxicity"]

            # ====================================================
            # NORMAL FOUR-LABEL MODE
            # ====================================================

            else:
                labels = parse_labels(user_input)

                if labels is None:
                    print(
                        "\n[INVALID INPUT]"
                        "\nUse format:"
                        "\nsentiment actionability toxicity question_type"
                        "\nExample: 3 2 1 1"
                        "\nOr use n / s / q / h."
                    )
                    continue

                (
                    sentiment,
                    actionability,
                    toxicity,
                    question_type,
                ) = labels

            print_selected_labels(
                sentiment,
                actionability,
                toxicity,
                question_type,
            )

            # Preserve existing original labels when in
            # question-type-only mode.
            if not question_only:
                df.at[index, "sentiment"] = sentiment
                df.at[index, "actionability"] = actionability
                df.at[index, "toxicity"] = toxicity

            df.at[index, "question_type"] = question_type

            if pending_note:
                df.at[index, "annotation_notes"] = pending_note

            dirty = True
            annotations_since_save += 1

            break

        if annotations_since_save >= 10:
            save_dataset()
            annotations_since_save = 0

    save_dataset()

    print("\n" + "=" * 80)
    print("ANNOTATION COMPLETE")
    print("=" * 80)

    print(f"\nAll {total:,} comments have been annotated across all four dimensions.")


if __name__ == "__main__":
    atexit.register(emergency_save)

    try:
        main()

    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt detected.")

        if df is not None:
            save_dataset()

        print("Progress saved. Exiting.")

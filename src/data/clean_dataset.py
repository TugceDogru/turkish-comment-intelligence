import re
from pathlib import Path

import pandas as pd

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = ROOT / "data" / "raw" / "youtube_comments_50k.csv"

OUTPUT_PATH = ROOT / "data" / "processed" / "comments_clean.csv"


# ============================================================
# HELPERS
# ============================================================


def is_url_only(text):
    """
    Returns True if the entire comment consists of a URL.
    """

    text = str(text).strip()

    if not text:
        return False

    pattern = r"^(https?://\S+|www\.\S+)$"

    return bool(re.fullmatch(pattern, text, flags=re.IGNORECASE))


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================


def load_dataset():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input dataset not found:\n{INPUT_PATH}")

    df = pd.read_csv(
        INPUT_PATH,
        dtype={
            "comment_id": "string",
            "video_id": "string",
        },
        keep_default_na=False,
    )

    return df


# ============================================================
# CLEAN DATASET
# ============================================================


def clean_dataset(df):
    original_count = len(df)

    working_df = df.copy()

    # --------------------------------------------------------
    # 1. Remove empty / whitespace-only comments
    # --------------------------------------------------------

    text_stripped = working_df["text"].astype(str).str.strip()

    empty_mask = text_stripped.eq("")

    empty_count = int(empty_mask.sum())

    working_df = working_df.loc[~empty_mask].copy()

    # --------------------------------------------------------
    # 2. Remove URL-only comments
    # --------------------------------------------------------

    url_only_mask = working_df["text"].astype(str).apply(is_url_only)

    url_only_count = int(url_only_mask.sum())

    working_df = working_df.loc[~url_only_mask].copy()

    # --------------------------------------------------------
    # 3. Strip leading/trailing whitespace
    # --------------------------------------------------------

    working_df["text"] = working_df["text"].astype(str).str.strip()

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # We intentionally DO NOT remove:
    #
    # - duplicate text
    # - emoji-only comments
    # - short comments
    # - long comments
    #
    # These may contain useful information for sentiment,
    # actionability and toxicity classification.
    # --------------------------------------------------------

    working_df.reset_index(drop=True, inplace=True)

    final_count = len(working_df)

    removed_count = original_count - final_count

    cleaning_stats = {
        "original_rows": original_count,
        "empty_removed": empty_count,
        "url_only_removed": url_only_count,
        "total_removed": removed_count,
        "final_rows": final_count,
    }

    return working_df, cleaning_stats


# ============================================================
# VALIDATION
# ============================================================


def validate_clean_dataset(df):
    print_section("VALIDATION")

    # Empty text
    empty_count = df["text"].astype(str).str.strip().eq("").sum()

    # URL-only text
    url_only_count = df["text"].astype(str).apply(is_url_only).sum()

    # Duplicate comment IDs
    duplicate_ids = df["comment_id"].duplicated().sum()

    # Unique comment IDs
    unique_ids = df["comment_id"].nunique()

    # Duplicate text
    duplicate_texts = df["text"].duplicated().sum()

    print(f"Rows: {len(df):,}")

    print(f"Unique comment IDs: {unique_ids:,}")

    print(f"Duplicate comment IDs: {duplicate_ids:,}")

    print(f"Empty comments: {empty_count:,}")

    print(f"URL-only comments: {url_only_count:,}")

    print(f"Duplicate text beyond first: {duplicate_texts:,}")

    # Hard validation
    if empty_count != 0:
        raise ValueError("Validation failed: empty comments remain.")

    if url_only_count != 0:
        raise ValueError("Validation failed: URL-only comments remain.")

    if duplicate_ids != 0:
        raise ValueError("Validation failed: duplicate comment IDs detected.")

    if unique_ids != len(df):
        raise ValueError("Validation failed: comment_id is not unique.")

    print("\nValidation passed.")


# ============================================================
# CATEGORY REPORT
# ============================================================


def print_category_report(df):
    print_section("COMMENTS PER CATEGORY AFTER CLEANING")

    counts = df["source_category"].value_counts()

    percentages = (counts / len(df) * 100).round(2)

    report = pd.DataFrame(
        {
            "comments": counts,
            "percentage": percentages,
        }
    )

    print(report.to_string())


# ============================================================
# SAVE
# ============================================================


def save_dataset(df):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")


# ============================================================
# MAIN
# ============================================================


def main():
    print_section("TURKISH COMMENT INTELLIGENCE - DATA CLEANING")

    print(f"Input:\n{INPUT_PATH}")

    print(f"\nOutput:\n{OUTPUT_PATH}")

    # Load
    df = load_dataset()

    print_section("BEFORE CLEANING")

    print(f"Rows: {len(df):,}")

    print(f"Unique videos: {df['video_id'].nunique():,}")

    print(f"Unique comment IDs: {df['comment_id'].nunique():,}")

    # Clean
    clean_df, stats = clean_dataset(df)

    # Report
    print_section("CLEANING REPORT")

    print(f"Original rows: {stats['original_rows']:,}")

    print(f"Empty/whitespace removed: {stats['empty_removed']:,}")

    print(f"URL-only removed: {stats['url_only_removed']:,}")

    print(f"Total removed: {stats['total_removed']:,}")

    print(f"Final rows: {stats['final_rows']:,}")

    # Validate before saving
    validate_clean_dataset(clean_df)

    print_category_report(clean_df)

    # Save
    save_dataset(clean_df)

    print_section("DONE")

    print(f"Clean dataset saved to:\n{OUTPUT_PATH}")

    print(f"\nFinal dataset shape: {clean_df.shape}")

    print("\nRaw dataset was not modified.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

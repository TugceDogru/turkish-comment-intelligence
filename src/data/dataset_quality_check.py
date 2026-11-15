import re
from pathlib import Path

import pandas as pd

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = ROOT / "data" / "raw" / "youtube_comments_50k.csv"


# ============================================================
# SETTINGS
# ============================================================

EXPECTED_COLUMNS = [
    "comment_id",
    "video_id",
    "video_title",
    "text",
    "like_count",
    "published_at",
    "source_category",
    "comment_url",
]

CATEGORY_ORDER = [
    "news",
    "technology",
    "education",
    "entertainment",
    "review",
]


# ============================================================
# HELPERS
# ============================================================


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def is_url_only(text):
    text = str(text).strip()

    if not text:
        return False

    pattern = r"^(https?://\S+|www\.\S+)$"

    return bool(re.fullmatch(pattern, text, flags=re.IGNORECASE))


def is_symbol_or_emoji_only(text):
    """
    Returns True when the comment contains no alphabetic
    or numeric characters.

    Examples:
        ❤
        😂😂😂
        !!!
        👍🔥
    """

    text = str(text).strip()

    if not text:
        return False

    return not any(character.isalnum() for character in text)


# ============================================================
# LOAD DATA
# ============================================================


def load_dataset():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Dataset not found:\n{INPUT_PATH}")

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
# BASIC STRUCTURE
# ============================================================


def analyze_structure(df):
    print_section("1. DATASET STRUCTURE")

    print(f"Shape: {df.shape}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")

    for column in df.columns:
        print(f"  - {column}")

    missing_columns = set(EXPECTED_COLUMNS) - set(df.columns)

    unexpected_columns = set(df.columns) - set(EXPECTED_COLUMNS)

    print(
        "\nMissing expected columns:",
        sorted(missing_columns) if missing_columns else "None",
    )

    print(
        "Unexpected columns:",
        sorted(unexpected_columns) if unexpected_columns else "None",
    )


# ============================================================
# MISSING VALUES
# ============================================================


def analyze_missing_values(df):
    print_section("2. MISSING / EMPTY VALUES")

    print("Missing values (NaN):")

    print(df.isna().sum().to_string())

    print("\nEmpty/whitespace values:")

    for column in df.columns:
        if pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_string_dtype(
            df[column]
        ):
            count = df[column].astype(str).str.strip().eq("").sum()

            print(f"{column}: {count:,}")


# ============================================================
# COMMENT ID QUALITY
# ============================================================


def analyze_comment_ids(df):
    print_section("3. COMMENT ID QUALITY")

    unique_ids = df["comment_id"].nunique()

    duplicate_ids = df["comment_id"].duplicated().sum()

    empty_ids = df["comment_id"].astype(str).str.strip().eq("").sum()

    print(f"Total rows: {len(df):,}")

    print(f"Unique comment IDs: {unique_ids:,}")

    print(f"Duplicate comment IDs: {duplicate_ids:,}")

    print(f"Empty comment IDs: {empty_ids:,}")


# ============================================================
# CATEGORY DISTRIBUTION
# ============================================================


def analyze_categories(df):
    print_section("4. CATEGORY DISTRIBUTION")

    counts = df["source_category"].value_counts().reindex(CATEGORY_ORDER, fill_value=0)

    percentages = counts / len(df) * 100

    result = pd.DataFrame({"comments": counts, "percentage": percentages.round(2)})

    print(result.to_string())

    print("\nUnique videos per category:")

    video_counts = (
        df.groupby("source_category")["video_id"]
        .nunique()
        .reindex(CATEGORY_ORDER, fill_value=0)
    )

    print(video_counts.to_string())


# ============================================================
# TEXT LENGTH
# ============================================================


def analyze_text_length(df):
    print_section("5. TEXT LENGTH ANALYSIS")

    text = df["text"].astype(str)

    stripped = text.str.strip()

    char_count = stripped.str.len()

    word_count = stripped.apply(lambda value: len(value.split()) if value else 0)

    print("Character count:")

    print(
        char_count.describe(
            percentiles=[
                0.01,
                0.05,
                0.25,
                0.50,
                0.75,
                0.95,
                0.99,
            ]
        )
        .round(2)
        .to_string()
    )

    print("\nWord count:")

    print(
        word_count.describe(
            percentiles=[
                0.01,
                0.05,
                0.25,
                0.50,
                0.75,
                0.95,
                0.99,
            ]
        )
        .round(2)
        .to_string()
    )

    print("\nShort comment counts:")

    print(f"0 characters: {(char_count == 0).sum():,}")

    print(f"<= 2 characters: {(char_count <= 2).sum():,}")

    print(f"<= 5 characters: {(char_count <= 5).sum():,}")

    print(f"<= 10 characters: {(char_count <= 10).sum():,}")


# ============================================================
# SYMBOL / EMOJI COMMENTS
# ============================================================


def analyze_symbol_comments(df):
    print_section("6. EMOJI / SYMBOL-ONLY COMMENTS")

    mask = df["text"].astype(str).apply(is_symbol_or_emoji_only)

    count = mask.sum()

    print(f"Emoji/symbol-only comments: {count:,}")

    print(f"Percentage: {count / len(df) * 100:.2f}%")

    if count > 0:
        print("\nExamples:")

        examples = df.loc[mask, "text"].drop_duplicates().head(20)

        for value in examples:
            print(f"  {repr(value)}")


# ============================================================
# URL ONLY
# ============================================================


def analyze_url_comments(df):
    print_section("7. URL-ONLY COMMENTS")

    mask = df["text"].astype(str).apply(is_url_only)

    count = mask.sum()

    print(f"URL-only comments: {count:,}")

    if count > 0:
        print("\nExamples:")

        examples = df.loc[mask, "text"].head(10)

        for value in examples:
            print(f"  {value}")


# ============================================================
# DUPLICATE TEXT
# ============================================================


def analyze_duplicate_text(df):
    print_section("8. DUPLICATE TEXT ANALYSIS")

    normalized_text = df["text"].astype(str).str.strip()

    duplicate_mask = normalized_text.duplicated(keep=False) & normalized_text.ne("")

    duplicate_rows = duplicate_mask.sum()

    repeated_groups = normalized_text[duplicate_mask].value_counts()

    extra_duplicate_rows = normalized_text[normalized_text.ne("")].duplicated().sum()

    print(f"Rows belonging to repeated-text groups: {duplicate_rows:,}")

    print(f"Duplicate rows beyond first occurrence: {extra_duplicate_rows:,}")

    print(f"Unique repeated text values: {len(repeated_groups):,}")

    if not repeated_groups.empty:
        print("\nTop 20 repeated texts:")

        for text, count in repeated_groups.head(20).items():
            display_text = text.replace("\n", " ")

            if len(display_text) > 100:
                display_text = display_text[:100] + "..."

            print(f"{count:>5}x | {repr(display_text)}")


# ============================================================
# DUPLICATES ACROSS VIDEOS
# ============================================================


def analyze_cross_video_duplicates(df):
    print_section("9. CROSS-VIDEO DUPLICATE TEXT")

    temp = df.copy()

    temp["normalized_text"] = temp["text"].astype(str).str.strip()

    temp = temp[temp["normalized_text"].ne("")]

    video_counts = temp.groupby("normalized_text")["video_id"].nunique()

    cross_video = video_counts[video_counts > 1].sort_values(ascending=False)

    print(f"Text values appearing in multiple videos: {len(cross_video):,}")

    if not cross_video.empty:
        print("\nTop 20 by number of videos:")

        for text, video_count in cross_video.head(20).items():
            row_count = temp[temp["normalized_text"] == text].shape[0]

            display_text = text.replace("\n", " ")

            if len(display_text) > 100:
                display_text = display_text[:100] + "..."

            print(
                f"{video_count:>3} videos | {row_count:>4} rows | {repr(display_text)}"
            )


# ============================================================
# SHORTEST / LONGEST EXAMPLES
# ============================================================


def analyze_examples(df):
    print_section("10. SHORTEST AND LONGEST EXAMPLES")

    temp = df.copy()

    temp["char_count"] = temp["text"].astype(str).str.strip().str.len()

    print("\n20 shortest comments:")

    shortest = temp.sort_values("char_count", ascending=True)[
        ["source_category", "char_count", "text"]
    ].head(20)

    for _, row in shortest.iterrows():
        print(
            f"[{row['source_category']}] "
            f"{row['char_count']} chars | "
            f"{repr(row['text'])}"
        )

    print("\n20 longest comments:")

    longest = temp.sort_values("char_count", ascending=False)[
        ["source_category", "char_count", "text"]
    ].head(20)

    for _, row in longest.iterrows():
        text = str(row["text"]).replace("\n", " ")

        preview = text[:250] + "..." if len(text) > 250 else text

        print(f"[{row['source_category']}] {row['char_count']} chars | {repr(preview)}")


# ============================================================
# LIKE COUNT
# ============================================================


def analyze_likes(df):
    print_section("11. LIKE COUNT")

    likes = pd.to_numeric(df["like_count"], errors="coerce")

    print(
        likes.describe(
            percentiles=[
                0.50,
                0.75,
                0.90,
                0.95,
                0.99,
            ]
        )
        .round(2)
        .to_string()
    )


# ============================================================
# SUMMARY
# ============================================================


def print_summary(df):
    print_section("12. QUALITY CHECK SUMMARY")

    text = df["text"].astype(str).str.strip()

    empty_text = text.eq("").sum()

    duplicate_ids = df["comment_id"].duplicated().sum()

    duplicate_text = text[text.ne("")].duplicated().sum()

    symbol_only = text.apply(is_symbol_or_emoji_only).sum()

    url_only = text.apply(is_url_only).sum()

    print(f"Total rows: {len(df):,}")

    print(f"Unique videos: {df['video_id'].nunique():,}")

    print(f"Empty text: {empty_text:,}")

    print(f"Duplicate comment IDs: {duplicate_ids:,}")

    print(f"Duplicate text beyond first: {duplicate_text:,}")

    print(f"Emoji/symbol-only: {symbol_only:,}")

    print(f"URL-only: {url_only:,}")

    print("\nNo rows were modified or deleted.")


# ============================================================
# MAIN
# ============================================================


def main():
    print_section("TURKISH COMMENT INTELLIGENCE - DATA QUALITY CHECK")

    print(f"Input:\n{INPUT_PATH}")

    df = load_dataset()

    analyze_structure(df)

    analyze_missing_values(df)

    analyze_comment_ids(df)

    analyze_categories(df)

    analyze_text_length(df)

    analyze_symbol_comments(df)

    analyze_url_comments(df)

    analyze_duplicate_text(df)

    analyze_cross_video_duplicates(df)

    analyze_examples(df)

    analyze_likes(df)

    print_summary(df)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

import re
from pathlib import Path

import pandas as pd

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = ROOT / "data" / "processed" / "comments_clean.csv"

OUTPUT_PATH = ROOT / "data" / "annotated" / "annotation_dataset_5000.csv"


# ============================================================
# SETTINGS
# ============================================================

RANDOM_STATE = 42

CATEGORIES = [
    "news",
    "technology",
    "education",
    "entertainment",
    "review",
]

SAMPLES_PER_CATEGORY = 1000
TOTAL_TARGET = len(CATEGORIES) * SAMPLES_PER_CATEGORY

# We do not want very short / emoji-only comments
# to dominate the manually annotated dataset.
MAX_SYMBOL_ONLY_PER_CATEGORY = 50
MAX_VERY_SHORT_PER_CATEGORY = 100

# Very short = 5 or fewer characters
VERY_SHORT_THRESHOLD = 5


# ============================================================
# HELPERS
# ============================================================


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def normalize_text(text):
    """
    Normalization is used ONLY for duplicate detection.

    The original comment text is preserved in the output.
    """

    text = str(text)

    text = text.strip()

    text = re.sub(r"\s+", " ", text)

    return text.casefold()


def is_symbol_or_emoji_only(text):
    """
    True when a comment contains no alphabetic
    or numeric characters.
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
        raise FileNotFoundError(f"Clean dataset not found:\n{INPUT_PATH}")

    df = pd.read_csv(
        INPUT_PATH,
        dtype={
            "comment_id": "string",
            "video_id": "string",
        },
        keep_default_na=False,
    )

    required_columns = {
        "comment_id",
        "video_id",
        "video_title",
        "text",
        "source_category",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    return df


# ============================================================
# PREPARE SAMPLING DATA
# ============================================================


def prepare_dataset(df):
    df = df.copy()

    df["normalized_text"] = df["text"].apply(normalize_text)

    df["character_count"] = df["text"].astype(str).str.strip().str.len()

    df["symbol_only"] = df["text"].apply(is_symbol_or_emoji_only)

    df["very_short"] = df["character_count"] <= VERY_SHORT_THRESHOLD

    return df


# ============================================================
# REMOVE NORMALIZED TEXT DUPLICATES
# ============================================================


def remove_text_duplicates(df):
    """
    For annotation sampling only.

    The clean 50K dataset is NOT modified.

    We keep one instance of each normalized text so annotation
    effort is not wasted labeling identical comments repeatedly.
    """

    before = len(df)

    df = (
        df.sample(frac=1, random_state=RANDOM_STATE)
        .drop_duplicates(subset=["normalized_text"], keep="first")
        .copy()
    )

    removed = before - len(df)

    print(f"Repeated normalized texts excluded from sampling pool: {removed:,}")

    return df


# ============================================================
# BALANCED VIDEO SAMPLING
# ============================================================


def balanced_video_sample(pool, target, random_state):
    """
    Samples comments in rounds across videos.

    This prevents a small number of videos from dominating
    the annotation dataset.

    Example:
        round 1 -> one comment from each video
        round 2 -> one more comment from each video
        ...
    """

    if target <= 0:
        return pool.iloc[0:0].copy()

    if len(pool) < target:
        raise ValueError(
            f"Sampling pool contains only {len(pool)} rows "
            f"but {target} rows were requested."
        )

    working = pool.sample(frac=1, random_state=random_state).copy()

    video_groups = {}

    for video_id, group in working.groupby("video_id", sort=False):
        video_groups[video_id] = group.sample(
            frac=1, random_state=random_state
        ).index.tolist()

    video_ids = list(video_groups.keys())

    selected_indices = []

    round_number = 0

    while len(selected_indices) < target:
        active_videos = [video_id for video_id in video_ids if video_groups[video_id]]

        if not active_videos:
            break

        order = (
            pd.Series(active_videos)
            .sample(frac=1, random_state=(random_state + round_number))
            .tolist()
        )

        for video_id in order:
            if len(selected_indices) >= target:
                break

            if video_groups[video_id]:
                selected_indices.append(video_groups[video_id].pop())

        round_number += 1

    if len(selected_indices) < target:
        raise ValueError(f"Could select only {len(selected_indices)} / {target} rows.")

    return working.loc[selected_indices].copy()


# ============================================================
# CATEGORY SAMPLING
# ============================================================


def sample_category(category_df, category, category_seed):
    print(f"\nSampling category: {category}")

    print(f"Available unique-text comments: {len(category_df):,}")

    # --------------------------------------------------------
    # Separate symbol-only comments
    # --------------------------------------------------------

    symbol_pool = category_df[category_df["symbol_only"]].copy()

    normal_pool = category_df[~category_df["symbol_only"]].copy()

    symbol_target = min(MAX_SYMBOL_ONLY_PER_CATEGORY, len(symbol_pool))

    selected_symbol = balanced_video_sample(
        symbol_pool, symbol_target, category_seed + 1
    )

    # --------------------------------------------------------
    # Very short textual comments
    # --------------------------------------------------------

    short_pool = normal_pool[normal_pool["very_short"]].copy()

    short_target = min(MAX_VERY_SHORT_PER_CATEGORY, len(short_pool))

    selected_short = balanced_video_sample(short_pool, short_target, category_seed + 2)

    # --------------------------------------------------------
    # Main textual comments
    # --------------------------------------------------------

    excluded_indices = selected_short.index.union(selected_symbol.index)

    main_pool = category_df[
        ~category_df.index.isin(excluded_indices)
        & ~category_df["symbol_only"]
        & ~category_df["very_short"]
    ].copy()

    remaining_target = SAMPLES_PER_CATEGORY - len(selected_symbol) - len(selected_short)

    selected_main = balanced_video_sample(
        main_pool, remaining_target, category_seed + 3
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    selected = pd.concat(
        [
            selected_symbol,
            selected_short,
            selected_main,
        ],
        ignore_index=False,
    )

    # Final shuffle inside category
    selected = selected.sample(frac=1, random_state=category_seed + 4).copy()

    if len(selected) != SAMPLES_PER_CATEGORY:
        raise ValueError(
            f"{category}: expected {SAMPLES_PER_CATEGORY} rows, got {len(selected)}."
        )

    print(f"Selected: {len(selected):,}")

    print(f"Symbol-only selected: {selected['symbol_only'].sum():,}")

    print(f"Very short selected: {selected['very_short'].sum():,}")

    print(f"Videos represented: {selected['video_id'].nunique():,}")

    return selected


# ============================================================
# CREATE SAMPLE
# ============================================================


def create_sample(df):
    print_section("PREPARING SAMPLING POOL")

    prepared = prepare_dataset(df)

    prepared = remove_text_duplicates(prepared)

    selected_parts = []

    for index, category in enumerate(CATEGORIES):
        category_df = prepared[prepared["source_category"] == category].copy()

        if len(category_df) < SAMPLES_PER_CATEGORY:
            raise ValueError(
                f"Not enough comments for "
                f"category '{category}'. "
                f"Available: {len(category_df):,}"
            )

        selected = sample_category(
            category_df=category_df,
            category=category,
            category_seed=(RANDOM_STATE + (index * 100)),
        )

        selected_parts.append(selected)

    sample = pd.concat(selected_parts, ignore_index=True)

    # Final dataset shuffle
    sample = sample.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    return sample


# ============================================================
# BUILD ANNOTATION FILE
# ============================================================


def build_annotation_dataset(sample):
    output = sample[
        [
            "comment_id",
            "video_id",
            "video_title",
            "text",
            "source_category",
        ]
    ].copy()

    output["sentiment"] = ""
    output["actionability"] = ""
    output["toxicity"] = ""
    output["annotation_notes"] = ""

    return output


# ============================================================
# VALIDATION
# ============================================================


def validate_sample(sample, annotation_df):
    print_section("ANNOTATION SAMPLE VALIDATION")

    print(f"Total rows: {len(annotation_df):,}")

    print(f"Unique comment IDs: {annotation_df['comment_id'].nunique():,}")

    duplicate_ids = annotation_df["comment_id"].duplicated().sum()

    print(f"Duplicate comment IDs: {duplicate_ids:,}")

    normalized = annotation_df["text"].apply(normalize_text)

    duplicate_texts = normalized.duplicated().sum()

    print(f"Duplicate normalized texts: {duplicate_texts:,}")

    print(f"Unique videos represented: {annotation_df['video_id'].nunique():,}")

    print(f"Symbol-only comments: {sample['symbol_only'].sum():,}")

    print(
        f"Very short comments "
        f"(<= {VERY_SHORT_THRESHOLD} chars): "
        f"{sample['very_short'].sum():,}"
    )

    print("\nComments per category:")

    print(
        annotation_df["source_category"].value_counts().reindex(CATEGORIES).to_string()
    )

    print("\nVideos represented per category:")

    print(
        annotation_df.groupby("source_category")["video_id"]
        .nunique()
        .reindex(CATEGORIES)
        .to_string()
    )

    print("\nComments per video statistics:")

    comments_per_video = annotation_df.groupby("video_id").size()

    print(comments_per_video.describe().round(2).to_string())

    print("\nCharacter length statistics:")

    char_count = annotation_df["text"].astype(str).str.len()

    print(
        char_count.describe(
            percentiles=[
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

    # --------------------------------------------------------
    # Hard validation
    # --------------------------------------------------------

    if len(annotation_df) != TOTAL_TARGET:
        raise ValueError(f"Expected {TOTAL_TARGET:,} rows, got {len(annotation_df):,}.")

    if duplicate_ids != 0:
        raise ValueError("Duplicate comment IDs detected.")

    if duplicate_texts != 0:
        raise ValueError("Duplicate normalized texts detected.")

    category_counts = annotation_df["source_category"].value_counts()

    for category in CATEGORIES:
        count = category_counts.get(category, 0)

        if count != SAMPLES_PER_CATEGORY:
            raise ValueError(
                f"{category}: expected {SAMPLES_PER_CATEGORY}, got {count}."
            )

    print("\nValidation passed.")


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
    print_section("TURKISH COMMENT INTELLIGENCE - ANNOTATION SAMPLE")

    print(f"Input:\n{INPUT_PATH}")

    print(f"\nOutput:\n{OUTPUT_PATH}")

    df = load_dataset()

    print_section("SOURCE DATASET")

    print(f"Rows: {len(df):,}")

    print(f"Unique videos: {df['video_id'].nunique():,}")

    print("\nComments per category:")

    print(df["source_category"].value_counts().reindex(CATEGORIES).to_string())

    sample = create_sample(df)

    annotation_df = build_annotation_dataset(sample)

    validate_sample(sample, annotation_df)

    save_dataset(annotation_df)

    print_section("DONE")

    print("Annotation dataset saved to:")

    print(OUTPUT_PATH)

    print(f"\nFinal shape: {annotation_df.shape}")

    print("\nThe source clean dataset was not modified.")


if __name__ == "__main__":
    main()

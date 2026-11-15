from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_INPUT = (
    PROJECT_ROOT / "data" / "annotated" / "annotation_dataset_5000_reviewed.csv"
)

DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "splits"
DEFAULT_REPORTS = PROJECT_ROOT / "reports" / "splits"

LABELS = {
    "sentiment": ["POSITIVE", "NEUTRAL", "NEGATIVE", "MIXED"],
    "actionability": [
        "NOT_ACTIONABLE",
        "IMPLICITLY_ACTIONABLE",
        "EXPLICITLY_ACTIONABLE",
    ],
    "toxicity": ["NON_TOXIC", "TOXIC"],
    "question_type": [
        "NOT_QUESTION",
        "INFORMATION_SEEKING",
        "ACTION_REQUEST",
        "RHETORICAL",
    ],
}

SPLIT_NAMES = ["train", "val", "test"]
TARGET_RATIOS = np.array([0.70, 0.15, 0.15])

SEED = 42
N_TRIALS = 5000


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype={
            "comment_id": "string",
            "video_id": "string",
        },
        keep_default_na=False,
    )

    required = {
        "comment_id",
        "video_id",
        "text",
        *LABELS.keys(),
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("Dataset is empty.")

    for column in ["comment_id", "video_id", "text"]:
        if df[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Empty values found in {column}")

    if df["comment_id"].duplicated().any():
        raise ValueError("Duplicate comment IDs found.")

    if df["video_id"].nunique() < 3:
        raise ValueError("At least 3 distinct videos are required.")

    for task, valid_labels in LABELS.items():
        invalid = set(df[task]) - set(valid_labels)

        if invalid:
            raise ValueError(f"Invalid {task} labels: {sorted(invalid)}")

    return df


def build_group_statistics(df: pd.DataFrame):
    """
    Create one row per video.

    Each video stores:
    - Number of comments
    - Number of examples of every label
    """
    videos = sorted(df["video_id"].unique())

    feature_names = ["total"]

    for task, labels in LABELS.items():
        for label in labels:
            feature_names.append(f"{task}::{label}")

    matrix = np.zeros(
        (len(videos), len(feature_names)),
        dtype=np.int64,
    )

    video_to_index = {video: i for i, video in enumerate(videos)}

    for video, group in df.groupby("video_id"):
        i = video_to_index[video]

        matrix[i, 0] = len(group)

        column = 1

        for task, labels in LABELS.items():
            counts = group[task].value_counts()

            for label in labels:
                matrix[i, column] = int(counts.get(label, 0))
                column += 1

    return videos, matrix, feature_names


def candidate_assignment(
    rng: np.random.Generator,
    matrix: np.ndarray,
) -> np.ndarray:
    """
    Assign whole videos to train, val and test.

    The assignment targets comment counts rather
    than simply the number of videos.
    """
    n_groups = len(matrix)
    order = rng.permutation(n_groups)

    total = matrix[:, 0].sum()
    targets = TARGET_RATIOS * total

    assignment = np.full(n_groups, -1, dtype=int)
    current = np.zeros(3, dtype=np.int64)

    # Randomize which holdout split is filled first.
    holdouts = [1, 2]
    rng.shuffle(holdouts)

    for split_index in holdouts:
        for group_index in order:
            if assignment[group_index] != -1:
                continue

            if current[split_index] >= targets[split_index]:
                break

            assignment[group_index] = split_index
            current[split_index] += matrix[group_index, 0]

    assignment[assignment == -1] = 0

    return assignment


def evaluate_assignment(
    assignment: np.ndarray,
    matrix: np.ndarray,
) -> tuple[float, np.ndarray] | None:

    split_counts = np.stack([matrix[assignment == i].sum(axis=0) for i in range(3)])

    # No empty split.
    if (split_counts[:, 0] == 0).any():
        return None

    # Every class must appear in every split.
    if (split_counts[:, 1:] == 0).any():
        return None

    total_counts = matrix.sum(axis=0)

    # Penalize deviations from target sizes.
    actual_ratios = split_counts[:, 0] / total_counts[0]

    size_error = np.abs(actual_ratios - TARGET_RATIOS).sum()

    # Compare per-class proportions across splits.
    # Each class gets equal importance, including
    # rare classes.
    class_ratios = split_counts[:, 1:] / total_counts[None, 1:]

    class_error = np.abs(class_ratios - TARGET_RATIOS[:, None]).mean()

    # Additional penalty for very small holdout
    # class counts. This is a preference, not a
    # hard constraint.
    rare_penalty = (
        np.maximum(
            0,
            3 - split_counts[1:, 1:],
        ).sum()
        * 0.005
    )

    score = 2.0 * size_error + class_error + rare_penalty

    return float(score), split_counts


def find_best_split(
    matrix: np.ndarray,
    seed: int,
    trials: int,
):
    rng = np.random.default_rng(seed)

    best_assignment = None
    best_score = float("inf")
    best_counts = None

    for _ in range(trials):
        assignment = candidate_assignment(rng, matrix)

        evaluated = evaluate_assignment(assignment, matrix)

        if evaluated is None:
            continue

        score, counts = evaluated

        if score < best_score:
            best_score = score
            best_assignment = assignment.copy()
            best_counts = counts.copy()

    if best_assignment is None:
        raise RuntimeError(
            "Could not find a group-aware split "
            "containing every class in every subset. "
            "Inspect rare classes across video IDs. "
            "Do not silently fall back to a "
            "comment-level random split."
        )

    return best_assignment, best_score, best_counts


def make_dataframes(
    df: pd.DataFrame,
    videos: list,
    assignment: np.ndarray,
) -> dict[str, pd.DataFrame]:

    video_to_split = {
        video: SPLIT_NAMES[int(split_index)]
        for video, split_index in zip(videos, assignment)
    }

    split_labels = df["video_id"].map(video_to_split)

    return {
        name: df.loc[split_labels == name].copy().reset_index(drop=True)
        for name in SPLIT_NAMES
    }


def validate_splits(
    source: pd.DataFrame,
    splits: dict[str, pd.DataFrame],
) -> None:

    # Check complete and disjoint comment coverage.
    all_ids = []

    video_sets = []

    for name in SPLIT_NAMES:
        part = splits[name]

        if part.empty:
            raise ValueError(f"{name} split is empty.")

        all_ids.extend(part["comment_id"].tolist())

        video_sets.append(set(part["video_id"]))

        for task, labels in LABELS.items():
            missing = set(labels) - set(part[task])

            if missing:
                raise ValueError(f"{name}: missing {task} classes: {sorted(missing)}")

    if len(all_ids) != len(source):
        raise ValueError("Total split rows do not match source.")

    if len(set(all_ids)) != len(all_ids):
        raise ValueError("Comment leakage detected.")

    if set(all_ids) != set(source["comment_id"]):
        raise ValueError("Some source comments are missing.")

    for i in range(3):
        for j in range(i + 1, 3):
            overlap = video_sets[i] & video_sets[j]

            if overlap:
                raise ValueError(
                    f"Video leakage detected: {len(overlap)} shared videos."
                )


def create_reports(
    splits: dict[str, pd.DataFrame],
    score: float,
    seed: int,
    trials: int,
):
    total = sum(len(part) for part in splits.values())

    summary = {
        "strategy": "group_aware_video_split",
        "group_column": "video_id",
        "seed": seed,
        "trials": trials,
        "selection_score": round(score, 6),
        "target_ratios": dict(zip(SPLIT_NAMES, TARGET_RATIOS.tolist())),
        "splits": {},
        "class_distributions": {},
    }

    records = []

    for name, part in splits.items():
        summary["splits"][name] = {
            "comments": len(part),
            "ratio": round(len(part) / total, 4),
            "unique_videos": int(part["video_id"].nunique()),
        }

        summary["class_distributions"][name] = {}

        for task, labels in LABELS.items():
            counts = part[task].value_counts().reindex(labels, fill_value=0)

            summary["class_distributions"][name][task] = counts.astype(int).to_dict()

            for label, count in counts.items():
                records.append(
                    {
                        "split": name,
                        "task": task,
                        "label": label,
                        "count": int(count),
                        "percentage": round(100 * count / len(part), 2),
                    }
                )

    return summary, pd.DataFrame(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create leakage-safe video splits")

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--report-dir",
        type=Path,
        default=DEFAULT_REPORTS,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
    )

    parser.add_argument(
        "--trials",
        type=int,
        default=N_TRIALS,
    )

    args = parser.parse_args()

    if args.trials < 1:
        raise ValueError("--trials must be at least 1.")

    df = load_dataset(args.input)

    videos, matrix, _ = build_group_statistics(df)

    assignment, score, _ = find_best_split(
        matrix,
        seed=args.seed,
        trials=args.trials,
    )

    splits = make_dataframes(df, videos, assignment)

    validate_splits(df, splits)

    summary, distributions = create_reports(
        splits,
        score,
        args.seed,
        args.trials,
    )

    output_files = [args.output_dir / f"{name}.csv" for name in SPLIT_NAMES]

    report_files = [
        args.report_dir / "split_summary.json",
        args.report_dir / "class_distributions.csv",
    ]

    all_outputs = output_files + report_files

    if len({path.resolve() for path in all_outputs}) != len(all_outputs):
        raise ValueError("Output paths must be distinct.")

    if any(path.resolve() == args.input.resolve() for path in all_outputs):
        raise ValueError("Cannot overwrite source dataset.")

    existing = [str(path) for path in all_outputs if path.exists()]

    if existing:
        raise FileExistsError(
            "Outputs already exist; refusing to overwrite:\n" + "\n".join(existing)
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    args.report_dir.mkdir(parents=True, exist_ok=True)

    for name, path in zip(SPLIT_NAMES, output_files):
        splits[name].to_csv(
            path,
            index=False,
            encoding="utf-8-sig",
        )

    summary_path = report_files[0]

    summary_path.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    distributions.to_csv(
        report_files[1],
        index=False,
        encoding="utf-8-sig",
    )

    print("=" * 60)
    print("TRAIN / VALIDATION / TEST SPLIT")
    print("=" * 60)

    print(f"Total comments: {len(df)}")
    print(f"Total videos: {len(videos)}")
    print(f"Best split score: {score:.6f}")

    print("\nSplit distribution:")

    for name in SPLIT_NAMES:
        info = summary["splits"][name]

        print(
            f"  {name.upper()}: "
            f"{info['comments']} comments "
            f"({info['ratio'] * 100:.2f}%), "
            f"{info['unique_videos']} videos"
        )

    print("\nRare class coverage:")

    rare_classes = [
        ("sentiment", "MIXED"),
        ("actionability", "IMPLICITLY_ACTIONABLE"),
        ("toxicity", "TOXIC"),
        ("question_type", "ACTION_REQUEST"),
    ]

    for task, label in rare_classes:
        counts = [
            summary["class_distributions"][name][task][label] for name in SPLIT_NAMES
        ]

        print(
            f"  {task} / {label}: train={counts[0]}, val={counts[1]}, test={counts[2]}"
        )

    print("\nValidation checks passed:")
    print("  No duplicate comment IDs")
    print("  No video overlap between splits")
    print("  All comments assigned exactly once")
    print("  Every label present in all splits")

    print("\nGenerated files:")
    for path in all_outputs:
        print(f"  {path}")

    print("\nSplit completed successfully.")


if __name__ == "__main__":
    main()

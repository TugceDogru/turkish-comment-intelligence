from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_INPUT = (
    PROJECT_ROOT / "data" / "annotated" / "annotation_dataset_5000_reviewed.csv"
)

DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "eda"

LABEL_COLUMNS = [
    "sentiment",
    "actionability",
    "toxicity",
    "question_type",
]

VALID_LABELS = {
    "sentiment": [
        "POSITIVE",
        "NEUTRAL",
        "NEGATIVE",
        "MIXED",
    ],
    "actionability": [
        "NOT_ACTIONABLE",
        "IMPLICITLY_ACTIONABLE",
        "EXPLICITLY_ACTIONABLE",
    ],
    "toxicity": [
        "NON_TOXIC",
        "TOXIC",
    ],
    "question_type": [
        "NOT_QUESTION",
        "INFORMATION_SEEKING",
        "ACTION_REQUEST",
        "RHETORICAL",
    ],
}

COLORS = {
    "sentiment": "#457B9D",
    "actionability": "#2A9D8F",
    "toxicity": "#E76F51",
    "question_type": "#8E6CBE",
}


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype={"comment_id": "string"},
        keep_default_na=False,
    )

    required = {
        "comment_id",
        "text",
        *LABEL_COLUMNS,
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("Dataset is empty.")

    if df["comment_id"].duplicated().any():
        raise ValueError("Duplicate comment IDs detected.")

    if df["comment_id"].str.strip().eq("").any():
        raise ValueError("Empty comment IDs detected.")

    if df["text"].astype(str).str.strip().eq("").any():
        raise ValueError("Empty comment texts detected.")

    for column, labels in VALID_LABELS.items():
        invalid = set(df[column]) - set(labels)

        if invalid:
            raise ValueError(f"Invalid labels in {column}: {sorted(invalid)}")

    return df


def save_json(data: dict, path: Path) -> None:
    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def save_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(
        path,
        dpi=180,
        bbox_inches="tight",
    )
    plt.close()


def dataset_overview(df: pd.DataFrame) -> dict:
    overview = {
        "total_comments": int(len(df)),
        "unique_comment_ids": int(df["comment_id"].nunique()),
        "unique_texts": int(df["text"].nunique()),
        "duplicate_texts": int(df["text"].duplicated().sum()),
    }

    if "video_id" in df.columns:
        overview["unique_videos"] = int(df["video_id"].nunique())

    if "source_category" in df.columns:
        overview["source_categories"] = df["source_category"].value_counts().to_dict()

    return overview


def analyze_label_distribution(
    df: pd.DataFrame,
    output_dir: Path,
) -> dict:

    distributions = {}

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    for ax, column in zip(axes.flat, LABEL_COLUMNS):
        counts = (
            df[column]
            .value_counts()
            .reindex(
                VALID_LABELS[column],
                fill_value=0,
            )
        )

        percentages = (counts / len(df) * 100).round(2)

        distribution = pd.DataFrame(
            {
                "label": counts.index,
                "count": counts.values,
                "percentage": percentages.values,
            }
        )

        distribution.to_csv(
            output_dir / f"{column}_distribution.csv",
            index=False,
            encoding="utf-8-sig",
        )

        distributions[column] = {
            label: {
                "count": int(counts[label]),
                "percentage": float(percentages[label]),
            }
            for label in counts.index
        }

        bars = ax.bar(
            counts.index,
            counts.values,
            color=COLORS[column],
        )

        ax.set_title(column.replace("_", " ").title())
        ax.set_ylabel("Number of comments")
        ax.tick_params(
            axis="x",
            labelrotation=20,
        )

        for bar, count in zip(bars, counts.values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                str(count),
                ha="center",
                va="bottom",
                fontsize=9,
            )

    save_figure(output_dir / "label_distributions.png")

    return distributions


def analyze_text_lengths(
    df: pd.DataFrame,
    output_dir: Path,
) -> dict:

    lengths = pd.DataFrame(
        {
            "comment_id": df["comment_id"],
            "char_length": (df["text"].astype(str).str.len()),
            "word_count": (df["text"].astype(str).str.split().str.len()),
        }
    )

    lengths.to_csv(
        output_dir / "text_lengths.csv",
        index=False,
        encoding="utf-8-sig",
    )

    statistics = {}

    for column in ["char_length", "word_count"]:
        series = lengths[column]

        statistics[column] = {
            "mean": round(float(series.mean()), 2),
            "median": float(series.median()),
            "std": round(float(series.std(ddof=0)), 2),
            "min": int(series.min()),
            "max": int(series.max()),
            "p90": float(series.quantile(0.90)),
            "p95": float(series.quantile(0.95)),
            "p99": float(series.quantile(0.99)),
        }

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, column, title in [
        (
            axes[0],
            "char_length",
            "Comment Character Length",
        ),
        (
            axes[1],
            "word_count",
            "Comment Word Count",
        ),
    ]:
        series = lengths[column]

        # Limit only the visualization to p99.
        # Full statistics still use all comments.
        upper = max(
            1,
            float(series.quantile(0.99)),
        )

        clipped = series.clip(upper=upper)

        ax.hist(
            clipped,
            bins=40,
            color="#457B9D",
            edgecolor="white",
        )

        ax.set_title(title)
        ax.set_xlabel("Length (values above p99 clipped)")
        ax.set_ylabel("Number of comments")

    save_figure(output_dir / "text_length_distributions.png")

    return statistics


def analyze_categories(
    df: pd.DataFrame,
    output_dir: Path,
) -> dict:

    if "source_category" not in df.columns:
        print("Skipping category analysis: source_category column not found.")
        return {
            "available": False,
            "reason": "source_category column missing",
        }

    category_counts = (
        df["source_category"]
        .value_counts()
        .rename_axis("source_category")
        .reset_index(name="count")
    )

    category_counts.to_csv(
        output_dir / "category_distribution.csv",
        index=False,
        encoding="utf-8-sig",
    )

    for column in LABEL_COLUMNS:
        counts = pd.crosstab(
            df["source_category"],
            df[column],
        ).reindex(
            columns=VALID_LABELS[column],
            fill_value=0,
        )

        counts.to_csv(
            output_dir / f"category_{column}_counts.csv",
            encoding="utf-8-sig",
        )

        percentages = (
            counts.div(
                counts.sum(axis=1),
                axis=0,
            ).fillna(0)
            * 100
        )

        percentages.to_csv(
            output_dir / f"category_{column}_percentages.csv",
            encoding="utf-8-sig",
        )

        ax = percentages.plot(
            kind="bar",
            stacked=True,
            figsize=(12, 6),
            colormap="tab20",
        )

        ax.set_title(f"{column.title()} by Source Category")
        ax.set_ylabel("Percentage (%)")
        ax.set_xlabel("Source Category")
        ax.legend(
            title=column,
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
        )
        ax.tick_params(
            axis="x",
            labelrotation=25,
        )

        save_figure(output_dir / f"category_{column}.png")

    return {
        "available": True,
        "categories": category_counts.to_dict(orient="records"),
    }


def analyze_label_relationships(
    df: pd.DataFrame,
    output_dir: Path,
) -> None:

    pairs = [
        ("sentiment", "toxicity"),
        ("sentiment", "actionability"),
        ("question_type", "actionability"),
        ("question_type", "toxicity"),
    ]

    for first, second in pairs:
        table = pd.crosstab(
            df[first],
            df[second],
        ).reindex(
            index=VALID_LABELS[first],
            columns=VALID_LABELS[second],
            fill_value=0,
        )

        name = f"{first}_vs_{second}"

        table.to_csv(
            output_dir / f"{name}.csv",
            encoding="utf-8-sig",
        )

        fig, ax = plt.subplots(figsize=(10, 6))

        image = ax.imshow(
            table.values,
            cmap="Blues",
            aspect="auto",
        )

        ax.set_xticks(
            range(len(table.columns)),
            labels=table.columns,
            rotation=30,
            ha="right",
        )

        ax.set_yticks(
            range(len(table.index)),
            labels=table.index,
        )

        ax.set_xlabel(second)
        ax.set_ylabel(first)
        ax.set_title(f"{first} vs {second}")

        for i in range(len(table.index)):
            for j in range(len(table.columns)):
                value = int(table.iloc[i, j])

                ax.text(
                    j,
                    i,
                    str(value),
                    ha="center",
                    va="center",
                    color=("white" if value > table.values.max() / 2 else "black"),
                )

        fig.colorbar(
            image,
            ax=ax,
            label="Number of comments",
        )

        save_figure(output_dir / f"{name}.png")


def analyze_class_imbalance(
    df: pd.DataFrame,
    output_dir: Path,
) -> dict:

    results = {}
    records = []

    for column in LABEL_COLUMNS:
        counts = (
            df[column]
            .value_counts()
            .reindex(
                VALID_LABELS[column],
                fill_value=0,
            )
        )

        nonzero = counts[counts > 0]

        majority = int(counts.max())
        minority = int(nonzero.min())

        imbalance_ratio = round(majority / minority, 2) if minority > 0 else None

        results[column] = {
            "majority_class": str(counts.idxmax()),
            "majority_count": majority,
            "minority_class": str(nonzero.idxmin()),
            "minority_count": minority,
            "imbalance_ratio": imbalance_ratio,
            "missing_classes": [label for label, count in counts.items() if count == 0],
        }

        for label, count in counts.items():
            records.append(
                {
                    "task": column,
                    "label": label,
                    "count": int(count),
                    "percentage": round(
                        count / len(df) * 100,
                        2,
                    ),
                    "inverse_frequency_weight": (
                        round(
                            len(df) / (len(counts) * count),
                            4,
                        )
                        if count > 0
                        else None
                    ),
                }
            )

    pd.DataFrame(records).to_csv(
        output_dir / "class_imbalance.csv",
        index=False,
        encoding="utf-8-sig",
    )

    return results


def create_markdown_report(
    overview: dict,
    distributions: dict,
    lengths: dict,
    imbalance: dict,
    output_dir: Path,
) -> None:

    lines = [
        "# Turkish Comment Intelligence - EDA Report",
        "",
        "## Dataset Overview",
        "",
    ]

    for key, value in overview.items():
        lines.append(f"- **{key}:** {value}")

    lines.extend(
        [
            "",
            "## Label Distributions",
            "",
        ]
    )

    for task, labels in distributions.items():
        lines.extend(
            [
                f"### {task}",
                "",
                "| Label | Count | Percentage |",
                "|---|---:|---:|",
            ]
        )

        for label, values in labels.items():
            lines.append(
                f"| {label} | {values['count']} | {values['percentage']:.2f}% |"
            )

        lines.append("")

    lines.extend(
        [
            "## Text Length Statistics",
            "",
        ]
    )

    for measure, stats in lengths.items():
        lines.append(f"### {measure}")

        for key, value in stats.items():
            lines.append(f"- {key}: {value}")

        lines.append("")

    lines.extend(
        [
            "## Class Imbalance",
            "",
        ]
    )

    for task, values in imbalance.items():
        lines.append(f"### {task}")
        lines.append(
            f"- Majority: {values['majority_class']} ({values['majority_count']})"
        )
        lines.append(
            f"- Minority: {values['minority_class']} ({values['minority_count']})"
        )
        lines.append(f"- Imbalance ratio: {values['imbalance_ratio']}")

        if values["missing_classes"]:
            lines.append("- Missing classes: " + ", ".join(values["missing_classes"]))

        lines.append("")

    lines.extend(
        [
            "## Interpretation Notes",
            "",
            "- These are descriptive dataset statistics.",
            "- Source categories are metadata, not model labels.",
            "- Category comparisons do not imply causation.",
            "- Inverse-frequency weights are diagnostic "
            "estimates, not automatically selected model weights.",
            "- Train/validation/test splitting must happen "
            "before fitting any text vectorizer or model.",
            "- Rare classes require special attention during splitting and evaluation.",
            "",
        ]
    )

    (output_dir / "eda_report.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Turkish Comment Intelligence EDA")

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

    args = parser.parse_args()

    df = load_dataset(args.input)

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 60)
    print("TURKISH COMMENT INTELLIGENCE - EDA")
    print("=" * 60)

    overview = dataset_overview(df)

    distributions = analyze_label_distribution(df, args.output_dir)

    lengths = analyze_text_lengths(df, args.output_dir)

    categories = analyze_categories(df, args.output_dir)

    analyze_label_relationships(df, args.output_dir)

    imbalance = analyze_class_imbalance(df, args.output_dir)

    summary = {
        "overview": overview,
        "label_distributions": distributions,
        "text_lengths": lengths,
        "category_analysis": categories,
        "class_imbalance": imbalance,
    }

    save_json(
        summary,
        args.output_dir / "eda_summary.json",
    )

    create_markdown_report(
        overview,
        distributions,
        lengths,
        imbalance,
        args.output_dir,
    )

    print(f"Total comments: {len(df)}")
    print(f"Unique comment IDs: {df['comment_id'].nunique()}")

    print("\nClass distributions:")

    for column in LABEL_COLUMNS:
        print(f"\n{column.upper()}")

        for label, values in distributions[column].items():
            print(f"  {label}: {values['count']} ({values['percentage']:.2f}%)")

    print("\nClass imbalance ratios:")

    for task, values in imbalance.items():
        print(f"  {task}: {values['imbalance_ratio']}")

    print("\nText length statistics:")
    print(f"  Median words: {lengths['word_count']['median']}")
    print(f"  P95 words: {lengths['word_count']['p95']}")

    print("\nGenerated reports:")
    print(f"  {args.output_dir}")

    print("\nEDA completed successfully.")


if __name__ == "__main__":
    main()

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.models.inference import DEFAULT_MODEL_DIR, TASKS, CommentClassifier

st.set_page_config(
    page_title="Turkish Comment Intelligence",
    page_icon="💬",
    layout="wide",
)

TASK_TITLES = {
    "sentiment": "Sentiment",
    "actionability": "Actionability",
    "toxicity": "Toxicity",
    "question_type": "Question Type",
}

TASK_DESCRIPTIONS = {
    "sentiment": "Overall sentiment expressed in the comment.",
    "actionability": "Whether the comment contains actionable feedback.",
    "toxicity": "Whether the comment contains toxic language.",
    "question_type": "The communicative function of a question.",
}

EXAMPLE_COMMENTS = [
    "Harika bir video olmuş!",
    "Ses kalitesini artırabilir misiniz?",
    "Bu konuyu nasıl öğrenebilirim?",
    "Video çok güzel olmuş ama ses kalitesi biraz kötü.",
]


@st.cache_resource(show_spinner="Loading classification models...")
def load_classifier() -> CommentClassifier:
    """Load trusted local models once per Streamlit process."""
    return CommentClassifier(model_dir=DEFAULT_MODEL_DIR)


def show_prediction(result: dict, index: int | None = None) -> None:
    """Display the four classification results for one comment."""

    if index is not None:
        st.subheader(f"Comment {index}")

    st.markdown(f"**Input:** {result['text']}")

    columns = st.columns(2)

    for task_index, task in enumerate(TASKS):
        prediction = result["predictions"][task]

        with columns[task_index % 2], st.container(border=True):
            st.markdown(f"#### {TASK_TITLES[task]}")
            st.caption(TASK_DESCRIPTIONS[task])

            st.markdown(f"**Prediction:** `{prediction['label']}`")

            probabilities = prediction["probabilities"]

            probability_df = pd.DataFrame(
                {
                    "Class": list(probabilities.keys()),
                    "Probability": list(probabilities.values()),
                }
            ).set_index("Class")

            st.bar_chart(
                probability_df,
                horizontal=True,
                x_label="Model-estimated probability",
                y_label="Class",
            )

            st.caption(
                "Scores are model estimates, not calibrated "
                "confidence or guarantees of correctness."
            )


def main() -> None:
    st.title("💬 Turkish Comment Intelligence")

    st.markdown(
        "Explore four NLP classification tasks for Turkish comments "
        "using locally stored tuned baseline models."
    )

    st.info(
        "Research prototype: predictions are exploratory and must "
        "not be used for automated moderation or high-stakes decisions."
    )

    with st.sidebar:
        st.header("Model Information")
        st.write("**Model family:** Tuned classical ML baselines")
        st.write("**Features:** TF-IDF")
        st.write("**Tasks:** Sentiment, Actionability, Toxicity, Question Type")

        st.divider()

        st.header("Limitations")
        st.write(
            "Minority-class performance is limited, especially "
            "for mixed sentiment, actionable feedback, and toxic comments."
        )
        st.write(
            "Model weights are stored locally and are not included "
            "in the GitHub repository."
        )

    try:
        classifier = load_classifier()
    except (FileNotFoundError, TypeError, ValueError) as exc:
        st.error("Unable to load the local classification models.")
        st.code(str(exc))
        st.info(
            "Place the four trusted .joblib model files inside "
            "models/baseline_tuned/ before starting the demo."
        )
        st.stop()

    mode = st.radio(
        "Analysis mode",
        options=["Single comment", "Multiple comments"],
        horizontal=True,
    )

    if mode == "Single comment":
        example = st.selectbox(
            "Example comments",
            options=["Write my own comment", *EXAMPLE_COMMENTS],
        )

        default_text = "" if example == "Write my own comment" else example

        text = st.text_area(
            "Enter a Turkish comment",
            value=default_text,
            height=120,
            placeholder="Yorumunuzu buraya yazın...",
        )

        if st.button("Analyze Comment", type="primary"):
            try:
                result = classifier.predict(text)
            except (TypeError, ValueError) as exc:
                st.warning(str(exc))
            else:
                st.divider()
                show_prediction(result)

    else:
        st.caption(
            "Enter one comment per line. Each non-empty line "
            "will be analyzed independently."
        )

        text = st.text_area(
            "Enter multiple Turkish comments",
            height=200,
            placeholder=(
                "Harika bir video olmuş!\n"
                "Ses kalitesini artırabilir misiniz?\n"
                "Bu konuyu nasıl öğrenebilirim?"
            ),
        )

        if st.button("Analyze Comments", type="primary"):
            comments = [line.strip() for line in text.splitlines() if line.strip()]

            if not comments:
                st.warning("Please enter at least one comment.")
            elif len(comments) > 50:
                st.warning("Please analyze no more than 50 comments at once.")
            else:
                with st.spinner("Analyzing comments..."):
                    results = classifier.predict_batch(comments)

                st.success(f"Analyzed {len(results)} comments.")

                summary = pd.DataFrame(
                    [
                        {
                            "Comment": result["text"],
                            **{
                                TASK_TITLES[task]: result["predictions"][task]["label"]
                                for task in TASKS
                            },
                        }
                        for result in results
                    ]
                )

                st.subheader("Prediction Summary")
                st.dataframe(summary, width="stretch", hide_index=True)

                st.divider()

                for index, result in enumerate(results, start=1):
                    with st.expander(
                        f"Comment {index}: {result['text'][:70]}",
                        expanded=index == 1,
                    ):
                        show_prediction(result)

    st.divider()

    st.caption(
        "Turkish Comment Intelligence | Research prototype | "
        "Predictions are not manually verified labels."
    )


if __name__ == "__main__":
    main()

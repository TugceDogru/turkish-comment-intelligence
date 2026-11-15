
# Limitations

**Project:** Turkish Comment Intelligence  
**Target release:** v1.0 (in preparation)
**Scope:** Turkish YouTube comment classification

## 1. Overview

Turkish Comment Intelligence v1.0 classifies comments along four dimensions: sentiment, actionability, toxicity, and question type. The system provides a reproducible starting point for analyzing Turkish-language audience feedback, but its outputs should be interpreted with care.

This document separates **measured model weaknesses**, **dataset and evaluation constraints**, and **limitations of the current task definition**. The reported metrics refer to the held-out test set; large-scale inference results are model predictions, not verified labels.

## 2. Evaluation Summary

| Task | Selected Model | Test Accuracy | Test Macro F1 |
|---|---|---:|---:|
| Sentiment | Weighted BERTurk | 0.7215 | 0.5775 |
| Actionability | Weighted BERTurk | 0.9629 | 0.5113 |
| Toxicity | TF-IDF + Logistic Regression | 0.9483 | 0.5332 |
| Question Type | Weighted BERTurk | 0.9390 | 0.6728 |

**Interpretation:** High accuracy does not necessarily indicate reliable recognition of rare classes. Macro F1 and per-class error analysis are particularly important for this imbalanced classification setting.

## 3. Measured Model Limitations

### 3.1 Sentiment

The model has difficulty distinguishing nuanced or conflicting opinions. In particular, the `MIXED` class achieved an F1 score of approximately **0.17** on the test set. A comment may contain both praise and criticism, and these signals are not always captured reliably.

### 3.2 Actionability

Although test accuracy is high, the model did not correctly identify any of the **7 `IMPLICITLY_ACTIONABLE`** examples in the held-out test set. This is a critical limitation because implicit feedback is one of the intended use cases of the project.

The large proportion of `NOT_ACTIONABLE` examples can make overall accuracy appear stronger than minority-class performance warrants.

### 3.3 Toxicity

The toxicity classifier correctly identified only **2 of 23** toxic comments in the held-out test set and produced **18 false positives**. It is therefore **not suitable for autonomous moderation, sanctions, or other consequential decisions**.

The classifier may miss harmful language and may incorrectly flag benign comments. Human review would be required for any practical moderation-oriented workflow.

### 3.4 Question Type

The question-type model performs better overall than the other tasks by macro F1, but recognition remains uneven. The `ACTION_REQUEST` class achieved an F1 score of approximately **0.20** on the test set.

Questions requesting creator actions can be difficult to distinguish from factual information requests, rhetorical questions, and non-interrogative requests.

## 4. Dataset and Evaluation Constraints

- **Limited manually labeled data:** The supervised dataset contains **5,000 annotated comments**, which constrains the number of examples available for uncommon linguistic patterns and minority classes.
- **Class imbalance:** Some classes have very few labeled test examples. Their metrics can be unstable, and small changes in predictions can substantially affect the reported scores.
- **Platform and sampling scope:** The data originates from a selected collection of Turkish YouTube comments. Results should not be generalized to all Turkish social media or to the entire YouTube population without additional validation.
- **Video-grouped evaluation:** Training, validation, and test data were separated by video to reduce leakage from comments belonging to the same video. This is more conservative than a random comment split, but it does not establish robustness across every channel, topic, time period, or domain.
- **Annotation ambiguity:** Sarcasm, implicit requests, short comments, emojis, and mixed opinions can reasonably admit more than one interpretation. The frozen annotation guideline provides a consistent operational definition, not an objective resolution of every ambiguous utterance.
- **No independent external benchmark:** The reported results describe performance on the project's held-out test set, not a separately collected external evaluation dataset.

## 5. Comment-Only Input

The current models use **comment text only**. They do not receive video titles, video categories, transcripts, creator identities, or conversation history as model inputs.

This design avoids relying on unavailable context and is consistent with the v1.0 annotation protocol. However, it limits interpretation of references such as "this part," sarcasm whose meaning depends on the video, and questions about statements made in the content.

Adding context is not a drop-in change to the existing evaluation: the labeling policy and assessment protocol would need to be revisited explicitly.

## 6. Limits of the Four-Task Schema

The four tasks capture useful but incomplete aspects of comment meaning. They do not explicitly identify:

- The topics discussed in a comment.
- The particular product feature or content segment being praised or criticized.
- Specific emotions such as frustration, gratitude, or excitement.
- Sarcasm as a standalone classification target.
- Detailed feedback categories or the underlying issue being reported.
- The relationship between a comment and a claim made in the video.

These are **potential extensions**, not labels that exist in the current dataset. Qualitative observations motivate exploring them, but the project has not established through a separate study that each proposed dimension will improve downstream outcomes.

## 7. Large-Scale Inference Is Not Ground Truth

After excluding the 5,000 annotated comments, the trained models were applied to **45,739 additional comments**. The resulting label distributions describe **model outputs**, not manually verified population statistics.

In particular, the absence of predicted `IMPLICITLY_ACTIONABLE` comments in this inference run should **not** be interpreted as evidence that such comments are absent from the underlying data. The test-set results already show that the actionability model struggles with this class.

Similarly, predicted toxicity rates should not be treated as validated prevalence estimates given the classifier's measured false negatives and false positives.

## 8. Confidence and Operational Use

- Model scores are not established as **calibrated probabilities**. A high score should not be interpreted as a verified probability that a label is correct.
- The system is intended for **research, experimentation, and exploratory analysis**.
- Predictions should not be used as the sole basis for moderation, penalties, reputational judgments, or decisions affecting individuals.
- Aggregated dashboards and analyses should clearly distinguish predictions from human annotations and include uncertainty or quality caveats where appropriate.

## 9. Data Release and Reproducibility

The original collected comments, annotated records, and comment-level inference outputs are **excluded from the version-controlled repository and will not be included in the planned public release**. Public documentation can include aggregate metrics, figures, annotation policies, and synthetic examples.

This protects the project's data-release boundary, but it also means that third parties cannot independently reproduce the exact training results from the repository alone. Public code and documented procedures support methodological transparency; they do not replace access to the private dataset.

## 10. Next Steps

Proposed improvements, including minority-class evaluation, richer annotation dimensions, and video-context-aware classification, are documented in [Future Work](future_work.md).

**Bottom line:** v1.0 is a research prototype with documented limitations, not a production-ready moderation or audience-understanding service.

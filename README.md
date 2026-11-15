
# Turkish Comment Intelligence

A multi-task Natural Language Processing (NLP) research project for analyzing Turkish-language YouTube comments across four dimensions: **sentiment, actionability, toxicity, and question type**.

The project covers data collection, preprocessing, manual annotation, exploratory analysis, classical machine learning, transformer-based classification, evaluation, large-scale inference, and an interactive Streamlit demo.

> **Project status:** Research prototype. Model training, evaluation, the reusable tuned-baseline inference pipeline, the Streamlit demo, and automated tests are implemented. The source code and documentation are publicly available. Original datasets and model artifacts remain private.
>
> **Responsible use:** The models are intended for research and educational experimentation. They are not suitable for unsupervised content moderation or high-stakes decision-making.

## Overview

Online comments contain opinions, questions, requests, and potentially harmful language. Analyzing these signals can help researchers understand audience feedback and identify patterns in user-generated content.

Turkish Comment Intelligence investigates four complementary classification tasks using Turkish YouTube comments.

| Task | Labels |
|---|---|
| Sentiment | `POSITIVE`, `NEUTRAL`, `NEGATIVE`, `MIXED` |
| Actionability | `NOT_ACTIONABLE`, `IMPLICITLY_ACTIONABLE`, `EXPLICITLY_ACTIONABLE` |
| Toxicity | `NON_TOXIC`, `TOXIC` |
| Question Type | `NOT_QUESTION`, `INFORMATION_SEEKING`, `ACTION_REQUEST`, `RHETORICAL` |

Each task is modeled independently. A single comment can receive one prediction from each classifier.

### Research Models vs. Interactive Demo

The research experiments evaluated both classical machine learning and transformer-based approaches.

The **interactive demo and reusable inference pipeline currently use four tuned TF-IDF + Logistic Regression baseline models**.

They do not use the weighted BERTurk models selected for three tasks in the final research evaluation.

This distinction is important when interpreting the results presented below.

## Dataset

The dataset was collected from publicly accessible Turkish-language YouTube videos across five source categories:

- News
- Technology
- Education
- Entertainment
- Review

### Dataset Statistics

| Stage | Number of comments |
|---|---:|
| Raw collection | 50,781 |
| After cleaning | 50,739 |
| Manually annotated | 5,000 |
| Remaining unlabeled comments | 45,739 |

The cleaning process removed 37 empty or whitespace-only comments and 5 URL-only comments.

Repeated text, short comments, long comments, and emoji-only comments were retained when they contained potentially useful information.

### Annotation

A subset of 5,000 comments was manually annotated for all four classification tasks.

The annotation process followed documented labeling guidelines and included review and correction procedures.

The annotated dataset was divided using video-grouped splitting to reduce overlap between source videos across partitions.

| Split | Comments |
|---|---:|
| Training | 3,494 |
| Validation | 752 |
| Test | 754 |

Only comment text was used as model input. Video titles, transcripts, and other video-level context were not included in the classifiers.

### Data Privacy

The GitHub repository does not distribute:

- Collected comment texts or annotated datasets
- Comment identifiers or video identifiers
- Private source metadata
- Individual prediction records

The trained tuned-baseline model artifacts are hosted separately in a Hugging Face model repository.

These artifacts contain learned TF-IDF vocabularies and classifier parameters. They may retain fragments derived from training comments.

Heuristic vocabulary scans found no matches for the tested email, phone number, or long numeric identifier patterns. This limited check does not guarantee the absence of personal information or other privacy risks.

Public accessibility of source comments does not automatically establish unrestricted redistribution rights.

The model repository remains private while data-use, privacy, and publication considerations are reviewed.

## Methodology

### 1. Data Collection and Preprocessing

The data pipeline includes:

- YouTube comment collection
- Source-category organization
- Data quality checks
- Conservative text cleaning
- Annotation sampling
- Video-grouped dataset splitting

### 2. Manual Annotation

Comments were labeled independently for the four tasks using a documented annotation protocol.

See:

- [Annotation Guidelines](docs/annotation_guideline.md)
- [Ambiguous Annotation Cases](docs/ambiguous_cases.md)

### 3. Classical Machine Learning Baselines

The baseline experiments use TF-IDF features with Logistic Regression.

The experiments compare:

- Word-level n-grams
- Character-level n-grams
- Character n-grams within word boundaries
- Weighted and unweighted classification

Model selection was based on validation macro-F1.

The research results are summarized in this README. Detailed experiment reports are not included in this public release.

The four distributed tuned-baseline models use the following configurations:

| Task | TF-IDF configuration | Classifier |
|---|---|---|
| Sentiment | Word n-grams (1, 2) | Balanced Logistic Regression |
| Actionability | Word n-grams (1, 2) | Balanced Logistic Regression |
| Toxicity | Character n-grams (`char_wb`, 3–5) | Balanced Logistic Regression |
| Question Type | Character n-grams (`char_wb`, 3–5) | Balanced Logistic Regression |

### 4. Transformer-Based Classification

Transformer-based experiments use the Turkish BERT model:

`dbmdz/bert-base-turkish-cased`

The sentiment, actionability, and question-type classifiers use weighted BERTurk models.

The selected toxicity classifier uses TF-IDF with Logistic Regression.

The trained BERTurk artifacts are not currently distributed with the interactive demo.

### 5. Evaluation

Models were evaluated using:

- Accuracy
- Macro-F1
- Weighted-F1
- Per-class precision, recall, and F1
- Confusion matrices

Macro-F1 is emphasized because several important classes are underrepresented.

The validation set was used for model selection, hyperparameter tuning, and threshold selection where applicable.

The held-out test set was used to evaluate the selected research models.

## Final Research Test Results

The following results correspond to the selected research approaches evaluated on the **754-example held-out test set**.

They are not the performance results of the four distributed tuned-baseline demo models.

| Task | Selected approach | Test accuracy | Test macro-F1 |
|---|---|---:|---:|
| Sentiment | Weighted BERTurk | 0.7215 | 0.5775 |
| Actionability | Weighted BERTurk | 0.9629 | 0.5113 |
| Toxicity | TF-IDF + Logistic Regression | 0.9483 | 0.5332 |
| Question Type | Weighted BERTurk | 0.9390 | 0.6728 |

### Important Limitations

- The sentiment model has difficulty identifying the `MIXED` class.
- The actionability model does not reliably identify `IMPLICITLY_ACTIONABLE` comments.
- The toxicity model has low recall for toxic comments and should not be used for automatic moderation.
- The question-type model has limited performance on `ACTION_REQUEST`.

High accuracy on imbalanced tasks should not be interpreted as uniformly strong performance across all classes.

### Interpreting the Results

The evaluation results reveal substantial differences between overall performance and minority-class detection.

For example, the selected toxicity classifier achieved 94.83% accuracy but correctly identified only 2 of the 23 toxic comments in the held-out test set.

This illustrates why accuracy alone is insufficient for evaluating classifiers trained on imbalanced datasets.

Similarly, the selected actionability classifier struggled with `IMPLICITLY_ACTIONABLE`, while the sentiment and question-type classifiers showed weaknesses on `MIXED` and `ACTION_REQUEST`, respectively.

For further discussion, see [Limitations](docs/limitations.md).

## Tuned Baseline Results

The following results describe the four tuned-baseline models used by the reusable inference pipeline and Streamlit demo.

These results are from the **752-example validation set**, not the held-out final test set.

| Task | Validation accuracy | Validation macro-F1 |
|---|---:|---:|
| Sentiment | 0.6356 | 0.4873 |
| Actionability | 0.9255 | 0.4306 |
| Toxicity | 0.9601 | 0.6326 |
| Question Type | 0.8497 | 0.6764 |

Important observations:

- `MIXED` sentiment has an F1 of approximately 0.111.
- `IMPLICITLY_ACTIONABLE` has an F1 of approximately 0.231.
- `EXPLICITLY_ACTIONABLE` has an F1 of approximately 0.100.
- The toxicity model has approximately 0.194 recall for `TOXIC`.
- The `ACTION_REQUEST` class has only five validation examples.

These results demonstrate significant minority-class limitations.

Model probability outputs should not be interpreted as calibrated confidence estimates.

## Large-Scale Inference

As part of the research workflow, the selected research classifiers were applied to the remaining 45,739 unlabeled comments.

The resulting prediction distributions were used for exploratory analysis of the collected corpus.

These outputs are **model-generated predictions, not manually verified ground-truth labels**.

They should not be interpreted as representative statistics for all Turkish YouTube comments.

Individual inference records are not distributed to protect the privacy of the collected data.

This research-stage large-scale inference experiment is separate from the reusable tuned-baseline inference interface described below.

## Repository Structure

The public repository contains:

- `app.py` — Streamlit application
- `src/models/` — model training and inference code
- `src/data/` — preprocessing and dataset preparation utilities
- `src/annotation/` — annotation workflow utilities
- `src/eda/` — exploratory analysis utilities
- `scripts/` — model download and verification utilities
- `docs/` — annotation guidelines, limitations, and future work
- `tests/` — automated tests
- `.github/workflows/` — continuous integration

The original YouTube collection scripts, datasets, detailed experiment reports, and model artifacts are not distributed.

The structure above highlights the main project components. Additional source files and reports may exist within the listed directories.

Private datasets and downloaded model artifacts are excluded from Git version control.

## Installation

**Python:** Developed and tested with Python 3.14.5. Compatibility with other Python versions has not been fully verified.

### 1. Clone the Repository

```bash
git clone https://github.com/TugceDogru/turkish-comment-intelligence.git
cd turkish-comment-intelligence
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Download the Models

The tuned-baseline model artifacts are hosted at:

[Turkish Comment Intelligence — Tuned Baselines](https://huggingface.co/TugceDogru/turkish-comment-intelligence-baselines)

**Current access:** Private. An authorized Hugging Face account is required to download the artifacts.

Authenticate using the Hugging Face CLI:

```powershell
hf auth login
```

Then download the verified models:

```powershell
python scripts/download_models.py
```

The downloader:

- Retrieves the four approved model artifacts.
- Uses a pinned Hugging Face repository revision by default.
- Verifies each file using SHA-256.
- Skips files that already match the approved checksums.
- Preserves existing files if a download fails before replacement.
- Does not deserialize models during download.

The default destination is:

```text
models/baseline_tuned/
```

To use a different destination:

```powershell
python scripts/download_models.py --model-dir ./custom_models
```

The custom destination can also be supplied to `CommentClassifier`.

**Important:** The model repository is currently private. Cloning the GitHub repository alone does not grant access to its model artifacts.

## Model Artifact Integrity

The approved Hugging Face repository revision is:

`de3bace638060b19fe41e448e1931df6f73948fc`

Expected SHA-256 checksums:

| Artifact | SHA-256 |
|---|---|
| `actionability.joblib` | `ba028bd869f9ba0b05e54c503fd721a22ba43363067b55bdd9b91270999c919a` |
| `question_type.joblib` | `27f36a67ea383cfbd81075cf179a270237d3b78388eec06535a2cc782dca8bbc` |
| `sentiment.joblib` | `32b9438b8277f13656d9d027630748713d0146b4190db557fedda7fe21e1541e` |
| `toxicity.joblib` | `1048cd36f371b027938db97ce0b6d561a80720aea3e4c0fcc9c5c36103daa1a0` |

The artifacts have been successfully downloaded from Hugging Face and verified against these checksums.

**Security:** `joblib` files use Python object serialization. Loading untrusted artifacts may execute arbitrary code.

SHA-256 verification confirms that downloaded bytes match the approved artifacts. It does not independently prove that the artifacts are safe.

Only load models from trusted sources.

## Running Inference

**Model access requirement:** The inference pipeline and Streamlit demo require the four tuned-baseline model artifacts. These artifacts are hosted in a private Hugging Face repository and are not available to the general public. Without authorized access to the model repository, users can inspect the source code and run the mocked unit tests, but cannot run predictions using the original trained models.

The reusable inference pipeline supports single-comment and batch predictions.

### Single Comment

```python
from src.models.inference import CommentClassifier

classifier = CommentClassifier()

result = classifier.predict(
    "Video çok güzel olmuş ama ses kalitesi biraz kötü."
)

print(result)
```

Each result contains predictions for:

- Sentiment
- Actionability
- Toxicity
- Question Type

The output also includes model-estimated class probabilities.

### Batch Predictions

```python
from src.models.inference import CommentClassifier

classifier = CommentClassifier()

comments = [
    "Video çok faydalı olmuş, teşekkürler.",
    "Ses kalitesini biraz iyileştirebilir misiniz?",
    "Bu konu hakkında daha fazla bilgi verebilir misiniz?",
]

results = classifier.predict_batch(comments)

for result in results:
    print(result)
```

### Command-Line Interface

Predict a single comment:

```powershell
python -m src.models.inference --text "Video çok faydalı olmuş."
```

Predict multiple comments:

```powershell
python -m src.models.inference --texts "Harika video!" "Ses çok kötü."
```

The CLI prints structured JSON predictions.

## Interactive Streamlit Demo

The project includes a Streamlit interface for exploring model predictions.

Start the application:

```powershell
streamlit run app.py
```

The application supports:

- Single-comment analysis
- Batch analysis of up to 50 comments
- Predictions for all four tasks
- Visualization of model-estimated class probabilities

The application uses the **tuned baseline models**, not the selected BERTurk research models.

The four verified model artifacts must be available in the expected local model directory before launching the demo.

This is a research demonstration, not a production moderation system.

## Automated Testing and Code Quality

The project includes automated tests for the inference pipeline and model downloader.

The test suite currently contains **28 tests**.

Install development dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

Run all tests:

```powershell
python -m pytest -v
```

Run Ruff lint checks across the entire project:

```powershell
python -m ruff check .
```

Check formatting across the entire project:

```powershell
python -m ruff format --check .
```

Check dependency consistency:

```powershell
python -m pip check
```

GitHub Actions is configured to run automated checks on pushes to `main` and pull requests.

The inference and downloader unit tests use mocked model behavior or downloads where appropriate, allowing them to run without the private model artifacts.

## Reproducibility

The repository provides:

- Data processing and research code
- Annotation documentation
- Research results summarized in the README
- Reusable tuned-baseline inference
- Streamlit demo
- Automated tests
- A SHA-256 verified model downloader

The four tuned-baseline artifacts are hosted separately on Hugging Face.

Exact retraining of the original models is not possible from the public source repository alone because the original collected and annotated datasets are not distributed.

The weighted BERTurk artifacts used in the final research evaluation are not currently provided.

Inference using the tuned-baseline models is reproducible for users with access to the approved model artifacts and a compatible environment.

## Responsible Use

This project is intended for research, experimentation, and educational purposes.

Predictions may be unreliable for:

- Rare or underrepresented classes
- Ambiguous language
- Sarcasm and irony
- Context-dependent comments
- Domain-specific expressions
- Evolving slang and vocabulary

The toxicity classifier is not appropriate for fully automated content moderation.

Model outputs should not be used as the sole basis for consequential decisions.

Human review is recommended whenever predictions could affect individuals.

## Documentation

- [Annotation Guidelines](docs/annotation_guideline.md)
- [Ambiguous Annotation Cases](docs/ambiguous_cases.md)

- [Limitations](docs/limitations.md)
- [Future Work](docs/future_work.md)

## Future Work

Potential improvements include:

- Better handling of minority classes
- Improved probability calibration and uncertainty estimation
- Additional Turkish-language transformer experiments
- Context-aware classification using video titles and transcripts
- Topic classification and aspect-based sentiment analysis
- More comprehensive privacy and data-provenance reviews
- Broader model evaluation and robustness testing
- Improved experiment reproducibility

See [Future Work](docs/future_work.md) for details.


## License and Release Status

### Source Code

The original source code in this repository is licensed under the **Apache License, Version 2.0**.

See the [LICENSE](LICENSE) file for the full license text.

This license applies only to material for which the repository owner has the necessary licensing rights. Third-party components remain subject to their respective licenses.

### Dataset

The original YouTube comments, annotated datasets, comment identifiers, video identifiers, and individual prediction records are not distributed with this repository.

The Apache-2.0 license does not grant rights to the underlying YouTube content or other third-party data.

### Model Artifacts

The four tuned-baseline model artifacts are hosted separately on [Hugging Face](https://huggingface.co/TugceDogru/turkish-comment-intelligence-baselines).

The model repository remains private pending further review of data provenance, privacy, platform terms, and redistribution rights.

The model artifacts are **not covered by the source code's Apache-2.0 license**. No public model license has been assigned.

### Public Release

This public release contains source code, documentation, and summarized research results. Original datasets, model artifacts, and detailed experiment reports are excluded.

The repository does not distribute raw or annotated YouTube comments, comment or video identifiers, individual prediction records, or trained model artifacts.

The Hugging Face model repository remains private pending further review of data provenance, privacy, platform terms, and redistribution rights.

Public access to the source code does not imply permission to redistribute the underlying data or model artifacts. Users are responsible for complying with applicable platform terms, privacy requirements, and third-party licenses when collecting or processing their own data.

This repository is the public source-code release. The original research repository and trained model artifacts remain private.

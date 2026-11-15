
# Future Work

**Project:** Turkish Comment Intelligence  
**Target release:** v1.0 (in preparation)
**Status:** Proposed research and engineering directions; not implemented unless explicitly stated otherwise

## 1. Vision

Turkish Comment Intelligence v1.0 provides four comment-level classification tasks: **sentiment**, **actionability**, **toxicity**, and **question type**.

Reviewing annotation edge cases suggests that these dimensions, while useful, do not exhaust the information expressed in Turkish YouTube comments. Comments can simultaneously refer to particular topics, express multiple emotions, use irony, evaluate specific product or video attributes, and react to statements made in the video.

The long-term goal is to investigate a richer **Turkish-language, context-aware comment understanding system**. The extensions below are research proposals, not claims of demonstrated performance improvements.

## 2. Priority 1 — Improve the Existing Four Tasks

Before expanding the label schema, the most important goal is to improve reliability on the current tasks, especially minority classes.

### 2.1 Targeted error analysis

- Review false positives and false negatives for each task, prioritizing `TOXIC`, `IMPLICITLY_ACTIONABLE`, `MIXED`, and `ACTION_REQUEST`.
- Group errors by linguistic phenomenon: sarcasm, colloquial Turkish, spelling variation, emojis, short messages, and indirect requests.
- Distinguish errors caused by ambiguous annotation definitions from errors caused by model behavior.
- Report per-class precision, recall, F1, confusion matrices, and support alongside aggregate metrics.

### 2.2 Data and modeling experiments

- Collect and annotate additional examples for underrepresented classes using a documented sampling strategy.
- Evaluate class weighting, targeted sampling, data augmentation where appropriate, and alternative model architectures.
- Compare stronger Turkish-language and multilingual text encoders with the existing BERTurk and TF-IDF baselines.
- Investigate threshold selection and probability calibration, using validation data rather than tuning on the held-out test set.
- Repeat evaluations with multiple random seeds and, when feasible, an independently collected external test set.

**Success criterion:** Demonstrable improvement in minority-class recall and macro F1 without unacceptable increases in false positives. Accuracy alone is insufficient.

## 3. Priority 2 — Expand the Analytical Dimensions

The following tasks may provide additional insight beyond the current four labels.

| Proposed Task | Research Question | Potential Value |
|---|---|---|
| Topic Classification | What subject is the comment discussing? | Summarize audience interests and recurring themes. |
| Aspect-Based Sentiment Analysis | Which feature or content aspect is being evaluated, and how? | Separate praise or criticism of audio, pacing, price, product features, and explanations. |
| Feedback / Issue Categorization | What kind of improvement or problem is mentioned? | Organize actionable comments into useful categories. |
| Sarcasm Detection | Is the comment sarcastic or ironic? | Investigate a major source of sentiment ambiguity. |
| Emotion Classification | Which emotions are expressed? | Distinguish frustration, excitement, gratitude, disappointment, and other reactions. |
| Intent Classification | What is the commenter's communicative purpose? | Explore intents beyond the existing question-type and actionability schema. |

These proposed tasks may overlap. Their usefulness, definitions, class boundaries, and annotation cost should be studied before committing to a new schema.

### 3.1 Annotation strategy for new tasks

1. Define a narrow research question and intended use case for each new dimension.
2. Draft label definitions and ambiguous-case examples.
3. Pilot-annotate a small, diverse sample and inspect disagreements.
4. Revise the new guideline based on the pilot, then freeze a versioned protocol.
5. Create new labels and train/evaluate new models without silently rewriting the v1.0 ground truth.

The original four-task annotation guideline remains the authoritative policy for v1.0.

## 4. Priority 3 — Context-Aware Classification Using Video Titles and Transcripts

### 4.1 Motivation

The current system classifies each comment **using its text alone**. Although video-related metadata was available during dataset preparation, it was not used as model input. In particular, the models do not read the video's title or spoken content.

A future extension could analyze a comment together with the **video title**, **transcript** (spoken content), and potentially other relevant metadata. This may help with comments whose meaning depends on what the creator said or showed.

For example, "Bu kısmı anlamadım" ("I did not understand this part") does not identify the referenced segment without context. A video transcript may help determine which explanation is being discussed, although a comment alone may still be insufficient to locate it precisely.

### 4.2 Proposed capabilities

- **Contextual interpretation:** Test whether title and transcript context improve understanding of ambiguous reactions and apparent sarcasm.
- **Comment–video relevance:** Determine whether a comment refers to a topic, product, claim, or explanation present in the video.
- **Aspect and segment linking:** Associate feedback with relevant content aspects or transcript passages when sufficient evidence exists.
- **Context-aware question analysis:** Investigate whether a question seeks information already covered in the video or requests additional explanation.
- **Creator-facing summaries:** Aggregate recurring issues and audience interests with references to the content being discussed.

### 4.3 Possible technical approaches

1. **Title-aware baseline:** Concatenate a comment with its video title and compare it with the comment-only model.
2. **Transcript retrieval:** Divide transcripts into passages, retrieve potentially relevant segments for each comment, and classify using the comment plus retrieved context.
3. **Joint representations:** Explore cross-encoders, dual-encoder retrieval with a downstream classifier, or other transformer-based architectures.
4. **Optional multimodal extension:** Investigate visual or audio features only if transcript and title context prove insufficient and suitable data can be obtained.

These are candidate approaches, not implemented components.

### 4.4 Evaluation and annotation requirements

The v1.0 annotation protocol deliberately excludes external video context. Introducing context can legitimately change how some comments are interpreted. Therefore, **context-aware evaluation must not silently reuse or relabel the existing ground truth as though the task were unchanged**.

A defensible study would:

- Define whether the goal is to predict the original comment-only labels or a new set of context-aware labels.
- Create a separately versioned context-aware annotation protocol and, where necessary, a newly annotated evaluation set.
- Preserve **video-grouped** train/validation/test separation to reduce leakage across comments from the same video.
- Compare comment-only, comment-plus-title, and comment-plus-transcript systems under a clearly stated, compatible evaluation setup.
- Measure macro F1, per-class performance, error patterns, computational cost, and the effect of missing or low-quality transcripts.
- Examine whether retrieved transcript segments are actually relevant rather than assuming that more context always helps.

### 4.5 Practical constraints

Transcript availability, language identification, automatic-caption errors, long-video processing costs, and permission or platform-policy requirements will affect feasibility. Some comments may refer to visuals or events that transcripts cannot capture. Transcript access and storage must follow applicable terms and privacy requirements.

**Research hypothesis:** Video context may improve certain context-dependent classifications and enable richer analyses. This has not yet been demonstrated by v1.0 experiments.

## 5. Priority 4 — Better Evaluation and Reliability

- Build a small, independently sourced evaluation set to test generalization beyond the original collection.
- Assess performance across topics, video categories, comment lengths, and informal language patterns when sample sizes permit.
- Quantify annotation agreement on a representative subset and document unresolved ambiguities.
- Study confidence calibration and selective prediction, including an "uncertain / needs review" workflow outside the existing label schema.
- Monitor model drift and changes in Turkish online language over time.
- Consider human-in-the-loop review for sensitive predictions, especially toxicity.

## 6. Priority 5 — Reproducible Research and Usability

The following engineering improvements are planned as part of the v1.0 release preparation:

- Implement a reusable inference interface for the four existing classification tasks.
- Provide a Streamlit-based interactive demonstration using synthetic or user-provided text inputs.
- Add automated tests and continuous integration checks.
- Document model-loading requirements, dependency versions, and setup instructions.
- Maintain clear model versioning, configuration files, and evaluation reports.
- Complete a public release review covering privacy, repository contents, and documentation.

Additional usability improvements may be explored after v1.0:

- Develop aggregate reporting and visualization tools that distinguish model predictions from verified labels.
- Investigate more advanced analysis workflows based on evaluated model capabilities.

The planned inference interface and demo are not yet implemented. Their availability in the v1.0 release depends on successful development, testing, and model artifact access.

## 7. Suggested Roadmap

| Phase | Main Focus | Expected Deliverable |
|---|---|---|
| v1.0 preparation | Documentation, reusable inference pipeline, interactive demo, automated tests, and release review | Public research repository with documented evaluation results and a usable demonstration interface. |
| v1.x research | Minority-class error analysis, additional annotations, and model improvements | Updated benchmarks with class-level comparisons. |
| v2.0 research | Additional annotation dimensions | Pilot guidelines, labeled evaluation samples, and baseline models. |
| v2.x research | Video-title and transcript context | Context-aware dataset protocol and controlled comparison with comment-only baselines. |
| Later exploration | Aspect/segment linking and richer interfaces | Evaluated creator-facing analytical workflows. |

This roadmap is **illustrative, not a delivery commitment**. Version numbers and priorities may change based on experimental findings, implementation constraints, and data availability.

## 8. Guiding Principles

- **Measure improvements:** New tasks or more complex models should earn their place through evaluation.
- **Keep protocols versioned:** Never silently change frozen v1.0 label meanings.
- **Prioritize rare-class reliability:** Aggregate accuracy must not obscure failures on important minority classes.
- **Separate evidence from hypotheses:** Distinguish measured results, qualitative observations, and future research ideas.
- **Respect data boundaries:** Do not publish the private collected, annotated, or comment-level inference datasets.
- **Avoid overclaiming:** Treat the system as an exploratory research prototype until broader validation supports stronger uses.

For the current system's measured weaknesses and constraints, see [Limitations](limitations.md).

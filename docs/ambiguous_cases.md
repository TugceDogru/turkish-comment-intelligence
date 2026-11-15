
# Ambiguous Annotation Cases

**Project:** Turkish Comment Intelligence  
**Document version:** 1.1 (documentation update)  
**Reference guideline:** `annotation_guideline.md` — Version 1.3 FINAL  
**Annotation dimensions:** Sentiment, Actionability, Toxicity, Question Type

> **Scope and provenance:** All comments in this document are synthetic, illustrative examples, not excerpts from the private YouTube dataset. This document explains the existing annotation policy; it does not introduce new labels, change the frozen annotation guideline, or imply that the training dataset was re-annotated.

---

## 1. How to Use This Document

This document explains difficult annotation boundaries through concrete Turkish comment examples.

Each comment must be evaluated independently across four dimensions:


| Dimension     | Allowed Labels                                                          | Core Question                                                                        |
|---------------|-------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| Sentiment     | `POSITIVE`, `NEUTRAL`, `NEGATIVE`, `MIXED`                                | What emotional or evaluative orientation does the complete comment express?         |
| Actionability | `NOT_ACTIONABLE`, `IMPLICITLY_ACTIONABLE`, `EXPLICITLY_ACTIONABLE`        | Does the comment contain useful creator/content-related feedback or direction?       |
| Toxicity      | `NON_TOXIC`, `TOXIC`                                                      | Does the comment contain a hostile or degrading attack against a human target?       |
| Question Type | `NOT_QUESTION`, `INFORMATION_SEEKING`, `ACTION_REQUEST`, `RHETORICAL`     | Does the comment contain a meaningful question, and what is its communicative function? |

### General Principles

1. Use only the comment text as evidence.
2. Do not infer meaning from video titles, categories, channels, or external context.
3. Evaluate all four annotation dimensions independently.
4. Negative sentiment does not automatically indicate toxicity.
5. A question is not automatically actionable.
6. A request is not automatically a question.
7. Sarcasm must be supported by linguistic evidence within the comment.
8. When evidence is insufficient, prefer the least assumptive interpretation.
9. Use `annotation_notes` for genuinely ambiguous or unusual cases.
10. Do not introduce new labels or redefine existing labels based on individual examples.

---

## 2. Original Boundary Cases

### Case 001 — Specific Problem Without Explicit Suggestion

**Comment:**  
"Video gereksiz uzun olmuş."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `IMPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment expresses dissatisfaction with the video's length.

Video length is a specific and modifiable content characteristic. The creator can infer that shortening or editing the video could address the problem.

Although no direct instruction is provided, the feedback is sufficiently specific to be actionable.

There is no personal attack or meaningful question.

**Compare:**

"Video güzel değil."

→ `NEGATIVE` / `NOT_ACTIONABLE` / `NON_TOXIC` / `NOT_QUESTION`

General dissatisfaction does not identify a specific improvement.

---

### Case 002 — Strong Negative Evaluation vs. Toxicity

**Comment:**  
"Berbat."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment expresses strong dissatisfaction.

However, strong negative sentiment alone is insufficient for toxicity.

The wording does not establish a targeted interpersonal attack.

It also does not identify a specific problem that the creator could improve.

The comment is a reaction rather than a question.

**Key distinction:**

Negative evaluation and toxicity are separate annotation dimensions.

---

### Case 003 — Personal Experience vs. Implicit Feedback

**Comment:**  
"Hiçbir şey anlamadım."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The viewer reports a negative learning experience.

However, the comment does not explain why the viewer failed to understand the content.

No specific improvement can be reliably inferred.

**Compare:**

"Anlatım çok hızlı olduğu için hiçbir şey anlamadım."

→ `NEGATIVE` / `IMPLICITLY_ACTIONABLE` / `NON_TOXIC` / `NOT_QUESTION`

The speaking pace is identified as a modifiable problem.

"Hiçbir şey anlamadım, daha fazla örnek verirseniz daha anlaşılır olabilir."

→ `NEGATIVE` / `EXPLICITLY_ACTIONABLE` / `NON_TOXIC` / `NOT_QUESTION`

The commenter explicitly suggests providing additional examples.

Although the suggestion is polite, it is not expressed as a question.

---

### Case 004 — Request Without Negative Criticism

**Comment:**  
"İkinci yöntemin performansını da karşılaştırabilir misiniz?"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

**Reasoning:**

The commenter asks the creator to perform a concrete content-related action: comparing another method.

The comment does not express dissatisfaction or criticism.

It is actionable because it directly requests additional content.

It is an action-request question rather than a factual information-seeking question.

**Key distinction:**

A content request does not automatically introduce negative sentiment.

---

### Case 005 — Disagreement and Mixed Sentiment

**Comment:**  
"Anlattıklarınızın bazılarını çok beğendim ama verdiğiniz örnekler oldukça kötüydü."

**Decision:**

- Sentiment: `MIXED`
- Actionability: `IMPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The first clause expresses meaningful appreciation for some aspects of the explanation.

The second clause expresses a negative evaluation of the examples provided in the content.

Both positive and negative evaluations contribute meaningfully to the overall sentiment, so the comment is classified as `MIXED`.

The criticism identifies a specific and modifiable content-related aspect: the quality of the examples. The creator can infer that improving or replacing the examples could address the problem.

Therefore, the comment is `IMPLICITLY_ACTIONABLE`, even though it does not contain a direct request for improvement.

The comment contains neither a hostile interpersonal attack nor a meaningful question.

**Key distinction:**

A comment can express mixed sentiment while also providing implicitly actionable feedback when it identifies a specific content-related problem.

---

### Case 006 — General Negative Evaluation vs. Implicit Actionability

**Comment:**  
"Video güzel değil."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment expresses dissatisfaction with the video as a whole.

However, it does not identify a specific aspect that should be changed.

**Compare:**

"Video çok uzun."

→ `NEGATIVE` / `IMPLICITLY_ACTIONABLE` / `NON_TOXIC` / `NOT_QUESTION`

The second comment identifies video length as a modifiable characteristic.

---

### Case 007 — Toxic Attack vs. Actionable Feedback

**Comment:**  
"Sen bu işi gerçekten bilmiyorsun."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment belittles the creator's competence.

It attacks the person rather than identifying a specific problem in the content.

The hostile interpersonal characterization makes the comment toxic.

No useful improvement direction or question is provided.

---

### Case 008 — Toxic Command Without Useful Actionability

**Comment:**  
"Hiçbir şey bilmiyorsun, video çekmeyi bırak."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The first clause attacks the creator personally.

The second clause is a hostile command to stop creating content.

Although grammatically imperative, it does not provide useful feedback for improving or extending the content.

The command is not a meaningful question.

**Key distinction:**

Not every command is actionable.

---

### Case 009 — Possible Sarcasm Without Sufficient Evidence

**Comment:**  
"Bravo, yine harika anlatmışsın."

**Decision:**

- Sentiment: `POSITIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment could be sarcastic in certain contexts.

However, the annotation process does not use external video context.

The wording alone does not establish a sarcastic interpretation.

Therefore, the literal positive interpretation is the most defensible decision.

**Key distinction:**

Annotators must not invent sarcasm when textual evidence is insufficient.

---

### Case 010 — Positive Comment With a Continuation Request

**Comment:**  
"Lütfen bu seri devammm etsinnn"

**Decision:**

- Sentiment: `POSITIVE`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The enthusiastic wording expresses a positive reaction to the content.

The commenter explicitly requests that the series continue.

The request is actionable because it concerns future content production.

However, the comment is not phrased as a question.

Therefore, Question Type is `NOT_QUESTION`, not `ACTION_REQUEST`.

---

### Case 011 — Information-Seeking Question

**Comment:**  
"Bu telefon ne zaman çıktı?"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `INFORMATION_SEEKING`

**Reasoning:**

The commenter requests factual information about a product.

The question does not request content improvement, correction, or future production.

A creator may choose to answer the question, but that does not automatically make it actionable under this annotation scheme.

---

### Case 012 — Question Requesting Future Content

**Comment:**  
"Bir sonraki videoda Pro modelini de karşılaştırabilir misiniz?"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

**Reasoning:**

The commenter explicitly requests a comparison in future content.

This is a creator-directed action request rather than a simple request for an existing fact.

The question form makes Question Type `ACTION_REQUEST`.

---

### Case 013 — Emoji-Only Positive Reaction

**Comment:**  
"❤❤❤"

**Decision:**

- Sentiment: `POSITIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The hearts provide a clear positive emotional signal.

The comment does not contain an improvement request, personal attack, or question.

Emoji-only comments can express sentiment when the emotional meaning is sufficiently clear.

---

### Case 014 — Ambiguous Emoji

**Comment:**  
"🤔"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The emoji can communicate thought, uncertainty, or hesitation.

However, it does not independently establish a reliable positive or negative evaluation.

It also does not constitute a meaningful information-seeking question.

The least assumptive interpretation is neutral.

---

### Case 015 — Profanity Without Personal Attack

**Comment:**  
"Bu fiyat ne lan?"

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `RHETORICAL`

**Reasoning:**

The wording expresses negative surprise or dissatisfaction about the price.

The informal expression "lan" does not automatically establish toxicity because no person is being attacked.

The question functions primarily as an emotional reaction to the price rather than a genuine request for factual information.

It does not provide creator/content improvement direction.

**Key distinction:**

Profanity, negative sentiment, and toxicity must be evaluated separately.

---

### Case 016 — Direct Personal Insult

**Comment:**  
"Sen ne salak adamsın."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The insulting expression directly targets a person.

It communicates a hostile and degrading interpersonal judgment.

The comment does not identify a specific content problem or request an improvement.

It is a statement, not a meaningful question.

---

### Case 017 — Toxicity and Useful Feedback Together

**Comment:**  
"Gerizekalı gibi anlatmışsın, bari kodları ekranda daha büyük göster."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment contains a degrading personal attack.

At the same time, it explicitly requests that the creator display code in a larger size.

The useful improvement request remains actionable despite the hostile language.

The instruction is imperative rather than interrogative.

**Key distinction:**

Toxicity does not automatically eliminate actionability.

---

### Case 018 — Specific Technical Problem

**Comment:**  
"Altyazılar sesle senkron değil."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `IMPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment identifies a specific technical problem: subtitle synchronization.

The creator can infer that the subtitles should be synchronized with the audio.

No direct request is necessary for implicit actionability.

The comment contains no personal attack or question.

---

### Case 019 — Product Criticism

**Comment:**  
"Bu telefon tam bir çöp."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The negative expression targets a product rather than a person.

It does not identify a specific improvement in the creator's content.

Strong product criticism does not automatically constitute toxicity.

---

### Case 020 — Positive Comment With an Improvement Request

**Comment:**  
"Çok güzel anlatmışsınız, bir sonraki videoda daha fazla örnek de gösterebilir misiniz?"

**Decision:**

- Sentiment: `POSITIVE`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

**Reasoning:**

The first clause clearly praises the explanation.

The second clause requests additional examples in future content.

The request does not automatically introduce negative sentiment.

Because it is phrased as a question requesting a content-related action, Question Type is `ACTION_REQUEST`.

---

## 3. Additional Cases — Question Type Boundaries

### Case 021 — Information-Seeking Question Without a Question Mark

**Comment:**  
"Abi bunun markası ne"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `INFORMATION_SEEKING`

**Reasoning:**

The wording clearly requests factual information even though punctuation is missing.

Question Type must be determined by linguistic meaning rather than punctuation alone.

---

### Case 022 — Content Request Expressed as a Statement

**Comment:**  
"Mchose V9 Pro inceleme istiyoruz."

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The commenter explicitly requests a product review.

The request concerns future content production.

However, it is expressed as a declarative statement rather than a question.

**Key distinction:**

`EXPLICITLY_ACTIONABLE` does not automatically imply `ACTION_REQUEST`.

---

### Case 023 — Content Request Expressed as a Question

**Comment:**  
"Mchose V9 Pro'yu da inceler misiniz?"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

**Reasoning:**

The requested content action is similar to Case 022.

However, this version uses an interrogative structure.

The difference in Question Type comes from the form and communicative function of the request.

---

### Case 024 — Rhetorical Question Expressing Criticism

**Comment:**  
"Bu kadar da kötü yapılır mı?"

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `RHETORICAL`

**Reasoning:**

The question primarily expresses criticism and disbelief.

It does not genuinely seek an informational answer.

The wording does not identify a specific modifiable content problem.

No personal attack is present.

---

### Case 025 — Genuine Question With Potentially Negative Framing

**Comment:**  
"Bu telefon neden bu kadar pahalı?"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `INFORMATION_SEEKING`

**Reasoning:**

Under a straightforward interpretation, the commenter asks for an explanation of the product's price.

The wording alone does not conclusively establish sarcasm, criticism, or disbelief.

A different interpretation could be justified if the comment contained additional linguistic evidence of frustration.

External context must not be used to invent that interpretation.

---

### Case 026 — Question Requesting a Content Improvement

**Comment:**  
"Kodları ekranda biraz daha büyük gösterebilir misiniz?"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

**Reasoning:**

The commenter directly requests an improvement in content presentation.

The request is specific and creator-directed.

No explicit dissatisfaction is expressed, so the request alone does not justify negative sentiment.

---

### Case 027 — Imperative Request for the Same Improvement

**Comment:**  
"Kodları ekranda daha büyük gösterin."

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The requested action is similar to Case 026.

However, the sentence is imperative rather than interrogative.

It is actionable but not a question.

---

### Case 028 — Rhetorical Question About Prices

**Comment:**  
"Bu fiyatlar şaka mı?"

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `RHETORICAL`

**Reasoning:**

The wording expresses disbelief and dissatisfaction about prices.

It does not literally request confirmation of a joke.

The comment contains no personal attack and no creator/content improvement request.

---

## 4. Additional Cases — Cross-Dimension Boundaries

### Case 029 — Clear Irony Supported by the Comment

**Comment:**  
"Harika, yine uygulama çökmüş."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The contrast between "Harika" and the application crashing provides linguistic evidence of irony.

The intended evaluation is negative despite the positive surface vocabulary.

The failure concerns an application rather than an explicitly identified defect in the creator's content.

Therefore, creator/content actionability must not be inferred without additional evidence.

---

### Case 030 — Positive and Negative Feedback Together

**Comment:**  
"Anlatım güzel ama video gereksiz uzun olmuş."

**Decision:**

- Sentiment: `MIXED`
- Actionability: `IMPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment meaningfully praises the explanation and criticizes video length.

Both sentiment components contribute to the overall evaluation.

The length problem is specific and modifiable, making the comment implicitly actionable.

The presence of "ama" alone is not the reason for the mixed sentiment classification.

---

### Case 031 — Social Demand Outside Creator/Content Scope

**Comment:**  
"Seyyanen zam ve 3600 ek gösterge hakkımızı istiyoruz."

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment expresses a social or political demand.

However, it does not request that the content creator improve, correct, or produce content.

The demand alone does not establish a clear positive or negative evaluation.

It also contains no personal attack or meaningful question.

---

### Case 032 — Negative Technical Observation Without a Direct Request

**Comment:**  
"Ses çok düşük."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `IMPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The comment identifies a specific problem with the audio level.

The creator can reasonably infer that increasing the audio volume would address the issue.

The absence of a direct instruction does not prevent implicit actionability.

---

### Case 033 — Insult Toward an Implied Human Target

**Comment:**  
"Şeytanın dölü."

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The expression is a degrading characterization conventionally directed toward a person.

The human target does not need to be explicitly named when the wording itself establishes an interpersonal insult.

No useful content-related feedback or question is present.

---

### Case 034 — Ambiguous Laughter Emoji

**Comment:**  
"🤣"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

**Reasoning:**

The emoji may communicate amusement, mockery, or another emotional reaction.

Without additional wording or a clearly identifiable target, its sentiment cannot be determined reliably.

Do not infer sarcasm, hostility, or positive sentiment from unavailable context.

---

### Case 035 — Direct Request for Additional Explanation

**Comment:**  
"BERT'i de anlatabilir misiniz?"

**Decision:**

- Sentiment: `NEUTRAL`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

**Reasoning:**

The question asks the creator to explain an additional topic.

It requests a content-related action rather than an existing factual answer.

Therefore, the comment is explicitly actionable and classified as an action-request question.

---

### Case 036 — Information Request With Negative Framing

**Comment:**  
"Bu model neden bu kadar yavaş çalışıyor?"

**Decision:**

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `INFORMATION_SEEKING`

**Reasoning:**

The phrase "bu kadar yavaş" communicates dissatisfaction with the model's performance.

However, the question can genuinely seek a technical explanation.

It does not request that the creator change their content or identify a modifiable defect in the creator's content.

Negative sentiment does not automatically make a question rhetorical.

---

## 5. Quick Decision Checks

When uncertain, apply the following checks separately.

### Sentiment

Does the complete comment express:

- Clear approval or appreciation? → `POSITIVE`
- Clear dissatisfaction or criticism? → `NEGATIVE`
- Meaningful positive and negative evaluations? → `MIXED`
- No reliably identifiable evaluative polarity? → `NEUTRAL`

Do not classify sentiment using isolated keywords.

### Actionability

Does the comment:

- Directly request or suggest a creator/content-related action? → `EXPLICITLY_ACTIONABLE`
- Identify a specific modifiable creator/content problem without requesting a change? → `IMPLICITLY_ACTIONABLE`
- Only react, insult, seek information, or make an unrelated demand? → `NOT_ACTIONABLE`

### Toxicity

Does the comment contain a hostile or degrading interpersonal attack?

- Yes → `TOXIC`
- No → `NON_TOXIC`

Ordinary criticism, product dissatisfaction, disagreement, and untargeted profanity do not automatically qualify as toxicity.

### Question Type

Does the comment contain a meaningful question?

- No → `NOT_QUESTION`
- Yes, and it requests a creator/content action → `ACTION_REQUEST`
- Yes, and it genuinely seeks information → `INFORMATION_SEEKING`
- Yes, and it primarily expresses criticism, disbelief, sarcasm, or another reaction without seeking an answer → `RHETORICAL`

Question marks alone do not determine Question Type.

---

## 6. Final Documentation Notes

- All examples in this document are synthetic.
- No private YouTube dataset records are reproduced.
- The document is intended to clarify annotation decisions, not redefine the production schema.
- The authoritative annotation policy remains `docs/annotation_guideline.md`, Version 1.3 FINAL.
- All four dimensions must be evaluated independently.
- Significant ambiguity should be recorded in `annotation_notes`.
- `annotation_notes` must never be used as model input.
- Updating this documentation does not imply that previously annotated comments were re-annotated or that trained models were changed.

**Final principle:** Annotate what the comment itself linguistically supports, not what might be true given unavailable context.

# Annotation Guidelines

**Project:** Turkish Comment Intelligence  
**Guideline Version:** 1.3 FINAL  
**Document Status:** Frozen Production Annotation Policy  
**Annotation Language:** Turkish  
**Documentation Language:** English  
**Annotation Dimensions:** Sentiment, Actionability, Toxicity, Question Type

---

## 1. Overview

### 1.1 Purpose

This document defines the annotation methodology used in the **Turkish Comment Intelligence** project.

The project aims to analyze Turkish-language YouTube comments across four independent classification tasks:

1. **Sentiment Analysis:** Identifying the emotional or evaluative orientation of a comment.
2. **Actionability Detection:** Identifying whether a comment provides useful feedback or direction for improving or producing creator-related content.
3. **Toxicity Detection:** Identifying hostile or degrading language directed toward human targets.
4. **Question Type Classification:** Identifying whether a comment contains a meaningful question and determining its communicative function.

The annotation policy is designed to support consistent, reproducible labeling decisions.

Each comment receives exactly one label from each of the four dimensions.

The dimensions are evaluated independently. A decision in one dimension must not automatically determine a decision in another.

### 1.2 Scope

These guidelines apply to Turkish-language social media comments collected for the project.

Comments may include:

- Informal Turkish
- Spelling mistakes
- Missing punctuation
- Abbreviations
- Slang
- Emojis
- Sarcasm and irony
- Incomplete expressions
- Product evaluations
- Creator-directed feedback
- Information-seeking questions
- Rhetorical questions
- Requests for future content

Annotators must interpret the linguistic evidence available in the comment itself.

The objective is not to reconstruct the author's complete intention using external information.


### 1.3 Dataset and Documentation Policy

The project's annotated dataset is not publicly distributed.

All example comments in this guideline are synthetic, illustrative examples and are not excerpts from the private YouTube dataset. No real user comments or associated user identifiers are reproduced.

The annotation policy is documented publicly to explain the methodology without requiring access to the underlying comments.

The companion document, [`ambiguous_cases.md`](ambiguous_cases.md), provides detailed examples of difficult annotation boundaries.


### 1.4 Policy Authority

This document defines the authoritative production annotation policy for version **1.3 FINAL**.

The companion ambiguous-cases document explains and illustrates these rules but does not override them.

Documentation improvements must not silently introduce new labels, change label meanings, or imply that the existing dataset was re-annotated.

---

## 2. General Annotation Principles

### 2.1 Comment-Only Annotation

All labels must be assigned using the **comment text itself**.

Annotators must not use the following information to determine labels:

- `video_title`
- `source_category`
- Channel information
- Creator identity inferred from metadata
- Like counts
- Publication dates
- External knowledge about the video
- Assumptions about the creator's intentions
- Assumptions about the commenter's political or social position
- Information not expressed in the comment

For example:

> Harika anlatmışsın.

Without textual evidence of sarcasm, this comment should be interpreted positively.

The annotator must not use the video's actual quality or surrounding context to reinterpret it as sarcastic.

### 2.2 Interpret Complete Linguistic Meaning

Although external context is prohibited, annotators should interpret linguistic relationships expressed within the comment.

These include:

- Comparisons
- References
- Praise
- Criticism
- Explicit requests
- Implied alternatives
- Contradictions
- Clearly supported sarcasm
- Clearly supported irony
- References to people or products mentioned in the comment

The annotation decision should reflect the overall communicative meaning rather than isolated keywords.

### 2.3 Independence of Annotation Dimensions

Each dimension must be evaluated separately.

For example:

> Kodları ekranda daha büyük gösterebilir misiniz?

This comment is:

- Sentiment: `NEUTRAL`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

The presence of an explicit request does not automatically make the sentiment negative.

Similarly, a toxic comment may still contain useful actionable feedback.

### 2.4 Conservative Interpretation

When the comment does not provide sufficient evidence for a more specific interpretation, prefer the least assumptive label.

Examples:

- Do not infer sarcasm without textual evidence.
- Do not infer a human target when the target is genuinely unclear.
- Do not infer negative sentiment solely from the topic being discussed.
- Do not infer actionable feedback from general dissatisfaction.
- Do not classify a question as rhetorical solely because it contains negative wording.

If the ambiguity is significant, document it in `annotation_notes`.

### 2.5 Annotation Notes

The `annotation_notes` field is used only for genuinely ambiguous, unusual, or difficult cases.

It is annotation audit metadata.

It must never be used as a model input feature.

---

## 3. Annotation Label Schema

The project uses four independent classification dimensions.

### 3.1 Sentiment

| Label | Definition |
|---|---|
| `POSITIVE` | Primarily positive evaluation, appreciation, approval, enthusiasm, gratitude, or positive wishes |
| `NEUTRAL` | No reliably identifiable positive or negative evaluative orientation |
| `NEGATIVE` | Primarily negative evaluation, dissatisfaction, criticism, rejection, or frustration |
| `MIXED` | Meaningful positive and negative evaluations within the same comment |

### 3.2 Actionability

| Label | Definition |
|---|---|
| `NOT_ACTIONABLE` | No useful creator/content-related improvement direction |
| `IMPLICITLY_ACTIONABLE` | A specific, modifiable content-related problem is identified without a direct request |
| `EXPLICITLY_ACTIONABLE` | A creator/content-related action is directly requested or suggested |

### 3.3 Toxicity

| Label | Definition |
|---|---|
| `NON_TOXIC` | No sufficiently supported hostile or degrading interpersonal attack |
| `TOXIC` | Hostile, insulting, humiliating, threatening, or degrading language directed toward a human target |

### 3.4 Question Type

| Label | Definition |
|---|---|
| `NOT_QUESTION` | No meaningful question is expressed |
| `INFORMATION_SEEKING` | A genuine request for information or an answer |
| `ACTION_REQUEST` | A question requesting a creator/content-related action |
| `RHETORICAL` | A question primarily expressing opinion, criticism, disbelief, sarcasm, or emotional reaction rather than seeking an answer |

### 3.5 One Label Per Dimension

Every annotated comment must have exactly one label for each dimension.

For example:

> Ses çok düşük, biraz artırabilir misiniz?

- Sentiment: `NEGATIVE`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

The explicit request takes precedence over implicit actionability because the commenter directly asks for a change.

---

## 4. Sentiment Annotation Guidelines

Sentiment represents the overall emotional or evaluative orientation expressed by the commenter.

Allowed labels:

- `POSITIVE`
- `NEUTRAL`
- `NEGATIVE`
- `MIXED`

### 4.1 POSITIVE

Use `POSITIVE` when the comment primarily expresses:

- Praise
- Appreciation
- Gratitude
- Approval
- Admiration
- Enthusiasm
- Satisfaction
- Encouragement
- Positive wishes
- Hope for a desirable outcome

Examples:

> Emeğinize sağlık.

`POSITIVE`

> İyi ki varsın.

`POSITIVE`

> Sağ ol.

`POSITIVE`

> Allah'ım emeklerimizin karşılığını ver.

`POSITIVE`

> İnşallah atanmak nasip olur.

`POSITIVE`

A positive wish or prayer can be classified as `POSITIVE` even when it does not directly praise the creator.

Positive sentiment does not require an explicit evaluation of the video.

### 4.2 NEUTRAL

Use `NEUTRAL` when the comment primarily contains:

- Factual information
- Observations without clear polarity
- Genuine information-seeking questions
- Unclear expressions
- Incomplete language
- Statements whose emotional orientation cannot reasonably be determined

Examples:

> Bu telefon ne zaman çıktı?

`NEUTRAL`

> 15:20 GTA açar mı?

`NEUTRAL`

> Zina

`NEUTRAL`

> Allah diyecem deee

`NEUTRAL`

Do not infer positive or negative sentiment merely because a comment discusses a sensitive or controversial topic.

An incomplete expression should not be assigned a strong emotional interpretation without sufficient evidence.

### 4.3 NEGATIVE

Use `NEGATIVE` when the comment primarily expresses:

- Dissatisfaction
- Criticism
- Frustration
- Rejection
- Disapproval
- Negative judgment
- Negative comparison

Examples:

> Video güzel değil.

`NEGATIVE`

> Bu paralar çok uçuk.

`NEGATIVE`

> Ses çok düşük.

`NEGATIVE`

> Berbat.

`NEGATIVE`

Negative sentiment does not automatically indicate toxicity.

For example:

> Bu telefon tam bir çöp.

Sentiment: `NEGATIVE`

Toxicity: `NON_TOXIC`

The negative expression targets a product rather than a human.

#### Comparative Praise and Criticism

A comment may praise one option primarily to criticize or dismiss another.

In such cases, annotate the overall communicative direction rather than counting positive and negative words.

Example:

> Benim kulak içi Redmi Buds 6 Pro 3k ya her özelliği var, saplar.

When the commenter presents their own product as superior to dismiss the compared alternative, the overall direction can be:

`NEGATIVE`

The presence of positive product descriptions does not automatically make the sentiment `POSITIVE`.

### 4.4 MIXED

Use `MIXED` when a comment contains meaningful positive and negative evaluations.

Example:

> Anlatım güzel ama video gereksiz uzun olmuş.

`MIXED`

The comment praises the explanation while criticizing the video's length.

Both components contribute meaningfully to the overall evaluation.

However, the presence of conjunctions such as:

- ama
- fakat
- ancak

does not automatically justify `MIXED`.

Example:

> Çok güzel anlatmışsınız, bir sonraki videoda daha fazla örnek gösterebilir misiniz?

`POSITIVE`

The request for additional examples does not independently express dissatisfaction.

### 4.5 Sentiment Decision Principles

When deciding between sentiment labels:

1. Read the complete comment.
2. Identify explicit evaluative or emotional language.
3. Consider linguistic relationships between clauses.
4. Interpret clearly supported irony or sarcasm.
5. Determine whether positive and negative evaluations are both meaningful.
6. Avoid inferring sentiment from unavailable external context.

Use `MIXED` only when both positive and negative components are genuinely supported.

---

## 5. Actionability Annotation Guidelines

Actionability measures whether a comment provides **usable feedback or direction for improving or producing creator/content-related output**.

It does not mean that every request, command, question, or desire is actionable.

Allowed labels:

- `NOT_ACTIONABLE`
- `IMPLICITLY_ACTIONABLE`
- `EXPLICITLY_ACTIONABLE`

### 5.1 NOT_ACTIONABLE

Use `NOT_ACTIONABLE` for comments containing only:

- General praise
- General dissatisfaction
- Emotional reactions
- Opinions
- Insults
- Information-seeking questions
- Personal wishes
- Political or social demands unrelated to creator/content improvement
- Hostile commands without useful improvement direction

Examples:

> Video güzel.

`NOT_ACTIONABLE`

> Berbat.

`NOT_ACTIONABLE`

> Teşekkürler.

`NOT_ACTIONABLE`

> Video güzel değil.

`NOT_ACTIONABLE`

The final example expresses dissatisfaction but does not identify a specific modifiable problem.

#### Information-Seeking Questions

Questions requesting existing information are not automatically actionable.

Examples:

> Bu telefon ne zaman çıktı?

`NOT_ACTIONABLE`

> Markası nedir bunun?

`NOT_ACTIONABLE`

> 15:20 GTA açar mı?

`NOT_ACTIONABLE`

These questions may be useful for the creator to answer, but their primary function is captured separately by Question Type.

#### Non-Creator Requests

A request is not automatically actionable.

Example:

> Seyyanen zam ve 3600 ek gösterge hakkımızı istiyoruz.

`NOT_ACTIONABLE`

The demand is not a request to improve or produce the creator's content.

Similarly:

> Video çekmeyi bırak.

`NOT_ACTIONABLE`

A hostile command to stop producing content is not considered useful improvement feedback under this policy.

### 5.2 IMPLICITLY_ACTIONABLE

Use `IMPLICITLY_ACTIONABLE` when a comment identifies a **specific and modifiable content-related problem** without directly requesting a change.

Examples:

> Ses çok düşük.

`IMPLICITLY_ACTIONABLE`

The creator can infer that the audio level should be increased.

> Video çok uzun.

`IMPLICITLY_ACTIONABLE`

The creator can infer that shortening the video could address the issue.

> Altyazılar senkron değil.

`IMPLICITLY_ACTIONABLE`

The creator can infer that subtitle synchronization should be corrected.

> Biraz da klavyeye para harcasaymış.

`IMPLICITLY_ACTIONABLE`

The comment indirectly points to a specific aspect that could be improved.

The key requirement is specificity.

General dissatisfaction without an identifiable modifiable aspect is not sufficient.

### 5.3 EXPLICITLY_ACTIONABLE

Use `EXPLICITLY_ACTIONABLE` when the commenter directly requests or suggests a creator/content-related action.

This includes:

- Direct suggestions
- Requests for improvement
- Correction requests
- Requests for future content
- Review requests
- Topic requests
- Requests for additional explanation
- Continuation requests

Examples:

> Sesi artırabilirsiniz.

`EXPLICITLY_ACTIONABLE`

> Daha fazla örnek gösterin.

`EXPLICITLY_ACTIONABLE`

> BERT'i de anlatabilir misiniz?

`EXPLICITLY_ACTIONABLE`

> Mchose V9 Pro inceleme istiyoruz.

`EXPLICITLY_ACTIONABLE`

> Abi AYT fen de gelsin lütfen.

`EXPLICITLY_ACTIONABLE`

> Seriye devam edin.

`EXPLICITLY_ACTIONABLE`

A content request phrased as a question remains explicitly actionable.

### 5.4 Explicit vs. Implicit Actionability

Compare:

> Ses çok düşük.

`IMPLICITLY_ACTIONABLE`

The problem is identified, but no direct request is made.

> Sesi biraz artırabilir misiniz?

`EXPLICITLY_ACTIONABLE`

The commenter directly requests a specific change.

> Ses çok düşük, biraz artırabilir misiniz?

`EXPLICITLY_ACTIONABLE`

The comment identifies a problem and explicitly requests a solution.

When an explicit creator/content-related request is present, classify the comment as `EXPLICITLY_ACTIONABLE`.

### 5.5 Actionability Decision Principles

Use the following order:

**Step 1:** Does the comment directly request or suggest a creator/content-related action?

- Yes → `EXPLICITLY_ACTIONABLE`
- No → Continue

**Step 2:** Does the comment identify a specific modifiable creator/content-related problem?

- Yes → `IMPLICITLY_ACTIONABLE`
- No → Continue

**Step 3:** Does the comment contain only a general reaction, information request, insult, personal wish, or unrelated demand?

- Yes → `NOT_ACTIONABLE`

Do not confuse grammatical commands with useful creator/content feedback.

---

## 6. Toxicity Annotation Guidelines

Toxicity measures hostile or degrading language directed toward a human target.

Allowed labels:

- `NON_TOXIC`
- `TOXIC`

### 6.1 NON_TOXIC

Use `NON_TOXIC` for:

- Ordinary criticism
- Disagreement
- Dissatisfaction
- Negative product evaluation
- Negative content evaluation
- Negative idea evaluation
- Political disagreement without personal attack
- Profanity that does not function as a targeted interpersonal attack

Examples:

> Bu telefon tam bir çöp.

`NON_TOXIC`

The target is a product.

> Bu fiyat ne lan?

`NON_TOXIC`

The wording is informal or profane, but it does not attack a human.

> Bu paralar çok uçuk.

`NON_TOXIC`

> Video çok kötü.

`NON_TOXIC`

Strong negative sentiment alone is insufficient for toxicity.

### 6.2 TOXIC

Use `TOXIC` when a comment contains a hostile interpersonal attack such as:

- Insult
- Humiliation
- Belittling
- Harassment
- Threat
- Degrading characterization
- Dehumanizing characterization

Examples:

> Sen ne salak adamsın.

`TOXIC`

> Hiçbir şey bilmiyorsun.

`TOXIC`

> Bu adam olduğu gibi kolpa.

`TOXIC`

The target is a person, and the wording communicates hostility or degradation.

### 6.3 Implied Human Targets

A human target does not need to be explicitly named.

If the expression clearly functions as an insult, humiliation, or degrading characterization of an implied person, it may still be classified as `TOXIC`.

Examples:

> Şeytanın dölü.

`TOXIC`

> CANLI CESET 😂

`TOXIC`

However:

> Bu bilgisayar çöp.

`NON_TOXIC`

The target is an object or product.

If the target cannot reasonably be identified as human and multiple interpretations remain plausible, prefer `NON_TOXIC`.

Use `annotation_notes` when the ambiguity is significant.

### 6.4 Political and Social Comments

Political or social opinions are not automatically toxic.

Example:

> Sandıkta dersini vereceğiz.

This may express negative political sentiment but does not automatically constitute a toxic threat.

Similarly, mentioning:

- Nationality
- Ethnicity
- Religion
- Political affiliation
- Social identity

does not automatically make a comment toxic.

Toxicity must be determined from the actual hostile or degrading language.

### 6.5 Toxicity and Actionability

Toxicity and actionability are independent.

Example:

> Gerizekalı gibi anlatmışsın, bari kodları ekranda daha büyük göster.

- Sentiment: `NEGATIVE`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `TOXIC`
- Question Type: `NOT_QUESTION`

The comment contains both a degrading personal attack and a concrete improvement request.

The presence of toxicity does not eliminate useful actionable feedback.

### 6.6 Toxicity Decision Principles

1. Identify the target of the expression.
2. Determine whether the target is human or clearly implied to be human.
3. Evaluate whether the language is hostile, insulting, threatening, humiliating, or degrading.
4. Distinguish criticism of products, ideas, and content from interpersonal attacks.
5. Do not treat profanity or negative sentiment alone as sufficient evidence.
6. When the target is genuinely ambiguous, use the least assumptive interpretation.

---

## 7. Question Type Annotation Guidelines

Question Type identifies whether a comment contains a meaningful question and, if so, what communicative function that question serves.

Allowed labels:

- `NOT_QUESTION`
- `INFORMATION_SEEKING`
- `ACTION_REQUEST`
- `RHETORICAL`

Do not classify questions based only on the presence of a question mark.

Turkish social media comments frequently omit punctuation.

### 7.1 NOT_QUESTION

Use `NOT_QUESTION` when the comment does not contain a meaningful question.

Examples:

> Video çok güzel.

`NOT_QUESTION`

> Ses çok düşük.

`NOT_QUESTION`

> Teşekkürler.

`NOT_QUESTION`

Commands, suggestions, and requests that are not expressed as questions remain `NOT_QUESTION`.

Example:

> Mchose V9 Pro inceleme istiyoruz.

- Actionability: `EXPLICITLY_ACTIONABLE`
- Question Type: `NOT_QUESTION`

The comment requests future content but is not phrased as a question.

### 7.2 INFORMATION_SEEKING

Use `INFORMATION_SEEKING` when the commenter genuinely seeks information or expects an answer.

Examples:

> Markası nedir bunun?

`INFORMATION_SEEKING`

> Bu telefon ne zaman çıktı?

`INFORMATION_SEEKING`

> 15:20 GTA açar mı?

`INFORMATION_SEEKING`

A question mark is not required.

Example:

> Abi bunun markası ne

`INFORMATION_SEEKING`

The communicative function matters more than punctuation.

### 7.3 ACTION_REQUEST

Use `ACTION_REQUEST` when a question explicitly requests a creator/content-related action.

Examples include questions requesting:

- A video
- A review
- A comparison
- An explanation
- Coverage of another topic
- A correction
- A content improvement

Examples:

> Pro modelini de inceler misiniz?

`ACTION_REQUEST`

> BERT'i de anlatabilir misiniz?

`ACTION_REQUEST`

> Bunun karşılaştırma videosunu yapar mısınız?

`ACTION_REQUEST`

These comments will generally also be classified as:

`EXPLICITLY_ACTIONABLE`

#### Important Distinction

Compare:

> Mchose V9 Pro inceleme istiyoruz.

- Actionability: `EXPLICITLY_ACTIONABLE`
- Question Type: `NOT_QUESTION`

With:

> Mchose V9 Pro'yu da inceler misiniz?

- Actionability: `EXPLICITLY_ACTIONABLE`
- Question Type: `ACTION_REQUEST`

Actionability captures useful creator/content direction.

Question Type captures the form and communicative function of a meaningful question.

### 7.4 RHETORICAL

Use `RHETORICAL` when a question primarily expresses:

- Opinion
- Criticism
- Disbelief
- Frustration
- Sarcasm
- Emotional reaction

and does not genuinely seek an informational answer.

Examples:

> Bu fiyatlar şaka mı?

`RHETORICAL`

> Nasıl hâlâ buna para veriyorlar?

`RHETORICAL`

> Bu kadar da kötü yapılır mı?

`RHETORICAL`

Do not assume every negatively worded question is rhetorical.

Example:

> Bu telefon neden bu kadar pahalı?

If the commenter genuinely seeks an explanation:

`INFORMATION_SEEKING`

If the wording clearly functions only as criticism or disbelief:

`RHETORICAL`

When genuinely ambiguous, choose the interpretation best supported by the wording and document significant uncertainty in `annotation_notes`.

### 7.5 Question Type Decision Procedure

Apply the following steps in order.

**Step 1 — Is there a meaningful question?**

- No → `NOT_QUESTION`
- Yes → Continue

**Step 2 — Does the question request a creator/content-related action?**

- Yes → `ACTION_REQUEST`
- No → Continue

**Step 3 — Does the commenter genuinely seek information or an answer?**

- Yes → `INFORMATION_SEEKING`
- No → Continue

**Step 4 — Does the question primarily express an opinion, criticism, disbelief, sarcasm, or emotional reaction?**

- Yes → `RHETORICAL`

Do not rely on punctuation alone.

---

## 8. Cross-Dimension Annotation Rules

All four dimensions must be evaluated independently.

### Example 1 — Information-Seeking Question

> Markası nedir bunun?

- Sentiment: `NEUTRAL`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `INFORMATION_SEEKING`

### Example 2 — Content Action Request

> Pro modelini de inceler misiniz?

- Sentiment: `NEUTRAL`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

### Example 3 — Rhetorical Criticism

> Bu fiyatlar şaka mı?

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `RHETORICAL`

### Example 4 — Implicit Technical Feedback

> Ses çok düşük.

- Sentiment: `NEGATIVE`
- Actionability: `IMPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

### Example 5 — Personal Insult

> Sen ne salak adamsın.

- Sentiment: `NEGATIVE`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `TOXIC`
- Question Type: `NOT_QUESTION`

### Example 6 — Positive Feedback With a Request

> Çok güzel anlatmışsınız, daha fazla örnek gösterebilir misiniz?

- Sentiment: `POSITIVE`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `ACTION_REQUEST`

### Example 7 — Mixed Sentiment and Implicit Feedback

> Anlatım güzel ama video gereksiz uzun olmuş.

- Sentiment: `MIXED`
- Actionability: `IMPLICITLY_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `NOT_QUESTION`

### Example 8 — Toxicity With Useful Feedback

> Gerizekalı gibi anlatmışsın, bari kodları ekranda daha büyük göster.

- Sentiment: `NEGATIVE`
- Actionability: `EXPLICITLY_ACTIONABLE`
- Toxicity: `TOXIC`
- Question Type: `NOT_QUESTION`

### 8.1 Common Annotation Mistakes

Avoid the following assumptions:

- `NEGATIVE` does not imply `TOXIC`.
- `TOXIC` does not imply `NOT_ACTIONABLE`.
- `EXPLICITLY_ACTIONABLE` does not imply `ACTION_REQUEST`.
- `INFORMATION_SEEKING` does not imply `EXPLICITLY_ACTIONABLE`.
- `RHETORICAL` does not automatically imply `TOXIC`.
- A polite request does not automatically imply `POSITIVE`.
- A request for more content does not automatically imply dissatisfaction.
- A question mark does not automatically establish a meaningful question.
- Positive and negative words in the same comment do not automatically imply `MIXED`.

---

## 9. Special Annotation Cases

### 9.1 Emoji Handling

Emojis should be interpreted together with the complete comment.

Clearly positive emojis may indicate positive sentiment.

Example:

> ❤

`POSITIVE`

Example:

> 👏👏👏

`POSITIVE`

Ambiguous emojis should not be assigned sentiment without sufficient evidence.

Example:

> 🤔

`NEUTRAL`

For laughter-only comments such as:

> 🤣

use:

`NEUTRAL`

when the target and intention cannot be determined from the comment itself.

Do not infer mockery or sarcasm from external video context.

### 9.2 Sarcasm and Irony

Sarcasm and irony are interpretation rules, not separate annotation dimensions.

Do not introduce production labels such as:

- `SARCASTIC`
- `NON_SARCASTIC`

When sufficient linguistic evidence of sarcasm or irony exists within the comment, annotate the intended communicative meaning rather than relying only on literal surface wording.

Example:

> Çok güzel, yine mükemmel çalışıyor (!)

The wording provides evidence of ironic criticism.

Sentiment:

`NEGATIVE`

Example:

> Harika, yine uygulama çökmüş.

The contradiction between praise and the application crashing establishes a negative intended evaluation.

Sentiment:

`NEGATIVE`

#### 9.2.1 Linguistic Evidence of Sarcasm

Possible indicators include:

- Contradiction between praise and a negative situation described in the same comment
- Exaggerated praise followed by an explicitly negative consequence
- Ironic quotation marks
- Expressions such as `(!)` when they clearly reverse literal meaning
- Rhetorical constructions expressing ridicule or disbelief
- Internal contrasts that make the intended meaning reasonably clear

No single marker automatically proves sarcasm.

Quotation marks, laughter emojis, or exaggerated wording alone are insufficient when the intended meaning remains unclear.

#### 9.2.2 No External Context

Do not infer sarcasm from:

- Video titles
- Source categories
- Creator identity
- Knowledge of the video
- Current events
- Assumed political positions
- External cultural context unavailable in the comment
- Personal assumptions about the commenter's intention

Example:

> Çok iyi olmuş 😂

If the comment itself does not establish whether the statement is sincere praise or mockery, do not use surrounding video context to decide.

Choose the most defensible interpretation supported by the wording.

#### 9.2.3 Sarcasm and Sentiment

Sarcasm can reverse apparent surface sentiment.

Example:

> Mükemmel telefon, iki günde bozuldu.

Sentiment:

`NEGATIVE`

The intended evaluation is negative despite positive vocabulary.

However, sarcasm does not automatically imply negative sentiment.

Determine the actual communicative meaning of the complete comment.

#### 9.2.4 Sarcasm and Toxicity

Sarcasm does not automatically make a comment toxic.

Example:

> Harika telefon, iki günde bozuldu.

- Sentiment: `NEGATIVE`
- Toxicity: `NON_TOXIC`

The target is a product.

If sarcasm is used to insult, humiliate, belittle, or degrade a human target, evaluate toxicity under the normal rules.

Example:

> Vay be, Einstein da aramıza katılmış.

If the wording clearly functions as a degrading interpersonal attack, it may be:

`TOXIC`

The decision must be based on the interpersonal attack, not sarcasm alone.

#### 9.2.5 Sarcasm and Question Type

A sarcastic question is not automatically `RHETORICAL`.

Apply the normal Question Type decision procedure.

Example:

> Bu kadar da kötü yapılır mı?

`RHETORICAL`

The question expresses criticism rather than genuinely seeking an answer.

However:

> Bu telefon neden bu kadar pahalı?

may be:

`INFORMATION_SEEKING`

when the commenter genuinely requests an explanation.

#### 9.2.6 Ambiguous Sarcasm

When sarcasm cannot be established from the comment text:

1. Do not invent sarcastic intent.
2. Do not consult external context.
3. Prefer the most defensible literal interpretation.
4. Record important ambiguity in `annotation_notes`.

Example:

> Süper 😂

Without additional evidence, the comment may represent sincere praise or mockery.

Do not automatically interpret the laughter emoji as sarcasm.

### 9.3 Incomplete and Context-Dependent Expressions

Some comments cannot be reliably interpreted without external information.

Example:

> Allah diyecem deee

Sentiment:

`NEUTRAL`

The expression is incomplete, and its intended evaluation cannot be reliably determined from the comment text alone.

Use `annotation_notes` when the ambiguity is significant.

### 9.4 Informal Turkish and Missing Punctuation

Turkish social media comments may contain:

- Missing question marks
- Repeated letters
- Abbreviations
- Slang
- Nonstandard spelling
- Incomplete punctuation

Annotators must focus on linguistic meaning rather than formal writing conventions.

Example:

> Abi bunun markası ne

Question Type:

`INFORMATION_SEEKING`

The absence of a question mark does not change the communicative function.

### 9.5 Profanity Without a Personal Attack

Profanity does not automatically establish toxicity.

Example:

> Bu fiyat ne lan?

- Sentiment: `NEGATIVE`
- Toxicity: `NON_TOXIC`
- Question Type: `RHETORICAL`

The wording expresses dissatisfaction or disbelief about the price.

It does not contain a targeted interpersonal attack.

---

## 10. Annotation Notes and Ambiguity Management

### 10.1 Purpose of annotation_notes

The `annotation_notes` field is annotation audit metadata.

Use it only when a comment is:

- Genuinely ambiguous
- Context-dependent
- An unusual boundary case
- Difficult to classify under existing rules
- Useful for later error analysis

Do not write notes for routine comments.

### 10.2 Example — Incomplete Expression

**Comment:**

> Allah diyecem deee

**Possible note:**

`Incomplete/context-dependent expression; sentiment cannot be determined reliably from comment text alone.`

### 10.3 Example — Comparative Criticism

**Comment:**

> Benim kulak içi Redmi Buds 6 Pro 3k ya her özelliği var, saplar.

**Possible note:**

`Implicit negative comparison; the commenter presents their own product as superior to the compared alternative.`

### 10.4 Example — Ambiguous Sarcasm

**Comment:**

> Süper 😂

**Possible note:**

`Potential sarcasm, but sarcastic intent cannot be established reliably from comment text alone; literal interpretation used.`

### 10.5 Annotation Notes Restrictions

`annotation_notes` must:

- Explain genuine uncertainty when necessary
- Be based on the comment text
- Avoid unsupported external assumptions
- Remain separate from prediction features
- Never be used as model input

The purpose is to document difficult decisions without changing the annotation schema.

---

## 11. Annotation Consistency and Quality Principles

### 11.1 Consistency Over Assumptions

The objective is to produce a consistent and reproducible annotation dataset.

Annotators should apply the same rules to linguistically similar comments.

For example:

> Video güzel değil.

Actionability:

`NOT_ACTIONABLE`

> Video çok uzun.

Actionability:

`IMPLICITLY_ACTIONABLE`

The difference is the identification of a specific modifiable issue.

### 11.2 Separate Linguistic Evidence From External Knowledge

An annotator may know that a particular video contains inaccurate information.

However, if the comment says:

> Harika anlatmışsın.

the annotator must not classify it as negative solely because of that knowledge.

The comment text remains the only permitted evidence.

### 11.3 Apply the Same Rules Across Categories

The annotation rules do not change based on whether a comment comes from:

- Technology
- Education
- Entertainment
- News
- Product reviews

The same linguistic evidence should lead to the same annotation decision regardless of source category.

### 11.4 Resolve Boundary Cases Using Existing Rules

When a difficult case appears:

1. Identify the relevant annotation dimension.
2. Review the corresponding label definitions.
3. Compare the comment with existing boundary examples.
4. Apply the closest established rule.
5. Record significant uncertainty when necessary.
6. Do not redefine labels based on a single example.

The companion document [`ambiguous_cases.md`](ambiguous_cases.md) provides additional synthetic examples.

### 11.5 Avoid Unsupported Claims About Annotation Reliability

These guidelines define the intended annotation procedure.

They do not, by themselves, establish measured inter-annotator agreement or guarantee error-free labels.

Any quantitative claims about annotation reliability must be supported by a separately documented evaluation.

---

## 12. Annotation Tool Codes and Model Label Indices

### 12.1 Annotation Tool Selection Codes

The annotation interface uses the following human-facing selection codes.

#### Sentiment

| Selection Code | Label |
|---|---|
| 1 | `POSITIVE` |
| 2 | `NEUTRAL` |
| 3 | `NEGATIVE` |
| 4 | `MIXED` |

#### Actionability

| Selection Code | Label |
|---|---|
| 1 | `NOT_ACTIONABLE` |
| 2 | `IMPLICITLY_ACTIONABLE` |
| 3 | `EXPLICITLY_ACTIONABLE` |

#### Toxicity

| Selection Code | Label |
|---|---|
| 1 | `NON_TOXIC` |
| 2 | `TOXIC` |

#### Question Type

| Selection Code | Label |
|---|---|
| 1 | `NOT_QUESTION` |
| 2 | `INFORMATION_SEEKING` |
| 3 | `ACTION_REQUEST` |
| 4 | `RHETORICAL` |

The annotation interface therefore uses the following order:

`[Sentiment] [Actionability] [Toxicity] [Question Type]`

Example:

`2 1 1 2`

represents:

- Sentiment: `NEUTRAL`
- Actionability: `NOT_ACTIONABLE`
- Toxicity: `NON_TOXIC`
- Question Type: `INFORMATION_SEEKING`

These codes are annotation-interface selection values.

They should not be confused with machine-learning class indices.

### 12.2 Model Class Indices

Machine-learning models may use zero-based class indices.

For the selected BERTurk models in Turkish Comment Intelligence v1.0, the label mappings are:

#### Sentiment Model

| Model Index | Label |
|---|---|
| 0 | `POSITIVE` |
| 1 | `NEUTRAL` |
| 2 | `NEGATIVE` |
| 3 | `MIXED` |

#### Actionability Model

| Model Index | Label |
|---|---|
| 0 | `NOT_ACTIONABLE` |
| 1 | `IMPLICITLY_ACTIONABLE` |
| 2 | `EXPLICITLY_ACTIONABLE` |

#### Question Type Model

| Model Index | Label |
|---|---|
| 0 | `NOT_QUESTION` |
| 1 | `INFORMATION_SEEKING` |
| 2 | `ACTION_REQUEST` |
| 3 | `RHETORICAL` |

The selected toxicity model uses a TF-IDF and logistic regression pipeline.

Its class ordering must be read from the saved classifier's `classes_` attribute rather than assumed from annotation-interface codes.

The selected v1.0 toxicity decision threshold is `0.48` for the `TOXIC` class probability.

### 12.3 Important Distinction

Annotation selection codes and model indices serve different purposes.

The annotation selection codes define how labels were entered through the annotation interface.

Model indices define how trained classifiers represent their output classes internally.

For reliable inference, use the mappings stored with the trained models or verified model configuration.

Never infer class ordering solely from the annotation selection codes.

---

## 13. Guideline Versioning and Annotation Freeze

### 13.1 Frozen Production Version

Version **1.3 FINAL** is the frozen production annotation guideline.

The production schema contains exactly four dimensions:

1. Sentiment
2. Actionability
3. Toxicity
4. Question Type

Sarcasm and irony are interpretation rules.

They do not introduce an additional annotation dimension.

### 13.2 Handling New Difficult Cases

When a new difficult case appears:

1. Apply the closest existing rule.
2. Interpret clear sarcasm or irony according to Section 9.
3. Use `annotation_notes` when the case is genuinely ambiguous.
4. Record recurring difficult patterns for later error analysis.
5. Do not redefine a label based on one example.
6. Do not introduce a new production annotation dimension.

### 13.3 Changes After Annotation Freeze

If a systematic annotation issue is discovered later, document it as a limitation or error-analysis finding.

Do not silently change the established label definitions.

Comments annotated before version 1.3 do not need to be re-annotated solely because the sarcasm rule was clarified.

That clarification formalized the intended interpretation of the existing labels rather than changing the production schema.

### 13.4 Documentation Updates

Documentation may be reorganized, clarified, and expanded with synthetic examples without changing the frozen annotation policy.

Such changes must remain consistent with the original production label definitions.

Any future modification to the actual annotation policy should be explicitly versioned and documented separately.

---

## 14. Final Annotation Checklist

Before finalizing a comment's labels, verify the following:

- [ ] All four annotation dimensions have been assigned.
- [ ] Decisions are based on comment text only.
- [ ] No external video context has been used.
- [ ] Sentiment reflects the complete communicative meaning.
- [ ] Actionability is limited to useful creator/content-related feedback or direction.
- [ ] Toxicity is based on a sufficiently supported hostile or degrading human-targeted attack.
- [ ] Question Type reflects the function of a meaningful question rather than punctuation alone.
- [ ] Sarcasm has not been inferred without sufficient textual evidence.
- [ ] The four dimensions have been evaluated independently.
- [ ] Significant ambiguity has been documented when necessary.
- [ ] No new labels or unsupported interpretation rules have been introduced.

---

## 15. Final Principle

**Annotate what the comment itself linguistically supports, not what might be true given surrounding video context or external information.**

Interpret the complete communicative meaning rather than isolated words.

When sarcasm or irony is clearly supported by the wording, annotate the intended meaning.

When the evidence is insufficient, do not invent unavailable context.

The objective is to create a **consistent, reproducible annotation dataset** using a stable and clearly documented annotation policy.

---

## Related Documentation

- [`ambiguous_cases.md`](ambiguous_cases.md) — Synthetic examples and explanations of difficult annotation boundaries.
- [`../README.md`](../README.md) — Project overview, methodology, model information, and usage instructions.

**Guideline:** 1.3 FINAL  
**Project:** Turkish Comment Intelligence

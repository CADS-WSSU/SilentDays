# SilentDays human validation protocol

## Purpose
Measure how well the released LLM labels agree with human judgment, and how well two human annotators
agree with each other, when the annotators see exactly the information the LLM grader saw.

## Design principle
Same inputs, same grade definitions, same scale as the LLM grader; only the judge differs.

| Shown to | Topic title + narrative | Question | Reference answers | Day | Full document text | Already-reported facts |
|---|---|---|---|---|---|---|
| LLM grader | yes | yes | no | yes | yes (≤16,000 characters) | yes, complete |
| Set A annotators | yes | yes | no | yes | identical text | no (relevance only) |
| Set B annotators | yes | yes | no | yes | identical text | the grader's exact list |
| Set C annotators | yes | yes | no | yes | all of that day's relevant documents, identical text | the question grader's exact list |

Only the layout differs from the grader prompt: documents are shown before the already-reported list,
the list is numbered and searchable, and a short plain-language guide is shown. In Sets B and C the guide's steps quote the grader's grade
definitions verbatim, and the grader's full definitions are available in the booklet.

## Sets (60 items each)
| Set | Task | Sampling (on the released labels) | Compared with |
|---|---|---|---|
| C | Question-day grade 0/1/5/10 | 15 per grade | question label |
| A | Document relevance 0/1 | 30 graded 0; 10 each graded 1, 5, 10 | document label, binarized (0 vs ≥1) |
| B | Document grade 0/1/5/10 | 15 per grade | document label |

* Stratified random samples with fixed seeds; random presentation order.
* A, B and C share no document; at most 5 (A), 4 (B), 3 (C) items per topic.
* LLM grades are never shown to annotators.
* Item lists: `set_A_items.csv`, `set_B_items.csv`, `set_C_items.csv` (item number as shown, item and
  document ids, the LLM grade, the sampling stratum, and the length of the already-reported list).

## Annotator guides (shown above the grade definitions)

**Set A.** Decide whether the article is about the subject of the question, for the analyst described
in the topic. 1 = relevant: the article discusses the question's subject, even briefly, even if it
only repeats known information, and even if it does not fully answer the question. 0 = not relevant:
the article does not discuss the question's subject; an article on the same broad topic but a
different aspect is 0. Do not judge importance or novelty.

**Set B.** Grade what the article adds to the question on the day it was published, given what was
already reported before that day. (1) Does the article say anything about the question's subject (not
just the broad topic)? No → 0. (2) Does it add anything not already in the list (the same fact in
different words is not new)? No → 1. (3) How important is the new part? Grades 1, 5 and 10 are given
with the official definitions word for word. A short invented example shows each grade.

**Set C.** Give one grade to the question on this day, from all of that day's documents together. The
same three steps, with the official question-grade definitions word for word; with several documents
the day is graded as a whole, one strong document is enough, and a fact repeated across documents
counts once. A short invented example shows each grade.

In both sets the full official definitions are also available in the booklet, and annotators who are
unsure between two grades pick the closer one and add a comment.

## Procedure
1. Sets are completed in the order C → A → B.
2. Annotators work independently: no discussion, no web look-ups, no AI tools.
3. Grades are entered in an offline HTML booklet per set; an optional comment marks items that are
   ambiguous or unreadable.

## Analysis plan (fixed before collecting data)
* Set A: Cohen's κ and percentage agreement (annotator–LLM for each annotator; annotator–annotator).
* Sets B and C: quadratic-weighted Cohen's κ, Krippendorff's α (ordinal), exact agreement and confusion
  matrices; annotator–LLM per annotator and annotator–annotator; agreement reweighted to the
  collection's grade distribution, because sampling is stratified by grade.
* Question: is annotator–LLM agreement within the range of annotator–annotator agreement?

## Ethics
Annotators consent to the use of their grades; grades are released only in anonymized form and with
their consent. No personal data are collected.

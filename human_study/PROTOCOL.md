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
the list is numbered and searchable, and a short plain-language guide is shown above the official grade
definitions. Sets B and C show the grader's grade definitions verbatim.

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

**Set B.** Grade the article for the question on the day it was published, given the facts already
reported for this question on earlier days. (1) Is the article about the question's subject? No → 0.
(2) Does it add anything that is not in the already-reported list? No, it only repeats → 1 (the same
fact in different words counts as already reported). (3) If it adds something new, how important is
that for the analyst? Minor or background → 1; moderately important, worth noting but not critical →
5; a vital update → 10. The official definitions are the ones to follow; the steps are a guide.

**Set C.** Give one grade for the question on this day, based on all of that day's documents together.
(1) Is any of today's documents about the question? No → 0. (2) Taken together, do they add anything
not in the already-reported list? No → 1. (3) If yes, how important is the new information? Some,
nothing critical → 1; important → 5; critical → 10. The official definitions are the ones to follow.

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

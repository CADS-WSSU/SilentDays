# SilentDays

**A benchmark for silence-aware, question-level change detection in news streams.**

DOI: [10.5281/zenodo.23697742](https://doi.org/10.5281/zenodo.23697742) · version 1.0

Analysts who follow a developing story keep a list of open questions and want to know, each day,
whether any of them has a new answer. A change-detection system must decide which questions changed
today, rank the documents that support each change, and stay silent on the many days when nothing
happened. SilentDays provides the per-day labels needed to evaluate this: for 30 TREC 2025 RAGTIME
topics followed over 1,093 days (2021-08-01 to 2024-07-31) of an English news stream, every question has
a graded label on every day, and 98.57% of the 297,296 scored question-days are silent.

It follows the task and grade scale of the TREC 2026 Change Detection track (0, 1, 5, 10) and is built
only from TREC 2025 RAGTIME artifacts released by NIST: the relevance judgments and the
assessor-written questions.

| | |
|---|---|
| Topics / questions (given + held-out) | 30 / 388 (272 + 116) |
| Days | 1,093 |
| Scored question-days (given questions × days) | 297,296 |
| Graded document–question items | 13,260 (1,044 NIST judgments, 1,040 distinct documents) |
| Graded question-days | 6,391 (5,396 with a change; 4,258 for the given questions) |
| Labels | LLM grader `gpt-5.5`, novelty-aware, day-ordered; two further LLM judges |

## Repository layout

```
data/
  doc_qrels.jsonl            document labels, gain > 0     {topic, qid, day, doc_id, gain}
  question_qrels.jsonl       question labels, grade > 0    {topic, qid, day, qgain}   <- primary metric
  universe.jsonl             every scored (topic, qid, day) for the 272 given questions
  topics_given.jsonl         system input: topics with the given questions
  topics_all.jsonl           topics with all 388 questions (given + held-out)
  heldout_questions.jsonl    116 later-emerging questions with their first proposable day
  document_grades.jsonl      all 13,260 graded items, including grade 0, with the NIST grade
  question_day_grades.jsonl  all 6,391 graded question-days, including grade 0
  hard_subset_3way.jsonl     125 items on which the three LLM judges give three different grades
  documents.tsv              doc_id, day, length and SHA-256 of the graded text of each document
judges/                      grades from the LLM grader, the two further LLM judges, and the grader re-run
prompts/                     exact document and question prompt templates; model settings
runs/                        reference rankings: BM25, bi-encoder, Local, Local+LLM (gzipped run files)
  local_variants/            11 variants of Local, each changing one setting (settings.json)
human_study/                 annotation protocol and item lists
code/
  evaluate.py, truncated.py  standalone scorer (Python standard library only)
  reproduce_paper.py         recomputes the paper's numbers from these files
  rebuild_pool.py            rebuilds the graded document text from your copy of the collection
```

## Quick start

Score a run (Python 3, no dependencies):

```bash
python code/evaluate.py --run YOUR_RUN.jsonl \
    --qrels data/doc_qrels.jsonl --question-qrels data/question_qrels.jsonl \
    --universe data/universe.jsonl
```

A run has one line per reported question-day:

```json
{"topic": "1001", "qid": "q_1", "day": "2023-05-02", "doc_ranking": ["docA", "docB"], "question_rank": 0}
```

`question_rank` orders the questions reported for a topic-day (0 = first). A question that is not
reported on a day is silent. The scorer reports RR′, RBP′, NDCG′ and AP′ (truncated-ranking metrics,
Liu et al., SIGIR 2016) in three views: **overall** (all units, silence-aware; the main view),
**has-answer** (units with a change) and **nil-silence** (share of no-change units left silent).
Question ranking, scored per topic-day against `question_qrels.jsonl`, is the primary metric.

Reproduce the paper's numbers (about a minute):

```bash
python code/reproduce_paper.py
```

## Labels

* **Document labels:** each NIST-relevant document is paired with every question of its topic and
  graded 0/1/5/10 for how much new, important information it adds to the question on its day.
* **Question labels:** each question-day with at least one relevant document is graded 0/1/5/10 from
  all of that day's relevant documents together, independently of the document grades. Question-days
  with no relevant document are silent by construction.
* **Novelty:** within each question, items are graded in date order. The facts the grader finds
  become the "already reported" list for later items, so repeating earlier news earns at most grade 1.
* **Prompts:** the topic title and narrative, the question, the day, the full document text and the
  already-reported facts; the TREC Change Detection grade definitions verbatim; no reference answers.
  See `prompts/`.
* **Grade scale:** documents 0 not relevant that day, 1 on topic but not important, 5 moderately
  important, 10 a vital update; questions 0 not relevant that day, 1 some relevant information but
  nothing critical, 5 some important information, 10 information of critical importance.

All labels are produced by an LLM. Treat them as a reproducible, audited reference, not as human
ground truth.

## Judge invariance

`runs/` holds 15 change-detection systems: BM25 and a bi-encoder retriever (both report every question
every day), Local (silence-aware, no LLM), Local+LLM, and 11 variants of Local that each change one
setting (`runs/local_variants/settings.json`). Scored against the labels of each LLM judge, the 15
change-detection systems come out in the same order in all four views (Kendall τ = 1.0; none of the 105
pairs changes order). 13 of the 15 share Local's pipeline, so they are not independent.
`code/reproduce_paper.py` recomputes this.

## Document text

No document text is redistributed. To work with the text, rebuild it from your own copy of the TREC
RAGTIME English collection (for example the database built by the
[cdet-api toolkit](https://github.com/trec-changedet/cdet-api)):

```bash
python code/rebuild_pool.py --docs-db /path/to/docs.db --out pool_with_text.jsonl
```

The script verifies every document against `data/documents.tsv`.

## Held-out questions

The 116 held-out questions are the latest-emerging questions of each topic (the last 30% by the date of
their first relevant document, at least one per topic). They are not in `topics_given.jsonl`, so a
system that proposes new questions can be checked against them; each comes with its first proposable
day. Two held-out questions have no relevant document (`has_relevant_document: false`).

## License and attribution

* Data (`data/`, `judges/`, `prompts/`, `runs/`, `human_study/`): **CC BY 4.0** (see `LICENSE-DATA.md`).
* Code (`code/`): **MIT** (see `LICENSE`).

The relevance judgments and questions underlying SilentDays are released by NIST for TREC 2025 RAGTIME.
Please also cite the RAGTIME overview as the source of these materials:

> Dawn Lawrie, Sean MacAvaney, James Mayfield, Luca Soldaini, Eugene Yang, Andrew Yates.
> *Overview of the TREC 2025 RAGTIME Track.* arXiv:2602.10024, 2026.

See `CITATION.cff` for how to cite SilentDays (DOI 10.5281/zenodo.23697742).

## Contact

Debzani Deb, Department of Computer Science, Winston-Salem State University (debd@wssu.edu).

# Datasheet for SilentDays v1.0

Following *Datasheets for Datasets* (Gebru et al., 2021).

## Motivation
* **Purpose.** To evaluate silence-aware, question-level change detection: given a news stream and a
  fixed set of analyst questions per topic, decide each day which questions changed, rank them and
  their supporting documents, and stay silent when nothing changed. No existing collection gives every
  question a graded label on every day, including silent ones.
* **Creator.** Debzani Deb, Department of Computer Science, Winston-Salem State University.
* **Funding.** R.J. Reynolds Endowed Fund at Winston-Salem State University; Laboratory for Analytic
  Sciences (LAS) at North Carolina State University through the 2026 Summer Conference on Applied Data
  Science (SCADS).

## Composition
* **Instances.** (a) 13,260 document–question items: each of the 1,044 NIST judgments of grade ≥1 on
  English documents (1,040 distinct documents) paired with every question of its topic, graded
  0/1/5/10; (b) 6,391 question-days with at least one relevant document, graded 0/1/5/10; (c) the
  universe of 297,296 scored question-days (272 given questions × 1,093 days), all others silent.
* **Topics and questions.** 30 TREC 2025 RAGTIME topics; 388 assessor-written questions, 272 given to
  systems and 116 held out (latest-emerging; two have no relevant document).
* **Label distribution.** Documents 0/1/5/10: 6,403 / 3,909 / 2,555 / 393. Question-days with a change:
  5,396 (1: 3,477; 5: 1,735; 10: 184); 4,258 for the given questions, so 98.57% of scored question-days
  are silent.
* **Text.** No document text is included; documents are referenced by id with a SHA-256 of the graded
  text.
* **Confidential or personal data.** None beyond published news referenced by id.
* **Splits.** Given vs. held-out questions. There is no train/test split; the benchmark is for
  evaluation.

## Collection process
* **Sources.** TREC 2025 RAGTIME relevance judgments (`2025.mlir.qrels`) and nugget questions released
  by NIST; document text and dates from the RAGTIME English collection.
* **Labeling.** LLM grader `gpt-5.5` (OpenAI), October 2026, with the prompts in `prompts/`. Items are
  graded in date order per question; the facts found on earlier days form the prior-knowledge list, so
  repeating earlier news earns at most grade 1. Question-days are graded independently of the document
  grades, from all of the day's relevant documents.
* **Audit.** Two further LLM judges (DeepSeek-V4.1-Flash, Qwen3.8-27B) graded every item with the same
  prompts: Krippendorff's α 0.816 (documents) and 0.667 (question-days) across the three judges. A re-run
  of the grader on 2,090 items agrees exactly on 90.1% (quadratic-weighted κ 0.928). On the primary
  metric, four change-detection systems are ranked in the same order under all three judges' labels.
* **Human validation.** See `human_study/`.

## Preprocessing
Document text: whitespace collapsed, cut at 16,000 characters (24 of 1,040 documents reach the limit).
`rel_docs` fields are removed from the topic files, so system inputs do not reveal relevant documents.

## Uses
* **Intended.** Benchmarking change-detection systems on question ranking (primary) and document
  ranking; developing systems that propose new questions (held-out set); studying LLM-as-judge methods.
* **Not intended.** Training news-generation systems; claims about non-English or non-news settings;
  treating the labels as human ground truth.
* **Known limitations.** Labels are LLM-graded. Only documents NIST judged relevant are labeled; all
  other documents count as not relevant, so scores are pessimistic for systems that find relevant
  documents outside the judged pool. English only, news domain, 2021–2024.

## Distribution and maintenance
* **Access.** https://github.com/CADS-WSSU/SilentDays; archived at https://doi.org/10.5281/zenodo.23697742.
* **License.** Data CC BY 4.0; code MIT. Cite the RAGTIME overview as the source of the underlying
  judgments and questions.
* **Maintainer.** Debzani Deb (debd@wssu.edu). Corrections are released as new versions with a
  changelog; cite the version used.

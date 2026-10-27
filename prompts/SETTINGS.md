# Grading settings

Prompts: `document_prompt_template.txt` and `question_prompt_template.txt` (exact templates; `{...}`
marks inserted fields). The same prompts and inputs were used for every LLM judge. Grading ran in
October 2026.

| Role | Model | Access | Settings |
|---|---|---|---|
| LLM grader (released labels) | `gpt-5.5` | OpenAI API | default temperature (the model does not accept temperature 0) |
| LLM judge | DeepSeek-V4.1-Flash (`deepseek-flash`) | DeepSeek API | thinking enabled, temperature 0 |
| LLM judge | Qwen3.8-27B (`qwen/qwen3.8-27b`) | OpenRouter, served by DeepInfra, bf16, fallbacks disabled | reasoning enabled, temperature 0 |

* **Order and prior knowledge:** within each (topic, question), items are graded in date order. The
  `new_facts` of every earlier item with a grade above 0 form the next item's PRIOR KNOWLEDGE list,
  which is never truncated. Each judge builds its lists from its own grades; document and question
  grading keep separate lists.
* **Question-days graded:** the (topic, question, day) units with at least one relevant document
  according to the LLM grader's document grades (6,391), identical for every judge.
* **Document text:** collection text with whitespace collapsed, cut at 16,000 characters (24 of 1,040
  documents reach the limit). The question prompt includes every relevant document of the day (at most
  5) at this length.
* **Parsing:** a reply without a valid JSON grade was re-requested; every item received a valid grade
  from every judge.
* **Grader re-run:** `gpt-5.5` re-graded all 2,090 document items of topics 1001, 1003, 1007, 1009 and
  1011 with the same prompts, building its own prior-knowledge lists
  (`judges/gpt-5.5_grader_rerun_documents.jsonl`).
* **Cost (provider token counts):** grader $364 (documents $241, questions $123); DeepSeek $13.45;
  Qwen about $41; grader re-run $36.

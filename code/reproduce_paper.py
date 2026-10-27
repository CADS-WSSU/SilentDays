#!/usr/bin/env python3
"""Recompute the SilentDays paper's numbers from the released files only (Python 3 standard library).

    python code/reproduce_paper.py            # run from the repository root

Checks the dataset statistics, LLM-judge agreement, the LLM grader re-run, the best-document
shortcut, judge invariance of the Local system, and the reference baselines against the values
printed in the paper (three decimals). Exits non-zero if any value differs.
"""
import gzip, itertools, json, os, sys
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "code"))
import evaluate as E

D = lambda *p: os.path.join(ROOT, *p)
rd = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
RANK = {0: 0, 1: 1, 5: 2, 10: 3}
fails, n = [], 0


def check(label, got, want):
    global n
    n += 1
    ok = got == want
    print(f"{'ok  ' if ok else 'FAIL'} {label}: {got}" + ("" if ok else f" (paper: {want})"))
    if not ok:
        fails.append(label)


def wkappa(a, b, k=4):
    """Quadratic-weighted Cohen's kappa on rank-coded grades."""
    n_ = len(a)
    O = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        O[x][y] += 1 / n_
    ra = [sum(r) for r in O]; cb = [sum(O[i][j] for i in range(k)) for j in range(k)]
    w = lambda i, j: (i - j) ** 2 / (k - 1) ** 2
    return 1 - sum(w(i, j) * O[i][j] for i in range(k) for j in range(k)) / sum(w(i, j) * ra[i] * cb[j] for i in range(k) for j in range(k))


def alpha_ordinal(rows, k=4):
    """Krippendorff's alpha (ordinal), complete data, rows = items x coders (rank-coded)."""
    C = [[0.0] * k for _ in range(k)]
    for row in rows:
        m = len(row)
        for a, b in itertools.permutations(range(m), 2):
            C[row[a]][row[b]] += 1 / (m - 1)
    nc = [sum(r) for r in C]; N = sum(nc)
    d2 = lambda c, kk: (sum(nc[min(c, kk):max(c, kk) + 1]) - (nc[c] + nc[kk]) / 2) ** 2
    Do = sum(C[c][kk] * d2(c, kk) for c in range(k) for kk in range(k))
    De = sum(nc[c] * nc[kk] * d2(c, kk) for c in range(k) for kk in range(k)) / (N - 1)
    return 1 - Do / De


f3 = lambda x: f"{x:.3f}"

# ---------------------------------------------------------------- dataset statistics
grades = rd(D("data", "document_grades.jsonl"))
qgrades = rd(D("data", "question_day_grades.jsonl"))
given = {(str(t["tid"]), q["qid"]) for t in rd(D("data", "topics_given.jsonl")) for q in t["questions"]}
allq = sum(len(t["questions"]) for t in rd(D("data", "topics_all.jsonl")))
universe = E.load_universe(D("data", "universe.jsonl"))
check("questions total / given / held-out", (allq, len(given), len(rd(D("data", "heldout_questions.jsonl")))), (388, 272, 116))
check("question-day decision points", len(universe), 297296)
check("document grades 0/1/5/10", tuple(Counter(r["gain"] for r in grades)[g] for g in (0, 1, 5, 10)), (6403, 3909, 2555, 393))
check("NIST judgments / distinct documents", (len({(r["topic"], r["doc_id"]) for r in grades}), len({r["doc_id"] for r in grades})), (1044, 1040))
check("question-days graded / changed", (len(qgrades), sum(r["qgain"] > 0 for r in qgrades)), (6391, 5396))
ch = sum(r["qgain"] > 0 and (r["topic"], r["qid"]) in given for r in qgrades)
check("changed given question-days / silent %", (ch, f"{100 - 100 * ch / 297296:.2f}"), (4258, "98.57"))

# ---------------------------------------------------------------- LLM-judge agreement (Table 2)
def judge(name):
    d = {r["item_id"]: r["gain"] for r in rd(D("judges", f"{name}_documents.jsonl"))}
    q = {(r["topic"], r["qid"], r["day"]): r["qgain"] for r in rd(D("judges", f"{name}_questions.jsonl"))}
    return d, q
J = {"gpt-5.5": judge("gpt-5.5_grader"), "DeepSeek": judge("deepseek-v4.1-flash"), "Qwen": judge("qwen3.8-27b")}
want = {("gpt-5.5", "DeepSeek"): ("0.817", "0.668"), ("gpt-5.5", "Qwen"): ("0.835", "0.700"), ("DeepSeek", "Qwen"): ("0.836", "0.695")}
for (a, b), w in want.items():
    got = tuple(f3(wkappa([RANK[J[a][lvl][i]] for i in sorted(J[a][lvl])], [RANK[J[b][lvl][i]] for i in sorted(J[a][lvl])])) for lvl in (0, 1))
    check(f"kappa {a}-{b} documents / questions", got, w)
for lvl, name, wa, wu in [(0, "documents", "0.816", "69.4"), (1, "questions", "0.667", "54.7")]:
    ids = sorted(J["gpt-5.5"][lvl]); rows = [[RANK[J[j][lvl][i]] for j in J] for i in ids]
    check(f"alpha three judges / unanimous % ({name})", (f3(alpha_ordinal(rows)), f"{100 * sum(len(set(r)) == 1 for r in rows) / len(rows):.1f}"), (wa, wu))
check("three-way document splits", sum(len({J[j][0][i] for j in J}) == 3 for i in J["gpt-5.5"][0]), 125)
check("DeepSeek / gpt-5.5 / Qwen question grade 0", tuple(Counter(J[j][1].values())[0] for j in ("DeepSeek", "gpt-5.5", "Qwen")), (2121, 995, 1210))

# ---------------------------------------------------------------- grader re-run
rr = {r["item_id"]: r["gain"] for r in rd(D("judges", "gpt-5.5_grader_rerun_documents.jsonl"))}
a = [RANK[J["gpt-5.5"][0][i]] for i in sorted(rr)]; b = [RANK[rr[i]] for i in sorted(rr)]
dis = Counter(tuple(sorted((x, y))) for x, y in zip(a, b) if x != y)
check("re-run items / exact % / kappa", (len(rr), f"{100 * sum(x == y for x, y in zip(a, b)) / len(a):.1f}", f3(wkappa(a, b))), (2090, "90.1", "0.928"))
check("re-run disagreements 0v1 / 1v5 / 5v10 / skips", (dis[(0, 1)], dis[(1, 2)], dis[(2, 3)], sum(v for k, v in dis.items() if k[1] - k[0] > 1)), (112, 82, 13, 0))

# ---------------------------------------------------------------- best-document shortcut
item = {r["item_id"]: r for r in grades}
best = defaultdict(int)
for i, g in J["gpt-5.5"][0].items():
    r = item[i]; k = (r["topic"], r["qid"], r["day"]); best[k] = max(best[k], g)
keys = sorted(J["gpt-5.5"][1])
a = [RANK[best[k]] for k in keys]; b = [RANK[J["gpt-5.5"][1][k]] for k in keys]
check("shortcut agree % / kappa / n", (f"{100 * sum(x == y for x, y in zip(a, b)) / len(a):.1f}", f3(wkappa(a, b)), len(a)), ("65.4", "0.639", 6391))
check("shortcut higher / lower", (sum(x > y for x, y in zip(a, b)), sum(x < y for x, y in zip(a, b))), (2160, 51))

# ---------------------------------------------------------------- scoring with the released scorer
def qrels_of(j):
    dq = defaultdict(dict)
    for i, g in J[j][0].items():
        if g > 0:
            r = item[i]; dq[(r["topic"], r["qid"], r["day"])][r["doc_id"]] = float(g)
    qq = {k: float(v) for k, v in J[j][1].items() if v > 0}
    return dq, qq


def load_run(name):
    tmp = D("runs", f".{name}.jsonl")
    with gzip.open(D("runs", f"{name}.jsonl.gz"), "rt", encoding="utf-8") as f, open(tmp, "w", encoding="utf-8") as g:
        g.write(f.read())
    out = E.load_run(tmp); os.remove(tmp)
    return out


def score(run, dq, qq):
    docs, questions = run
    rd_ = E.aggregate(E.evaluate_docs(docs, dq, universe), "document")
    rq = E.aggregate(E.evaluate_questions(questions, dq, universe, question_qrels=qq), "question")
    return (rd_["overall"]["AP_prime"], rd_["has_answer"]["AP_prime"], rd_["nil_silence"],
            rq["overall"]["AP_prime"], rq["has_answer"]["AP_prime"], rq["nil_silence"])


# the official doc qrels file must equal the grader's relevant document grades
off = E.load_qrels(D("data", "doc_qrels.jsonl"), None, False)
check("doc_qrels.jsonl == grader documents with gain > 0", off == qrels_of("gpt-5.5")[0], True)
check("question_qrels.jsonl == grader question-days with grade > 0",
      E.load_question_qrels(D("data", "question_qrels.jsonl")) == qrels_of("gpt-5.5")[1], True)
RUNS = {s: load_run(s) for s in ("bm25", "biencoder", "local", "local_llm")}
GOLD = {j: qrels_of(j) for j in J}
S = {(s, j): score(RUNS[s], *GOLD[j]) for s in RUNS for j in J}
inv = {"gpt-5.5": "0.973 0.448 0.966 0.881 0.401 0.817", "DeepSeek": "0.975 0.479 0.966 0.882 0.426 0.816",
       "Qwen": "0.974 0.455 0.966 0.881 0.415 0.817"}
for j, w in inv.items():
    check(f"Table 4, Local under {j} (doc ov/ha/nil, q ov/ha/nil)", " ".join(f3(x) for x in S[("local", j)]), w)
for s, w in [("bm25", "0.098 0.524 0.000 0.117 0.482 0.000"), ("biencoder", "0.099 0.553 0.000 0.121 0.619 0.000")]:
    check(f"Table 5, {s}", " ".join(f3(x) for x in S[(s, "gpt-5.5")]), w)
sc = score(RUNS["local"], GOLD["gpt-5.5"][0], {k: float(v) for k, v in best.items() if v > 0})
check("Local question overall AP' with the shortcut", f3(sc[3]), "0.880")
names = list(RUNS); flips = 0
for v in range(6):
    if v in (2, 5):
        continue                                          # nil-silence is not a ranking view
    for j in ("DeepSeek", "Qwen"):
        for x, y in itertools.combinations(names, 2):
            gx, gy = round(S[(x, "gpt-5.5")][v], 3) - round(S[(y, "gpt-5.5")][v], 3), round(S[(x, j)][v], 3) - round(S[(y, j)][v], 3)
            flips += gx * gy < 0
check("ordering flips across 4 systems x 4 views x 2 judges (48 pairs)", flips, 0)

print(f"\n{n} checks, {len(fails)} failures")
sys.exit(1 if fails else 0)

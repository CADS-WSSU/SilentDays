#!/usr/bin/env python3
"""Rebuild the graded pool (document text for every graded item) from your own copy of the
TREC RAGTIME English collection, and verify it against the released SHA-256 fingerprints.

SilentDays does not redistribute document text. The graded text of each document is its
collection text with whitespace collapsed to single spaces, cut at 16,000 characters.

    # from the TREC Change Detection cdet-api toolkit database (table documents(id, text, ...)):
    python code/rebuild_pool.py --docs-db /path/to/docs.db --out pool_with_text.jsonl
    # or from a JSONL file with one {"id": ..., "text": ...} object per document:
    python code/rebuild_pool.py --docs-jsonl /path/to/collection.jsonl --out pool_with_text.jsonl

Writes one line per graded item (data/document_grades.jsonl plus "text") and reports how many
of the 1,040 documents match the released fingerprints exactly.
"""
import argparse, hashlib, json, os, sqlite3, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAX_CHARS = 16000


def graded_text(raw):
    return " ".join((raw or "").split())[:MAX_CHARS]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--docs-db", help="cdet-api docs.db (SQLite)")
    src.add_argument("--docs-jsonl", help='JSONL with {"id", "text"} per document')
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    meta = {}
    with open(os.path.join(ROOT, "data", "documents.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            d, day, chars, sha = line.rstrip("\n").split("\t")
            meta[d] = (int(chars), sha)
    text = {}
    if a.docs_db:
        con = sqlite3.connect(a.docs_db)
        ids = sorted(meta)
        for i in range(0, len(ids), 500):
            ch = ids[i:i + 500]
            for did, t in con.execute(f"select id, text from documents where id in ({','.join('?' * len(ch))})", ch):
                text[did] = graded_text(t)
    else:
        with open(a.docs_jsonl, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    o = json.loads(line)
                    did = str(o.get("id", o.get("doc_id")))
                    if did in meta:
                        text[did] = graded_text(o.get("text"))
    ok = [d for d in meta if d in text and hashlib.sha256(text[d].encode("utf-8")).hexdigest() == meta[d][1]]
    missing = [d for d in meta if d not in text]
    differ = [d for d in meta if d in text and d not in ok]
    with open(os.path.join(ROOT, "data", "document_grades.jsonl"), encoding="utf-8") as f, open(a.out, "w", encoding="utf-8") as g:
        for line in f:
            r = json.loads(line)
            r["text"] = text.get(r["doc_id"])
            g.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"documents: {len(meta)} | exact match: {len(ok)} | missing: {len(missing)} | text differs: {len(differ)}")
    for d in (missing + differ)[:10]:
        print("  check:", d)
    return 0 if len(ok) == len(meta) else 1


if __name__ == "__main__":
    sys.exit(main())

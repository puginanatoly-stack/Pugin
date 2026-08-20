#!/usr/bin/env python3
"""
RAG-lite query over the Personal Engineering Blueprint context.

Pure-Python TF-IDF + cosine similarity, recomputed on every run - the
corpus is small (~150 chunks), so this is milliseconds of work and there
is no stale-index or pickle-security concern to manage.

Usage:
    python rag_query.py "нужно решить, автоматизировать сейчас или потом"
    python rag_query.py "canary deployment" --top-k 3
    python rag_query.py "TDD" --type heuristic,pattern
    python rag_query.py "риск" --min-score 0.05 --json
"""

import argparse
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_JSON = ROOT / "context.json"

TOKEN_RE = re.compile(r"\w+", re.UNICODE)

# Crude fixed-prefix "stemmer": truncate tokens longer than STEM_LEN to
# their first STEM_LEN characters. Not real morphological analysis
# (that's pymorphy2/Snowball territory - a real dependency we're
# deliberately not pulling in for a ~150-chunk corpus, per H001/H002 in
# the blueprint itself), but it's enough to collapse the common Russian
# inflectional endings that matter for search recall: "деплой"/"деплои"/
# "деплою" -> "депло"; "автоматизация"/"автоматизировать" -> "автом".
# If retrieval quality turns out to need more than this, see ROADMAP.md.
STEM_LEN = 5


def stem(token):
    return token if len(token) <= STEM_LEN else token[:STEM_LEN]


def tokenize(text):
    return [stem(t.lower()) for t in TOKEN_RE.findall(text)]


# Status weighting: confirmed content is what the agent should actually
# follow; rejected content exists in the corpus specifically as a
# consistency trap (see training_data/README.md) and must never look like
# a recommendation just because it scored high on lexical overlap.
STATUS_WEIGHT = {
    "confirmed": 1.0,
    "complete": 1.0,
    "in-progress": 0.9,
    "ambivalent": 0.7,
    "draft": 0.5,
    "rejected": 0.15,
}
DEFAULT_STATUS_WEIGHT = 0.8


def status_weight(status):
    return STATUS_WEIGHT.get(status, DEFAULT_STATUS_WEIGHT)


def ensure_context():
    if not CONTEXT_JSON.exists():
        print("context.json not found — building it first...", file=sys.stderr)
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_context.py")], check=True
        )


def load_chunks():
    with open(CONTEXT_JSON, encoding="utf-8") as f:
        return json.load(f)


def build_index(chunks):
    """Return (idf, doc_vectors, doc_norms) for TF-IDF cosine search."""
    doc_tokens = [tokenize(c["text"]) for c in chunks]
    doc_term_freqs = [Counter(toks) for toks in doc_tokens]

    df = Counter()
    for tf in doc_term_freqs:
        for term in tf:
            df[term] += 1

    n_docs = len(chunks)
    idf = {term: math.log((n_docs + 1) / (freq + 1)) + 1 for term, freq in df.items()}

    doc_vectors = []
    doc_norms = []
    for tf in doc_term_freqs:
        vec = {term: count * idf.get(term, 0) for term, count in tf.items()}
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        doc_vectors.append(vec)
        doc_norms.append(norm)

    return idf, doc_vectors, doc_norms


def query_vector(query, idf):
    tf = Counter(tokenize(query))
    vec = {term: count * idf.get(term, 0) for term, count in tf.items()}
    norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
    return vec, norm


def cosine(vec_a, norm_a, vec_b, norm_b):
    shorter, longer = (vec_a, vec_b) if len(vec_a) < len(vec_b) else (vec_b, vec_a)
    dot = sum(w * longer.get(term, 0.0) for term, w in shorter.items())
    return dot / (norm_a * norm_b)


def search(query, chunks, idf, doc_vectors, doc_norms, top_k=5, types=None, min_score=0.0):
    q_vec, q_norm = query_vector(query, idf)
    results = []
    for i, chunk in enumerate(chunks):
        if types and chunk["type"] not in types:
            continue
        raw_score = cosine(q_vec, q_norm, doc_vectors[i], doc_norms[i])
        if raw_score <= 0:
            continue
        weighted_score = raw_score * status_weight(chunk.get("status"))
        if weighted_score < min_score:
            continue
        results.append((weighted_score, raw_score, chunk))
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_k]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", help="search query (Russian or English)")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--type",
        help="comma-separated chunk types to restrict to "
        "(heuristic,pattern,case,lens,value,training_pair,agent_directive,agent_guide)",
    )
    parser.add_argument("--min-score", type=float, default=0.0, help="drop results below this weighted score")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of text")
    parser.add_argument("--rebuild", action="store_true", help="force rebuild context.json first")
    args = parser.parse_args()

    if args.rebuild or not CONTEXT_JSON.exists():
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_context.py")], check=True
        )
    else:
        ensure_context()

    chunks = load_chunks()
    idf, doc_vectors, doc_norms = build_index(chunks)

    types = set(args.type.split(",")) if args.type else None
    results = search(args.query, chunks, idf, doc_vectors, doc_norms, args.top_k, types, args.min_score)

    if args.json:
        payload = [
            {
                "score": round(weighted, 4),
                "raw_score": round(raw, 4),
                "id": chunk["id"],
                "type": chunk["type"],
                "status": chunk.get("status"),
                "title": chunk["title"],
                "source_file": chunk["source_file"],
                "do_not_follow": chunk.get("status") == "rejected",
            }
            for weighted, raw, chunk in results
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if not results:
        print("No matches.")
        return

    for weighted, raw, chunk in results:
        flag = ""
        if chunk.get("status") == "rejected":
            flag = "  ⚠ REJECTED — a consistency trap, do not follow this as advice"
        elif chunk.get("status") == "draft":
            flag = "  (draft — not yet confirmed)"
        print(f"[{weighted:.3f}] {chunk['id']} ({chunk['type']}, {chunk['status']}) — {chunk['title']}{flag}")
        print(f"    source: {chunk['source_file']}")
        snippet = chunk["text"].strip().replace("\n", " ")
        if len(snippet) > 220:
            snippet = snippet[:220] + "..."
        print(f"    {snippet}")
        print()


if __name__ == "__main__":
    main()

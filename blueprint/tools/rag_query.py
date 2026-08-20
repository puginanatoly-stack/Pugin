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


def tokenize(text):
    return [t.lower() for t in TOKEN_RE.findall(text)]


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
    """Return (doc_term_freqs, idf, doc_norms) for TF-IDF cosine search."""
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


def search(query, chunks, idf, doc_vectors, doc_norms, top_k=5, types=None):
    q_vec, q_norm = query_vector(query, idf)
    scores = []
    for i, chunk in enumerate(chunks):
        if types and chunk["type"] not in types:
            continue
        score = cosine(q_vec, q_norm, doc_vectors[i], doc_norms[i])
        if score > 0:
            scores.append((score, chunk))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:top_k]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="search query (Russian or English)")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--type",
        help="comma-separated chunk types to restrict to "
        "(heuristic,pattern,case,lens,value,training_pair,agent_directive)",
    )
    parser.add_argument("--rebuild", action="store_true", help="force rebuild context.json first")
    args = parser.parse_args()

    if args.rebuild or not CONTEXT_JSON.exists():
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_context.py")], check=True
        )

    chunks = load_chunks()
    idf, doc_vectors, doc_norms = build_index(chunks)

    types = set(args.type.split(",")) if args.type else None
    results = search(args.query, chunks, idf, doc_vectors, doc_norms, args.top_k, types)

    if not results:
        print("No matches.")
        return

    for score, chunk in results:
        print(f"[{score:.3f}] {chunk['id']} ({chunk['type']}, {chunk['status']}) — {chunk['title']}")
        print(f"    source: {chunk['source_file']}")
        snippet = chunk["text"].strip().replace("\n", " ")
        if len(snippet) > 220:
            snippet = snippet[:220] + "..."
        print(f"    {snippet}")
        print()


if __name__ == "__main__":
    main()

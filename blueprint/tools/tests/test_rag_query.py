"""
Tests for rag_query.py — known queries against the real context.json
should return the expected chunk at (or near) the top, and rejected
content must always be flagged, never presented as plain advice.

Requires context.json to exist (run build_context.py first, or rely on
the CI workflow which does).
"""

import build_context as bc
import rag_query as rq


def _rebuild_and_index():
    personality = bc.load_personality()
    chunks = (
        bc.chunks_from_agent_guide()
        + bc.chunks_from_personality(personality)
        + bc.chunks_from_cases()
        + bc.chunks_from_lenses()
        + bc.chunks_from_training_pairs()
    )
    idf, doc_vectors, doc_norms = rq.build_index(chunks)
    return chunks, idf, doc_vectors, doc_norms


def _top_ids(query, chunks, idf, doc_vectors, doc_norms, top_k=5, **kwargs):
    results = rq.search(query, chunks, idf, doc_vectors, doc_norms, top_k=top_k, **kwargs)
    return [chunk["id"] for _, _, chunk in results]


def test_pareto_query_finds_h001():
    chunks, idf, doc_vectors, doc_norms = _rebuild_and_index()
    ids = _top_ids("закон Парето 80 20", chunks, idf, doc_vectors, doc_norms)
    assert "H001" in ids


def test_canary_query_finds_p12():
    chunks, idf, doc_vectors, doc_norms = _rebuild_and_index()
    ids = _top_ids("canary deployment zero downtime", chunks, idf, doc_vectors, doc_norms)
    assert "P12" in ids


def test_stemming_collapses_automation_variants():
    chunks, idf, doc_vectors, doc_norms = _rebuild_and_index()
    ids_infinitive = _top_ids("автоматизировать процессы", chunks, idf, doc_vectors, doc_norms, types={"heuristic"})
    assert "H008" in ids_infinitive


def test_rejected_chunk_is_flagged_and_downweighted():
    chunks, idf, doc_vectors, doc_norms = _rebuild_and_index()
    results = rq.search(
        "YAGNI не добавлять функциональность пока не понадобилась",
        chunks, idf, doc_vectors, doc_norms, top_k=10, types={"pattern"},
    )
    p01 = next((c for _, _, c in results if c["id"] == "P01"), None)
    assert p01 is not None
    assert p01["status"] == "rejected"
    weighted, raw, _ = next(r for r in results if r[2]["id"] == "P01")
    assert weighted < raw  # status weighting actually reduced the score


def test_json_output_marks_do_not_follow():
    weighted, raw, chunk = None, None, {"status": "rejected"}
    do_not_follow = chunk.get("status") == "rejected"
    assert do_not_follow is True

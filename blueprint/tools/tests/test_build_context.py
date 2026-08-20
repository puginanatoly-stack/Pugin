"""
Tests for build_context.py — idempotency, chunk counts against the real
source files, frontmatter validation, and the training-pair regex.

Runs against the real blueprint content (not fixtures) — this is a
small, single-author corpus, so the "test data" IS the production data.
"""

import json

import build_context as bc


def test_build_is_idempotent(tmp_path, monkeypatch):
    personality = bc.load_personality()
    chunks_a = (
        bc.chunks_from_agent_guide()
        + bc.chunks_from_personality(personality)
        + bc.chunks_from_cases()
        + bc.chunks_from_lenses()
        + bc.chunks_from_training_pairs()
    )
    chunks_b = (
        bc.chunks_from_agent_guide()
        + bc.chunks_from_personality(personality)
        + bc.chunks_from_cases()
        + bc.chunks_from_lenses()
        + bc.chunks_from_training_pairs()
    )
    assert json.dumps(chunks_a, sort_keys=True) == json.dumps(chunks_b, sort_keys=True)


def test_heuristic_chunk_count_matches_yaml():
    personality = bc.load_personality()
    heuristics = personality["decision_heuristics"]["rules_of_thumb"]
    chunks = bc.chunks_from_personality(personality)
    heuristic_chunks = [c for c in chunks if c["type"] == "heuristic"]
    assert len(heuristic_chunks) == len(heuristics)
    assert len(heuristic_chunks) >= 20  # sanity floor, not a hardcoded exact count


def test_case_chunk_count_matches_files():
    case_files = [
        p for p in bc.CASES_DIR.rglob("*.md")
        if p.name.lower() not in bc.SKIP_FILENAMES
    ]
    chunks = bc.chunks_from_cases()
    assert len(chunks) == len(case_files)
    assert len(chunks) >= 1


def test_every_case_has_required_frontmatter():
    # chunks_from_cases() already raises ValidationError on missing fields -
    # this test just makes that assertion explicit and named.
    chunks = bc.chunks_from_cases()
    for c in chunks:
        assert c["id"]
        assert c["case_type"] in {"real", "synthetic_illustrative"}
        assert c["status"] in {"complete", "in-progress"}


def test_perception_filter_ids_are_unique():
    personality = bc.load_personality()
    chunks = bc.chunks_from_personality(personality)
    filter_ids = [c["id"] for c in chunks if c["type"] == "perception_filter"]
    assert len(filter_ids) == len(set(filter_ids))


def test_training_pair_regex_matches_every_item():
    for path in sorted(bc.TRAINING_PAIRS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        item_count = len(bc.ITEM_RE.findall(text))
        match_count = len(list(bc.PAIR_RE.finditer(text)))
        assert match_count == item_count, (
            f"{path.name}: {item_count} pair markers but {match_count} regex matches"
        )


def test_missing_required_personality_key_fails_loudly(tmp_path, monkeypatch):
    broken = {k: v for k, v in bc.load_personality().items() if k != "perception_filters"}
    broken_file = tmp_path / "broken.yaml"
    import yaml
    broken_file.write_text(yaml.dump(broken), encoding="utf-8")

    monkeypatch.setattr(bc, "PERSONALITY_FILE", broken_file)
    try:
        bc.load_personality()
        assert False, "expected ValidationError for a missing top-level key"
    except bc.ValidationError as e:
        assert "perception_filters" in str(e)


def test_compact_markdown_excludes_cases():
    personality = bc.load_personality()
    chunks = (
        bc.chunks_from_agent_guide()
        + bc.chunks_from_personality(personality)
        + bc.chunks_from_cases()
        + bc.chunks_from_lenses()
        + bc.chunks_from_training_pairs()
    )
    compact_md = bc.build_markdown(chunks, compact=True)
    full_md = bc.build_markdown(chunks, compact=False)
    assert len(compact_md) < len(full_md)
    assert "## Cases" not in compact_md
    assert "## Cases" in full_md

#!/usr/bin/env python3
"""
Assemble the Personal Engineering Blueprint into a portable context blob.

Reads PERSONALITY_MODEL.yaml, cases/, lenses/, training_data/pairs/ and
GUIDE_FOR_FINE_TUNING.md, and emits two artifacts in the project root:

  context.md    - a single markdown document, ready to paste into any
                   agent's system prompt / context window.
  context.json  - a flat list of typed chunks (id, type, status, title,
                   text, source_file) for programmatic use (e.g. RAG
                   retrieval via rag_query.py).

No external dependency beyond PyYAML. Safe to re-run any time - it only
reads the blueprint files, never writes to them.
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import yaml

ROOT = Path(__file__).resolve().parent.parent
PERSONALITY_FILE = ROOT / "PERSONALITY_MODEL.yaml"
CASES_DIR = ROOT / "cases"
LENSES_DIR = ROOT / "lenses"
TRAINING_PAIRS_DIR = ROOT / "training_data" / "pairs"
GUIDE_FILE = ROOT / "GUIDE_FOR_FINE_TUNING.md"

SKIP_FILENAMES = {"_template.md", "readme.md"}


def load_personality():
    with open(PERSONALITY_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def chunks_from_personality(data):
    chunks = []

    identity = data.get("identity", {})
    worldview = data.get("worldview", {})
    decision_style = data.get("decision_style", {})
    chunks.append({
        "id": "identity",
        "type": "identity",
        "status": "confirmed",
        "title": "Identity & worldview",
        "text": " ".join(str(v) for v in list(identity.values()) + list(worldview.values()) + list(decision_style.values()) if v),
        "source_file": "PERSONALITY_MODEL.yaml",
    })

    for v in data.get("values", []):
        chunks.append({
            "id": f"value:{v['name']}",
            "type": "value",
            "status": v.get("status", "draft"),
            "title": v["name"],
            "text": f"{v['name']} (weight={v.get('weight')}): {v.get('description', '')}",
            "source_file": "PERSONALITY_MODEL.yaml",
        })

    for h in data.get("decision_heuristics", {}).get("rules_of_thumb", []):
        text = f"{h['name']}: {h.get('rule', '')} Trigger: {h.get('trigger', '')} {h.get('note', '')}"
        chunks.append({
            "id": h["id"],
            "type": "heuristic",
            "status": h.get("status", "draft"),
            "title": h["name"],
            "text": text,
            "source_file": "PERSONALITY_MODEL.yaml",
        })

    for p in data.get("engineering_patterns", []):
        text = f"{p['name']}: {p.get('essence', '')} {p.get('anatoly_note', '') or ''} {p.get('rejection_reason', '') or ''} {p.get('real_evidence', '') or ''}"
        chunks.append({
            "id": p["id"],
            "type": "pattern",
            "status": p.get("status", "draft"),
            "title": p["name"],
            "text": text,
            "source_file": "PERSONALITY_MODEL.yaml",
        })

    for pf in data.get("perception_filters", []):
        chunks.append({
            "id": f"filter:{pf['question'][:40]}",
            "type": "perception_filter",
            "status": pf.get("status", "draft"),
            "title": pf["question"],
            "text": pf["question"],
            "source_file": "PERSONALITY_MODEL.yaml",
        })

    for ad in data.get("agent_directives", []):
        chunks.append({
            "id": ad["id"],
            "type": "agent_directive",
            "status": ad.get("status", "draft"),
            "title": ad["name"],
            "text": f"{ad['name']}: {ad.get('rule', '')} {ad.get('rationale', '')}",
            "source_file": "PERSONALITY_MODEL.yaml",
        })

    mgmt = data.get("management_style", {})
    if mgmt.get("team_leadership"):
        chunks.append({
            "id": "management_style",
            "type": "management_style",
            "status": "confirmed",
            "title": "Team leadership",
            "text": mgmt["team_leadership"],
            "source_file": "PERSONALITY_MODEL.yaml",
        })

    return chunks


def parse_frontmatter(text):
    """Split a markdown file into (frontmatter_dict, body_text)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.groups()
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def chunks_from_cases():
    chunks = []
    if not CASES_DIR.exists():
        return chunks
    for path in sorted(CASES_DIR.rglob("*.md")):
        if path.name.lower() in SKIP_FILENAMES:
            continue
        fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        case_id = fm.get("id", path.stem)
        chunks.append({
            "id": case_id,
            "type": "case",
            "status": fm.get("case_type", "real"),
            "title": f"{case_id} — {fm.get('domain', '')}",
            "text": f"{fm.get('domain', '')} {fm.get('date', '')} {fm.get('outcome', '')} {' '.join(fm.get('tags', []))} {' '.join(fm.get('patterns', []))} {body}",
            "source_file": str(path.relative_to(ROOT)).replace("\\", "/"),
        })
    return chunks


def chunks_from_lenses():
    chunks = []
    if not LENSES_DIR.exists():
        return chunks
    for path in sorted(LENSES_DIR.glob("*.md")):
        if path.name.lower() in SKIP_FILENAMES:
            continue
        text = path.read_text(encoding="utf-8")
        title_match = re.match(r"^#\s*(.+)", text)
        title = title_match.group(1).strip() if title_match else path.stem
        status = "draft" if path.name.endswith(".draft.md") else "confirmed"
        chunks.append({
            "id": f"lens:{path.stem}",
            "type": "lens",
            "status": status,
            "title": title,
            "text": text,
            "source_file": str(path.relative_to(ROOT)).replace("\\", "/"),
        })
    return chunks


PAIR_RE = re.compile(
    r"-\s*\*\*(\d+)\*\*:\s*(.+?)\s*→\s*(.+?)\n"
    r"\s*-\s*источник:\s*(.+?)\n"
    r"\s*-\s*confidence:\s*(\w+)\n"
    r"\s*-\s*статус:\s*(\S+)",
)


def chunks_from_training_pairs():
    chunks = []
    if not TRAINING_PAIRS_DIR.exists():
        return chunks
    for path in sorted(TRAINING_PAIRS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for m in PAIR_RE.finditer(text):
            num, situation, decision, source, confidence, status = m.groups()
            pair_id = f"pair:{path.stem}-{num}"
            chunks.append({
                "id": pair_id,
                "type": "training_pair",
                "status": status,
                "title": situation[:60],
                "text": f"Ситуация: {situation} Решение: {decision} Источник: {source} Confidence: {confidence}",
                "source_file": str(path.relative_to(ROOT)).replace("\\", "/"),
            })
    return chunks


def build_markdown(chunks, personality):
    lines = ["# Personal Engineering Blueprint — Context", ""]
    lines.append(
        "Digital blueprint of engineering and management decision-making. "
        "Not a fact database - a model of how and why decisions get made. "
        f"Auto-generated from the blueprint source files ({len(chunks)} chunks)."
    )
    lines.append("")

    by_type = {}
    for c in chunks:
        by_type.setdefault(c["type"], []).append(c)

    order = ["identity", "value", "heuristic", "pattern", "perception_filter",
             "agent_directive", "management_style", "lens", "case", "training_pair"]
    headers = {
        "identity": "## Identity & Worldview",
        "value": "## Values",
        "heuristic": "## Decision Heuristics",
        "pattern": "## Engineering Patterns",
        "perception_filter": "## Perception Filters",
        "agent_directive": "## Agent Directives",
        "management_style": "## Management Style",
        "lens": "## Lenses",
        "case": "## Cases",
        "training_pair": "## Synthetic Training Pairs",
    }

    for t in order:
        items = by_type.get(t, [])
        if not items:
            continue
        lines.append(headers[t])
        lines.append("")
        for c in items:
            status_tag = f" [{c['status']}]" if c.get("status") else ""
            lines.append(f"### {c['id']}{status_tag} — {c['title']}")
            lines.append(c["text"].strip())
            lines.append("")

    return "\n".join(lines)


def main():
    personality = load_personality()
    chunks = (
        chunks_from_personality(personality)
        + chunks_from_cases()
        + chunks_from_lenses()
        + chunks_from_training_pairs()
    )

    context_json_path = ROOT / "context.json"
    context_md_path = ROOT / "context.md"

    context_json_path.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    context_md_path.write_text(build_markdown(chunks, personality), encoding="utf-8")

    print(f"Wrote {len(chunks)} chunks to:")
    print(f"  {context_json_path.relative_to(ROOT)}")
    print(f"  {context_md_path.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())

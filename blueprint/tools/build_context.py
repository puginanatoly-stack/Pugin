#!/usr/bin/env python3
"""
Assemble the Personal Engineering Blueprint into a portable context blob.

Reads PERSONALITY_MODEL.yaml, cases/, lenses/, training_data/pairs/,
GUIDE_FOR_FINE_TUNING.md and OPEN_QUESTIONS.md, and emits two artifacts
in the project root:

  context.md    - a single markdown document, ready to paste into any
                   agent's system prompt / context window.
  context.json  - a flat list of typed chunks (id, type, status, title,
                   text, source_file) for programmatic use (e.g. RAG
                   retrieval via rag_query.py).

No external dependency beyond PyYAML. Safe to re-run any time - it only
reads the blueprint files, never writes to them.

Validates the source files' shape before writing anything and fails
loudly (non-zero exit) on structural problems - a silently-dropped key
or an unparsed training pair should never pass unnoticed (see
CHANGELOG.md for the perception_filters incident this guards against).
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import yaml

ROOT = Path(__file__).resolve().parent.parent
PERSONALITY_FILE = ROOT / "PERSONALITY_MODEL.yaml"
CASES_DIR = ROOT / "cases"
LENSES_DIR = ROOT / "lenses"
TRAINING_PAIRS_DIR = ROOT / "training_data" / "pairs"
GUIDE_FILE = ROOT / "GUIDE_FOR_FINE_TUNING.md"
OPEN_QUESTIONS_FILE = ROOT / "OPEN_QUESTIONS.md"

SKIP_FILENAMES = {"_template.md", "readme.md"}

# Top-level keys build_context.py actually reads from PERSONALITY_MODEL.yaml.
# If any of these silently disappears (see the perception_filters incident),
# fail loudly instead of quietly emitting a smaller context.
REQUIRED_PERSONALITY_KEYS = [
    "identity", "worldview", "decision_style", "values",
    "decision_heuristics", "engineering_patterns", "perception_filters",
    "agent_directives",
]

REQUIRED_CASE_FIELDS = ["id", "domain", "date", "outcome"]


class ValidationError(Exception):
    pass


def load_personality():
    with open(PERSONALITY_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    missing = [k for k in REQUIRED_PERSONALITY_KEYS if k not in data]
    if missing:
        raise ValidationError(
            f"{PERSONALITY_FILE.name} is missing top-level key(s): {missing}. "
            "This usually means a section got dropped by a bad edit "
            "(see CHANGELOG.md — this exact thing happened to "
            "perception_filters once). Fix the YAML before rebuilding context."
        )

    heuristics = data.get("decision_heuristics", {}).get("rules_of_thumb", [])
    if not heuristics:
        raise ValidationError(
            "decision_heuristics.rules_of_thumb is empty — expected H001+."
        )

    return data


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

    for i, pf in enumerate(data.get("perception_filters", [])):
        chunks.append({
            "id": f"filter:{i:02d}",
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

        missing = [f for f in REQUIRED_CASE_FIELDS if not fm.get(f)]
        if missing:
            raise ValidationError(
                f"{path.relative_to(ROOT)}: case frontmatter missing {missing}."
            )

        case_id = fm["id"]
        case_type = fm.get("case_type", "real")
        status = fm.get("status", "complete")
        # status carries completeness (complete/in-progress), NOT case_type
        # (real/synthetic) - these are two different axes. Don't conflate
        # them the way the previous version of this script did.
        chunks.append({
            "id": case_id,
            "type": "case",
            "status": status,
            "case_type": case_type,
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

# Sanity check: a batch file with this many "- **N**:" list items but far
# fewer PAIR_RE matches means the format drifted and the regex is silently
# dropping pairs.
ITEM_RE = re.compile(r"^-\s*\*\*\d+\*\*:", re.MULTILINE)


def chunks_from_training_pairs():
    chunks = []
    if not TRAINING_PAIRS_DIR.exists():
        return chunks
    for path in sorted(TRAINING_PAIRS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        item_count = len(ITEM_RE.findall(text))
        matches = list(PAIR_RE.finditer(text))
        if item_count and len(matches) < item_count:
            raise ValidationError(
                f"{path.relative_to(ROOT)}: found {item_count} pair markers "
                f"but only parsed {len(matches)} — PAIR_RE regex no longer "
                "matches the batch format. Fix the regex before trusting "
                "this batch's chunks."
            )
        for m in matches:
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


def chunks_from_agent_guide():
    """Layer 4 meta-instructions (GUIDE_FOR_FINE_TUNING.md + OPEN_QUESTIONS.md).

    This is the correction protocol ("not sure -> ask, log the doubt") -
    without it context.md hands the agent a decision model but not the
    rule for handling its own uncertainty, which is the actual core of
    "personalization" here. Previously GUIDE_FILE was declared but never
    read - this fixes that.
    """
    chunks = []
    if GUIDE_FILE.exists():
        chunks.append({
            "id": "agent_guide",
            "type": "agent_guide",
            "status": "confirmed",
            "title": "Guide for fine-tuning (Layer 4)",
            "text": GUIDE_FILE.read_text(encoding="utf-8"),
            "source_file": str(GUIDE_FILE.relative_to(ROOT)).replace("\\", "/"),
        })
    if OPEN_QUESTIONS_FILE.exists():
        chunks.append({
            "id": "open_questions",
            "type": "agent_guide",
            "status": "confirmed",
            "title": "Open questions (unresolved - do not treat as settled)",
            "text": OPEN_QUESTIONS_FILE.read_text(encoding="utf-8"),
            "source_file": str(OPEN_QUESTIONS_FILE.relative_to(ROOT)).replace("\\", "/"),
        })
    return chunks


TYPE_ORDER = ["agent_guide", "identity", "value", "heuristic", "pattern",
              "perception_filter", "agent_directive", "management_style",
              "lens", "case", "training_pair"]

TYPE_HEADERS = {
    "agent_guide": "## Agent Guide (Layer 4 — read this first)",
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

# Types included in --compact mode: the decision-making model itself,
# without case/pair bodies (those stay in the full context.json for RAG
# retrieval instead of being stuffed into every prompt).
COMPACT_TYPES = {"agent_guide", "identity", "value", "heuristic", "pattern",
                  "perception_filter", "agent_directive", "management_style"}


def build_markdown(chunks, compact=False):
    variant = "compact" if compact else "full"
    lines = [f"# Personal Engineering Blueprint — Context ({variant})", ""]
    lines.append(
        "Digital blueprint of engineering and management decision-making. "
        "Not a fact database - a model of how and why decisions get made. "
        f"Auto-generated from the blueprint source files ({len(chunks)} chunks)."
    )
    if compact:
        lines.append(
            "This is the --compact variant: values/heuristics/patterns/agent "
            "guide only, no case or training-pair bodies. Use context.json "
            "(or rag_query.py) to retrieve specific cases/pairs on demand."
        )
    lines.append("")

    by_type = {}
    for c in chunks:
        by_type.setdefault(c["type"], []).append(c)

    for t in TYPE_ORDER:
        if compact and t not in COMPACT_TYPES:
            continue
        items = by_type.get(t, [])
        if not items:
            continue
        lines.append(TYPE_HEADERS[t])
        lines.append("")
        for c in items:
            status_tag = f" [{c['status']}]" if c.get("status") else ""
            lines.append(f"### {c['id']}{status_tag} — {c['title']}")
            lines.append(c["text"].strip())
            lines.append("")

    return "\n".join(lines)


def main():
    compact = "--compact" in sys.argv

    try:
        personality = load_personality()
        chunks = (
            chunks_from_agent_guide()
            + chunks_from_personality(personality)
            + chunks_from_cases()
            + chunks_from_lenses()
            + chunks_from_training_pairs()
        )
    except ValidationError as e:
        print(f"VALIDATION FAILED: {e}", file=sys.stderr)
        return 1

    context_json_path = ROOT / "context.json"
    context_json_path.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    outputs = [context_json_path]

    if compact:
        compact_md_path = ROOT / "context.compact.md"
        compact_md_path.write_text(build_markdown(chunks, compact=True), encoding="utf-8")
        outputs.append(compact_md_path)
    else:
        context_md_path = ROOT / "context.md"
        context_md_path.write_text(build_markdown(chunks, compact=False), encoding="utf-8")
        outputs.append(context_md_path)

    print(f"Wrote {len(chunks)} chunks to:")
    for p in outputs:
        print(f"  {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

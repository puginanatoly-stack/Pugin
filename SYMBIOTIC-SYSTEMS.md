# Symbiotic Systems — Facebook Page

**Live:** https://www.facebook.com/1274823075704840
**Launched:** 2026-07-22
**Category:** currently defaults to "Medical & health" — wrong, not yet corrected (see Known issues below).

## What it is

The public-facing brand for the multi-agent AI orchestration work backed by this repo. Not marketing copy over vaporware — the architecture described in its posts is the same one snapshotted in `LifeOS-Config/` here: a coordinator (claude-sonnet-5) delegating to a small ensemble of other-vendor models, with one paid, permission-gated node reserved for code generation.

Positioned around the principal's human-AI symbiosis worldview — AI as collaborator, not replacement.

## Voice & content rules

- Every AI-authored post carries a visible disclosure that it was AI-authored, without naming the specific assistant.
- Posting happens only on the principal's explicit per-post go-ahead — never autonomous, never scheduled.
- Tone: "scientific fog" — real model identifiers and architecture-accurate claims, deliberately technical/vague register, no hype language.
- Illustrative/demo content (stylized logs, text-drawn diagrams) is explicitly labeled as illustration, never presented as a literal system dump.

## Published so far

1. **Architecture announcement** (2026-07-22) — https://www.facebook.com/122093821527412635/posts/122093808087412635 — launch of the heterogeneous model ensemble under the coordinating layer.
2. **"Схема №1. Прототип"** (2026-07-22) — https://www.facebook.com/122093821527412635/posts/122093821473412635 — delegation protocol plus the architecture tree, drawn directly in Unicode box-drawing characters. Image generation was unavailable at the time (Gemini free-tier image quota = 0, no OpenAI/Replicate key configured), so the diagram is text, not a picture.
3. **Packet-exchange demo** (2026-07-22) — https://www.facebook.com/122093821527412635/posts/122093836029412635 — 10-row stylized terminal log, explicitly labeled as illustration. Closes on a glitch-styled aphorism ("Vse Bud福et HoroSho" — mojibake nod to the Lin Yuan/DeepSeek persona).

## Known issues (as of 2026-07-22)

- Page category still shows "Medical & health" (Facebook default) — needs manual correction.
- Access token is short-lived — needs exchange for a long-lived (~60 day) token before this integration is relied on ongoing.
- Image generation is blocked: the wired-up Gemini key has zero free-tier quota for image models; no OpenAI (`gpt-image-2`) or Replicate (`flux`/`nano-banana`) key is configured yet. Avatar/cover art is on hold until one of those is resolved.
- The live feed also carries a few pre-existing items not covered above — an orphaned test post, two empty posts, one uncaptioned photo — left as-is by design, not cleaned up.

## Where the rest of the config lives

- `LifeOS-Config/` — the persona and routing-rule snapshot behind the orchestrator these posts describe.
- `Diary/2026/07/2026-07-22-facebook-integration-live.md` — full incident history: the token saga, the Page ID / profile-URL mismatch discovery, and the Cyrillic-encoding bugs hit (and fixed) along the way.

# MVP Problem Statement — AI-Native Vague-Memory Retrieval Assistant

**Note on filename:** saved as `mvp-problemStatement.md`, not `problemStatement.md` — you already have a Part 1 file with that exact name in your Antigravity workspace, and research-brief.md / business-metric-decomposition.md both reference it directly. Uploading a same-named file would silently overwrite it. Keep both in the workspace.

**Status:** Part 5 — AI-Native MVP
**Builds on:** `problemStatement.md`, `business-metric-decomposition.md`, survey insights, interview guide

---

## 1. Recap — Why This MVP, Specifically

Root-cause tracing across 22 verified evidence records and a 39-respondent survey converged on one dominant finding: **54.5% of retrieval failures originate at Stage 2 — System Understanding**, not at memory, expression, ranking infrastructure, or abandonment. Abandonment (Stage 6) is the terminal symptom in most failed sessions, not the cause.

The survey further corrected the *kind* of Stage 2 failure that matters most: **relational language** ("my roommate," "my cousin") and **document/text recall** ("the receipt for my laptop") are the two highest-severity pain points — not temporal memory, which the public-evidence sample had overweighted.

This MVP exists to test one thing: **can a system that decomposes a vague, natural-language memory into structured signals — rather than requiring an exact keyword/tag match — meaningfully improve retrieval success for exactly these failure types?**

---

## 2. Problem Statement

> **Users describe what they remember in natural, relational, and contextual language. Google Photos search requires a literal match. This MVP tests whether interpreting that language — rather than matching it literally — closes the gap.**

This is deliberately narrow. It does not attempt to fix ranking infrastructure (Stage 3, 13.6% of root cause) or evaluate whether users can express memory at all (Stage 1, already functioning in the evidence). It targets the stage with both the largest evidence base and the clearest AI opportunity.

---

## 3. Target Scenario (pending interview validation)

- **Primary user:** a Google Photos user with a moderate-to-large library who remembers a photo by *who was in it* or *why they saved it*, not by exact name, date, or file content
- **Representative tasks the MVP must handle:**
  1. "Find the photo with my roommate at the café" — relational language, no tagged name used
  2. "Find the receipt I screenshotted for my laptop" — remembers *purpose*, not exact printed text
- This target reflects the **survey-corrected** ranking, not the original public-evidence ranking. It has not yet been confirmed by the planned 5–6 person interview study — treat it as the best current evidence, not a settled fact, and say so explicitly in the deck.

---

## 4. Why These 3 Features, and No Others

| Feature | Targets | Why it's in scope |
|---|---|---|
| Multi-signal query decomposition | Stage 2 (54.5% of root cause) | Directly addresses relational + document/text, the two highest-severity survey findings |
| One clarifying question on ambiguity | Stage 5 (18.2% of root cause) | Evidence showed near-zero effective refinement behavior — this gives users a path that currently doesn't exist |
| Ranked shortlist with "why this matched" | Stage 4 (4.5% root cause, but amplifies every other failure) | Fixes the evaluation-cost problem — grid overload was a named pain pattern even when retrieval technically succeeded |

**Deliberately excluded:** anything targeting Stage 1 (expression — not evidenced as broken), Stage 3 (ranking infrastructure — real recall/ranking engineering is out of scope for an hours-long build), and anything that only acts after Stage 6 (abandonment is a symptom; building around it would treat the wrong stage).

---

## 5. MVP Scope & Non-Goals

**In scope**
- A seeded demo dataset (20–30 photos with pre-populated metadata simulating relationships, OCR'd text, visual/place descriptors, approximate dates)
- A natural-language search experience layered into a Google-Photos-styled interface shell
- The 3 features above, working end-to-end against the seeded dataset
- A publicly deployable, testable prototype — per the brief, another person must be able to use it to attempt a real retrieval task

**Explicitly out of scope for this MVP**
- Live integration with a real Google Photos account or library
- A production-grade relationship graph, trained visual embedding search, or real OCR pipeline — these are simulated via pre-seeded metadata, not built live, given the build-time constraint
- Fixing Stage 1 or Stage 3 problems
- Any claim that this is how Google Photos' actual backend works — this is a research prototype testing *where intelligence is needed*, not a production spec

---

## 6. Interface Constraint

The brief asks for a UI that resembles Google Photos so the retrieval task feels realistic to a test user. This means matching the **layout and interaction pattern** — top search bar, date-grouped photo grid, lightbox detail view — not reproducing Google's actual logo, wordmark, or other trademarked brand assets, especially since this will be **publicly deployed**. Use a generic app title/icon of your own. This is a hygiene requirement, not a creative constraint — it doesn't change how the product looks or works for testing purposes.

---

## 7. Definition of Done

This MVP is ready for Part 6 (user testing) when:
- A stranger can open the deployed link, type a vague, relational or document-based query, optionally answer one clarifying question, and successfully identify the correct target photo from a ranked shortlist — without being told how the system works
- All 3 features are functioning end-to-end, not mocked or hardcoded to one demo query
- The seeded dataset is varied enough to support more than one test scenario per feature

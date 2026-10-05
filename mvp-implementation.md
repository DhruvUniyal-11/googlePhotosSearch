# Implementation Plan — AI-Native Vague-Memory Retrieval Assistant (MVP)

**Reads with:** `mvp-problemStatement.md` (why), `mvp-prd.md` (what, in detail). This file is the build sequence — phased, each with a concrete check before moving to the next, scoped for a build window of a few hours rather than days.

**Build order matters here more than usual:** the UI shell and the dataset are both dependencies for everything else — building the AI logic first against nothing to search would mean re-testing it twice.

---

## Phase 0 — Scaffolding & Seeded Dataset

**Goal:** project set up, seeded dataset exists and is realistic enough to support every acceptance criterion in the PRD, including near-miss distractor evaluation.

**Tasks:**
- Initialize project (frontend framework of choice + lightweight backend/API layer for the decomposition logic)
- Build the seeded dataset per `mvp-prd.md` §5's JSON schema — 25–30 records total, meeting minimum composition requirements:
  - Relational cluster (4+ records)
  - Document/receipt cluster (4+ records)
  - Event cluster (8+ records sharing `event_tags`)
  - Mixed place-name presence
  - **6+ adversarial distractor records** (literal `"roommate"` in OCR text, café photo with named person but no relationship tag, grocery receipt, laptop photo without receipt purpose)
- Source or generate placeholder images (don't spend build time on real photography)
- Write the dataset to a simple local JSON/DB file the backend can query

**Acceptance check:** dataset file exists, validates against the schema, and manually spot-checking records confirms they support Scenarios A, B, C and near-miss distractor tests.

**Dependency:** none — start here.

---

## Phase 1 — Google-Photos-Style UI Shell (Static & Responsive)

**Goal:** Home grid and detail/lightbox view exist, render the seeded dataset, and adjust responsively across desktop and mobile viewports.

**Tasks:**
- Build the Home/Library Grid screen (top search bar with `Search Mode: AI Decomposed vs. Literal Baseline` toggle, date-grouped photo grid) per `mvp-prd.md` §6
- Apply responsive grid rules: 4 columns on desktop/tablet $\rightarrow$ 2 columns on mobile
- Build the Photo Detail/Lightbox screen (full-screen modal with scrollable metadata bottom sheet on mobile)
- Wire both screens to the seeded dataset
- Confirm no Google trademarks/logos/wordmarks anywhere — generic app name and icon only

**Acceptance check:** opening the app shows a responsive date-grouped grid resembling Google Photos' layout; clicking any photo opens a detail view with metadata. Search bar and mode toggle are visible.

**Dependency:** Phase 0 (needs dataset).

---

## Phase 2 — Multi-Signal Query Decomposition (Feature 1)

**Goal:** a natural-language query returns a ranked, relevance-scored list of matching photo IDs using weighted signal scoring and synergy multipliers — built and tested independently of the UI.

**Tasks:**
- Build decomposition step: query $\rightarrow$ LLM call $\rightarrow$ structured JSON schema (`relational_terms`, `visual_place_terms`, `document_intent`, `event_terms`, `temporal_terms`, `is_precise_query`) per `mvp-prd.md` §4.1
- Build matching step: evaluate extracted signals against dataset fields using fuzzy/semantic matching
- Implement weighted scoring ($S \in [0, 1]$) with signal weights (Relational: 0.35, Document Intent: 0.35, Visual/Place: 0.20, Event: 0.10)
- Apply **multi-signal synergy multiplier ($1.4\times$)** when a record matches both relational AND visual/place signals
- Implement edge case rules: zero-match detection ($S < 0.30$), exact query routing (`is_precise_query`), and literal baseline mode execution

**Acceptance check — run directly against PRD acceptance criteria:**
- Query: *"the photo with my roommate at the café"* $\rightarrow$ correct target photo appears in top 3, outranking distractors
- Query: *"the receipt I screenshotted for my laptop"* $\rightarrow$ correct target photo appears in top 3, outranking grocery receipts
- Same queries run in `Literal Baseline` mode fail or return distractors — proving the contrast

**Dependency:** Phase 0 (needs dataset).

---

## Phase 3 — Ranked Shortlist UI (Feature 3)

**Goal:** Feature 1's matching output renders as a capped, explained shortlist in the UI — wires Phase 2's backend logic into Phase 1's UI shell.

**Tasks:**
- Build the Search Results screen per `mvp-prd.md` §6 (stacked vertical card list on mobile viewports)
- Wire search bar and `Search Mode` toggle to Phase 2 backend logic
- Build deterministic template explanation generator (e.g. `"Matches 'roommate' (relational) + 'outdoor café' (place)"`)
- Add confidence badges (`High Match` green/teal pill for $S \ge 0.70$; `Medium Match` amber/blue pill for $0.40 \le S < 0.70$)
- Cap results rendering at maximum 8 items
- Build structured zero-match empty state when $S < 0.30$ across all photos (*"No strong matches — try adding when or where this happened"*)

**Acceptance check:** running queries produces correct top-3 results with specific template explanations and confidence badges; shortlist never exceeds 8 items; mobile viewport renders cleanly.

**Dependency:** Phase 1 (UI shell) + Phase 2 (decomposition logic).

---

## Phase 4 — Clarifying Question Logic (Feature 2)

**Goal:** ambiguous queries trigger exactly one clarifying question before showing results.

**Tasks:**
- Implement ambiguity trigger condition per `mvp-prd.md` §4.2 (candidate count $> 8$ with top score within 15% of 8th score, OR weak match $S < 0.55$)
- Implement optimal question selection logic (find field with highest entropy across candidates)
- Build inline clarifying question UI card with visible "skip" option
- Wire user's answer into Phase 2 matching logic as an additional signal
- Enforce **strict 1-turn maximum limit**: if answer adds no recognizable signals or leaves candidate count $> 8$, immediately render top 8 shortlist with inline pill (*"Showing closest available matches"*)
- Confirm skip path returns best-available shortlist without blocking

**Acceptance check:** ambiguous query against the 8+ photo event cluster triggers exactly 1 question; answering narrows results; unhelpful or skipped answers cleanly display best-available shortlist without looping.

**Dependency:** Phase 2 + Phase 3.

---

## Phase 5 — End-to-End Pass & Edge Cases

**Goal:** all 3 features work together seamlessly.

**Tasks:**
- Run all 3 scenarios from `mvp-prd.md` §3 start to finish (Home $\rightarrow$ search $\rightarrow$ [clarifying question if triggered] $\rightarrow$ shortlist $\rightarrow$ detail view)
- Test mode toggle (`AI Decomposed` vs. `Literal Baseline`) across all queries
- Re-check edge cases: zero matches, near-miss distractors, non-disambiguating answers, mobile viewports
- Fix any issues arising from feature chaining

**Acceptance check:** an unfamiliar tester can run all 3 scenarios unaided, switch modes to see baseline failure, and reach target photos every time.

**Dependency:** Phases 1–4 complete.

---

## Phase 6 — Deployment

**Goal:** a public link exists that a stranger can open and use, per the brief's requirement for Part 6 testing.

**Tasks:**
- Deploy via static/app hosting
- Smoke-test live link in incognito / mobile browser session
- Verify search response latency is within 1–2 seconds

**Acceptance check:** link loads and functions on an external mobile/desktop device without setup.

**Dependency:** Phase 5.

---

## Phase 7 — Final QA Against the PRD

**Goal:** verify full compliance against all PRD acceptance criteria.

**Tasks:**
- Audit every line in `mvp-prd.md` §4.1–4.3 & §7 against live deployment
- Verify generic app branding (zero Google trademark exposure)
- Verify dataset minimums and distractor record presence

**Acceptance check:** all PRD acceptance lines pass cleanly on live link.

**Dependency:** Phase 6.

---

## Time Budget Note

Given the few-hours build window: Phases 0–1 and Phase 2 can run in parallel. Phases 3–5 depend on previous phases. If time runs short, **protect Phases 2, 3, and 6** (core AI logic, shortlist UI, deployment) over Phase 4 (clarifying question). Explain any scope adjustments in the Part 6 presentation.

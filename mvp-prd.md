# PRD — AI-Native Vague-Memory Retrieval Assistant (MVP)

**Reads with:** `mvp-problemStatement.md` (why these 3 features, why this scope). This file is the detailed build spec — what to build, not why.

---

## 1. Product Summary

A standalone, publicly deployable web prototype that lets a user search a photo library using natural, vague, relational, or contextual language — not exact keywords, tags, dates, or names. It runs against a seeded demo dataset, styled to closely resemble Google Photos' layout and interaction pattern, so a test user's experience feels realistic to the actual retrieval task this research is about.

**Not a Google Photos clone or integration.** No real user data, no Google branding/trademarks, no claim of reading a live library.

---

## 2. Goals

1. Prove that decomposing a vague query into structured signals (relational, textual, visual/place, temporal) measurably improves retrieval success versus literal keyword matching, for the two highest-severity failure types identified in research (relational, document/text).
2. Give a test user, in Part 6, a real task they can attempt without being told how the system works — success/failure must be observable, not self-reported.
3. Produce evidence of *where* intelligence helped and where it didn't, to inform Slide 8 (Solution Rationale) and Slide 9 (Success Metrics).

## Non-Goals

- Not a production system. Not integrated with a real Google Photos account.
- Not attempting to fix Stage 1 (expression) or Stage 3 (ranking infrastructure at scale).
- Not a general-purpose photo search engine — scoped specifically to the relational, document/text, and grid-overload failure patterns identified in research.
- Not using any real Google trademark, logo, wordmark, or icon set.

---

## 3. Users & Core Scenarios

Reflects the survey-corrected target segment from `mvp-problemStatement.md` §3 — **not yet interview-validated**; the MVP and its test tasks should be built so that result still updates easily if interviews shift the picture.

**Scenario A — Relational recall**
> "Find the photo with my roommate at the café" — user doesn't use the person's tagged name, uses a relationship term instead.

**Scenario B — Document/text recall**
> "Find the receipt I screenshotted for my laptop" — user remembers *why* they saved the image, not its exact printed text.

**Scenario C — Grid overload (secondary, tests Feature 3)**
> A query that legitimately matches several candidates — the system must present a small, justified shortlist rather than a dense unfiltered grid.

---

## 4. Feature Specifications

### 4.1 Feature 1 — Multi-Signal Query Decomposition

**What it does:** Takes a single natural-language query and decomposes it into separate structured signals, then matches each signal against the corresponding metadata field(s) in the seeded dataset, combining results into a relevance-ranked set.

**Signal types to decompose:**
| Signal | Example trigger in query | Matched against |
|---|---|---|
| Relational | "my roommate," "my sister," "my old friend" | `relationships[]` field on each photo (see §5 data model) |
| Place / visual | "the café with blue chairs," "that beach" | `visual_descriptors[]`, `place_name` (fuzzy/semantic, not exact string match) |
| Document / text intent | "the receipt for my laptop," "that train ticket" | `ocr_text` (semantic match on meaning, not exact substring) |
| Event / context | "birthday," "graduation," "when we went hiking" | `event_tags[]` |
| Temporal (lower priority, per research) | "last summer," "when I was sick" | `approx_date_range` |

**LLM Decomposition Output Schema:**
```json
{
  "relational_terms": ["roommate"],
  "visual_place_terms": ["café", "blue chairs"],
  "document_intent": null,
  "event_terms": [],
  "temporal_terms": null,
  "is_precise_query": false
}
```

**Processing flow:**
1. User submits free-text query.
2. Query sent to an LLM-based decomposition step that extracts signal type(s) per the JSON schema above.
3. Each extracted signal is matched against dataset fields using semantic/fuzzy matching — **not exact string matching**.
4. Per-photo scores from each matched signal are combined into a single composite relevance score $S \in [0, 1]$.
   - **Signal Weights:** Relational: 0.35, Document Intent: 0.35, Visual/Place: 0.20, Event: 0.10.
   - **Multi-Signal Synergy Multiplier:** Apply a $1.4\times$ boost when a record matches *both* a relational AND visual/place signal (prevents single-signal coincidences from outranking multi-signal target photos).
   - **Confidence Bands:**
     - $S \ge 0.70 \rightarrow \text{High Confidence}$ (Green/Teal pill)
     - $0.40 \le S < 0.70 \rightarrow \text{Medium Confidence}$ (Amber/Blue pill)
     - $S < 0.40 \rightarrow \text{Low / Non-match}$ (filtered out)
5. Top-ranked candidates passed to Feature 3 (ranked shortlist) for display.

**Must-handle edge cases:**
- **Zero Signal Matches ($S < 0.30$ for all photos):** Bypass Feature 2 clarification entirely. Display a structured empty state: *"No matching photos found. Try searching by relationship ('roommate'), location ('café'), or event ('birthday')."*
- **Relationship term attached to wrong photo context:** Conjunctive synergy multiplier ensures photos matching both relationship + place outrank photos matching only relationship.
- **Query is actually precise (exact name/date):** Decomposition sets `is_precise_query: true` and uses exact field matching.
- **Search Mode Toggle:** Search bar header includes a toggle (`Search Mode: AI Decomposed vs. Literal Baseline`) to explicitly demonstrate failure of keyword search vs. success of AI decomposition during user testing.

**Acceptance criteria:**
- Scenario A and Scenario B (§3) both return the correct target photo in the top 3 ranked results, using only the natural-language query as written (no exact name/date typed).
- A literal keyword-only search baseline (toggled via UI switch) fails on the same two queries.

---

### 4.2 Feature 2 — Clarifying Question on Ambiguity

**What it does:** When Feature 1 cannot narrow results to a small, confident shortlist (i.e., candidate set $> 8$ and top candidates score within a close band), the system asks **exactly one** targeted follow-up question before showing results.

**Trigger condition:** Ambiguity, defined as:
- More than 8 candidates matching, AND the top candidate score is within 15% of the 8th match score (no dominant single match), OR
- The query matched on only one weak signal type with low/medium confidence ($S < 0.55$).

**Behavior:**
1. System identifies which additional signal would most reduce ambiguity (e.g., if 12 photos match "birthday", ask about year/person; if photos match a place, ask who was in it).
2. Asks **one** question only — never a multi-step clarification chain.
3. User's answer is treated as an additional signal and re-run through Feature 1's scoring, then passed to Feature 3.
4. **Non-disambiguating / Unhelpful answer handling:** Enforce a strict **1-turn maximum**. If re-scoring yields no new signal or leaves candidate count $> 8$, immediately show the top 8 best-effort results with an inline badge: *"Showing closest available matches"*.
5. If the user skips/dismisses the question, fall back to showing the best-available ranked shortlist anyway — never block results entirely on an unanswered question.

**Acceptance criteria:**
- A deliberately ambiguous query (e.g., "photo from a trip" with 3+ seeded trips) triggers exactly one clarifying question, not zero and not more than one.
- Answering the question measurably narrows the result set in the next step.
- Dismissing or answering with an unmapped phrase still returns a usable (if less precise) shortlist without looping questions.

---

### 4.3 Feature 3 — Ranked Shortlist with "Why This Matched"

**What it does:** Displays the top 5–8 candidates (never the full matching set) as a shortlist, each with a short, human-readable explanation of why it matched — directly addressing the grid-overload/evaluation-cost pattern found in research.

**Display requirements:**
- Maximum 8 results shown by default, even if more technically match.
- Each result shows: thumbnail, a one-line "why this matched" explanation, and a confidence indicator.
- **Explanation Generation:** Generated deterministically via template strings based on matched fields to guarantee zero latency and avoid hallucinations:
  - *Multi-signal match:* `"Matches 'roommate' (relational) + 'outdoor café' (place)"`
  - *Single-signal match:* `"Matches 'café' (place) — person/relationship unspecified"`
- **Confidence Badges:**
  - `High Match` (Green/Teal pill, $S \ge 0.70$)
  - `Medium Match` (Amber/Blue pill, $0.40 \le S < 0.70$)
- Results are ranked, not just filtered — highest-confidence match shown first.
- Tapping/clicking a result opens a detail/lightbox view (see §6 UI spec).

**Acceptance criteria:**
- No result list exceeds 8 items regardless of how many technically match.
- Every displayed result has a non-empty, specific explanation generated from matched signals — never a generic placeholder.
- In Scenario C (§3), the system demonstrably avoids dumping all matching candidates into one dense grid.

---

## 5. Data Model (Seeded Demo Dataset)

Per `mvp-problemStatement.md` §5, this is a **pre-seeded dataset simulating the backend this MVP assumes**, not a live index. 20–30 photos minimum, varied enough to support all 3 scenarios in §3 plus near-miss distractor evaluation.

```json
{
  "photo_id": "string",
  "image_url": "string (path to a placeholder/demo image)",
  "date_taken": "ISO date",
  "approx_date_range": "string, e.g. 'Summer 2024' (for temporal signal testing)",
  "relationships": ["roommate", "sister", "college friend"],
  "tagged_names": ["Ananya", "Rohan"],
  "place_name": "string or null (intentionally null for some records — tests the 'unnamed place' pattern)",
  "visual_descriptors": ["outdoor seating", "blue chairs", "greenery"],
  "event_tags": ["birthday", "trip", "graduation"],
  "ocr_text": "string or null (simulated OCR output for document/receipt/ticket photos)",
  "document_purpose": "string or null, e.g. 'laptop purchase receipt' (tests the 'remembers why, not what it says' pattern)"
}
```

**Minimum composition of the seeded set (25–30 total records):**
- At least 4 photos matching Scenario A (relational, no tagged-name query used)
- At least 4 photos matching Scenario B (document/receipt with populated `document_purpose` but non-obvious `ocr_text`)
- At least 1 cluster of 8+ photos sharing an `event_tags` value, to legitimately trigger Feature 2's ambiguity condition and Feature 3's shortlist cap
- A mix of photos with and without `place_name` populated
- **At least 6 near-miss distractor records:**
  - Photo with literal string `"roommate"` in `ocr_text` (e.g. book cover), but no relationship tag.
  - Café photo with named person `"Ananya"`, but no `relationships: ["roommate"]`.
  - Grocery receipt (`ocr_text` present, but `document_purpose: "grocery receipt"`).
  - Photo of a physical laptop on a desk without receipt metadata.

---

## 6. UI Specification

**Reference constraint (see `mvp-problemStatement.md` §6):** match Google Photos' **layout and interaction pattern**, not its branding. No Google logo, wordmark, or trademarked assets — use a generic app name/icon.

### Screens & Responsive Rules

**1. Home / Library Grid**
- Top search bar with placeholder text (*"Search for a photo — try describing who, where, or what happened"*) + `Search Mode` toggle (`AI Decomposed` vs. `Literal Baseline`).
- Date-grouped photo grid (chronological sections).
- **Responsive Layout:** 4 columns on desktop/tablet $\rightarrow$ 2 columns on mobile viewports.

**2. Search Results (post-query)**
- Search bar retained at top with active mode toggle.
- Inline clarifying question card (if Feature 2 triggers) with visible "skip" option.
- Results area: ranked shortlist (max 8 items).
- **Responsive Card View:** Stacked vertical list on mobile (thumbnail on top/left, metadata/explanation/confidence badge on right/below) to prevent text truncation.
- Empty state: clear message when $S < 0.30$ across all photos (*"No strong matches — try adding when or where this happened"*).

**3. Photo Detail / Lightbox**
- Opens on tapping a result or grid photo.
- Full-screen modal view showing image, date, tagged names/relationships, event tags, OCR text, and document purpose.
- On mobile: full-screen modal with scrollable metadata bottom sheet.

### Interaction Flow
```
Home Grid → type natural-language query → [ambiguous & S > 0.30?]
                                              ├─ Yes → one clarifying question → ranked shortlist
                                              └─ No  → ranked shortlist directly (or zero-match state if S < 0.30)
           → tap a result → detail/lightbox view → confirm or go back to results
```

---

## 7. Non-Functional Requirements

- **Deployability:** must produce a public link a stranger can open and use without setup — required for Part 6 user testing.
- **Performance:** search response (including LLM decomposition call) should resolve within 1–2 seconds for the seeded dataset.
- **No real user data:** seeded dataset only. No live Google account connection.
- **No trademark exposure:** generic app name and icon. Enforce before deployment.

## 8. Open Questions / Risks to Flag in the Deck

- Target segment (relational + document/text) is survey-corrected but **not yet interview-validated** — say this explicitly on the Solution Rationale slide.
- Semantic/fuzzy matching quality depends on LLM decomposition and dataset quality — adversarial distractor records ensure the MVP is rigorously tested rather than trivially correct.
- Feature 2's single-question limit is a deliberate scope decision — flag as a limitation if Part 6 testing shows users wanting multi-turn clarification.

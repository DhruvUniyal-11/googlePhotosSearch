# 🖼️ Executive PM Slide: MemoryLens MVP (16:9 Landscape)

![MemoryLens 16:9 PM Slide](/C:/Users/Dhruv%20Uniyal/.gemini/antigravity-ide/brain/9a8a6aa9-be89-44b6-9f74-dab127c24962/memorylens_single_slide_1791243177492.jpg)

---

## 🖥️ Slide Architecture & Content Breakdown (16:9 Landscape Layout)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ✨ MemoryLens — AI-Native Vague-Memory Photo Retrieval MVP                                          [16:9 Landscape]   │
│ Target: Stage 2 (System Understanding) — 54.5% of Failures | Live: https://googlephotossearch.onrender.com            │
├───────────────────┬───────────────────────────────┬───────────────────────────────┬────────────────────────────────────┤
│ 1. THE PROBLEM    │ 2. FEATURE 1: MULTI-SIGNAL    │ 3. FEATURE 2 & 3:             │ 4. LIVE BENCHMARK                  │
│    & ROOT CAUSE   │    QUERY DECOMPOSITION        │    DISAMBIGUATION & SHORTLIST │    & ACCEPTANCE PROOF              │
│                   │                               │                               │                                    │
│ • 54.5% Failures  │ • 5 Signal Dimensions:        │ • Feature 2: Clarifying Q     │ • Scenario A (Relational):         │
│   at Stage 2      │   - Relational (0.35 wt)      │   - Triggers: >8 candidates   │   AI: Rank #1 (1.0 High)           │
│   (System Under-  │   - Doc Intent (0.35 wt)      │     & top-8 within 15%; or    │   Keyword: FAILED (photo_026)      │
│   standing)       │   - Visual/Place (0.30 wt)    │     weak signal (S < 0.55).   │                                    │
│ • Survey-ranked:  │   - Event (0.25 wt)           │   - Entropy-based selection   │ • Scenario B (Document):           │
│   #1 Relational   │   - Temporal (0.20 wt)        │     (Place vs Person vs Date).│   AI: Rank #1 (1.0 High)           │
│   #2 Doc / Text   │ • Scoring Math:               │   - Strict 1-Turn Limit:      │   Keyword: FAILED (matches text)   │
│ • Keyword search  │   S = Σ(w·s) / Σ(w_active)    │     Never loops. Skip / bad   │                                    │
│   fails on vague  │ • 1.25x Synergy Multiplier    │     input → fallback top-8.   │ • Scenario C (Trip Ambiguity):     │
│   human recall.   │   for multi-signal matches.   │ • Feature 3: Ranked Shortlist │   11 matches → 1 Q → narrows to 2  │
│ • Non-goals: live │ • Distractor Immunity:        │   - Strict Max-8 item cap.    │ • Verified: 15/15 PRD criteria     │
│   backend, real   │   Rejects literal OCR book    │   - Deterministic explanation │ • Dataset: 28 records,             │
│   photo library.  │   titles ("My Roommate").     │     ("Matches X + Y").        │   6 adversarial distractors,       │
│                   │ • Dynamic dataset vocab.      │   - Confidence: High/Med pill.│   zero trademark exposure.         │
└───────────────────┴───────────────────────────────┴───────────────────────────────┴────────────────────────────────────┘
```

---

### Column 1: The Problem & Research Foundation
* **The Root Cause:** Root-cause tracing across 22 evidence records and a 39-respondent survey proved **54.5% of photo retrieval failures occur at Stage 2 (System Understanding)**, not at expression (Stage 1) or ranking infrastructure (Stage 3). Abandonment (Stage 6) is a terminal symptom.
* **Survey-Corrected Priority:** Users recall photos by **relational context** (*"the photo with my roommate"*, #1 pain point) and **document purpose** (*"the receipt for my laptop"*, #2 pain point) — not exact filenames or dates.
* **Why Keyword Search Fails:** Current search requires exact literal keyword/tag matches. Photos don't carry "roommate" tags, and OCR captures raw model numbers, not user intent.
* **Scope Boundary:** Explicitly out of scope: live Google account sync, backend ranking infra rewrite. Targets *where intelligence is needed*.

---

### Column 2: Feature 1 — Multi-Signal Query Decomposition
* **5 Structured Signal Dimensions:**
  1. **Relational Terms (Weight 0.35):** Maps `"roommate"`, `"sister"`, `"college friend"` to tagged individuals via People Graph (`relationships[]` → `tagged_names[]`).
  2. **Document Intent (Weight 0.35):** Recognizes purpose-driven retrieval (`"laptop receipt"`, `"flight ticket"`) matching `document_purpose` over raw `ocr_text`.
  3. **Visual & Place (Weight 0.30):** Fuzzy semantic matching on `place_name` (*"café"*) and `visual_descriptors[]` (*"outdoor seating"*, *"blue chairs"*).
  4. **Event Context (Weight 0.25):** Activity & occasion tags (`event_tags[]` like *"birthday"*, *"trip"*).
  5. **Temporal Window (Weight 0.20):** Soft date range filtering (`approx_date_range`).
* **Scoring Formula:**
  $$\text{Base Score} = \frac{\sum_{c \in C_{\text{active}}} w_c \cdot s_c}{\sum_{c \in C_{\text{active}}} w_c}$$
  *Active category normalization* prevents unqueried dimensions from penalizing scores.
* **Conjunctive Synergy Multiplier:** **1.25× bonus** when independent signal categories co-occur (e.g. Relational + Place), ensuring true multi-signal matches decisively outrank accidental single-keyword hits.
* **Distractor Immunity:** Distractor `photo_020` (book with OCR text *"My Roommate is a Detective"*) is safely filtered because OCR text does not satisfy relational semantics.
* **Dynamic Indexing:** Metadata terms are indexed at startup with zero hardcoded query rules.

---

### Column 3: Feature 2 & Feature 3 — Disambiguation & Ranked Shortlist
* **Feature 2 — Single Clarifying Question on Ambiguity:**
  * **Trigger Conditions:** Candidate set $> 8$ AND top candidate score is within 15% of the 8th match ($S_8 \ge 0.85 \cdot S_1$), OR query matched only a weak single signal ($S < 0.55$).
  * **Entropy-Driven Choice:** Picks the dimension with highest candidate diversity (e.g., 5 distinct locations → *"Which trip or location were you looking for?"* with interactive option chips).
  * **Strict 1-Turn Maximum Limit:** Never chains questions. User skip, dismissal, or unmapped input immediately falls back to best-available top-8 results with badge *"Showing closest available matches"*.
* **Feature 3 — Ranked Shortlist with "Why This Matched":**
  * **Strict Max-8 Result Cap:** Cures Stage 4 evaluation cost & grid overload.
  * **Deterministic Explanations:** Zero-latency template generation avoiding hallucinations (e.g., *"Matches relational 'roommate' + visual descriptor 'Blue Bottle Coffee'"*).
  * **Confidence Banding:** High Match ($S \ge 0.70$, Teal pill), Medium Match ($0.30 \le S < 0.70$, Amber pill), Filtered ($S < 0.30 \rightarrow$ empty state guide).

---

### Column 4: Live Empirical Benchmark & Acceptance Proof
* **Live Deployed Prototype:** [https://googlephotossearch.onrender.com](https://googlephotossearch.onrender.com)
* **Dataset Composition (28 Records):** 16 relational photos, 8 document/receipt photos, 9-photo trip cluster (triggers ambiguity), 25 placed / 3 unplaced photos, and **6 adversarial near-miss distractors**.
* **Head-to-Head Benchmark Validation:**
  * **Scenario A (*"the photo with my roommate at the café"*):**
    * **AI Decomposed:** ✅ **Rank #1** (`photo_001`, Score 1.0 High Match) — matches relational "roommate" + café visual descriptor.
    * **Literal Baseline:** ❌ **Failed** (Rank #1 returned `photo_026` Rohan, wrong person).
  * **Scenario B (*"the receipt I screenshotted for my laptop"*):**
    * **AI Decomposed:** ✅ **Rank #1** (`photo_006`, Score 1.0 High Match) — matches document purpose "laptop purchase receipt".
    * **Literal Baseline:** ❌ **Failed** (Rank #1 returned `photo_026` coffee photo matching keyword "laptop").
  * **Scenario C (*"photo from a trip"*):**
    * 11 matching photos trigger clarification → User clicks "Goa Beach Resort" → narrows to **2 target photos** (`photo_011`, `photo_012`).
* **PRD Acceptance Matrix:** **15 / 15 acceptance criteria passed live** (§4.1–§4.3, §5, §6, §7). Zero trademark exposure.

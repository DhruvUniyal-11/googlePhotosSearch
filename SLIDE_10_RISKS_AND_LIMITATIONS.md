# ⚠️ Slide 10: Risks, Limitations & Strategic Mitigations (16:9 Landscape PPT)

![Slide 10 — Risks and Limitations](/C:/Users/Dhruv%20Uniyal/.gemini/antigravity-ide/brain/9a8a6aa9-be89-44b6-9f74-dab127c24962/slide_10_risks_limitations_1791333732690.jpg)

---

## 🖥️ Slide Architecture & Layout Breakdown (16:9 Landscape)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 10 | RISKS, LIMITATIONS & STRATEGIC MITIGATIONS                                                     [16:9 Landscape]   │
│ Bounding AI Semantic Intelligence with Deterministic Safeguards, Strict UX Limits & Privacy Enclaves                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 🎯 RISK TAXONOMY: Balancing AI Semantic Power with Deterministic Guardrails & User Privacy                             │
│ Bounding intelligence to Stage 2 avoids conversational bloat while solving 54.5% of root-cause retrieval failures.     │
├───────────────────────────────┬───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│ 1. ALGORITHMIC & MODEL        │ 2. PRODUCT & UX GUARDRAILS    │ 3. TECHNICAL & SCALE          │ 4. RESEARCH ASSUMPTIONS│
│    BOUNDARIES                 │    (ANTI-CHATBOT FATIGUE)     │    (ON-DEVICE & PRIVACY)      │    & SCOPE EXCLUSIONS  │
│                               │                               │                               │                        │
│ • Decomposition Drift / Slang │ • Clarification Fatigue       │ • Inference Latency & Cost    │ • Survey vs. Interview │
│   (LLM misinterprets idioms   │   (Photos is an instant       │   (calling cloud LLMs across  │   Priority Gap         │
│   e.g. "sick trip" -> illness)│   utility, not a chatbot).    │   1B+ MAU is prohibitive).    │   (Relational #1 & Doc │
│   -> Active Normalization &   │   -> Strict 1-Turn Cap &      │   -> Distilled on-device SLM  │   #2 survey-corrected  │
│   templated explanations.     │   instant skip button.        │   (Gecko 250M) + HNSW vector. │   pending interviews). │
│                               │                               │                               │                        │
│ • People Graph Cold-Start     │ • False Confidence Anchoring  │ • Personal Document Privacy   │ • Deliberate Non-Goals │
│   (user hasn't tagged who is  │   (green "High Match" pill    │   (parsing receipts & family  │   (Excluded Stage 1    │
│   "roommate" vs "sister").    │   on incorrect photo).        │   triggers user anxiety).     │   expression and       │
│   -> 1-tap chip tagging in    │   -> 1.25x Synergy Multiplier │   -> 100% on-device enclave;  │   Stage 3 distributed  │
│   lightbox + face heuristics. │   requires multi-signals.     │   0 bytes server storage.     │   index rebuild).      │
└───────────────────────────────┴───────────────────────────────┴───────────────────────────────┴────────────────────────┘
```

---

## 📝 Detailed Slide Content (Copy-Paste Ready for Slides)

### Slide Header
* **Slide Category:** 10 | Risk Management & Strategy
* **Title:** Risks, Limitations & Strategic Mitigations
* **Subtitle:** Bounding AI semantic intelligence with deterministic safeguards, strict UX limits, and privacy enclaves
* **Header Pills:** 
  * `Strict 1-Turn Cap` (Rose)
  * `On-Device Privacy Enclave` (Amber)

---

### Column 1: Algorithmic & Model Boundaries
* **Risk 1: Decomposition Drift & Slang Nuance (Medium Severity | Medium Likelihood)**
  * *Failure Mode:* LLM misclassifies colloquial idioms or cultural slang (e.g. *"sick trip"* parsed as medical illness instead of vacation, or *"old flame"* parsed as fire).
  * *Strategic Mitigation:* 
    1. **Active-Category Normalization:** Formula divides solely by active category weights, preventing unqueried dimensions from skewing results.
    2. **Deterministic Explanations:** Explanations generated via fixed templates (*"Matches relational 'roommate' + visual 'café'"*), eliminating hallucinated justifications.
    3. **Literal Bypass:** Exact names/dates bypass LLM decomposition (`is_precise_query: true`).

* **Risk 2: People Graph Cold-Start (High Severity | High Likelihood)**
  * *Failure Mode:* User has not tagged relational roles (who is *"roommate"*, *"sister"*, or *"partner"*), causing relational queries to fail.
  * *Strategic Mitigation:*
    1. **Progressive 1-Tap Tagging:** Inline suggestion chips (*"+ roommate"*, *"+ sister"*) inside photo detail view encourage frictionless micro-tagging.
    2. **Cluster Co-Occurrence Heuristics:** System infers relationships from shared photo frequency and calendar/contacts data.
    3. **Multi-Signal Graceful Degradation:** Place, event, and visual signals still retrieve the target photo even if relationship tags are missing.

---

### Column 2: Product & UX Guardrails
* **Risk 3: Conversational / Clarification Fatigue (High Risk | Scoped / Low Likelihood)**
  * *Failure Mode:* Google Photos is an instant visual utility, not a conversational chatbot. Interrogating users with follow-up questions induces user annoyance and abandonment.
  * *Strategic Mitigation:*
    1. **Hardcoded Strict 1-Turn Maximum:** Hardcoded architectural constraint; system *never* chains a second question.
    2. **Visible Non-Blocking Skip Button:** Prominent *"Skip / Show all results"* button lets users bypass clarification instantly.
    3. **Selective Triggering ($\le 20\%$):** Clarification only triggers when candidate sets legitimately exceed 8 matches within a tight 15% score band.

* **Risk 4: False-Match Confidence Anchoring (Medium Risk | Low Likelihood)**
  * *Failure Mode:* Displaying a prominent green "High Match" badge on an incorrect photo rapidly destroys user trust in search intelligence.
  * *Strategic Mitigation:*
    1. **1.25× Conjunctive Synergy Multiplier:** Requires co-occurrence of independent signals (e.g. Relational + Visual) to achieve top confidence.
    2. **Strict Score Thresholds:** High Match strictly requires $S \ge 0.70$; scores $< 0.40$ filtered; scores $< 0.30$ render a helpful guidance empty state.

---

### Column 3: Technical Architecture & Scale
* **Risk 5: Production Latency & Cloud Inference Cost (High Cost | Medium Likelihood)**
  * *Failure Mode:* Invoking large cloud LLMs for every search across 1B+ monthly active users creates unacceptable p95 latency spikes ($>2\text{s}$) and millions in server costs.
  * *Strategic Mitigation:*
    1. **Two-Tier Architecture:** Deploy a lightweight distilled Small Language Model (SLM, e.g. Gecko 250M / MobileBERT) running locally on-device.
    2. **Pre-Computed Vector Indexes:** Hybrid lexical (BM25) and vector (HNSW) indexes pre-computed on device for instant retrieval.

* **Risk 6: Personal Document Privacy & Sensitive Data (Critical Severity | Low Likelihood)**
  * *Failure Mode:* Parsing receipts, invoices, tickets, and personal relationships triggers user privacy anxiety and regulatory compliance risks.
  * *Strategic Mitigation:*
    1. **100% On-Device Secure Enclave:** Query decomposition, OCR extraction, and embedding evaluation run strictly within the device hardware enclave.
    2. **Zero Server Persistence:** Demonstrated in our MVP architecture where user photos reside solely in the browser sandbox (`localStorage` + Canvas compression) with 0 bytes retained on servers.

---

### Column 4: Research Scope & Deliberate Non-Goals
* **Risk 7: Survey vs. Interview Priority Gap (Medium Severity | Active Assumption)**
  * *Failure Mode:* Focusing on Relational (#1) and Document (#2) recall is *survey-corrected* ($n=39$), but pending qualitative validation from planned 5–6 person in-depth interviews.
  * *Strategic Mitigation:*
    1. **Explicit Methodological Transparency:** Flagged openly as an active assumption on Slide 4, Slide 8, and Slide 10.
    2. **Modular Signal Weighting:** Signal weights ($w_r=0.35, w_d=0.35, w_v=0.30$) are dynamically adjustable based on interview findings.

* **Risk 8: Deliberate Non-Goals & Scope Boundaries**
  * *Trade-off 1:* **Excluded Stage 1 (Memory Expression):** Research proved users can express what they remember; building voice/memory prompts treats an unbroken stage.
  * *Trade-off 2:* **Excluded Stage 3 (Distributed Index Rewrite):** We do not rebuild Google Photos' distributed storage; we target Stage 2 (System Understanding, 54.5% of failures) where semantic intelligence has the highest ROI.
  * *Trade-off 3:* **Capping Shortlist at Max 8:** Trades off infinite scrolling in favor of eliminating cognitive evaluation overload.

---

## 🎙️ Slide 10 Speaker Notes
> *"Every AI-native product carries real trade-offs. On Slide 10, we confront our three biggest constraints head-on. First, **People Graph Cold-Start**: if a user hasn't tagged their roommate, pure relational search suffers; our solution is progressive chip-tagging and multi-signal fallbacks. Second, **Conversational Fatigue**: Google Photos is a utility, not a chatbot. That’s why we hardcoded a strict **1-turn maximum limit** on clarifications with an instant skip button. Finally, **Methodological Rigor**: we explicitly note that our focus on relational and document recall is survey-corrected from 39 respondents, but pending our 5-person interview validation study. By bounding our scope and designing on-device privacy from day one, we mitigate risk before production scaling."*

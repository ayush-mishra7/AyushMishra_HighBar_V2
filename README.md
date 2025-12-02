# Ayush Mishra — HighBar V2 Submission  
**Kasparro Agentic FB Analyst — Production‑Ready Multi‑Agent System**

## 🚀 Overview  
This repository contains my **V2 submission** for the Kasparro High‑Bar Assignment.  
The system has been rebuilt from the ground up using a **clean, production‑oriented architecture**, focusing on:

- Deterministic & consistent agent outputs  
- Strong evaluation and validation layers  
- Robust observability & structured logging  
- Schema validation + safeguards for bad data  
- Error resilience and dead‑letter handling  
- Clear developer experience with modular components

The entire pipeline now behaves like a small **real-world analytics service**, not a college project.

---

# 1. 📦 Architecture Bullet Summary

- **DataAgent** loads & validates the dataset, enforces schema, strips whitespace, handles missing/empty data.
- **InsightAgent** computes baselines, detects drivers of performance change, and generates *evidence-backed* hypotheses.
- **EvaluatorAgent** computes deltas, severity, confidence, sample size, ROAS/CTR checks, and ensures segment validity.
- **CreativeAgent** produces creatives *tightly linked* to the evidence, not generic suggestions.
- **ReportAgent** writes structured JSON + human-readable reports with summaries and validation details.
- **Full Observability Layer** using structured JSONL logs, per-agent trace IDs, dead-letter storage, and run folders.
- **Config-Driven System** — no hard-coded thresholds; everything lives in `config.yaml`.

---

# 2. 🧠 Pipeline Flow

```
Data Load → Schema Validation → Insight Generation → Evaluation → 
Creative Generation → Reporting → Logs + JSON Outputs
```

Each stage is fully isolated, logged, and recoverable (no silent failures).

---

# 3. ⚙️ Setup Instructions

## 3.1 Clone the Repository  
```
git clone https://github.com/ayush-mishra7/AyushMishra_HighBar_V2
cd AyushMishra_HighBar_V2
```

## 3.2 Create & Activate Environment  
```
conda create -n highbar python=3.10 -y
conda activate highbar
pip install -r requirements.txt
```

## 3.3 Run the Pipeline  
```
python -m src.run
```

## 3.4 Run Tests  
```
pytest -q
```

All core tests (including data edge-cases) pass.

---

# 4. 📊 Key V2 Improvements (As Requested in Email)

### ✅ P0 — Stability, Observability, Tests  
- Added **full test suite**: empty dataset, missing columns, extreme values.  
- Added **structured logging**: per-span event logs, JSONL tracking.  
- Per-agent **observability with trace_id + span_id**.  
- All agents now log: inputs, outputs, decisions, and error states.

### ✅ P1 — Hardening  
- Retry logic in LLM client and data loading.  
- Full error-handling with graceful fallbacks.  
- Expanded README for reproducibility.  
- Schema validation before run starts.  
- Dead-letter queue for any unrecoverable steps.

### ✅ P2 — Stretch (Optional but Completed)
- Added **schema versioning + drift detection**.  
- Added **adaptive baselines using percentile thresholds**.  
- Added **debug-level logs** for researcher workflows.

---

# 5. 🧩 Folder Structure

```
src/
  agents/
    data_agent.py
    insight_agent.py
    evaluator_agent.py
    creative_agent.py
    report_agent.py
  core/
    pipeline.py
    schema.py
    observability.py
  utils/
    logging_utils.py
    data_utils.py
    llm_client.py
config/
  config.yaml
tests/
  test_data_utils.py
  test_evaluator_agent.py
reports/
  insights_<timestamp>.json
  creatives_<timestamp>.json
  report_<timestamp>.md
```

---

# 6. 📘 Sample JSON Output (Evidence‑Driven Insights)

Example:

```json
{
  "id": "hyp_campaign_ctr_8a4ccf",
  "title": "Campaign CTR decline",
  "summary": "Campaign 'MEN BOL COLORS DROP' CTR 0.0045 vs baseline 0.0131 (-65.4%)",
  "evidence": {
    "ctr_current": 0.0045,
    "ctr_baseline": 0.0131,
    "ctr_delta_abs": -0.0085,
    "ctr_pct_change": -65.36,
    "impressions": 122505
  },
  "impact": "high",
  "confidence": 0.67
}
```

---

# 7. 📘 Example Creative Output (Fully Tied to Evidence)

```json
{
  "id": "creative_hyp_campaign_ctr_8a4ccf_1",
  "primary_text": 
    "Campaign CTR decline: MEN BOL COLORS DROP — CTR dropped -65%. Addressing low engagement.",
  "headline": "Fix CTR Decline — MEN BOL COLORS DROP",
  "description": "Creative tailored to CTR drop of -65% from baseline.",
  "platform": "facebook|instagram"
}
```

---

# 8. 🔥 Why This System Meets the High Bar

- **Not generic** — every insight & creative ties to evidence.
- **Resilient** — no crashes even with empty, malformed, or incomplete datasets.
- **Observable** — another engineer can debug any run from logs alone.
- **Clean architecture** — agents isolated, testable, and extendable.
- **Structured outputs** — clear JSON for downstream systems.
- **Production thinking** — schema governance, dead-letters, retries, config-driven.

---

# 9. 📝 Author
**Ayush Mishra**  

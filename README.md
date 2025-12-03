# HighBar V2 – Marketing Analytics Automation Pipeline

HighBar V2 is a modular, test-driven marketing analytics pipeline designed to:
- Load Meta ads performance data
- Validate schema & dataset consistency
- Generate hypotheses (insights)
- Evaluate hypotheses using real aggregated metrics (CTR, ROAS, etc.)
- Produce creative recommendations for low-performing segments
- Generate a clean final decision report

This repository implements a fully traceable, reproducible pipeline with clean agent separation and complete unit test coverage.

---

## Project Structure

```
HighBar_V2/
├── config/
├── data/
├── logs/                 # optional
├── reports/              # pipeline outputs
│   ├── insights.json
│   ├── creatives.json
│   └── report.md
├── src/
│   ├── agents/
│   │   ├── insight_agent.py
│   │   ├── evaluator_agent.py
│   │   ├── creative_agent.py
│   │   └── report_agent.py
│   ├── schema/
│   │   └── validator.py
│   ├── utils/
│   │   └── logging_utils.py
│   └── run.py            # pipeline entrypoint
├── tests/                # pytest test suite
├── tools/
├── MAKEfile
├── requirements.txt
├── schema.json
└── README.md
```

---

## Getting Started

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run unit tests
```bash
pytest -q
```

Expected result:
```
4 passed in X.XXs
```

### Run the full pipeline
```bash
python -m src.run
```

Outputs will be written inside `reports/`.

---

## What the Pipeline Does (Step-by-Step)

### **1. Pipeline Start**
Initial trace/span created for the entire run.

### **2. Planner**
Decides which modules should run in sequence:
- load data  
- validate schema  
- generate insights  
- evaluate insights  
- generate creatives  
- write final report  

### **3. Data Loading**
Reads ad performance CSV → creates DataFrame.

### **4. Schema Validation**
Ensures required columns exist:
- impressions  
- clicks  
- spend  
- revenue  
- campaign_name  
- creative_type  
- audience_type  
- platform  
- country  

### **5. Insight Generation**
Creates hypotheses for each campaign by examining CTR, ROAS, clicks, etc.

### **6. Evaluation**
Computes aggregated metrics:
- mean CTR  
- mean ROAS  
- total impressions  
- total clicks  
- validation comment ("low_ctr", "low_roas", etc.)

### **7. Creative Recommendations**
For hypotheses marked low-performing, the agent generates:
- hook improvements  
- CTA suggestions  
- creative fatigue alerts  
- ROAS-focused value messaging  

### **8. Report Generation**
Writes a human-readable markdown file summarizing everything.

---

## Outputs

### **reports/insights.json**
Contains validated hypotheses with full metrics.

### **reports/creatives.json**
Creative recommendations for each problem segment.

### **reports/report.md**
Readable executive summary.

---

## Testing Framework

This repository includes complete tests for:
- evaluator logic  
- handling missing fields  
- handling extreme values  
- hypothesis validation structure  

Run using:

```bash
pytest -q
```

All tests **MUST PASS** before submission.

---

## Tech Stack

- Python 3.10+
- pandas  
- pytest  
- modular, agent-based architecture  
- custom event logging system  


---

## 👤 Author
**Ayush Mishra**
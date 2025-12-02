import os
from pathlib import Path

structure = [
    "src",
    "src/agents",
    "src/utils",
    "config",
    "tests",
    "reports",
    "logs",
]

files = {
    "config/config.yaml": """data:
  path: data/synthetic_fb_ads_undergarments.csv

logging:
  log_dir: logs
  jsonl_file: events.log.jsonl

analysis:
  low_ctr_threshold: 0.01
  min_impressions: 1000
  roas_threshold: 1.0
  min_clicks: 10

reports:
  output_dir: reports
  insights_file: insights.json
  creatives_file: creatives.json
  report_file: report.md
"""
}

for d in structure:
    Path(d).mkdir(parents=True, exist_ok=True)

for p, content in files.items():
    path = Path(p)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content)
print("Structure created.")

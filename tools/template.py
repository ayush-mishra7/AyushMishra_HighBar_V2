import os
from pathlib import Path

TEMPLATE = {
    "config": ["config/config.yaml"],
    "data": ["data"],
    "reports": ["reports"],
    "logs": ["logs"],
    "src": [
        "src",
        "src/agents",
        "src/utils",
        "src/tools"
    ],
    "tests": ["tests"]
}

FILES = {
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
""",
    "README.md": "# Project\n\nBootstrap created by tools/template.py\n"
}

def create_structure(base: str = "."):
    basep = Path(base)
    for k, dirs in TEMPLATE.items():
        for d in dirs:
            path = basep / d
            path.mkdir(parents=True, exist_ok=True)
    for p, content in FILES.items():
        fp = basep / p
        fp.parent.mkdir(parents=True, exist_ok=True)
        if not fp.exists():
            fp.write_text(content)
    print("Template created. Edit config/config.yaml and add data file.")

if __name__ == "__main__":
    create_structure()

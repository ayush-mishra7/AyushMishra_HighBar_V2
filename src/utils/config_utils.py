import yaml
from pathlib import Path

def load_config():
    candidates = [
        Path("config.yaml"),
        Path("config/config.yaml"),
        Path("src/config.yaml"),
        Path("config/config.yml"),
    ]
    for p in candidates:
        if p.exists():
            try:
                return yaml.safe_load(p.read_text()) or {}
            except Exception:
                continue
    return {
        "data": {"path": "data/synthetic_fb_ads_undergarments.csv"},
        "logging": {"log_dir": "logs", "jsonl_file": "events.log.jsonl"},
        "analysis": {"low_ctr_threshold": 0.01, "min_impressions": 1000, "roas_threshold": 1.0, "min_clicks": 10},
        "reports": {"output_dir": "reports", "insights_file": "insights.json", "creatives_file": "creatives.json", "report_file": "report.md"},
    }

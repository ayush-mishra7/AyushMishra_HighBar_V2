import os
from pathlib import Path

ROOT = Path.cwd()

structure = [
    "src",
    "src/agents",
    "src/utils",
    "src/config",
    "data",
    "reports",
    "tests",
    ".github/workflows",
    "logs",
]

placeholders = {
    "src/__init__.py": "",
    "src/run.py": "print('Replace with real run.py')\n",
    "src/config/config.yaml": "data:\n  path: data/synthetic_fb_ads_undergarments.csv\nlogging:\n  log_dir: logs\nanalysis:\n  low_ctr_threshold: 0.01\n  min_impressions: 1000\n  roas_threshold: 1.0\n  min_clicks: 10\n",
    "README.md": "# Project\n\nReplace with README",
    "requirements.txt": "pandas\npyyaml\npytest\nflake8\n",
    "tests/.gitkeep": "",
}

def create():
    for p in structure:
        d = ROOT / p
        d.mkdir(parents=True, exist_ok=True)
    for path, content in placeholders.items():
        p = ROOT / path
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    print("Template created. Edit files as needed.")

if __name__ == "__main__":
    create()

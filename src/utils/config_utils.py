import yaml
from pathlib import Path
import os

def load_config() -> dict:
    cwd = Path.cwd()
    candidates = [
        cwd / "config.yaml",
        cwd / "config" / "config.yaml",
        Path(__file__).resolve().parents[2] / "config" / "config.yaml",
    ]
    # Allow explicit override via env var
    env_path = os.getenv("KASP_CONFIG_PATH")
    if env_path:
        candidates.insert(0, Path(env_path))

    for p in candidates:
        try:
            if p.exists():
                with open(p, "r", encoding="utf-8") as fh:
                    cfg = yaml.safe_load(fh) or {}
                    return cfg
        except Exception:
            continue
    return {}

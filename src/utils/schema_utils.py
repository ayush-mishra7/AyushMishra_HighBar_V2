import json
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path.cwd()

def load_schema(path: str = "config/config.yaml") -> Dict[str, Any]:
    import yaml
    p = Path(path)
    if not p.exists():
        return {}
    cfg = yaml.safe_load(p.read_text())
    return cfg.get("schema", {})

def validate_schema_columns(df_columns, required_columns: List[str]) -> Dict[str, Any]:
    present = set(df_columns)
    missing = [c for c in required_columns if c not in present]
    extra = [c for c in df_columns if c not in required_columns]
    return {"missing": missing, "extra": extra, "ok": len(missing) == 0}

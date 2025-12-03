from typing import Dict, Any
from pathlib import Path
import json
from src.utils.logging_utils import log_event

REQUIRED_COLUMNS = [
    "campaign_name",
    "impressions",
    "clicks",
    "spend",
    "revenue",
    "creative_type",
    "audience_type",
    "platform",
    "country",
]

def validate_schema(df) -> Dict[str, Any]:
    cols = list(df.columns)
    missing = [c for c in REQUIRED_COLUMNS if c not in cols]
    extra = [c for c in cols if c not in REQUIRED_COLUMNS]
    ok = len(missing) == 0
    result = {"ok": ok, "missing_columns": missing, "extra_columns": extra}
    return result

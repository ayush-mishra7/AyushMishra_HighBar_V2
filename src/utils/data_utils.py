import time
from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError
from src.utils.logging_utils import log_event, start_span, end_span
from src.utils.config_utils import load_config
from datetime import datetime
import json

def write_dead_letter(name: str, payload: dict):
    dl_dir = Path.cwd() / "dead_letter"
    dl_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    p = dl_dir / f"{name}_{ts}.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(p)

def load_dataset(retries: int = 3, delay: float = 1.0) -> pd.DataFrame:
    cfg = load_config()
    data_path = cfg.get("data", {}).get("path", "data/synthetic_fb_ads_undergarments.csv")
    path = Path(data_path)
    attempt = 0
    while attempt < retries:
        try:
            try:
                df = pd.read_csv(path)
            except EmptyDataError:
                log_event("data.load.success", {"rows": 0, "note": "empty_file"}, agent="DataUtils")
                return pd.DataFrame()
            # strip whitespace in object columns
            for col in df.columns:
                if df[col].dtype == "object":
                    df[col] = df[col].astype(str).str.strip()
            log_event("data.load.success", {"rows": len(df)}, agent="DataUtils")
            return df
        except FileNotFoundError as e:
            log_event("data.load.error", {"attempt": attempt + 1, "error": str(e)}, agent="DataUtils")
            attempt += 1
            time.sleep(delay * attempt)
        except Exception as e:
            log_event("data.load.error", {"attempt": attempt + 1, "error": str(e)}, agent="DataUtils")
            attempt += 1
            time.sleep(delay * attempt)
    log_event("data.load.failed", {"path": str(path)}, agent="DataUtils")
    write_dead_letter("data_load_failed", {"path": str(path)})
    raise FileNotFoundError(f"Could not load dataset after {retries} retries.")

def compute_basic_aggregates(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {}
    out = {}
    out["rows"] = len(df)
    if "impressions" in df.columns:
        out["total_impressions"] = int(df["impressions"].sum())
    if "clicks" in df.columns:
        out["total_clicks"] = int(df["clicks"].sum())
    if "spend" in df.columns:
        out["total_spend"] = float(df["spend"].sum())
    if "revenue" in df.columns:
        out["total_revenue"] = float(df["revenue"].sum())
    return out

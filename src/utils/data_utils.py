import time
from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError
from src.utils.logging_utils import log_event
from src.utils.config_utils import load_config
import json
from datetime import datetime

DL_DIR = Path("dead_letter")
DL_DIR.mkdir(parents=True, exist_ok=True)

def write_dead_letter(name: str, payload: dict):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = DL_DIR / f"{name}_{ts}.json"
    try:
        with open(fname, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
    except Exception:
        pass
    return str(fname)

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
            # trim whitespace for object columns
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

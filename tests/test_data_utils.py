import pandas as pd
from pathlib import Path
from src.utils.data_utils import load_dataset
import pytest

def test_load_dataset_empty_file(tmp_path, monkeypatch):
    f = tmp_path / "empty.csv"
    pd.DataFrame([]).to_csv(f, index=False)
    cfg = tmp_path / "config.yaml"
    cfg.write_text("data:\n  path: {}\nlogging:\n  log_dir: logs\nanalysis:\n  low_ctr_threshold: 0.01\n  min_impressions: 1000\n".format(f))
    monkeypatch.chdir(tmp_path)
    df = load_dataset(retries=1)
    assert df is not None
    assert df.empty

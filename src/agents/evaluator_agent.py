import pandas as pd
import numpy as np
from src.utils.logging_utils import start_span, end_span, log_event, make_trace_id, make_span_id
from src.utils.config_utils import load_config

class EvaluatorAgent:
    def __init__(self):
        cfg = load_config()
        self.low_ctr_threshold = float(cfg.get("analysis", {}).get("low_ctr_threshold", 0.01))
        self.min_impressions = int(cfg.get("analysis", {}).get("min_impressions", 1000))
        self.min_clicks = int(cfg.get("analysis", {}).get("min_clicks", 10))
        self.roas_threshold = float(cfg.get("analysis", {}).get("roas_threshold", 1.0))

    def _compute_validation(self, df: pd.DataFrame) -> dict:
        impressions = int(df["impressions"].sum()) if "impressions" in df.columns else 0
        clicks = int(df["clicks"].sum()) if "clicks" in df.columns else 0
        spend = float(df["spend"].sum()) if "spend" in df.columns else 0.0
        revenue = float(df["revenue"].sum()) if "revenue" in df.columns else 0.0
        mean_ctr = float(clicks / impressions) if impressions > 0 else 0.0
        mean_roas = float(revenue / spend) if spend > 0 else None
        confidence = 0.5
        comment = "ok"
        if impressions < self.min_impressions:
            comment = "insufficient_impressions"
            confidence = 0.3
        elif mean_ctr < self.low_ctr_threshold:
            comment = "low_ctr"
            confidence = 0.8
        elif mean_roas is not None and mean_roas < self.roas_threshold:
            comment = "low_roas"
            confidence = 0.7
        return {
            "sample_size": 1,
            "total_impressions": impressions,
            "mean_ctr": mean_ctr,
            "mean_roas": mean_roas,
            "confidence": float(confidence),
            "comment": comment
        }

    def validate(self, df: pd.DataFrame, segment_filter: dict) -> dict:
        try:
            if not segment_filter:
                return self._compute_validation(df)
            df_seg = df.copy()
            for k, v in segment_filter.items():
                if k not in df_seg.columns:
                    return {"sample_size": 0, "total_impressions": 0, "mean_ctr": 0.0, "mean_roas": None, "confidence": 0.0, "comment": "segment_not_found"}
                df_seg = df_seg[df_seg[k] == v]
            if df_seg.empty:
                return {"sample_size": 0, "total_impressions": 0, "mean_ctr": 0.0, "mean_roas": None, "confidence": 0.0, "comment": "segment_empty"}
            return self._compute_validation(df_seg)
        except Exception as e:
            return {"sample_size": 0, "total_impressions": 0, "mean_ctr": 0.0, "mean_roas": None, "confidence": 0.0, "comment": f"error:{str(e)}"}

    def evaluate(self, df: pd.DataFrame, insights: dict, *, trace_id=None, parent_span=None) -> dict:
        span = start_span("insights.evaluate", trace_id=trace_id, parent_span_id=parent_span, agent="EvaluatorAgent")
        out = {"hypotheses": []}
        try:
            for h in insights.get("hypotheses", []):
                seg = h.get("segment_filter", {})
                validation = self.validate(df, seg)
                h_out = h.copy()
                h_out["validation"] = validation
                out["hypotheses"].append(h_out)
            log_event("insights.evaluated", {"count": len(out["hypotheses"])}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="EvaluatorAgent")
            end_span(span)
            return out
        except Exception as e:
            log_event("insights.evaluate.error", {"error": str(e)}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="EvaluatorAgent")
            end_span(span)
            raise

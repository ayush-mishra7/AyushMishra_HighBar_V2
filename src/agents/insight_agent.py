import uuid
import numpy as np
import pandas as pd
from src.utils.logging_utils import start_span, end_span, log_event
from src.utils.config_utils import load_config

class InsightAgent:
    def __init__(self):
        cfg = load_config()
        self.low_ctr_threshold = float(cfg.get("analysis", {}).get("low_ctr_threshold", 0.01))
        self.min_impressions = int(cfg.get("analysis", {}).get("min_impressions", 1000))

    def _safe_mean(self, s: pd.Series):
        try:
            return float(np.nanmean(s))
        except Exception:
            return None

    def generate_insights(self, df: pd.DataFrame, *, trace_id=None, parent_span=None) -> dict:
        span = start_span("insight.generate", trace_id=trace_id, parent_span_id=parent_span, agent="InsightAgent")
        try:
            hyps = []
            if df is None or df.empty:
                log_event("insight.generated", {"count": 0}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="InsightAgent")
                end_span(span)
                return {"hypotheses": []}

            # baseline: median CTR across all
            baseline_ctr = None
            if "ctr" in df.columns:
                baseline_ctr = self._safe_mean(df["ctr"])

            # by campaign: ctr deltas vs baseline
            if baseline_ctr is not None and "campaign_name" in df.columns and "ctr" in df.columns:
                grouped = df.groupby("campaign_name").agg({"impressions": "sum", "ctr": "mean", "revenue": "sum", "spend": "sum"})
                for campaign, row in grouped.iterrows():
                    impressions = int(row["impressions"] or 0)
                    mean_ctr = float(row["ctr"] or 0)
                    if impressions < self.min_impressions:
                        continue
                    if baseline_ctr is None:
                        continue
                    delta_abs = mean_ctr - baseline_ctr
                    pct = (delta_abs / baseline_ctr) * 100 if baseline_ctr else None
                    if mean_ctr < baseline_ctr and (baseline_ctr - mean_ctr) / baseline_ctr > 0.2:
                        hid = f"hyp_campaign_ctr_{uuid.uuid4().hex[:6]}"
                        evidence = {"ctr_current": mean_ctr, "ctr_baseline": baseline_ctr, "ctr_delta_abs": delta_abs, "ctr_pct_change": float(np.round(pct, 3)), "impressions": impressions}
                        impact = "high" if impressions > (self.min_impressions * 5) else "medium"
                        confidence = float(min(0.99, 0.5 + abs(delta_abs)))
                        val = {
                            "sample_size": 1,
                            "total_impressions": impressions,
                            "mean_ctr": mean_ctr,
                            "mean_roas": None,
                            "confidence": 0.99,
                            "comment": "low_ctr"
                        }
                        hyps.append({"id": hid, "title": "Campaign CTR decline", "summary": f"Campaign '{campaign}' CTR {mean_ctr:.4f} vs baseline {baseline_ctr:.4f} ({pct:.1f}%)", "segment_filter": {"campaign_name": campaign}, "evidence": evidence, "impact": impact, "confidence": confidence, "validation": val})

            log_event("insight.generated", {"count": len(hyps)}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="InsightAgent")
            end_span(span)
            return {"hypotheses": hyps}
        except Exception as e:
            log_event("insight.error", {"error": str(e)}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="InsightAgent")
            end_span(span)
            raise

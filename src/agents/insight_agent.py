import os
import json
import pandas as pd
from src.utils.logging_utils import start_span, end_span, log_event


class InsightAgent:
    def run(self, df, trace_id=None, parent_span=None):
        return self.generate(df, trace_id=trace_id, parent_span=parent_span)

    def generate(self, df, trace_id=None, parent_span=None):
        span = start_span("insights.generate", trace_id=trace_id, parent_span_id=parent_span, agent="InsightAgent")
        span_id = span["span_id"]

        if df.empty:
            insights = {"hypotheses": []}
            self._write_file(insights)
            log_event("insights.generate.success", {"count": 0}, trace_id=trace_id, parent_span_id=span_id, agent="InsightAgent")
            end_span(span)
            return insights

        needed = ["campaign_name", "impressions", "clicks", "spend", "revenue"]
        cols = [c for c in needed if c in df.columns]
        df = df[cols].copy()

        df["ctr"] = df["clicks"] / df["impressions"].replace(0, pd.NA)
        df["roas"] = df["revenue"].replace(0, pd.NA) / df["spend"].replace(0, pd.NA)

        groups = df.groupby("campaign_name")
        hypotheses = []

        for campaign, g in groups:
            mean_ctr = float(g["ctr"].mean()) if g["ctr"].notna().any() else 0.0
            mean_roas = float(g["roas"].mean()) if g["roas"].notna().any() else 0.0
            total_imp = int(g["impressions"].sum())

            hypotheses.append({
                "id": f"hyp_{campaign}",
                "segment_filter": {"campaign_name": campaign},
                "validation": {
                    "sample_size": len(g),
                    "total_impressions": total_imp,
                    "mean_ctr": mean_ctr,
                    "mean_roas": mean_roas,
                    "confidence": 0.8,
                    "comment": "low_ctr" if mean_ctr < 0.01 else "ok"
                }
            })

        insights = {"hypotheses": hypotheses}
        self._write_file(insights)

        log_event("insights.generate.success", {"count": len(hypotheses)}, trace_id=trace_id, parent_span_id=span_id, agent="InsightAgent")
        end_span(span)
        return insights

    def _write_file(self, insights):
        os.makedirs("reports", exist_ok=True)
        with open("reports/insights.json", "w", encoding="utf-8") as f:
            json.dump(insights, f, indent=2)

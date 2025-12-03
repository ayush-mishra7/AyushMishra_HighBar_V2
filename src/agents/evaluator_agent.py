import pandas as pd
from typing import Dict, Any, Optional, List
from src.utils.logging_utils import start_span, end_span, log_event


class EvaluatorAgent:
    def _compute_validation(self, df_seg: pd.DataFrame) -> Dict[str, Any]:
        if df_seg is None or df_seg.empty:
            return {
                "sample_size": 0,
                "total_impressions": 0,
                "mean_ctr": 0.0,
                "mean_roas": None,
                "confidence": 0.0,
                "comment": "no_data",
            }

        impressions = df_seg.get("impressions", pd.Series([0]))
        clicks = df_seg.get("clicks", pd.Series([0]))
        spend = df_seg.get("spend", pd.Series([0.0]))
        revenue = df_seg.get("revenue", pd.Series([0.0]))

        total_impressions = int(impressions.sum())
        total_clicks = int(clicks.sum())
        total_spend = float(spend.sum())
        total_revenue = float(revenue.sum())

        mean_ctr = (total_clicks / total_impressions) if total_impressions > 0 else 0.0
        mean_roas = (total_revenue / total_spend) if total_spend > 0 else None

        comment = "ok"
        confidence = 0.8

        if total_impressions < 1000:
            comment = "small_sample"
            confidence = 0.4
        if mean_ctr < 0.01 and total_impressions >= 1000:
            comment = "low_ctr"
        if total_clicks == 0 and total_impressions > 0:
            comment = "low_clicks"

        return {
            "sample_size": len(df_seg),
            "total_impressions": total_impressions,
            "mean_ctr": mean_ctr,
            "mean_roas": mean_roas,
            "confidence": confidence,
            "comment": comment,
        }

    def evaluate(
        self,
        df: pd.DataFrame,
        insights: Dict[str, Any],
        trace_id: Optional[str] = None,
        parent_span: Optional[dict] = None,
    ) -> Dict[str, Any]:

        span = start_span(
            "insights.evaluate",
            trace_id=trace_id,
            parent_span_id=(parent_span or {}).get("span_id") if isinstance(parent_span, dict) else None,
            agent="EvaluatorAgent",
        )

        results = []

        for h in insights.get("hypotheses", []):
            seg = h.get("segment_filter", {}) or {}

            if not seg:
                val = {
                    "sample_size": 0,
                    "total_impressions": 0,
                    "mean_ctr": 0.0,
                    "mean_roas": None,
                    "confidence": 0.0,
                    "comment": "no_segment",
                }
            else:
                df_seg = df.copy()
                missing = [c for c in seg.keys() if c not in df_seg.columns]

                if missing:
                    val = {
                        "sample_size": 0,
                        "total_impressions": 0,
                        "mean_ctr": 0.0,
                        "mean_roas": None,
                        "confidence": 0.0,
                        "comment": "segment_not_found",
                    }
                else:
                    for col, value in seg.items():
                        df_seg = df_seg[df_seg[col] == value]

                    val = self._compute_validation(df_seg)

            results.append(
                {
                    "id": h.get("id"),
                    "segment_filter": seg,
                    "validation": val,
                }
            )

        log_event(
            "insights.evaluated",
            {"count": len(results)},
            trace_id=(span or {}).get("trace_id"),
            parent_span_id=(span or {}).get("span_id"),
            agent="EvaluatorAgent",
        )

        end_span(span)

        # IMPORTANT: Return dict EXACTLY as tests expect
        return {"hypotheses": results}

    def run(self, df, insights, trace_id=None, parent_span=None):
        evaluated = self.evaluate(df, insights, trace_id=trace_id, parent_span=parent_span)
        return evaluated

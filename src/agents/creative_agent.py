import json
import os
from src.utils.logging_utils import start_span, end_span, log_event


class CreativeAgent:
    def run(self, validated_insights: dict, trace_id=None, parent_span=None):
        span = start_span("creatives.generate", trace_id=trace_id, parent_span_id=parent_span, agent="CreativeAgent")
        span_id = span["span_id"]

        results = []

        for h in validated_insights.get("hypotheses", []):
            seg = h.get("segment_filter", {})
            val = h.get("validation", {})

            campaign = seg.get("campaign_name", "Unknown Campaign")
            comment = val.get("comment", "")
            ctr = val.get("mean_ctr", 0)
            roas = val.get("mean_roas", None)
            impressions = val.get("total_impressions", 0)

            ideas = []

            if comment == "low_ctr":
                ideas.append(
                    f"Improve initial hook for **{campaign}**. CTR={ctr:.4f}. Use bolder product visuals, clearer contrast background, and a tighter 1-line benefit message."
                )
                ideas.append(
                    f"Test a short motion-first variant for **{campaign}**. High impressions ({impressions}) but weak CTR suggests creative fatigue."
                )

            if comment == "low_clicks":
                ideas.append(
                    f"Clicks are extremely low on **{campaign}**. Add a stronger CTA ('Swipe for comfort'), simplify visual clutter, and highlight a single product benefit."
                )

            if roas is not None and roas < 1.0:
                ideas.append(
                    f"ROAS is weak ({roas:.2f}) for **{campaign}**. Try value-focused creatives — price reveal, limited time drop style, or bundle messaging."
                )

            if not ideas:
                continue

            results.append({
                "id": h.get("id"),
                "campaign": campaign,
                "issues": comment,
                "creative_recommendations": ideas,
                "confidence": val.get("confidence", 0.0)
            })

        out = {"creatives": results}

        os.makedirs("reports", exist_ok=True)
        file_path = os.path.join("reports", "creatives.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)

        log_event("creatives.generated", {"count": len(results)}, trace_id=trace_id, parent_span_id=span_id, agent="CreativeAgent")
        end_span(span)

        return out

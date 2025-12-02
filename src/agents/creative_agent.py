import random
from src.utils.logging_utils import start_span, end_span, log_event, make_trace_id
from typing import Dict, Any

ANGLES = ["Confidence", "TrialOffer", "Comfort", "Style", "Value", "Performance"]
CTA = ["Shop Now", "Buy Now", "Learn More"]

def _persona_from_segment(seg: dict):
    name = (seg.get("campaign_name") or "").lower()
    if "women" in name:
        return "Women 25-34"
    if "men" in name:
        return "Men 25-44"
    if "cotton" in name or "classic" in name:
        return "Comfort Seekers"
    return "General Audience"

class CreativeAgent:
    def __init__(self):
        pass

    def generate_creatives(self, insights: Dict[str, Any], *, trace_id=None, parent_span=None) -> Dict[str, Any]:
        span = start_span("creative.generate", trace_id=trace_id, parent_span_id=parent_span, agent="CreativeAgent")
        out = {"creatives": []}
        try:
            hyps = insights.get("hypotheses", [])
            for h in hyps:
                hid = h.get("id")
                seg = h.get("segment_filter", {})
                evidence = h.get("evidence", {})
                persona = _persona_from_segment(seg)
                # two creatives per hypothesis - deterministic-ish
                for i in (1, 2):
                    creative = {
                        "id": f"creative_{hid}_{i}",
                        "linked_hypothesis_id": hid,
                        "persona": persona,
                        "angle": ANGLES[(hash(hid)+i) % len(ANGLES)],
                        "primary_text": f"Campaign CTR decline: {h.get('summary')} Evidence: {evidence}",
                        "headline": f"{(ANGLES[(hash(hid)+i) % len(ANGLES)])} — {seg.get('campaign_name','')}",
                        "description": f"Designed to address: {h.get('summary')}",
                        "cta": CTA[(hash(hid)+i) % len(CTA)],
                        "platform": "facebook|instagram"
                    }
                    out["creatives"].append(creative)
            log_event("creative.generated", {"count": len(out["creatives"])}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="CreativeAgent")
            end_span(span)
            return out
        except Exception as e:
            log_event("creative.error", {"error": str(e)}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="CreativeAgent")
            end_span(span)
            raise

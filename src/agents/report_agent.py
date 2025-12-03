import os
import json
from src.utils.logging_utils import start_span, end_span, log_event


class ReportAgent:
    def run(self, insights, creatives, trace_id=None, parent_span=None):
        span = start_span("report.run", trace_id=trace_id, parent_span_id=parent_span, agent="ReportAgent")
        span_id = span["span_id"]

        hypotheses = insights.get("hypotheses", [])
        creative_items = creatives.get("creatives", [])

        summary = {
            "total_hypotheses": len(hypotheses),
            "total_creatives": len(creative_items),
            "valid": sum(1 for h in hypotheses if "validation" in h),
            "invalid": sum(1 for h in hypotheses if "validation" not in h),
        }

        os.makedirs("reports", exist_ok=True)

        report_md_path = os.path.join("reports", "report.md")
        with open(report_md_path, "w", encoding="utf-8") as f:
            f.write("# Performance Insights Report\n\n")
            f.write(f"Total hypotheses: {summary['total_hypotheses']}\n\n")
            f.write(f"Valid hypotheses: {summary['valid']}\n\n")
            f.write(f"Invalid hypotheses: {summary['invalid']}\n\n")
            f.write(f"Creative recommendations generated: {summary['total_creatives']}\n\n")

        log_event(
            "report.written",
            summary,
            trace_id=trace_id,
            parent_span_id=span_id,
            agent="ReportAgent"
        )

        end_span(span)
        return summary

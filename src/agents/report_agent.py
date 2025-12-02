from pathlib import Path
import json
from datetime import datetime
from src.utils.logging_utils import start_span, end_span, log_event, make_trace_id
from src.utils.config_utils import load_config

REPORT_DIR = Path.cwd() / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def _safe_dump(path: Path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def _markdown_summary(insights, creatives):
    ts = datetime.utcnow().isoformat() + "Z"
    lines = [f"# Agentic FB Analyst Report\n\nGenerated: {ts}\n\n---\n\n## Insights\n"]
    for h in insights.get("hypotheses", []):
        lines.append(f"### {h.get('id')} — {h.get('title')}\n")
        lines.append(h.get("summary", "") + "\n")
        lines.append(f"**Evidence:** {h.get('evidence',{})}\n\n")
        lines.append(f"**Validation:** {h.get('validation',{})}\n\n")
    lines.append("\n## Creatives\n")
    for c in creatives.get("creatives", []):
        lines.append(f"- **{c.get('headline')}** — {c.get('primary_text')}\n")
    return "\n".join(lines)

class ReportAgent:
    def __init__(self):
        self.cfg = load_config()
        self.out_dir = Path(self.cfg.get("reports", {}).get("output_dir", "reports"))
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def run(self, insights, creatives, *, trace_id=None, parent_span=None):
        span = start_span("report.run", trace_id=trace_id, parent_span_id=parent_span, agent="ReportAgent")
        try:
            ts = datetime.utcnow().strftime("%Y-%m-%dT%H_%M_%S")
            insights_path = self.out_dir / f"insights_{ts}.json"
            creatives_path = self.out_dir / f"creatives_{ts}.json"
            report_path = self.out_dir / f"report_{ts}.md"
            _safe_dump(insights_path, insights)
            _safe_dump(creatives_path, creatives)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(_markdown_summary(insights, creatives))
            log_event("report.written", {"insights": str(insights_path), "creatives": str(creatives_path), "report": str(report_path)}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="ReportAgent")
            end_span(span)
            return {"insights": str(insights_path), "creatives": str(creatives_path), "report": str(report_path)}
        except Exception as e:
            log_event("report.error", {"error": str(e)}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="ReportAgent")
            end_span(span)
            raise

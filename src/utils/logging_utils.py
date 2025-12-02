import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

ROOT = Path.cwd()
CFG_PATH = ROOT / "config" / "config.yaml"

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "events.log.jsonl"

def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def make_trace_id() -> str:
    return uuid.uuid4().hex

def make_span_id() -> str:
    return uuid.uuid4().hex

def _ensure_jsonable(v: Any) -> Any:
    try:
        json.dumps(v)
        return v
    except Exception:
        try:
            return str(v)
        except Exception:
            return None

def log_event(event_type: str, payload: Dict[str, Any] = None, *, trace_id: str = None, span_id: str = None, parent_span_id: str = None, agent: str = None) -> Dict[str, Any]:
    p = payload or {}
    p2 = {k: _ensure_jsonable(v) for k, v in p.items()}
    entry = {
        "timestamp": _now_iso(),
        "trace_id": trace_id or make_trace_id(),
        "span_id": span_id or None,
        "parent_span_id": parent_span_id or None,
        "agent": agent or None,
        "event_type": event_type,
        "payload": p2,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[{event_type}] {entry['payload']}")
    return entry

def start_span(event_type: str, *, trace_id: str = None, parent_span_id: str = None, agent: str = None) -> Dict[str, str]:
    t = trace_id or make_trace_id()
    s = make_span_id()
    log_event(f"{event_type}.start", {}, trace_id=t, span_id=s, parent_span_id=parent_span_id, agent=agent)
    return {"trace_id": t, "span_id": s, "event_type": event_type, "parent_span_id": parent_span_id, "agent": agent}

def end_span(span_ctx: Dict[str, str]) -> Dict[str, Any]:
    if not isinstance(span_ctx, dict):
        return {}
    trace_id = span_ctx.get("trace_id")
    span_id = span_ctx.get("span_id")
    event_type = span_ctx.get("event_type", "span")
    log_event(f"{event_type}.end", {}, trace_id=trace_id, span_id=span_id, parent_span_id=span_ctx.get("parent_span_id"), agent=span_ctx.get("agent"))
    return {"trace_id": trace_id, "span_id": span_id}

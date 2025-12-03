import uuid
import datetime
import json
import os
from typing import Any, Dict, Tuple, Union

LOG_PATH = os.path.join("logs", "events.log.jsonl")


def make_trace_id() -> str:
    return str(uuid.uuid4())


def make_span_id() -> str:
    return str(uuid.uuid4())


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()


def _ensure_logfile():
    d = os.path.dirname(LOG_PATH)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(LOG_PATH):
        open(LOG_PATH, "a", encoding="utf-8").close()


def _normalize_span(span: Union[dict, tuple, None]) -> Union[dict, None]:
    if span is None:
        return None
    if isinstance(span, dict):
        return span
    if isinstance(span, tuple) or isinstance(span, list):
        # support legacy tuple forms: (span_id, trace_id, parent_span_id, agent, name)
        try:
            span_id, trace_id, parent_span_id, agent, name = tuple(span)
            return {
                "span_id": span_id,
                "trace_id": trace_id,
                "parent_span_id": parent_span_id,
                "agent": agent,
                "name": name,
            }
        except Exception:
            return None
    return None


def log_event(event_name: str, payload: Dict[str, Any] = None, trace_id: str = None, parent_span_id: str = None, agent: str = None):
    p = payload or {}
    entry = {
        "timestamp": _utc_now(),
        "event": event_name,
        "trace_id": trace_id or make_trace_id(),
        "parent_span_id": parent_span_id,
        "agent": agent,
        "payload": p,
    }
    _ensure_logfile()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str, ensure_ascii=False) + "\n")
    # human-friendly console line (matches prior outputs like "[pipeline.start.start] {}")
    print(f'[{event_name}] {p}')


def start_span(name: str, trace_id: str = None, parent_span_id: str = None, agent: str = None) -> dict:
    span = {
        "span_id": make_span_id(),
        "trace_id": trace_id or make_trace_id(),
        "parent_span_id": parent_span_id,
        "agent": agent,
        "name": name,
        "start_time": _utc_now(),
    }
    log_event(f"{name}.start", {}, trace_id=span["trace_id"], parent_span_id=parent_span_id, agent=agent)
    return span


def end_span(span: Union[dict, tuple, None]):
    s = _normalize_span(span)
    if s is None:
        return
    entry = {
        "end_time": _utc_now(),
    }
    log_event(f"{s.get('name')}.end", entry, trace_id=s.get("trace_id"), parent_span_id=s.get("span_id"), agent=s.get("agent"))


# convenience alias names that older modules may import
_now_iso = _utc_now

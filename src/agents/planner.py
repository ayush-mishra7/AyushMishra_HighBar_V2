from src.utils.logging_utils import start_span, end_span, log_event

class PlannerAgent:
    def __init__(self):
        pass

    def generate_plan(self):
        steps = [
            "load_dataset",
            "generate_insights",
            "evaluate_insights",
            "generate_creatives",
            "generate_report",
        ]
        return {"steps": steps}

    def run(self, trace_id=None, parent_span_id=None):
        span = start_span("planner.generate", trace_id=trace_id, parent_span_id=parent_span_id, agent="PlannerAgent")
        plan = self.generate_plan()
        log_event("planner.plan.created", {"steps": plan["steps"]}, trace_id=span["trace_id"], parent_span_id=span["span_id"], agent="PlannerAgent")
        end_span(span)
        return plan

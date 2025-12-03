from src.utils.logging_utils import start_span, end_span

class PlannerAgent:
    def __init__(self):
        pass

    def generate_plan(self):
        steps = [
            "load_dataset",
            "validate_schema",
            "generate_insights",
            "evaluate_insights",
            "generate_creatives",
            "generate_report",
        ]
        return {"steps": steps}

    def run(self, trace_id=None, parent_span=None):
        span = start_span("planner.run", trace_id=trace_id, parent_span_id=parent_span, agent="PlannerAgent")
        plan = self.generate_plan()
        end_span(span)
        return plan

    # backward compat
    generate = generate_plan

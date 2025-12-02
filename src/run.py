import pandas as pd
from src.utils.logging_utils import start_span, end_span, log_event
from src.utils.data_utils import load_dataset
from src.schema.validator import SchemaValidator
from src.agents.planner import PlannerAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent
from src.agents.report_agent import ReportAgent


def main():
    root = start_span("pipeline.start", agent="Pipeline")

    try:
        planner = PlannerAgent()
        plan = planner.run(trace_id=root["trace_id"])

        if "load_dataset" in plan:
            span = start_span("dataset.load", trace_id=root["trace_id"])
            df = load_dataset()
            end_span(span)

        validator = SchemaValidator()
        validator.validate_or_raise(df)

        if "generate_insights" in plan:
            agent = InsightAgent()
            span = start_span("insight.generate", trace_id=root["trace_id"])
            insights = agent.generate(df)
            end_span(span)

        if "evaluate_insights" in plan:
            agent = EvaluatorAgent()
            span = start_span("insights.evaluate", trace_id=root["trace_id"])
            evaluated = agent.evaluate(df, insights)
            end_span(span)

        if "generate_creatives" in plan:
            agent = CreativeAgent()
            span = start_span("creatives.generate", trace_id=root["trace_id"])
            creatives = agent.generate(evaluated)
            end_span(span)

        if "generate_report" in plan:
            agent = ReportAgent()
            span = start_span("report.generate", trace_id=root["trace_id"])
            agent.run(evaluated, creatives)
            end_span(span)

    except Exception as e:
        log_event("pipeline.error", {"error": str(e)}, trace_id=root["trace_id"], agent="Pipeline")

    finally:
        end_span(root)


if __name__ == "__main__":
    main()

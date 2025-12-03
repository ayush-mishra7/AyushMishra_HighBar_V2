import pandas as pd
import os

from src.utils.logging_utils import start_span, end_span, log_event
from src.agents.planner import PlannerAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent
from src.agents.report_agent import ReportAgent


def main():
    root = start_span("pipeline.start", agent="Pipeline")
    trace_id = root["trace_id"]

    # 1. PLAN
    planner = PlannerAgent()
    steps = planner.run(trace_id=trace_id, parent_span=root["span_id"])

    # 2. LOAD DATA
    data_span = start_span("data.load", trace_id=trace_id, parent_span_id=root["span_id"], agent="Pipeline")

    df_path = os.path.join("data", "synthetic_fb_ads_undergarments.csv")
    df = pd.read_csv(df_path)
    log_event("data.load.success", {"rows": len(df)}, trace_id=trace_id, parent_span_id=data_span["span_id"])
    end_span(data_span)

    # 3. VALIDATE SCHEMA
    schema_span = start_span("schema.validate", trace_id=trace_id, parent_span_id=root["span_id"])
    from src.schema.validator import validate_schema
    validate_schema(df)
    end_span(schema_span)

    # 4. GENERATE INSIGHTS
    insights_agent = InsightAgent()
    insights = insights_agent.run(df, trace_id=trace_id, parent_span=root["span_id"])

    # 5. EVALUATE INSIGHTS
    evaluator = EvaluatorAgent()
    evaluated = evaluator.run(df, insights, trace_id=trace_id, parent_span=root["span_id"])

    # 6. GENERATE CREATIVES
    creative_agent = CreativeAgent()
    creatives = creative_agent.run(evaluated, trace_id=trace_id, parent_span=root["span_id"])

    # 7. GENERATE REPORT
    report_agent = ReportAgent()
    report = report_agent.run(evaluated, creatives, trace_id=trace_id, parent_span=root["span_id"])

    # CLOSE PIPELINE
    end_span(root)


if __name__ == "__main__":
    main()

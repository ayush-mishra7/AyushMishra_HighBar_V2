from pathlib import Path
from src.utils.logging_utils import start_span, end_span, log_event
from src.utils.data_utils import load_dataset, load_config
from src.agents.planner import PlannerAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent
from src.agents.report_agent import ReportAgent

def main():
    cfg = load_config()
    root = start_span("pipeline.start", agent="Pipeline")
    try:
        planner = PlannerAgent()
        planner_span = start_span("planner.run", trace_id=root["trace_id"], parent_span_id=root["span_id"], agent="Planner")
        plan = planner.run(trace_id=planner_span["trace_id"], parent_span_id=planner_span["span_id"])
        end_span(planner_span)

        df = None
        insights = {}
        creatives = {}

        if "load_dataset" in plan["steps"]:
            ds_span = start_span("dataset.load", trace_id=root["trace_id"], parent_span_id=root["span_id"], agent="DataAgent")
            df = load_dataset()
            end_span(ds_span)

        if df is None:
            log_event("pipeline.error", {"error": "no_dataset"}, trace_id=root["trace_id"], agent="Pipeline")
            raise RuntimeError("Dataset not loaded")

        if "generate_insights" in plan["steps"]:
            ia = InsightAgent()
            ins_span = start_span("insight.generate", trace_id=root["trace_id"], parent_span_id=root["span_id"], agent="InsightAgent")
            insights = ia.generate_insights(df, trace_id=ins_span["trace_id"], parent_span=ins_span["span_id"])
            end_span(ins_span)

        if "evaluate_insights" in plan["steps"]:
            ev = EvaluatorAgent()
            ev_span = start_span("insights.evaluate", trace_id=root["trace_id"], parent_span_id=root["span_id"], agent="EvaluatorAgent")
            evaluated = ev.evaluate(df, insights, trace_id=ev_span["trace_id"], parent_span=ev_span["span_id"])
            end_span(ev_span)
            insights = evaluated  # evaluated has validated hypotheses

        if "generate_creatives" in plan["steps"]:
            ca = CreativeAgent()
            cr_span = start_span("creatives.generate", trace_id=root["trace_id"], parent_span_id=root["span_id"], agent="CreativeAgent")
            creatives = ca.generate_creatives(insights, trace_id=cr_span["trace_id"], parent_span=cr_span["span_id"])
            end_span(cr_span)

        if "generate_report" in plan["steps"]:
            ra = ReportAgent()
            rp_span = start_span("report.generate", trace_id=root["trace_id"], parent_span_id=root["span_id"], agent="ReportAgent")
            ra.run(insights, creatives, trace_id=rp_span["trace_id"], parent_span=rp_span["span_id"])
            end_span(rp_span)

        log_event("pipeline.complete", {"insights_count": len(insights.get("hypotheses", []))}, trace_id=root["trace_id"], agent="Pipeline")

    except Exception as e:
        log_event("pipeline.error", {"error": str(e)}, trace_id=root["trace_id"], agent="Pipeline")
    finally:
        end_span(root)

if __name__ == "__main__":
    main()

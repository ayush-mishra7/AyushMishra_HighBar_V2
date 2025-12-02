import pandas as pd
from src.agents.evaluator_agent import EvaluatorAgent

def test_evaluator_missing_columns():
    df = pd.DataFrame({"foo": [1,2,3]})
    agent = EvaluatorAgent()
    insights = {"hypotheses": [{"id":"h1", "segment_filter":{"campaign_name":"nonexistent"}}]}
    out = agent.evaluate(df, insights)
    v = out["hypotheses"][0]["validation"]
    assert v["sample_size"] == 0
    assert v["total_impressions"] == 0
    assert v["mean_ctr"] == 0.0

def test_evaluator_extreme_values():
    df = pd.DataFrame({
        "campaign_name": ["A","A"],
        "creative_type": ["X","X"],
        "audience_type": ["Y","Y"],
        "platform": ["FB","FB"],
        "country": ["IN","IN"],
        "impressions": [1_000_000,2_000_000],
        "clicks": [0,0],
        "spend": [0,0],
        "revenue": [0,0],
    })
    agent = EvaluatorAgent()
    insights = {"hypotheses": [{"id":"h1","segment_filter":{"campaign_name":"A"}}]}
    out = agent.evaluate(df, insights)
    v = out["hypotheses"][0]["validation"]
    assert v["mean_ctr"] == 0.0
    assert v["total_impressions"] == 3000000

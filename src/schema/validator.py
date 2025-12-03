import pandas as pd


REQUIRED_COLUMNS = [
    "campaign_name",
    "creative_type",
    "audience_type",
    "platform",
    "country",
    "impressions",
    "clicks",
    "spend",
    "revenue",
]


def validate_schema(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    numeric_cols = ["impressions", "clicks", "spend", "revenue"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["ctr"] = df.apply(
        lambda r: (r["clicks"] / r["impressions"]) if r["impressions"] > 0 else 0,
        axis=1,
    )

    df["roas"] = df.apply(
        lambda r: (r["revenue"] / r["spend"]) if r["spend"] > 0 else 0,
        axis=1,
    )

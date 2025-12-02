EXPECTED_SCHEMA = {
    "campaign_name": "object",
    "creative_type": "object",
    "audience_type": "object",
    "platform": "object",
    "country": "object",

    "impressions": "int64",
    "clicks": "int64",
    "spend": "float64",
    "revenue": "float64",

    "ctr": "float64",
    "roas": "float64",
}

OPTIONAL_COLUMNS = [
    "ad_id",
    "creative_id",
    "adset_name",
]

CRITICAL_COLUMNS = [
    "campaign_name",
    "impressions",
    "clicks",
    "spend",
    "revenue",
]

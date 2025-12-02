from typing import Dict, Any
import pandas as pd
from src.schema.dataset_schema import EXPECTED_SCHEMA, OPTIONAL_COLUMNS, CRITICAL_COLUMNS
from src.utils.logging_utils import log_event


class SchemaValidator:
    def __init__(self):
        self.expected = EXPECTED_SCHEMA
        self.optional = OPTIONAL_COLUMNS
        self.critical = CRITICAL_COLUMNS

    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        issues = []
        warnings = []

        actual_cols = set(df.columns)
        expected_cols = set(self.expected.keys())

        # 1. Missing Columns
        missing_required = expected_cols - actual_cols
        missing_critical = set(self.critical) - actual_cols
        extra_columns = actual_cols - expected_cols - set(self.optional)

        if missing_required:
            issues.append({
                "type": "missing_required_columns",
                "columns": sorted(list(missing_required))
            })

        if missing_critical:
            issues.append({
                "type": "missing_critical_columns",
                "columns": sorted(list(missing_critical))
            })

        # 2. Extra/Unexpected Columns
        if extra_columns:
            warnings.append({
                "type": "unexpected_columns",
                "columns": sorted(list(extra_columns))
            })

        # 3. Type Mismatches
        type_mismatches = {}
        for col, expected_type in self.expected.items():
            if col in df:
                actual_type = str(df[col].dtype)
                if expected_type not in actual_type:
                    type_mismatches[col] = {"expected": expected_type, "actual": actual_type}

        if type_mismatches:
            warnings.append({"type": "dtype_mismatch", "columns": type_mismatches})

        # 4. Schema Drift Detection
        drift = {}
        for col in expected_cols:
            if col in df:
                # Check if column has become all-null
                if df[col].isna().all():
                    drift[col] = "all_null"
                # Check if column created new distinct dtype (object values instead of numbers)
                if self.expected[col].startswith("float") and df[col].dtype == "object":
                    drift[col] = "numeric_became_object"

        if drift:
            warnings.append({"type": "schema_drift", "columns": drift})

        # 5. Log & Return
        log_event("schema.validation", {
            "issues": issues,
            "warnings": warnings,
            "total_columns": len(df.columns)
        }, agent="SchemaValidator")

        return {
            "ok": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    def validate_or_raise(self, df: pd.DataFrame):
        result = self.validate(df)
        if not result["ok"]:
            raise ValueError(f"Schema validation failed: {result['issues']}")
        return result

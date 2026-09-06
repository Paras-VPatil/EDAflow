import pandas as pd
import numpy as np
from typing import Dict, Any, List

def analyze_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    total_rows = len(df)
    if total_rows == 0:
        return {
            "duplicate_rows_count": 0,
            "total_rows": 0,
            "duplicate_percentage": 0.0,
            "has_duplicates": False,
            "sample_duplicates": []
        }

    # Identify duplicate rows (excluding first occurrence)
    dups_mask = df.duplicated(keep='first')
    duplicate_rows_count = int(dups_mask.sum())
    duplicate_percentage = round((duplicate_rows_count / total_rows) * 100, 2)
    has_duplicates = duplicate_rows_count > 0

    sample_duplicates = []
    if has_duplicates:
        # Sample some duplicate rows (both first and subsequent occurrences to show pairs)
        all_dups = df[df.duplicated(keep=False)].head(10)
        for _, row in all_dups.iterrows():
            row_dict = {}
            for k, v in row.items():
                if pd.isna(v):
                    row_dict[str(k)] = None
                elif isinstance(v, (np.integer, int)):
                    row_dict[str(k)] = int(v)
                elif isinstance(v, (np.floating, float)):
                    row_dict[str(k)] = float(v)
                elif isinstance(v, (bool, np.bool_)):
                    row_dict[str(k)] = bool(v)
                else:
                    row_dict[str(k)] = str(v)
            sample_duplicates.append(row_dict)

    return {
        "duplicate_rows_count": duplicate_rows_count,
        "total_rows": total_rows,
        "duplicate_percentage": duplicate_percentage,
        "has_duplicates": has_duplicates,
        "sample_duplicates": sample_duplicates
    }

def deduplicate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a new dataframe with duplicate rows removed."""
    return df.drop_duplicates().copy()

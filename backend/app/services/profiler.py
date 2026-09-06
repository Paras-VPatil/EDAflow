import pandas as pd
import numpy as np
from typing import Dict, Any, List

def format_memory(bytes_val: int) -> str:
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.2f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

def infer_column_type(series: pd.Series, total_rows: int) -> Dict[str, Any]:
    non_null_series = series.dropna()
    unique_count = int(series.nunique(dropna=True))
    null_count = int(series.isnull().sum())
    unique_ratio = unique_count / total_rows if total_rows > 0 else 0.0
    null_ratio = null_count / total_rows if total_rows > 0 else 1.0

    dtype_str = str(series.dtype)
    is_constant = (unique_count <= 1 and total_rows > 0 and null_count == 0)
    is_all_null = (null_count == total_rows)
    is_boolean = False
    is_datetime = False
    is_numeric = False
    is_id_like = False
    is_categorical = False
    inferred_type = "categorical"

    # All-null or constant check
    if is_all_null:
        inferred_type = "constant"
        is_constant = True
    elif is_constant:
        inferred_type = "constant"
    
    # Boolean check
    elif pd.api.types.is_bool_dtype(series):
        is_boolean = True
        inferred_type = "boolean"
    elif unique_count == 2 and not non_null_series.empty:
        vals = set(non_null_series.unique())
        if vals.issubset({0, 1, 0.0, 1.0}) or vals.issubset({'0', '1', 'True', 'False', 'true', 'false', 'yes', 'no', 'Y', 'N', 't', 'f'}):
            is_boolean = True
            inferred_type = "boolean"

    # Datetime check
    elif pd.api.types.is_datetime64_any_dtype(series):
        is_datetime = True
        inferred_type = "datetime"
    elif dtype_str == "object" and not non_null_series.empty and unique_count > 2:
        sample = non_null_series.head(50)
        try:
            converted = pd.to_datetime(sample, errors='coerce')
            if converted.notnull().mean() > 0.85 and not sample.str.isnumeric().all():
                is_datetime = True
                inferred_type = "datetime"
        except Exception:
            pass

    # Numeric check
    if not is_boolean and not is_datetime and not is_constant and not is_all_null:
        if pd.api.types.is_numeric_dtype(series):
            is_numeric = True
            if unique_ratio > 0.95 and total_rows >= 20 and (series.name and any(k in str(series.name).lower() for k in ["id", "uuid", "guid", "key", "index"])):
                is_id_like = True
                inferred_type = "id_like"
            else:
                inferred_type = "numeric"
        elif unique_ratio > 0.95 and total_rows >= 20:
            is_id_like = True
            inferred_type = "id_like"
        else:
            is_categorical = True
            inferred_type = "categorical"

    # Sample values (safe extraction)
    samples = []
    if not non_null_series.empty:
        raw_samples = non_null_series.head(5).tolist()
        for v in raw_samples:
            if pd.isna(v):
                continue
            elif isinstance(v, (np.integer, int)):
                samples.append(int(v))
            elif isinstance(v, (np.floating, float)):
                samples.append(float(v))
            elif isinstance(v, (bool, np.bool_)):
                samples.append(bool(v))
            else:
                samples.append(str(v))

    memory_bytes = int(series.memory_usage(deep=True))

    return {
        "name": str(series.name),
        "dtype": dtype_str,
        "inferred_type": inferred_type,
        "is_numeric": is_numeric,
        "is_categorical": (inferred_type == "categorical"),
        "is_datetime": is_datetime,
        "is_boolean": is_boolean,
        "is_constant": is_constant,
        "is_id_like": is_id_like,
        "unique_count": unique_count,
        "unique_ratio": round(unique_ratio, 4),
        "null_count": null_count,
        "null_ratio": round(null_ratio, 4),
        "memory_bytes": memory_bytes,
        "sample_values": samples
    }

def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    rows_count = len(df)
    cols_count = len(df.columns)
    total_memory_bytes = int(df.memory_usage(deep=True).sum()) if cols_count > 0 else 0
    total_memory_formatted = format_memory(total_memory_bytes)

    columns = []
    numeric_columns = []
    categorical_columns = []
    datetime_columns = []
    boolean_columns = []
    constant_columns = []
    id_like_columns = []

    for col in df.columns:
        col_prof = infer_column_type(df[col], rows_count)
        columns.append(col_prof)

        inferred = col_prof["inferred_type"]
        if inferred == "numeric":
            numeric_columns.append(col_prof["name"])
        elif inferred == "categorical":
            categorical_columns.append(col_prof["name"])
        elif inferred == "datetime":
            datetime_columns.append(col_prof["name"])
        elif inferred == "boolean":
            boolean_columns.append(col_prof["name"])
        elif inferred == "constant":
            constant_columns.append(col_prof["name"])
        elif inferred == "id_like":
            id_like_columns.append(col_prof["name"])

    return {
        "rows_count": rows_count,
        "columns_count": cols_count,
        "total_memory_bytes": total_memory_bytes,
        "total_memory_formatted": total_memory_formatted,
        "columns": columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "datetime_columns": datetime_columns,
        "boolean_columns": boolean_columns,
        "constant_columns": constant_columns,
        "id_like_columns": id_like_columns
    }

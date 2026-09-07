import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression

def fit_baseline_model(
    df: pd.DataFrame,
    target_column: str,
    task_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fits a leakage-free cross-validated baseline machine learning model and computes
    feature importance rankings ("Score to Beat").
    
    Supports:
    - Pure numeric feature sets
    - Pure categorical feature sets
    - Mixed numeric + categorical feature sets
    - Graceful failure on single-class targets
    - Zero data leakage (imputation & scaling fit strictly inside CV folds via ColumnTransformer)
    - Discrete feature flags passed correctly to mutual information calculators
    """
    if target_column not in df.columns:
        return {"error": f"Target column '{target_column}' not found in dataset."}

    # Filter out null targets
    clean_mask = df[target_column].notnull()
    clean_df = df[clean_mask].copy()

    if len(clean_df) < 10:
        return {"error": "Insufficient non-null rows in target column (need at least 10 observations)."}

    y = clean_df[target_column]

    # Guard: Single-class target check
    if y.nunique() <= 1:
        return {
            "error": f"Target column '{target_column}' contains only 1 unique value ({y.iloc[0]}). Machine learning modeling requires at least 2 distinct classes or variations."
        }

    # Infer task type if not provided
    if task_type is None:
        if pd.api.types.is_numeric_dtype(y) and y.nunique() > 10:
            task_type = "regression"
        else:
            task_type = "classification"

    # Select feature columns
    feature_cols = [c for c in clean_df.columns if c != target_column]
    if not feature_cols:
        return {"error": "No feature predictor columns available in dataset."}

    numeric_features = []
    categorical_features = []

    for c in feature_cols:
        if pd.api.types.is_numeric_dtype(clean_df[c]) and not pd.api.types.is_bool_dtype(clean_df[c]):
            numeric_features.append(c)
        elif clean_df[c].nunique() <= 30:
            categorical_features.append(c)

    if not numeric_features and not categorical_features:
        return {"error": "No usable numeric or low-cardinality categorical features for modeling."}

    # Build Leakage-Free Preprocessing Pipeline with ColumnTransformer
    transformers = []
    
    if numeric_features:
        num_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        transformers.append(("num", num_pipeline, numeric_features))

    if categorical_features:
        cat_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])
        transformers.append(("cat", cat_pipeline, categorical_features))

    preprocessor = ColumnTransformer(transformers=transformers)

    # Subsample if extremely large for fast cross-validation
    X_df = clean_df[numeric_features + categorical_features]
    if len(X_df) > 10000:
        sample_idx = np.random.RandomState(42).choice(len(X_df), 10000, replace=False)
        X_sub_df = X_df.iloc[sample_idx]
        y_sub = y.iloc[sample_idx]
    else:
        X_sub_df = X_df
        y_sub = y

    # Compute Feature Importance via Mutual Information with discrete_features mask
    feature_importance: List[Dict[str, Any]] = []

    try:
        # Preprocess sample matrix for mutual information inspection
        X_transformed = preprocessor.fit_transform(X_sub_df)
        
        # Get output feature names
        output_feature_names = []
        discrete_mask = []

        if numeric_features:
            output_feature_names.extend(numeric_features)
            discrete_mask.extend([False] * len(numeric_features))

        if categorical_features:
            cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
            cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
            output_feature_names.extend(cat_names)
            discrete_mask.extend([True] * len(cat_names))

        discrete_mask_arr = np.array(discrete_mask, dtype=bool)

        if task_type == "classification":
            y_encoded = pd.factorize(y_sub)[0]
            unique_classes = np.unique(y_encoded)
            
            if len(unique_classes) < 2:
                return {
                    "error": f"Target column contains only 1 class in sample. Cannot train classification model."
                }

            # Mutual information with exact discrete feature indicators
            mi_scores = mutual_info_classif(
                X_transformed,
                y_encoded,
                discrete_features=discrete_mask_arr,
                random_state=42
            )

            # Full leakage-free CV Pipeline
            model_pipe = Pipeline([
                ("preprocessor", preprocessor),
                ("clf", LogisticRegression(max_iter=500, random_state=42))
            ])

            # Determine CV splits safely
            min_class_count = pd.Series(y_encoded).value_counts().min()
            n_splits = min(5, max(2, min_class_count))

            cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
            scores_acc = cross_val_score(model_pipe, X_sub_df, y_encoded, cv=cv, scoring="accuracy")
            scores_f1 = cross_val_score(model_pipe, X_sub_df, y_encoded, cv=cv, scoring="f1_weighted")

            for name, score in zip(output_feature_names, mi_scores):
                feature_importance.append({
                    "feature": str(name),
                    "importance_score": round(float(score), 4)
                })

            feature_importance.sort(key=lambda x: x["importance_score"], reverse=True)

            return {
                "task_type": "classification",
                "model_name": "Logistic Regression (L2 Regularized Baseline)",
                "target_column": target_column,
                "n_samples": int(len(X_sub_df)),
                "n_features": int(X_transformed.shape[1]),
                "metrics": {
                    "mean_accuracy": round(float(np.mean(scores_acc)), 4),
                    "std_accuracy": round(float(np.std(scores_acc)), 4),
                    "mean_f1_weighted": round(float(np.mean(scores_f1)), 4),
                    "std_f1_weighted": round(float(np.std(scores_f1)), 4)
                },
                "score_to_beat": f"{np.mean(scores_acc)*100:.1f}% Accuracy",
                "feature_importance": feature_importance[:15]
            }

        else:
            # Continuous Regression Task
            y_num = pd.to_numeric(y_sub, errors="coerce")
            valid_y_mask = y_num.notnull()
            y_num = y_num[valid_y_mask]
            X_reg_df = X_sub_df[valid_y_mask]

            if len(y_num) < 10 or y_num.nunique() <= 1:
                return {
                    "error": "Insufficient continuous variation in target column for regression modeling."
                }

            X_reg_transformed = preprocessor.fit_transform(X_reg_df)

            mi_scores = mutual_info_regression(
                X_reg_transformed,
                y_num,
                discrete_features=discrete_mask_arr,
                random_state=42
            )

            model_pipe = Pipeline([
                ("preprocessor", preprocessor),
                ("reg", Ridge(alpha=1.0))
            ])

            cv = KFold(n_splits=5, shuffle=True, random_state=42)
            scores_r2 = cross_val_score(model_pipe, X_reg_df, y_num, cv=cv, scoring="r2")
            scores_neg_rmse = cross_val_score(model_pipe, X_reg_df, y_num, cv=cv, scoring="neg_root_mean_squared_error")

            for name, score in zip(output_feature_names, mi_scores):
                feature_importance.append({
                    "feature": str(name),
                    "importance_score": round(float(score), 4)
                })

            feature_importance.sort(key=lambda x: x["importance_score"], reverse=True)

            return {
                "task_type": "regression",
                "model_name": "Ridge Linear Regression (L2 Regularized Baseline)",
                "target_column": target_column,
                "n_samples": int(len(X_reg_df)),
                "n_features": int(X_reg_transformed.shape[1]),
                "metrics": {
                    "mean_r2": round(float(np.mean(scores_r2)), 4),
                    "std_r2": round(float(np.std(scores_r2)), 4),
                    "mean_rmse": round(float(-np.mean(scores_neg_rmse)), 4),
                    "std_rmse": round(float(np.std(scores_neg_rmse)), 4)
                },
                "score_to_beat": f"R² = {np.mean(scores_r2):.3f} (RMSE: {-np.mean(scores_neg_rmse):.3f})",
                "feature_importance": feature_importance[:15]
            }

    except Exception as e:
        return {
            "error": f"Failed to compute baseline model: {str(e)}"
        }

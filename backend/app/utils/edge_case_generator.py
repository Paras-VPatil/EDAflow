import os
from pathlib import Path
import pandas as pd
import numpy as np

def generate_all_test_datasets(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    invalid_dir = target_dir / "invalid"
    invalid_dir.mkdir(parents=True, exist_ok=True)

    np.random.seed(42)

    # 1. 01_clean.csv
    pd.DataFrame({
        "age": [21, 25, 29, 35, 40],
        "income": [30000, 45000, 52000, 70000, 80000],
        "score": [72, 81, 85, 91, 95]
    }).to_csv(target_dir / "01_clean.csv", index=False)

    # 2. 02_mixed_types.csv
    pd.DataFrame({
        "age": [21, 25, 29, 35],
        "income": [30000, 45000, 52000, 70000],
        "city": ["Pune", "Mumbai", "Delhi", "Pune"],
        "gender": ["M", "F", "M", "F"]
    }).to_csv(target_dir / "02_mixed_types.csv", index=False)

    # 3. 03_empty.csv (completely 0 bytes)
    with open(target_dir / "03_empty.csv", "w") as f:
        pass

    # 4. 04_header_only.csv
    with open(target_dir / "04_header_only.csv", "w") as f:
        f.write("age,income,city\n")

    # 5. 05_one_row.csv
    pd.DataFrame({
        "age": [25],
        "income": [50000],
        "city": ["Pune"]
    }).to_csv(target_dir / "05_one_row.csv", index=False)

    # 6. 06_one_column.csv
    pd.DataFrame({
        "age": [20, 25, 30, 35]
    }).to_csv(target_dir / "06_one_column.csv", index=False)

    # 7. 07_missing.csv
    pd.DataFrame({
        "age": [20, 25, 30, np.nan],
        "income": [30000, np.nan, 50000, 60000]
    }).to_csv(target_dir / "07_missing.csv", index=False)

    # 8. 08_all_missing_column.csv
    pd.DataFrame({
        "age": [20, 25, 30],
        "income": [30000, 45000, 50000],
        "occupation": [np.nan, np.nan, np.nan]
    }).to_csv(target_dir / "08_all_missing_column.csv", index=False)

    # 9. 09_high_missing.csv
    n_hm = 100
    pd.DataFrame({
        "id": range(n_hm),
        "feature_a": np.random.randn(n_hm),
        "feature_sparse": [np.nan if i > 1 else float(i) for i in range(n_hm)]
    }).to_csv(target_dir / "09_high_missing.csv", index=False)

    # 10. 10_duplicates.csv
    pd.DataFrame({
        "age": [20, 25, 20, 30],
        "income": [30000, 40000, 30000, 50000]
    }).to_csv(target_dir / "10_duplicates.csv", index=False)

    # 11. 11_all_duplicates.csv
    pd.DataFrame({
        "age": [20, 20, 20, 20],
        "income": [30000, 30000, 30000, 30000]
    }).to_csv(target_dir / "11_all_duplicates.csv", index=False)

    # 12. 12_constant.csv
    pd.DataFrame({
        "age": [20, 25, 30, 35],
        "country": ["India", "India", "India", "India"],
        "constant": [1, 1, 1, 1]
    }).to_csv(target_dir / "12_constant.csv", index=False)

    # 13. 13_high_cardinality.csv
    n_hc = 200
    cities = [f"City_{i % 60}" for i in range(n_hc)]
    pd.DataFrame({
        "id": range(n_hc),
        "city": cities,
        "val": np.random.randn(n_hc)
    }).to_csv(target_dir / "13_high_cardinality.csv", index=False)

    # 14. 14_id_like.csv
    n_id = 100
    pd.DataFrame({
        "customer_id": [f"CUST_{10000+i}" for i in range(n_id)],
        "amount": np.random.exponential(100, size=n_id)
    }).to_csv(target_dir / "14_id_like.csv", index=False)

    # 15. 15_normal.csv
    pd.DataFrame({
        "norm_val": np.random.normal(50, 10, size=300)
    }).to_csv(target_dir / "15_normal.csv", index=False)

    # 16. 16_right_skewed.csv
    pd.DataFrame({
        "income": [10000, 12000, 15000, 20000, 25000, 30000, 35000, 1000000]
    }).to_csv(target_dir / "16_right_skewed.csv", index=False)

    # 17. 17_left_skewed.csv
    arr_ls = np.random.beta(7, 2, size=200) * 100
    pd.DataFrame({"score": arr_ls}).to_csv(target_dir / "17_left_skewed.csv", index=False)

    # 18. 18_heavy_tail.csv
    pd.DataFrame({
        "t_dist": np.random.standard_t(df=2, size=300)
    }).to_csv(target_dir / "18_heavy_tail.csv", index=False)

    # 19. 19_outliers.csv
    pd.DataFrame({
        "vals": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 1000]
    }).to_csv(target_dir / "19_outliers.csv", index=False)

    # 20. 20_multivariate_anomaly.csv
    n_multi = 100
    ages = np.random.normal(30, 5, size=n_multi)
    incomes = ages * 1500 + np.random.normal(0, 1000, size=n_multi)
    # Inject multivariate anomaly (age 22, income 5,000,000)
    ages[0] = 22.0
    incomes[0] = 5000000.0
    pd.DataFrame({"age": ages, "income": incomes}).to_csv(target_dir / "20_multivariate_anomaly.csv", index=False)

    # 21. 21_positive_corr.csv
    x_pos = np.linspace(1, 20, 30)
    y_pos = x_pos * 2.5 + np.random.normal(0, 0.2, 30)
    pd.DataFrame({"x": x_pos, "y": y_pos}).to_csv(target_dir / "21_positive_corr.csv", index=False)

    # 22. 22_negative_corr.csv
    x_neg = np.linspace(1, 20, 30)
    y_neg = -x_neg * 3.0 + np.random.normal(0, 0.2, 30)
    pd.DataFrame({"x": x_neg, "y": y_neg}).to_csv(target_dir / "22_negative_corr.csv", index=False)

    # 23. 23_no_corr.csv
    pd.DataFrame({
        "rand_a": np.random.uniform(0, 100, 50),
        "rand_b": np.random.uniform(0, 100, 50)
    }).to_csv(target_dir / "23_no_corr.csv", index=False)

    # 24. 24_nonlinear.csv
    x_nl = np.linspace(-10, 10, 50)
    y_nl = x_nl ** 2
    pd.DataFrame({"x": x_nl, "y_quadratic": y_nl}).to_csv(target_dir / "24_nonlinear.csv", index=False)

    # 25. 25_binary_target.csv
    pd.DataFrame({
        "age": [25, 30, 40, 35, 28, 50],
        "income": [30000, 40000, 70000, 60000, 35000, 90000],
        "churn": [0, 0, 1, 1, 0, 1]
    }).to_csv(target_dir / "25_binary_target.csv", index=False)

    # 26. 26_multiclass_target.csv
    pd.DataFrame({
        "age": [20, 30, 40, 50, 25, 35],
        "segment": ["A", "B", "C", "A", "B", "C"]
    }).to_csv(target_dir / "26_multiclass_target.csv", index=False)

    # 27. 27_regression_target.csv
    pd.DataFrame({
        "area": [1000, 1500, 2000, 2500, 3000],
        "bedrooms": [2, 3, 4, 4, 5],
        "price": [5000000, 7000000, 9000000, 11000000, 14000000]
    }).to_csv(target_dir / "27_regression_target.csv", index=False)

    # 28. 28_imbalanced_target.csv
    n_imb = 200
    target_imb = [1 if i < 4 else 0 for i in range(n_imb)]
    pd.DataFrame({
        "feature": np.random.randn(n_imb),
        "target": target_imb
    }).to_csv(target_dir / "28_imbalanced_target.csv", index=False)

    # 29. 29_single_class_target.csv
    pd.DataFrame({
        "feature": [10, 20, 30, 40],
        "target": [0, 0, 0, 0]
    }).to_csv(target_dir / "29_single_class_target.csv", index=False)

    # 30. 30_disaster_dataset.csv (Combined extreme test with nulls, dups, skew, high-cardinality, constant, all-null, outliers)
    n_disaster = 150
    disaster_df = pd.DataFrame({
        "customer_id": [f"ID_{i:04d}" for i in range(n_disaster)],
        "age": np.random.choice([25, 30, 35, np.nan], size=n_disaster),
        "income": np.random.exponential(40000, size=n_disaster),
        "city": [f"City_{i % 80}" for i in range(n_disaster)],
        "department": np.random.choice(["HR", "Engineering", "Sales"], size=n_disaster),
        "salary": np.random.normal(5000, 1000, size=n_disaster),
        "constant_col": [999] * n_disaster,
        "all_null_col": [np.nan] * n_disaster,
        "churn": [1 if i < 3 else 0 for i in range(n_disaster)]
    })
    # Inject extreme outlier in salary
    disaster_df.loc[0, "salary"] = 99999999.0
    # Inject duplicate rows
    disaster_df = pd.concat([disaster_df, disaster_df.iloc[[5, 10, 15, 20]]], ignore_index=True)
    disaster_df.to_csv(target_dir / "30_disaster_dataset.csv", index=False)

    # Invalid files for security tests
    with open(invalid_dir / "corrupt.csv", "w", encoding="latin-1") as f:
        f.write("col1,col2\n1,2\n3,\x00\xff\xfe,5\n")

    with open(invalid_dir / "test.py", "w") as f:
        f.write("import os\nprint('malicious script')\n")

    with open(invalid_dir / "malicious.exe", "wb") as f:
        f.write(b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    generate_all_test_datasets(base_dir / "test_datasets")
    print("All test datasets generated successfully.")

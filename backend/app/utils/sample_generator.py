import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

def generate_sample_datasets() -> Dict[str, pd.DataFrame]:
    np.random.seed(42)
    datasets: Dict[str, pd.DataFrame] = {}

    # 1. Telecom Customer Churn Dataset
    n_churn = 1200
    tenures = np.random.randint(1, 72, size=n_churn)
    monthly_charges = np.random.uniform(20.0, 118.0, size=n_churn)
    total_charges = tenures * monthly_charges * np.random.uniform(0.95, 1.05, size=n_churn)
    contracts = np.random.choice(["Month-to-month", "One year", "Two year"], size=n_churn, p=[0.55, 0.25, 0.20])
    payment_methods = np.random.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"], size=n_churn)
    internet_services = np.random.choice(["Fiber optic", "DSL", "No"], size=n_churn, p=[0.45, 0.35, 0.20])
    tech_support = np.random.choice(["Yes", "No", "No internet service"], size=n_churn, p=[0.30, 0.50, 0.20])
    
    # Target probability influenced by contract & monthly charges
    churn_prob = 0.2 + (contracts == "Month-to-month") * 0.35 + (monthly_charges > 75) * 0.20 - (tenures > 36) * 0.25
    churn_prob = np.clip(churn_prob, 0.05, 0.90)
    churn = np.where(np.random.rand(n_churn) < churn_prob, "Yes", "No")

    # Introduce realistic missing values and outliers
    total_charges_series = total_charges.copy()
    total_charges_series[np.random.choice(n_churn, size=45, replace=False)] = np.nan
    # Extreme outlier in monthly charges
    monthly_charges[np.random.choice(n_churn, size=8, replace=False)] = np.random.uniform(250, 400, size=8)

    churn_df = pd.DataFrame({
        "customerID": [f"7590-VHVEG{i:04d}" for i in range(n_churn)],
        "gender": np.random.choice(["Male", "Female"], size=n_churn),
        "SeniorCitizen": np.random.choice([0, 1], size=n_churn, p=[0.84, 0.16]),
        "Partner": np.random.choice(["Yes", "No"], size=n_churn),
        "Dependents": np.random.choice(["Yes", "No"], size=n_churn, p=[0.3, 0.7]),
        "tenure": tenures,
        "PhoneService": np.random.choice(["Yes", "No"], size=n_churn, p=[0.9, 0.1]),
        "InternetService": internet_services,
        "TechSupport": tech_support,
        "Contract": contracts,
        "PaymentMethod": payment_methods,
        "MonthlyCharges": np.round(monthly_charges, 2),
        "TotalCharges": np.round(total_charges_series, 2),
        "Churn": churn
    })
    # Add a constant column and a few duplicate rows to test quality engine
    churn_df["DataVersion"] = "v1.0"
    churn_df = pd.concat([churn_df, churn_df.iloc[[12, 45, 98, 120]]], ignore_index=True)
    datasets["customer_churn.csv"] = churn_df

    # 2. Titanic Survival Dataset
    n_titanic = 891
    pclasses = np.random.choice([1, 2, 3], size=n_titanic, p=[0.24, 0.21, 0.55])
    sexes = np.random.choice(["male", "female"], size=n_titanic, p=[0.65, 0.35])
    ages = np.random.normal(29.7, 14.5, size=n_titanic)
    ages = np.clip(ages, 0.42, 80.0)
    ages[np.random.choice(n_titanic, size=177, replace=False)] = np.nan
    sibsp = np.random.choice([0, 1, 2, 3, 4, 5, 8], size=n_titanic, p=[0.68, 0.23, 0.03, 0.02, 0.02, 0.01, 0.01])
    parch = np.random.choice([0, 1, 2, 3, 4, 5, 6], size=n_titanic, p=[0.76, 0.13, 0.08, 0.01, 0.01, 0.005, 0.005])
    fares = np.where(pclasses == 1, np.random.exponential(60, size=n_titanic) + 30,
            np.where(pclasses == 2, np.random.exponential(20, size=n_titanic) + 10,
                     np.random.exponential(10, size=n_titanic) + 4))
    fares[np.random.choice(n_titanic, size=5, replace=False)] = np.random.uniform(300, 512, size=5)
    embarked = np.random.choice(["S", "C", "Q"], size=n_titanic, p=[0.72, 0.19, 0.09])
    
    # Survival calculation
    surv_prob = 0.15 + (sexes == "female") * 0.50 + (pclasses == 1) * 0.25 - (pclasses == 3) * 0.15
    surv_prob = np.clip(surv_prob, 0.05, 0.95)
    survived = np.where(np.random.rand(n_titanic) < surv_prob, 1, 0)

    cabin_missing_mask = np.random.rand(n_titanic) < 0.77
    cabins = [np.nan if m else f"C{np.random.randint(10, 120)}" for m in cabin_missing_mask]

    titanic_df = pd.DataFrame({
        "PassengerId": np.arange(1, n_titanic + 1),
        "Survived": survived,
        "Pclass": pclasses,
        "Name": [f"Passenger, Traveler {i}" for i in range(1, n_titanic + 1)],
        "Sex": sexes,
        "Age": np.round(ages, 1),
        "SibSp": sibsp,
        "Parch": parch,
        "Fare": np.round(fares, 2),
        "Cabin": cabins,
        "Embarked": embarked
    })
    datasets["titanic_survival.csv"] = titanic_df

    # 3. California Housing Prices (Regression Dataset)
    n_house = 1500
    med_inc = np.random.gamma(3.0, 1.2, size=n_house)
    house_age = np.random.uniform(1.0, 52.0, size=n_house)
    ave_rooms = med_inc * 1.2 + np.random.normal(0, 0.5, size=n_house)
    ave_rooms = np.clip(ave_rooms, 2.0, 12.0)
    ave_bedrms = ave_rooms * 0.2 + np.random.normal(0, 0.1, size=n_house)
    population = np.random.exponential(1200, size=n_house) + 200
    ave_occup = np.random.normal(3.0, 0.8, size=n_house)
    latitude = np.random.uniform(32.5, 42.0, size=n_house)
    longitude = np.random.uniform(-124.3, -114.3, size=n_house)
    ocean_prox = np.random.choice(["<1H OCEAN", "INLAND", "NEAR OCEAN", "NEAR BAY", "ISLAND"], size=n_house, p=[0.44, 0.32, 0.13, 0.10, 0.01])
    
    # Target value (Median House Value in $100k)
    med_val = (med_inc * 40.0) - (ocean_prox == "INLAND") * 50.0 + (ocean_prox == "NEAR OCEAN") * 40.0 + (house_age * 0.8) + np.random.normal(50, 20, size=n_house)
    med_val = np.clip(med_val, 14.9, 500.0)

    housing_df = pd.DataFrame({
        "MedInc": np.round(med_inc, 3),
        "HouseAge": np.round(house_age, 1),
        "AveRooms": np.round(ave_rooms, 2),
        "AveBedrms": np.round(ave_bedrms, 2),
        "Population": np.round(population, 0),
        "AveOccup": np.round(ave_occup, 2),
        "Latitude": np.round(latitude, 3),
        "Longitude": np.round(longitude, 3),
        "OceanProximity": ocean_prox,
        "MedianHouseValue": np.round(med_val, 1)
    })
    datasets["california_housing.csv"] = housing_df

    # 4. Employee Attrition & HR Analytics Dataset
    n_hr = 1000
    dept = np.random.choice(["Sales", "Research & Development", "Human Resources"], size=n_hr, p=[0.30, 0.65, 0.05])
    job_role = np.random.choice(["Sales Executive", "Research Scientist", "Laboratory Technician", "Manufacturing Director", "Healthcare Representative", "Manager"], size=n_hr)
    monthly_income = np.random.exponential(4500, size=n_hr) + 1500
    monthly_income[np.random.choice(n_hr, size=15, replace=False)] = np.random.uniform(18000, 25000, size=15)
    years_at_co = np.random.geometric(0.15, size=n_hr)
    job_sat = np.random.choice([1, 2, 3, 4], size=n_hr, p=[0.15, 0.20, 0.35, 0.30])
    work_life = np.random.choice([1, 2, 3, 4], size=n_hr, p=[0.10, 0.25, 0.45, 0.20])
    overtime = np.random.choice(["Yes", "No"], size=n_hr, p=[0.28, 0.72])

    att_prob = 0.10 + (overtime == "Yes") * 0.20 + (job_sat == 1) * 0.25 - (monthly_income > 8000) * 0.15 - (years_at_co > 8) * 0.10
    att_prob = np.clip(att_prob, 0.03, 0.85)
    attrition = np.where(np.random.rand(n_hr) < att_prob, "Yes", "No")

    hr_df = pd.DataFrame({
        "EmployeeID": [f"EMP-{i:05d}" for i in range(1, n_hr + 1)],
        "Age": np.random.randint(20, 60, size=n_hr),
        "Department": dept,
        "JobRole": job_role,
        "MonthlyIncome": np.round(monthly_income, 2),
        "YearsAtCompany": years_at_co,
        "JobSatisfaction": job_sat,
        "WorkLifeBalance": work_life,
        "OverTime": overtime,
        "Attrition": attrition
    })
    datasets["employee_attrition.csv"] = hr_df

    return datasets

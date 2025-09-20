import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score, average_precision_score, roc_curve,
    precision_recall_curve, classification_report, confusion_matrix
)
import matplotlib.pyplot as plt

# Load trained pipeline + feature list
ARTIFACT = "ed_admit_model.joblib"
art = joblib.load(ARTIFACT)
pipe = art["pipeline"]
FEATURES = art["features"]

def ask_int(prompt, default=-1):
    while True:
        s = input(f"{prompt} (int, default {default}): ").strip()
        if s == "":
            return default
        try:
            return int(float(s))
        except ValueError:
            print("Please enter an integer (or press Enter for default).")

# Collect inputs
print("Enter patient values for these features (use -1 if unknown):")
# row = {f: ask_int(f) for f in FEATURES}

# print(row)

row = {'triage_category': 5, 
        'age': 50, 
        'primary_diagnosis_ICD10AM_chapter': 11, 
        'affected_by_drugs_and_or_alcohol': 0, 
        'mental_health_admission': 0
        }

# 

# Predict probability
X_new = pd.DataFrame([row], columns=FEATURES)
p = float(pipe.predict_proba(X_new)[:, 1][0])

print(f"\nPatient has {p*100:.2f}% probability to be admitted.")
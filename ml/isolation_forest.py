import os
import pandas as pd
from sklearn.ensemble import IsolationForest

# Get the project root directory (parent of ml/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, "data/processed")

INPUT = os.path.join(DATA_DIR, "feature_matrix.csv")
OUTPUT = os.path.join(DATA_DIR, "anomaly_scores.csv")

def main():
    df = pd.read_csv(INPUT)

    X = df.select_dtypes(include=["number"])

    model = IsolationForest(
        n_estimators=200,
        contamination=0.15,
        random_state=42
    )

    df["anomaly_score"] = model.fit_predict(X)
    df["anomaly_score"] = model.decision_function(X)

    df.to_csv(OUTPUT, index=False)

if __name__ == "__main__":
    main()

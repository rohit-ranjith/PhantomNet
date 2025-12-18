import pandas as pd
from sklearn.ensemble import IsolationForest

INPUT = "../data/processed/feature_matrix.csv"
OUTPUT = "../data/processed/anomaly_scores.csv"

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

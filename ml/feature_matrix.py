import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "num_sessions",
    "avg_duration",
    "std_duration",
    "total_commands",
    "login_success_rate",
    "protocol_error_rate",
    "unique_hassh"
]

def main():
    df = pd.read_csv("../data/processed/attackers_labeled.csv")
    X = df[FEATURES].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_df = pd.DataFrame(X_scaled, columns=FEATURES)
    X_df["src_ip"] = df["src_ip"]

    X_df.to_csv("../data/processed/feature_matrix.csv", index=False)

if __name__ == "__main__":
    main()

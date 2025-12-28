import os
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Get the project root directory (parent of ml/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, "data/processed")

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
    df = pd.read_csv(os.path.join(DATA_DIR, "attackers_labeled.csv"))
    X = df[FEATURES].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_df = pd.DataFrame(X_scaled, columns=FEATURES)
    X_df["src_ip"] = df["src_ip"]

    X_df.to_csv(os.path.join(DATA_DIR, "feature_matrix.csv"), index=False)

if __name__ == "__main__":
    main()

import os
import pandas as pd

# Get the project root directory (parent of ml/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, "data/processed")

# Load session-level data
df = pd.read_csv(os.path.join(DATA_DIR, "sessions.csv"))

# Basic cleanup - convert login_success to int (handles bool, int, or string)
if "login_success" in df.columns:
    df["login_success"] = df["login_success"].astype(bool).astype(int)
else:
    df["login_success"] = 0

# Aggregate by source IP
attackers = df.groupby("src_ip").agg(
    num_sessions=("session_id", "count"),
    avg_duration=("duration_seconds", "mean"),
    std_duration=("duration_seconds", "std"),
    total_commands=("num_commands", "sum"),
    sessions_with_commands=("num_commands", lambda x: (x > 0).sum()),
    login_success_rate=("login_success", "mean"),
    unique_client_versions=("client_version", "nunique"),
    unique_hassh=("hassh", "nunique"),
    protocol_error_rate=("protocol_errors", "mean"),
).reset_index()

# Fill NaNs (e.g., std with 1 session)
attackers = attackers.fillna(0)

# Save
attackers.to_csv(os.path.join(DATA_DIR, "attackers.csv"), index=False)

print(f"[+] Generated attacker profiles: {len(attackers)}")

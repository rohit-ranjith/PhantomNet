import pandas as pd

# Load session-level data
df = pd.read_csv("../data/processed/sessions.csv")

# Basic cleanup
df["login_success"] = df["login_success"].astype(int)

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
attackers.to_csv("../data/processed/attackers.csv", index=False)

print(f"[+] Generated attacker profiles: {len(attackers)}")

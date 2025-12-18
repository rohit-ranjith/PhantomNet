import json
import pandas as pd
from pathlib import Path

RAW_DIR = "../data/raw/cowrie_snapshots"
OUTPUT = "../data/processed/sessions.csv"

def iter_cowrie_files():
    return Path(RAW_DIR).rglob("cowrie.json*")

def main():
    rows = []
    seen_sessions = set()

    for file_path in iter_cowrie_files():
        if file_path.name == ".gitignore":
            continue

        try:
            with open(file_path) as f:
                for line in f:
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    session = event.get("session")
                    if not session or session in seen_sessions:
                        continue

                    seen_sessions.add(session)
                    rows.append(event)

        except Exception as e:
            print(f"[!] Failed to read {file_path}: {e}")

    if not rows:
        print("[!] No Cowrie events found")
        return

    df = pd.json_normalize(rows)

    # Minimal session-level aggregation
    sessions = (
        df.groupby("session")
        .agg(
            src_ip=("src_ip", "first"),
            start_time=("timestamp", "min"),
            end_time=("timestamp", "max"),
            num_commands=("input", "count"),
            client_version=("version", "first"),
            hassh=("hassh", "first"),
            protocol_errors=("eventid", lambda x: (x == "cowrie.client.version").sum())
        )
        .reset_index()
    )

    sessions["start_time"] = pd.to_datetime(sessions["start_time"])
    sessions["end_time"] = pd.to_datetime(sessions["end_time"])
    sessions["duration_seconds"] = (
        sessions["end_time"] - sessions["start_time"]
    ).dt.total_seconds()

    sessions.to_csv(OUTPUT, index=False)
    print(f"[+] Wrote {len(sessions)} sessions to {OUTPUT}")

if __name__ == "__main__":
    main()

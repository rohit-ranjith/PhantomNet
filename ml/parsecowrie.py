import json
import os
from collections import defaultdict
from datetime import datetime
import pandas as pd
from pathlib import Path

# Get the project root directory (parent of ml/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_DIR = os.path.join(PROJECT_ROOT, "data/raw/cowrie_snapshots")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data/processed")
OUTPUT = os.path.join(OUTPUT_DIR, "sessions.csv")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_timestamp(ts):
    """Parse Cowrie ISO timestamps safely."""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None

def iter_cowrie_files():
    """Find all cowrie log files in the raw directory."""
    raw_path = Path(RAW_DIR)
    if not raw_path.exists():
        # Fallback to sample file if snapshots don't exist
        sample_file = os.path.join(PROJECT_ROOT, "data/raw/cowrie_sample.json")
        if os.path.exists(sample_file):
            return [Path(sample_file)]
        return []
    
    # Find all JSON files that contain "cowrie" in the name
    # This matches: cowrie.json, cowrie.json.2025-12-16, cowrie_2025-12-23_12-00.json, etc.
    all_files = []
    for pattern in ["cowrie.json*", "cowrie_*.json"]:
        all_files.extend(raw_path.rglob(pattern))
    
    # Remove duplicates and filter out non-JSON files
    unique_files = list(set(all_files))
    json_files = [f for f in unique_files if f.suffix == '.json' or 'cowrie.json' in f.name]
    
    return sorted(json_files)

def main():
    sessions = defaultdict(lambda: {
        "session_id": None,
        "src_ip": None,
        "start_time": None,
        "end_time": None,
        "num_commands": 0,
        "num_login_attempts": 0,
        "login_success": False,
        "client_version": None,
        "hassh": None,
        "protocol_errors": 0,
    })

    file_paths = iter_cowrie_files()
    if not file_paths:
        print(f"[!] No Cowrie log files found in {RAW_DIR}")
        return

    for file_path in file_paths:
        if file_path.name == ".gitignore":
            continue

        try:
            with open(file_path, "r") as f:
                for line in f:
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    session_id = event.get("session")
                    if not session_id:
                        continue

                    s = sessions[session_id]
                    s["session_id"] = session_id

                    # Common fields
                    if "src_ip" in event:
                        s["src_ip"] = event["src_ip"]

                    if "timestamp" in event:
                        ts = parse_timestamp(event["timestamp"])
                        if ts:
                            if not s["start_time"] or ts < s["start_time"]:
                                s["start_time"] = ts
                            if not s["end_time"] or ts > s["end_time"]:
                                s["end_time"] = ts

                    event_id = event.get("eventid", "")

                    # SSH client fingerprint
                    if event_id == "cowrie.client.version":
                        s["client_version"] = event.get("version")

                    # HASSH is in cowrie.client.kex event
                    if event_id == "cowrie.client.kex":
                        s["hassh"] = event.get("hassh")

                    # Authentication attempts
                    if event_id == "cowrie.login.failed":
                        s["num_login_attempts"] += 1

                    if event_id == "cowrie.login.success":
                        s["num_login_attempts"] += 1
                        s["login_success"] = True

                    # Commands
                    if event_id == "cowrie.command.input":
                        s["num_commands"] += 1

                    # Protocol abuse (HTTP/TLS sent to SSH)
                    if "Bad protocol version" in event.get("message", ""):
                        s["protocol_errors"] += 1

        except Exception as e:
            print(f"[!] Failed to read {file_path}: {e}")

    if not sessions:
        print("[!] No Cowrie sessions found")
        return

    # Convert to DataFrame
    rows = []
    for s in sessions.values():
        if s["start_time"] and s["end_time"]:
            duration = (s["end_time"] - s["start_time"]).total_seconds()
        else:
            duration = 0

        rows.append({
            "session_id": s["session_id"],
            "src_ip": s["src_ip"],
            "start_time": s["start_time"],
            "end_time": s["end_time"],
            "duration_seconds": duration,
            "num_commands": s["num_commands"],
            "num_login_attempts": s["num_login_attempts"],
            "login_success": s["login_success"],
            "client_version": s["client_version"],
            "hassh": s["hassh"],
            "protocol_errors": s["protocol_errors"],
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT, index=False)

    print(f"[+] Parsed {len(df)} sessions")
    print(f"[+] Output written to {OUTPUT}")

if __name__ == "__main__":
    main()

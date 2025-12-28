#!/bin/bash
set -e

# Get the script directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "[!] Warning: venv not found, using system Python"
fi

echo "[+] Parsing Cowrie logs..."
python3 ml/parsecowrie.py

echo "[+] Aggregating attackers..."
python3 ml/aggregate_attackers.py

echo "[+] Applying heuristic labels..."
python3 ml/label_attackers.py

echo "[+] Building feature matrix..."
python3 ml/feature_matrix.py

echo "[+] Running Isolation Forest..."
python3 ml/isolation_forest.py

echo "[+] COMPLETE"

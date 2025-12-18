import pandas as pd

def label_attacker(row):
    if row["num_sessions"] <= 1 and row["avg_duration"] < 1:
        return "noise"

    if row["num_sessions"] >= 5 and row["total_commands"] == 0:
        return "credential_stuffer"

    if row["sessions_with_commands"] > 0 and row["avg_duration"] > 10:
        return "interactive_attacker"

    if row["num_sessions"] >= 3 and row["avg_duration"] < 1:
        return "scanner"

    return "unknown"

def main():
    print("[+] Loading attackers.csv")
    df = pd.read_csv("../data/processed/attackers.csv")

    print("[+] Applying heuristic labels")
    df["heuristic_label"] = df.apply(label_attacker, axis=1)

    output_path = "../data/processed/attackers_labeled.csv"
    df.to_csv(output_path, index=False)

    print(f"[+] Wrote labeled attackers to {output_path}")


if __name__ == "__main__":
    main()

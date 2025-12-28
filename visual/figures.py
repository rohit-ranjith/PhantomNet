import os
import warnings
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Suppress font warnings and other matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*Glyph.*missing from font.*')
warnings.filterwarnings('ignore', message='.*missing from font.*')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SESSIONS_CSV = os.path.join(PROJECT_ROOT, "data/processed/sessions.csv")
ATTACKERS_CSV = os.path.join(PROJECT_ROOT, "data/processed/attackers.csv")
LABELED_CSV = os.path.join(PROJECT_ROOT, "data/processed/attackers_labeled.csv")
SCORES_CSV = os.path.join(PROJECT_ROOT, "data/processed/anomaly_scores.csv")

OUT_DIR = os.path.join(PROJECT_ROOT, "figures")
os.makedirs(OUT_DIR, exist_ok=True)

def savefig(name: str):
    path = os.path.join(OUT_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    print(f"[+] Wrote {path}")

def main():
    # ---------- Load data ----------
    sessions = pd.read_csv(SESSIONS_CSV)
    attackers = pd.read_csv(ATTACKERS_CSV) if os.path.exists(ATTACKERS_CSV) else None
    labeled = pd.read_csv(LABELED_CSV) if os.path.exists(LABELED_CSV) else None
    scores = pd.read_csv(SCORES_CSV) if os.path.exists(SCORES_CSV) else None

    # Normalize timestamps (safe if already string)
    if "start_time" in sessions.columns:
        sessions["start_time"] = pd.to_datetime(sessions["start_time"], errors="coerce", utc=True)
    if "end_time" in sessions.columns:
        sessions["end_time"] = pd.to_datetime(sessions["end_time"], errors="coerce", utc=True)

    # ---------- FIG 1: Sessions per day ----------
    if "start_time" in sessions.columns:
        per_day = sessions.dropna(subset=["start_time"]).copy()
        per_day["day"] = per_day["start_time"].dt.date
        counts = per_day.groupby("day")["session_id"].count().sort_index()

        plt.figure(figsize=(10, 6))
        counts.plot(kind="bar")
        plt.xlabel("Day (UTC)")
        plt.ylabel("Number of sessions")
        plt.title("Cowrie sessions per day")
        plt.xticks(rotation=45, ha='right')
        savefig("fig1_sessions_per_day.png")

    # ---------- FIG 2: Session duration distribution ----------
    if "duration_seconds" in sessions.columns:
        d = sessions["duration_seconds"].fillna(0)
        # clamp huge outliers for readability (still keeps distribution)
        d_plot = d.clip(upper=d.quantile(0.99) if len(d) > 10 else d.max())

        plt.figure(figsize=(10, 6))
        plt.hist(d_plot, bins=30, edgecolor='black')
        plt.xlabel("Session duration (seconds)")
        plt.ylabel("Count")
        plt.title("Distribution of session durations (clipped at 99th percentile)")
        savefig("fig2_duration_distribution.png")

    # ---------- FIG 3: Login success rate (session-level) ----------
    if "login_success" in sessions.columns:
        rate = sessions["login_success"].fillna(False).mean()

        plt.figure(figsize=(6, 6))
        plt.bar(["Login Success Rate"], [rate], color='steelblue')
        plt.ylim(0, 1)
        plt.ylabel("Rate")
        plt.title("Overall login success rate (session-level)")
        plt.text(0, rate + 0.05, f'{rate:.2%}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        savefig("fig3_login_success_rate.png")

    # ---------- FIG 4: Top source IPs by session count ----------
    if "src_ip" in sessions.columns:
        top = sessions.groupby("src_ip")["session_id"].count().sort_values(ascending=False).head(10)

        plt.figure(figsize=(10, 6))
        top.sort_values().plot(kind="barh", color='coral')
        plt.xlabel("Sessions")
        plt.ylabel("Source IP")
        plt.title("Top 10 source IPs by session count")
        savefig("fig4_top_ips_by_sessions.png")

    # ---------- FIG 5: Client versions (top 10) ----------
    if "client_version" in sessions.columns:
        cv = sessions["client_version"].fillna("UNKNOWN")
        top_cv = cv.value_counts().head(10)

        plt.figure(figsize=(10, 6))
        top_cv.sort_values().plot(kind="barh", color='mediumseagreen')
        plt.xlabel("Count")
        plt.ylabel("Client version")
        plt.title("Top SSH client versions observed")
        savefig("fig5_top_client_versions.png")

    # ---------- FIG 6: Heuristic label breakdown (attacker-level) ----------
    if labeled is not None and "heuristic_label" in labeled.columns:
        counts = labeled["heuristic_label"].fillna("unknown").value_counts()

        plt.figure(figsize=(10, 6))
        counts.plot(kind="bar", color='purple', edgecolor='black')
        plt.xlabel("Heuristic label")
        plt.ylabel("Number of source IPs")
        plt.title("Attacker types (heuristic labels)")
        plt.xticks(rotation=45, ha='right')
        savefig("fig6_heuristic_label_breakdown.png")

    # ---------- FIG 7 (optional): ML anomaly score distribution ----------
    if scores is not None and "anomaly_score" in scores.columns:
        s = scores["anomaly_score"].dropna()

        plt.figure(figsize=(10, 6))
        plt.hist(s, bins=25, edgecolor='black', color='skyblue')
        plt.xlabel("Isolation Forest decision_function score")
        plt.ylabel("Count")
        plt.title("Anomaly score distribution (higher = more normal)")
        plt.axvline(s.mean(), color='red', linestyle='--', label=f'Mean: {s.mean():.3f}')
        plt.legend()
        savefig("fig7_anomaly_score_distribution.png")

        # Top most "anomalous" (lowest score)
        if "src_ip" in scores.columns:
            top_bad = scores.sort_values("anomaly_score").head(10).set_index("src_ip")["anomaly_score"]

            plt.figure(figsize=(10, 6))
            top_bad.sort_values().plot(kind="barh", color='firebrick')
            plt.xlabel("Anomaly score (lower = more anomalous)")
            plt.ylabel("Source IP")
            plt.title("Top 10 most anomalous source IPs (Isolation Forest)")
            savefig("fig8_top_anomalous_ips.png")

    print("[+] Done generating figures.")

if __name__ == "__main__":
    main()

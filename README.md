# PhantomNet — Cloud-Based SSH Honeynet & Behavioral Analysis

PhantomNet is a small-scale honeynet project I built to better understand how real SSH attacks look in practice and how security teams might analyze them at a session and behavioral level. As a student interested in SOC operations and entry-level cybersecurity roles, I wanted something more realistic than simulated logs, but still safe to deploy, observe, and analyze.

The core idea is simple: expose an intentionally vulnerable SSH service on the public internet, collect real attacker interaction data, and analyze that data using session-level features, heuristics, and unsupervised machine learning.

Over time, the project evolved into a Dockerized SSH honeypot running in Azure with an automated, pull-based data collection and analysis pipeline.

## Project Motivation

Most SSH attacks on the internet are automated, fast, and repetitive. By deploying a Cowrie honeypot on a cloud VM and allowing it to listen on the default SSH port (22), I was able to observe real-world credential stuffing attempts, scanning behavior, and occasional interactive sessions.

Instead of blocking or mitigating these attacks, the goal of this project is to study attacker behavior, focusing on questions such as:

- How often do attackers connect to an exposed SSH service?
- How long do attack sessions typically last?
- How frequently do login attempts succeed?
- What SSH clients and tools are commonly used?
- Which behaviors stand out as anomalous?

## Architecture Overview

### Cloud Environment

- **Azure Ubuntu VM**
- Network Security Groups (NSGs) to tightly control exposed ports
- Administrative SSH moved to a non-standard port
- Cowrie honeypot bound to port 22 for realistic exposure

### Honeypot Layer

- **Cowrie SSH honeypot** running inside Docker
- Safe emulation of SSH interaction (no real system access)
- Structured JSON event logs generated for every attacker interaction

### Data Pipeline

- Snapshot-based log extraction from the Cowrie container
- Pull-based log transfer from the Azure VM to a private analysis machine
- Python-based parsing and feature extraction
- CSV-based intermediate datasets for transparency and debugging

This design keeps the exposed VM minimal and reduces risk by avoiding analysis code or credentials on public-facing infrastructure.

## Automation and Data Collection

To avoid manual log handling, I implemented a lightweight automation workflow:

1. A scheduled job on the Azure VM periodically extracts Cowrie's JSON logs from the Docker container
2. Each snapshot is timestamped and stored locally on the VM
3. A pull-based sync from my private analysis environment retrieves new snapshots
4. Logs are parsed into session-level records for analysis

This pull-based approach mirrors real SOC workflows and avoids pushing data outward from an exposed system.

## Detection and Analysis Approach

Rather than relying on signatures alone, this project focuses on behavioral analysis at the SSH session level.

### Feature Extraction

Each SSH session is summarized using explainable features such as:

- Source IP address
- Session duration
- Number of login attempts
- Login success or failure
- Number of commands issued
- SSH client version
- Indicators of protocol misuse

Each row in the resulting dataset represents one attacker session.

### Heuristic Labeling

Simple, conservative rules are used to group sessions into rough behavioral categories:

- **Credential stuffing**
- **Scanning / background noise**
- **Interactive attackers**
- **Unknown behavior**

These labels are intentionally conservative and provide context rather than ground truth.

### Unsupervised Machine Learning (Isolation Forest)

An Isolation Forest model is trained on session-level features to identify anomalous behavior. The goal is not perfect classification, but to surface sessions that behave differently from the majority—such as unusually long interactions, abnormal command patterns, or unexpected timing.

## Visualization and Results

After running the honeypot on port 22 for approximately one day, several realistic patterns emerged:

- A rapid surge in SSH sessions shortly after exposure
- Very short session durations dominating the dataset
- A measurable login success rate consistent with known Cowrie behavior
- Heavy reuse of Go-based SSH clients commonly associated with botnets
- A small subset of IPs responsible for a large fraction of sessions
- Clear behavioral outliers identified by the anomaly detection model

These observations closely matched findings reported in public honeypot research and confirmed that switching from a high-numbered port to port 22 significantly improved data quality.

## Analysis Pipeline — File Overview

The analysis pipeline is intentionally modular and transparent:

- **`ml/parsecowrie.py`**  
  Parses raw Cowrie JSON logs and aggregates events into session-level records with extracted features.

- **`data/processed/sessions.csv`**  
  Clean intermediate dataset where each row represents a single SSH session.

- **`ml/aggregate_attackers.py`**  
  Aggregates session-level data by source IP to create attacker profiles with behavioral features.

- **`ml/label_attackers.py`**  
  Applies simple rule-based labels (credential stuffing, scanning, interactive, unknown) to attacker profiles.

- **`ml/feature_matrix.py`**  
  Builds a scaled feature matrix from labeled attacker data for machine learning.

- **`ml/isolation_forest.py`**  
  Trains and applies an Isolation Forest model to identify anomalous attackers based on behavioral features.

- **`visual/figures.py`**  
  Generates plots and summary statistics used to interpret attacker behavior and validate assumptions.

This separation makes the pipeline easy to debug, extend, or adapt to other honeypot datasets.

## Limitations and Future Work

This project is exploratory and observational by design. It does not attempt attribution or real-time defense. Possible future extensions include:

- Deploying multiple honeypot nodes in different regions
- Longer-term data collection for trend analysis
- Enriching IP data with ASN or geolocation metadata
- Comparing behavior across different SSH honeypot configurations

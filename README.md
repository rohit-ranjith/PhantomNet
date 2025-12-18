# PhantomNet
Cloud honeynet for botnet behavior analysis

PhantomNet is my personal security research project that deploys a cloud-based SSH honeypot to collect real-world attack telemetry and performs offline behavioral analysis and machine learning to characterize attacker behavior.

The project intentionally separates data collection from data analysis, mirroring real-world SOC and threat intelligence architectures. A public-facing cloud VM captures unsolicited attack traffic, while a local, isolated VM performs parsing, feature engineering, and analysis.

Internet Attackers
        |
        v
Azure VM (Public)
└── Docker
    └── Cowrie SSH Honeypot
        └── cowrie.json logs
                |
                | (manual SCP for now)
                v
Local Ubuntu VM (Private)
└── phantomnet/
    ├── collector/
    ├── ml/
    ├── data/
    │   ├── raw/
    │   └── processed/
    ├── dashboard/
    ├── venv/
    └── README.md


Design Rationale

Security-first design: The honeypot is treated as compromised by default; no analysis occurs on the cloud VM.

Realistic SOC workflow: Collection, normalization, and analysis are decoupled.

Scalability: Analysis tooling can evolve independently of the honeypot.

Research realism: Captures unsolicited, real-world attack traffic rather than simulated data.

Environments:
-----------------
Azure VM — Collection Layer

Purpose
Exposed to the public internet to attract real SSH attacks.
Collects raw telemetry only.

Key Details
OS: Ubuntu 22.04
Cloud provider: Microsoft Azure
Containerization: Docker
Honeypot: Cowrie SSH
Exposed port: 2222/tcp
Authentication: Fake credentials (Cowrie-managed)

Data Collected
Source IP addresses
SSH client banners and fingerprints (HASSH)
Authentication attempts (password / public key)
Executed commands
Session duration and activity
Protocol misuse and malformed traffic

------------
Local Ubuntu VM — Analysis Layer

Purpose
Safe environment for data processing and analysis.
No direct exposure to the internet.

Directory Structure
phantomnet/
├── collector/        # Future: automated log ingestion
├── ml/               # Parsing, feature engineering, ML
├── data/
│   ├── raw/          # Raw cowrie.json files
│   └── processed/    # CSVs and engineered datasets
├── dashboard/        # Future visualizations
├── venv/             # Python virtual environment
└── README.md


Data Flow

Cowrie logs SSH activity to:
/cowrie/cowrie-git/var/log/cowrie/cowrie.json


Logs are copied from the Azure VM to the local Ubuntu VM using scp.
Python scripts parse and normalize the logs into structured datasets.
Processed data is used for behavioral analysis and machine learning.
Note: Log transfer is currently manual by design. Automation is planned for a later phase.


Implemented Analysis Script
parsecowrie.py

Location

phantomnet/ml/parsecowrie.py


Purpose
Parse Cowrie JSON logs into structured, session-level data.

Extracted Fields:
Session ID
Source IP
Session start and end time
Session duration
Number of commands executed
Login attempts and success
SSH client version
HASSH fingerprint
Protocol anomalies

Output
phantomnet/data/processed/sessions.csv

Technologies Used
Cloud: Microsoft Azure
OS: Ubuntu 22.04
Containerization: Docker
Honeypot: Cowrie SSH
Language: Python 3.11
Data Processing: pandas
Machine Learning (planned): scikit-learn
Development: Cursor, Linux CLI

Project Goals:
Capture real-world SSH attack behavior
Engineer behavioral features from honeypot sessions
Distinguish automated bot activity from interactive attackers
Apply unsupervised ML techniques for attacker classification
Build a modular, extensible threat analysis pipeline

Roadmap
Behavioral analysis and attacker profiling
Visualization and dashboards
Machine learning–based clustering and anomaly detection
Automated log ingestion
Expanded honeynet surface (additional services)

Project Checklist
✅ Completed
Infrastructure
 Azure VM provisioned and secured
 Docker installed and verified
 Cowrie SSH honeypot deployed in Docker
 Honeypot exposed to public internet
 Confirmed real attack traffic

Data Collection
 Cowrie JSON logging enabled
 Logs persisted inside container
 Logs successfully copied off Azure VM

Local Analysis Setup
 Local Ubuntu VM configured
 Python virtual environment created
 pandas installed and verified
 Project directory structure created
 Cursor selected as development environment

Parsing
 parsecowrie.py implemented
 Raw JSON → structured CSV conversion
 Session-level feature extraction


🔜 To Be Done
Data Engineering
 Normalize multiple log files
 Aggregate sessions by source IP
 Engineer higher-level behavioral features (rate, entropy, repetition)

Analysis
 Bot vs interactive attacker heuristics
 Session clustering
 Temporal attack pattern analysis

Machine Learning
 Feature scaling and encoding
 Unsupervised clustering (Isolation Forest / DBSCAN)
 Compare heuristic vs ML classification

Visualization
 Session duration vs command count plots
 Source IP distribution maps
 SSH client fingerprint clustering

Automation (Later Phase)
 Scheduled log transfer (scp / rsync)
 Incremental ingestion
 Optional message queue or object storage

Expansion

 Consider switching to port 22
 Add additional honeypot services
 Multi-node honeynet deployment


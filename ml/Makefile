RAW = data/raw/cowrie.json
PROC = data/processed

all: anomaly

sessions:
	python3 ml/parsecowrie.py

attackers: sessions
	python3 ml/aggregate_attackers.py

labeled: attackers
	python3 ml/label_attackers.py

features: labeled
	python3 ml/feature_matrix.py

anomaly: features
	python3 ml/isolation_forest.py

clean:
	rm -f $(PROC)/*.csv

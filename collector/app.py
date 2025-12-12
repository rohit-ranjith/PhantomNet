from fastapi import FastAPI, Request
import json, os
from datetime import datetime

app = FastAPI()

DATA_DIR = os.path.expanduser("~/phantomnet/data/raw")
os.makedirs(DATA_DIR, exist_ok=True)

@app.post("/ingest")
async def ingest(request: Request):
    payload = await request.json()
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
    filename = f"{DATA_DIR}/{ts}.json"

    with open(filename, "w") as f:
        json.dump(payload, f)

    return {"status": "ok", "file": filename}


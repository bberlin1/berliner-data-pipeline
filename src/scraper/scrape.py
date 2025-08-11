import os
import json
import time
import random
from pathlib import Path
import boto3

def generate_fake_rows(n=20):
    values = [random.randint(0, 100) for _ in range(n)]
    return {"ts": int(time.time()), "values": values}

def write_local(out_path="out/local_raw.json"):
    payload = generate_fake_rows()
    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")

def write_s3(bucket):
    s3 = boto3.client("s3")
    payload = generate_fake_rows()
    key = f"raw/{payload['ts']}.json"
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(payload).encode("utf-8"))
    print(f"Uploaded s3://{bucket}/{key}")

if __name__ == "__main__":
    bucket = os.getenv("BUCKET_NAME")
    if bucket:
        write_s3(bucket)
    else:
        write_local()

# Berliner Data Pipeline (near-free AWS demo)

A tiny, portfolio-ready serverless data pipeline that stays in AWS free tiers. It generates a small dataset daily, stores a raw JSON file in **S3**, writes a summary to **DynamoDB**, and exposes a read-only endpoint via a **Lambda Function URL** (no API Gateway required).

## What you'll learn
- Event-driven serverless (EventBridge → Lambda)
- S3 object I/O and DynamoDB reads/writes
- Function URL for simple GET endpoint
- Cost controls & cleanup

---

## Prereqs (1x setup)
1. **AWS account** (root billing only) + a low-privilege **IAM user** with programmatic access.
2. **AWS CLI** (`aws --version`) and **SAM CLI** (`sam --version`).
3. **Python 3.11+** and **pip**.
4. **Docker Desktop** (optional) if you want to try LocalStack for fully local dev.
5. **Git** and a GitHub account (optional but recommended).

> Tip: Immediately create an **AWS Budget** for **$5/month** with email alerts. Then you’ll never be surprised.

---

## Quick start (cloud deploy in ~5 minutes)
```bash
# 0) Clone or unzip this project and cd into it
cd berliner-data-pipeline

# 1) (Optional) create/activate a virtualenv
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Build and deploy with SAM
sam build
sam deploy --guided
# Recommended answers:
#   Stack Name: berliner-data-pipeline
#   AWS Region: us-east-1 (or your choice)
#   Allow SAM to create roles with required permissions: Y
#   Save arguments to configuration file: Y
#   Confirm changes before deploy: N
```

### After deploy
- SAM will print an output named **FunctionUrl**. Copy it.
- Open it in a browser. You should see a JSON doc like `{"status":"ok","latest":...}`.
- The function also runs once per day by default and writes a row in DynamoDB plus a small JSON file in S3.

### Trigger a run now (optional)
After the first deploy, you can invoke the function manually:
```bash
aws lambda invoke --function-name $(aws cloudformation describe-stacks --stack-name berliner-data-pipeline --query "Stacks[0].Outputs[?OutputKey=='PipelineFunction'].OutputValue" --output text) /dev/stdout
```
Or just wait for the scheduled run.

---

## Local-only option (no AWS spend)
- You can run `src/scraper/scrape.py` locally to generate fake raw data to a local file and to S3 if you set `BUCKET_NAME` and AWS creds.  
- For full local cloud emulation, add **LocalStack** (already scaffolded via `docker-compose.yml`). Start it with:
```bash
docker-compose up -d
```
Then develop against LocalStack endpoints (advanced; optional).

---

## Cost guardrails
- **No EC2, no NAT Gateways** (big cost risks).
- **DynamoDB PAY_PER_REQUEST** (you only pay per request; stays within free tier for tiny usage).
- **S3 objects are tiny** (KBs).
- **CloudWatch retention**: you can lower retention in production; default is fine for demos.
- **Clean up** with `sam delete` when you're done.

---

## Cleanup
```bash
sam delete
# If SAM reports the S3 bucket isn't empty, empty it then re-run:
aws s3 rm s3://YOUR_BUCKET --recursive
sam delete
```

---

## Repo structure
```
src/
  scraper/scrape.py        # local data generator
  handler/app.py           # Lambda handler: daily generate+summarize + GET endpoint
infra/
  template.yaml            # SAM template: S3, DynamoDB, Lambda, schedule, function URL
.github/workflows/ci.yml   # simple CI (lint/tests)
tests/
  test_handler.py
  test_scraper.py
Makefile
docker-compose.yml         # LocalStack (optional)
```

## What to talk about in interviews
- Why you chose serverless to stay in free tiers.
- Idempotency and error handling in `app.py`.
- How you'd extend it: API Gateway auth, S3 lifecycle rules, schema validation, CI/CD with `sam sync`, etc.

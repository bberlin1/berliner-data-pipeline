import os
import json
import boto3
import random
import time
from decimal import Decimal
from botocore.exceptions import ClientError

# AWS clients/resources
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
lambda_client = boto3.client("lambda")
cf_client = boto3.client("cloudformation")

# Environment variables from template.yaml
BUCKET_NAME = os.environ.get("BUCKET_NAME")
TABLE_NAME = os.environ.get("TABLE_NAME")
STACK_NAME = os.environ.get("AWS_SAM_STACK_NAME")

table = dynamodb.Table(TABLE_NAME)


# --- Utilities ---
def decimalize(obj):
    """Convert all floats in an object to Decimal for DynamoDB."""
    if isinstance(obj, list):
        return [decimalize(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimalize(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj


def get_function_name():
    """Dynamically resolve our own Lambda function name from the stack outputs."""
    try:
        outputs = cf_client.describe_stacks(StackName=STACK_NAME)["Stacks"][0]["Outputs"]
        for o in outputs:
            if o["OutputKey"] == "PipelineFunction":
                return o["OutputValue"]
    except ClientError as e:
        print(f"Could not fetch function name: {e}")
    return None


# --- Core logic ---
def generate_synthetic_data():
    """Generate a fake metrics payload."""
    payload = {
        "timestamp": int(time.time()),
        "metrics": {
            "clicks": random.randint(50, 500),
            "impressions": random.randint(1000, 10000),
            "ctr": round(random.uniform(0.01, 0.2), 4)
        }
    }
    return payload


def write_to_s3(data):
    """Write the raw JSON to S3."""
    key = f"raw/{data['timestamp']}.json"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )
    return key


def write_summary_to_ddb(data):
    """Write summarized metrics to DynamoDB, ensuring Decimals for all floats."""
    item = {
        "run_id": str(data["timestamp"]),
        "clicks": data["metrics"]["clicks"],
        "impressions": data["metrics"]["impressions"],
        "ctr": Decimal(str(data["metrics"]["ctr"]))
    }
    table.put_item(Item=item)


# --- Lambda handler ---
def lambda_handler(event, context):
    try:
        # If triggered with query param ?action=run, generate a run
        if event.get("queryStringParameters", {}).get("action") == "run":
            payload = generate_synthetic_data()
            s3_key = write_to_s3(payload)
            write_summary_to_ddb(payload)
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "ok",
                    "message": "run complete",
                    "s3_key": s3_key
                })
            }

        # Otherwise, return the latest status
        resp = table.scan(Limit=1)
        items = resp.get("Items", [])
        latest = items[0] if items else {}
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "ok",
                "latest": latest
            }, default=str)
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)})
        }


# For local testing
if __name__ == "__main__":
    # Simulate a 'run' event
    event = {"queryStringParameters": {"action": "run"}}
    print(lambda_handler(event, None))

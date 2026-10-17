
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def save_road_report(report: dict) -> dict:
    """
    Save a road-risk report to Amazon S3.

    This function requires AWS credentials and an existing S3 bucket.
    It does not upload anything until called.
    """
    bucket_name = os.getenv("ROADSENSE_S3_BUCKET")
    region = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")

    if not bucket_name:
        return {
            "saved": False,
            "mode": "not_configured",
            "message": "S3 bucket is not configured yet."
        }

    timestamp = datetime.now(timezone.utc)
    report_id = timestamp.strftime("%Y%m%dT%H%M%S%fZ")
    key = f"road-reports/{timestamp:%Y/%m/%d}/{report_id}.json"

    payload = {
        "report_id": report_id,
        "created_at": timestamp.isoformat(),
        "report": report
    }

    try:
        s3 = boto3.client("s3", region_name=region)
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(payload, indent=2).encode("utf-8"),
            ContentType="application/json"
        )
        return {
            "saved": True,
            "mode": "aws_s3",
            "report_id": report_id,
            "key": key
        }
    except (BotoCoreError, ClientError) as exc:
        return {
            "saved": False,
            "mode": "aws_s3",
            "message": str(exc)
        }

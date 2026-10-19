
import json
import os
from datetime import datetime, timezone

import boto3
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="RoadSense API")

S3_BUCKET = os.environ.get(
    "ROADSENSE_S3_BUCKET",
    "roadsense-reports-yb-2026-unique"
)

s3 = boto3.client("s3")


@app.get("/")
def home():
    return {
        "project": "RoadSense",
        "status": "running",
        "purpose": "Road-risk report API"
    }


@app.post("/reports")
def save_report(report: dict):
    report_id = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    report["report_id"] = report_id
    report["created_at"] = datetime.now(timezone.utc).isoformat()

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"lambda-reports/{report_id}.json",
        Body=json.dumps(report).encode("utf-8"),
        ContentType="application/json"
    )

    return {
        "saved": True,
        "report_id": report_id,
        "storage": "AWS S3"
    }


handler = Mangum(app)

import json
from src.dependencies.s3_client import s3_client, S3_BUCKET_NAME


def read_file(s3_key: str) -> dict:
    response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
    content = response["Body"].read().decode("utf-8")
    return json.loads(content)


def write_file(s3_key: str, data: dict) -> str:
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )
    return f"s3://{S3_BUCKET_NAME}/{s3_key}"

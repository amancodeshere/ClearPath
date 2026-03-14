import json
import boto3
import csv
import logging
from io import StringIO
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('clearpath-weather-data')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TIMEZONE = "GMT+11"


def safe_float(value, field_name):
    if value is None:
        raise ValueError(f"Missing value for {field_name}")

    value = str(value).strip()
    if value == "":
        raise ValueError(f"Empty value for {field_name}")

    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid numeric value for {field_name}: {value}")


def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")


def format_timestamp(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


def build_adage_weather_object(bucket, output_key, date, rainfall, max_temp, min_temp, wind_speed):
    timestamp = format_timestamp(date)

    return {
        "data_source": "BOM",
        "dataset_type": "Daily weather observations",
        "dataset_id": f"s3://{bucket}/{output_key}",
        "time_object": {
            "timestamp": timestamp,
            "timezone": TIMEZONE
        },
        "events": [
            {
                "time_object": {
                    "timestamp": timestamp,
                    "duration": 1,
                    "duration_unit": "day",
                    "timezone": TIMEZONE
                },
                "event_type": "weather observation",
                "attribute": {
                    "rainfall_mm": rainfall,
                    "max_temp_c": max_temp,
                    "min_temp_c": min_temp,
                    "wind_speed_kmh": wind_speed
                }
            }
        ]
    }


def validate_adage_object(obj):
    required_top_fields = [
        "data_source",
        "dataset_type",
        "dataset_id",
        "time_object",
        "events"
    ]

    for field in required_top_fields:
        if field not in obj:
            raise ValueError(f"Missing top-level field: {field}")

    if not isinstance(obj["time_object"], dict):
        raise ValueError("time_object must be an object")

    if "timestamp" not in obj["time_object"]:
        raise ValueError("Missing top-level time_object.timestamp")

    if "timezone" not in obj["time_object"]:
        raise ValueError("Missing top-level time_object.timezone")

    if not isinstance(obj["events"], list) or len(obj["events"]) == 0:
        raise ValueError("events must be a non-empty list")

    for i, event in enumerate(obj["events"]):
        if not isinstance(event, dict):
            raise ValueError(f"Event at index {i} must be an object")

        for field in ["time_object", "event_type", "attribute"]:
            if field not in event:
                raise ValueError(f"Missing event field '{field}' at index {i}")

        event_time = event["time_object"]
        if not isinstance(event_time, dict):
            raise ValueError(f"event.time_object at index {i} must be an object")

        for field in ["timestamp", "duration", "duration_unit", "timezone"]:
            if field not in event_time:
                raise ValueError(f"Missing event.time_object.{field} at index {i}")

        if not isinstance(event["attribute"], dict):
            raise ValueError(f"event.attribute at index {i} must be an object")

        for field in ["rainfall_mm", "max_temp_c", "min_temp_c", "wind_speed_kmh"]:
            if field not in event["attribute"]:
                raise ValueError(f"Missing event.attribute.{field} at index {i}")

            if not isinstance(event["attribute"][field], (int, float)):
                raise ValueError(f"event.attribute.{field} at index {i} must be numeric")

    return True


def lambda_handler(event, context):
    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]
    except (KeyError, IndexError) as e:
        logger.error(f"Invalid event format: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps("Invalid S3 event payload")
        }

    logger.info(f"Processing file: s3://{bucket}/{key}")

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        csv_content = response["Body"].read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(csv_content))
    except Exception as e:
        logger.error(f"Failed to read CSV from S3: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps("Failed to read CSV file from S3")
        }

    processed_rows = 0
    skipped_rows = 0

    for row in csv_reader:
        try:
            date = row["Date"].strip()
            validate_date(date)

            rainfall = safe_float(row.get("Rainfall (mm)"), "Rainfall (mm)")
            max_temp = safe_float(row.get("Maximum temperature (°C)"), "Maximum temperature (°C)")
            min_temp = safe_float(row.get("Minimum temperature (°C)"), "Minimum temperature (°C)")
            wind_speed = safe_float(row.get("Wind speed (km/h)"), "Wind speed (km/h)")

            output_key = f"weather_collected/{date}.json"

            adage_object = build_adage_weather_object(
                bucket=bucket,
                output_key=output_key,
                date=date,
                rainfall=rainfall,
                max_temp=max_temp,
                min_temp=min_temp,
                wind_speed=wind_speed
            )

            validate_adage_object(adage_object)

            s3.put_object(
                Bucket=bucket,
                Key=output_key,
                Body=json.dumps(adage_object, indent=2),
                ContentType="application/json"
            )

            table.put_item(
                Item={
                    "Date": date,
                    "weather_raw_s3_path": f"s3://{bucket}/{key}",
                    "weather_collected_s3_path": f"s3://{bucket}/{output_key}",
                    "rainfall_mm": rainfall,
                    "wind_speed_kmh": wind_speed,
                    "max_temp_c": max_temp,
                    "min_temp_c": min_temp,
                    "status": "clean"
                }
            )

            processed_rows += 1

        except Exception as e:
            skipped_rows += 1
            logger.warning(f"Skipping row {row} due to error: {str(e)}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Processing complete",
            "processed_rows": processed_rows,
            "skipped_rows": skipped_rows
        })
    }
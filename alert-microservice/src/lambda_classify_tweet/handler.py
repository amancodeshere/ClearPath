import json
import logging
import os
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.services.sagemaker_service import (
    SageMakerClassificationService,
    SageMakerServiceError,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")

if not DYNAMODB_TABLE_NAME:
    raise ValueError("Missing required environment variable: DYNAMODB_TABLE_NAME")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

class DynamoDBServiceError(Exception):
    """
    Raised when DynamoDB read or write operations fail.
    """
    pass


def build_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds a standard Lambda proxy response.

    :param status_code: int -> HTTP-style status code.
    :param body: Dict[str, Any] -> Response payload.
    :returns Dict[str, Any] -> Lambda proxy response.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, default=str),
    }


def extract_date_from_event(event: Dict[str, Any]) -> Optional[str]:
    """
    Extracts the date value from a Lambda event.

    Supported event formats:
        1. Direct invocation:
           {"date": "2024-08-14"}

        2. API Gateway query params:
            { "queryStringParameters":
                {"date": "2024-08-14"}
            }

        3. API Gateway JSON body:
           {"body": "{\"date\": \"2024-08-14\"}"}

    :param event: Dict[str, Any] -> Lambda event payload.
    :returns _: Optional[str] -> Extracted date string or None.
    """
    if not event:
        return None

    if event.get("date"):
        return str(event["date"]).strip()

    query_params = event.get("queryStringParameters") or {}
    if query_params.get("date"):
        return str(query_params["date"]).strip()

    body = event.get("body")
    if body:
        try:
            if isinstance(body, str):
                parsed_body = json.loads(body)
            elif isinstance(body, dict):
                parsed_body = body
            else:
                parsed_body = {}
        except json.JSONDecodeError:
            parsed_body = {}

        if parsed_body.get("date"):
            return str(parsed_body["date"]).strip()

    return None


def get_item_by_date(date_value: str) -> Optional[Dict[str, Any]]:
    """
    Fetches one item from DynamoDB using Date as the partition key.

    Expected table shape:
        {
            "Date": "2024-08-14",
            "text": "tweet one EOT\\n tweet two EOT\\n tweet three",
            "account_name": "@T1SydneyTrain",
            "status": "DELAYED" | "CANCELLED" | EMPTY (NULL)
        }

    :param date_value: str -> Date partition key.
    :returns _: Optional[Dict[str, Any]] -> The DynamoDB item if found, else None.
    """
    try:
        response = table.get_item(Key={"Date": date_value})
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to fetch item from DynamoDB.")
        raise DynamoDBServiceError(
            f"Failed to fetch item for date {date_value}: {exc}"
        ) from exc

    return response.get("Item")


def update_item_classification(
    date_value: str,
    final_status: str,
    predictions: Optional[list] = None,
    tweets_processed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Updates the DynamoDB item with the final aggregated status.

    Required fields updated:
        - status

    Optional debug fields updated:
        - predictions
        - tweets_processed


    :param date_value: str -> Date partition key.
    :param final_status: str -> Final daily aggregated classification, expected to be
                                'cancelled' or 'delayed'.
    :param predictions: Optional[list] -> List of per-tweet predictions returned from SageMaker.
    :param tweets_processed : Optional[int] -> Number of tweets sent for inference.
    :returns _: Dict[str, Any] -> Updated DynamoDB item.
    """
    update_expression = "SET #status = :status"
    expression_attribute_names = {"#status": "status"}
    expression_attribute_values: Dict[str, Any] = {
        ":status": final_status.upper()
    }

    if predictions is not None:
        update_expression += ", predictions = :predictions"
        expression_attribute_values[":predictions"] = predictions

    if tweets_processed is not None:
        update_expression += ", tweets_processed = :tweets_processed"
        expression_attribute_values[":tweets_processed"] = tweets_processed

    try:
        response = table.update_item(
            Key={"Date": date_value},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to update DynamoDB item.")
        raise DynamoDBServiceError(
            f"Failed to update classification for date {date_value}: {exc}"
        ) from exc

    return response.get("Attributes", {})

def lambda_handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lambda entry point for classifying a single day's concatenated tweets.

    Processing flow:
        1. Extract the date from the event
        2. Read the corresponding row from DynamoDB
        3. Get the concatenated tweet text
        4. Split tweets on EOT and normalise them
        5. Invoke the SageMaker endpoint on the individual tweets
        6. Aggregate predictions into one final daily status
        7. Update the DynamoDB row with the result

    Final status aggregation rule:
        - if any prediction is 'cancelled' -> status = 'CANCELLED'
        - else if any prediction is 'delayed' -> status = 'DELAYED'
    """
    logger.info("Received event: %s", json.dumps(event))

    date_value = extract_date_from_event(event)
    if not date_value:
        return build_response(
            400,
            {
                "message": "Missing required parameter: date",
                "expected_format": {"date": "YYYY-MM-DD"},
            },
        )

    try:
        item = get_item_by_date(date_value)
    except DynamoDBServiceError as exc:
        return build_response(
            500,
            {
                "message": "Failed to retrieve record from DynamoDB.",
                "error": str(exc),
            },
        )

    if not item:
        return build_response(
            404,
            {
                "message": f"No record found for date {date_value}.",
            },
        )

    text_blob = item.get("text", "")
    account_name = item.get("account_name", "")

    if not text_blob or not str(text_blob).strip():
        return build_response(
            400,
            {
                "message": f"Record for date {date_value} has no valid text content.",
                "date": date_value,
            },
        )

    try:
        classifier = SageMakerClassificationService()
        classification_result = classifier.classify_daily_text(str(text_blob))
    except SageMakerServiceError as exc:
        return build_response(
            500,
            {
                "message": "SageMaker classification failed.",
                "error": str(exc),
                "date": date_value,
            },
        )
    except Exception as exc:
        logger.exception("Unexpected error during classification.")
        return build_response(
            500,
            {
                "message": "Unexpected classification error.",
                "error": str(exc),
                "date": date_value,
            },
        )

    cleaned_tweets = classification_result.get("tweets", [])
    predictions = classification_result.get("predictions", [])
    final_status = classification_result.get("final_status")

    logger.info(
        "Classification complete for date=%s, tweets_processed=%d, final_status=%s",
        date_value,
        len(cleaned_tweets),
        final_status,
    )

    if not final_status:
        return build_response(
            200,
            {
                "message": "No valid final classification could be produced.",
                "date": date_value,
                "account_name": account_name,
                "tweets_processed": len(cleaned_tweets),
                "predictions": predictions,
                "final_status": None,
            },
        )

    try:
        updated_item = update_item_classification(
            date_value=date_value,
            final_status=final_status,
            predictions=predictions,
            tweets_processed=len(cleaned_tweets),
        )
    except DynamoDBServiceError as exc:
        return build_response(
            500,
            {
                "message": "Classification succeeded, but DynamoDB update failed.",
                "error": str(exc),
                "date": date_value,
                "predictions": predictions,
                "final_status": final_status,
            },
        )

    return build_response(
        200,
        {
            "message": "Classification completed successfully.",
            "date": date_value,
            "account_name": account_name,
            "tweets_processed": len(cleaned_tweets),
            "predictions": predictions,
            "final_status": final_status.upper(),
            "updated_item": updated_item,
        },
    )


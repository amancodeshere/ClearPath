import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.parser.text_normalisation import normalise_text


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SageMakerServiceError(Exception):
    """
    Raised when there is a failure in preparing data, invoking the SageMaker
    endpoint, or parsing the endpoint response.
    """
    pass


class SageMakerClassificationService:
    """
    Service responsible for:
    1. splitting a concatenated daily text field into individual tweets
    2. normalising each tweet so it matches the model input format
    3. invoking the SageMaker endpoint in batches
    4. aggregating the per-tweet predictions into one final daily status

    Expected endpoint input -> {"texts": ["tweet one", "tweet two"]} (json)

    Expected endpoint output -> {"predictions": ["cancelled", "delayed"]} (json)
    """

    def __init__(
        self,
        endpoint_name: str = None,
        region_name: str = None,
        batch_size: int = None,
    ) -> None:
        """
        :param endpoint_name str -> The SageMaker endpoint name. If not provided, reads from the
                                        SAGEMAKER_ENDPOINT_NAME environment variable.

        :param region_name str -> AWS region for the SageMaker runtime client. If not provided,
                                        reads from AWS_REGION and defaults to ap-southeast-2.

        :param batch_size int -> Maximum number of tweets sent to SageMaker in one invocation.
                                    If not provided, reads from SAGEMAKER_BATCH_SIZE and defaults to 32.
        """
        self.endpoint_name = endpoint_name or os.getenv("SAGEMAKER_ENDPOINT_NAME")
        self.region_name = region_name or os.getenv("AWS_REGION", "ap-southeast-2")
        self.batch_size = batch_size or int(os.getenv("SAGEMAKER_BATCH_SIZE", "32"))

        if not self.endpoint_name:
            raise SageMakerServiceError(
                "Missing required environment variable: SAGEMAKER_ENDPOINT_NAME"
            )

        if self.batch_size <= 0:
            raise SageMakerServiceError(
                "SAGEMAKER_BATCH_SIZE must be a positive integer."
            )

        self.runtime_client = boto3.client(
            "sagemaker-runtime",
            region_name=self.region_name,
        )


    @staticmethod
    def split_daily_text_into_tweets(daily_text: str) -> List[str]:
        """
        Splits the concatenated DynamoDB text field into individual tweets.

        The DynamoDB text field is expected to look something like:
            "tweet one... EOT\\n tweet two... EOT\\n tweet three..."

        `EOT` is a text str we have used here as it will help signify the end of a tweet:
            i.e. EOT = End of Tweet

        :param daily_text: str
            The full concatenated text blob for one day.

        :returns List[str]
            A list of individual raw tweet strings.
        """
        if not daily_text or not daily_text.strip():
            return []

        # Split on EOT
        parts = re.split(r"\s*EOT\s*", daily_text)

        tweets = [part.strip() for part in parts if part and part.strip()]
        return tweets


    @staticmethod
    def validate_predictions(predictions: List[str]) -> List[str]:
        """
        Validates and normalises the predictions returned from SageMaker.

        Allowed labels for this MVP:
        - delayed
        - cancelled

        :param predictions: List[str] -> Raw preds returned by the endpoint

        :returns [str] -> Lowercased and validated predictions.

        :raises SageMakerServiceError -> If predictions are invalid or contain unsupported labels.
        """
        if not isinstance(predictions, list):
            raise SageMakerServiceError("Predictions must be returned as a list.")

        normalised_predictions: List[str] = []

        for prediction in predictions:
            label = str(prediction).strip().lower()

            if label not in {"delayed", "cancelled"}:
                raise SageMakerServiceError(
                    f"Unexpected prediction label received from SageMaker: {label}"
                )

            normalised_predictions.append(label)

        return normalised_predictions


    def prepare_tweets_for_inference(self, daily_text: str) -> List[str]:
        """
        Full preprocessing flow for one DynamoDB daily text field.

        Steps:
        1. split the concatenated text into individual tweets
        2. normalise each tweet using the parser normalisation function
        3. remove empty strings after cleaning

        :param daily_text: str -> Raw concatenated tweet blob from DynamoDB.

        :returns List[str] -> Cleaned tweets ready for SageMaker inference.
        """
        raw_tweets = self.split_daily_text_into_tweets(daily_text)

        cleaned_tweets = []
        for tweet in raw_tweets:
            cleaned = normalise_text(tweet)
            if cleaned and cleaned.strip():
                cleaned_tweets.append(cleaned.strip())

        logger.info(
            "Prepared %d tweets for inference after splitting and normalisation.",
            len(cleaned_tweets),
        )

        return cleaned_tweets


    def _invoke_single_batch(self, batch: List[str]) -> List[str]:
        """
        Invokes the SageMaker endpoint on a single batch of tweet texts.

        :param batch: List[str] -> List of cleaned tweets.

        :returns List[str] -> Validated predictions for this batch.

        :raises SageMakerServiceError -> If invocation fails or the response format is invalid.
        """
        if not batch:
            return []

        payload = {"texts": batch}

        logger.info(
            "Invoking SageMaker endpoint '%s' with batch size %d.",
            self.endpoint_name,
            len(batch),
        )

        try:
            response = self.runtime_client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType="application/json",
                Accept="application/json",
                Body=json.dumps(payload),
            )
        except (ClientError, BotoCoreError) as exc:
            logger.exception("Failed to invoke SageMaker endpoint.")
            raise SageMakerServiceError(
                f"SageMaker endpoint invocation failed: {exc}"
            ) from exc

        try:
            response_body = response["Body"].read().decode("utf-8")
            parsed_response = json.loads(response_body)
        except (KeyError, json.JSONDecodeError) as exc:
            logger.exception("Failed to parse SageMaker response.")
            raise SageMakerServiceError(
                f"Could not parse SageMaker response body: {exc}"
            ) from exc

        if "predictions" not in parsed_response:
            raise SageMakerServiceError(
                "SageMaker response is missing the 'predictions' field."
            )

        predictions = self.validate_predictions(parsed_response["predictions"])

        if len(predictions) != len(batch):
            raise SageMakerServiceError(
                "Mismatch between number of input tweets and number of predictions."
            )

        return predictions

    def invoke_classifier(self, texts: List[str]) -> List[str]:
        """
        Invokes the SageMaker endpoint over all texts using batching.

        :param texts : List[str] -> Cleaned tweet texts.

        :returns List[str] -> Combined predictions across all batches.
        """
        if not texts:
            logger.info("No texts provided for classification.")
            return []

        all_predictions: List[str] = []

        for start_index in range(0, len(texts), self.batch_size):
            batch = texts[start_index:start_index + self.batch_size]
            batch_predictions = self._invoke_single_batch(batch)
            all_predictions.extend(batch_predictions)

        logger.info(
            "Received %d predictions from SageMaker for %d tweets.",
            len(all_predictions),
            len(texts),
        )

        return all_predictions

    @staticmethod
    def aggregate_predictions(predictions: List[str]) -> Optional[str]:
        """
        Aggregates per-tweet predictions into a single daily status.

        Key rule:
        - if any prediction is 'cancelled' -> final status is 'cancelled'
        - else if any prediction is 'delayed' -> final status is 'delayed'
        - else -> None

        :param predictions : List[str] -> List of per-tweet labels.

        :returns Optional[str] -> 'cancelled', 'delayed', or None
        """
        if not predictions:
            return None

        normalised = [str(pred).strip().lower() for pred in predictions if pred]

        if "cancelled" in normalised:
            return "cancelled"

        if "delayed" in normalised:
            return "delayed"

        return None

    def classify_daily_text(self, daily_text: str) -> Dict[str, Any]:
        """
        Full end-to-end classification flow for one DynamoDB daily record.

        :param daily_text : str -> Concatenated tweets from the DynamoDB `text` field.


        :returns Dict[str, Any] -> A structured result containing:
            - tweets: cleaned individual tweets
            - predictions: per-tweet model outputs
            - final_status: aggregated daily label
        """
        cleaned_tweets = self.prepare_tweets_for_inference(daily_text)

        if not cleaned_tweets:
            logger.info("No valid tweets found after preprocessing.")
            return {
                "tweets": [],
                "predictions": [],
                "final_status": None,
            }

        predictions = self.invoke_classifier(cleaned_tweets)
        final_status = self.aggregate_predictions(predictions)

        result = {
            "tweets": cleaned_tweets,
            "predictions": predictions,
            "final_status": final_status,
        }

        logger.info(
            "Classification result generated. tweets=%d, final_status=%s",
            len(cleaned_tweets),
            final_status,
        )

        return result



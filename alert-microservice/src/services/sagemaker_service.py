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
    TODO: Add responses for errors later
    """
    pass


class SageMakerClassificationService:
    """
    Service responsible for:
    1. splitting a concatenated daily text field into individual tweets
    2. normalising each tweet so it matches the model input format
    3. invoking the SageMaker endpoint in batches
    4. aggregating the per-tweet predictions into one final daily status

    Expected endpoint input:
        {"texts": ["tweet one", "tweet two"]}

    Expected endpoint output:
        {"predictions": ["cancelled", "delayed"]}
    """

    def __init__(
        self,
        endpoint_name: str = None,
        region_name: str = None,
        batch_size: int = None,
    ) -> None:
        """
        @:param endpoint_name [str]
            -> The SageMaker endpoint name. If not provided, reads from the
               SAGEMAKER_ENDPOINT_NAME environment variable.

        @:param region_name [str]
            AWS region for the SageMaker runtime client. If not provided,
            reads from AWS_REGION and defaults to ap-southeast-2.

        @:param batch_size [int]
            Maximum number of tweets sent to SageMaker in one invocation.
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

        @:param daily_text : str
            The full concatenated text blob for one day.

        @:returns List[str]
            A list of individual raw tweet strings.
        """
        if not daily_text or not daily_text.strip():
            return []

        # Split on EOT
        parts = re.split(r"\s*EOT\s*", daily_text)

        tweets = [part.strip() for part in parts if part and part.strip()]
        return tweets




# Alert-Microservice

### Directory Structure
```
alert-microservice/
├── README.md
├── requirements.txt
├── template.yaml
├── .env
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── utils/
│   │   └── logging_utils.py
│   │
│   ├── parser/
│   │   └── text_normalisation.py
│   │
│   ├── services/
│   │   ├── dynamodb_service.py
│   │   ├── sagemaker_service.py
│   │   └── preprocessing_service.py
│   │
│   ├── scripts/
│   │   ├── backfill_twitter.py
│   │   └── twitter_client.py
│   │
│   ├── lambda-classify_tweets/
│   │   ├── __init__.py
│   │   └── handler.py
│   │
│   └── lambda-get_tweets/
│       ├── __init__.py
│       └── handler.py
│
├── events/
│   ├── classify_event.json
│   └── get_tweets_event.json
│
├── notebooks/
│   ├── dataset_exploration.ipynb
│   ├── train_model_sagemaker.ipynb
│   └── endpoint_testing.ipynb
│
└── tests/
```
import os
import argparse
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--val", type=str, default=os.environ.get("SM_CHANNEL_VAL"))

    args = parser.parse_args()

    train_path = os.path.join(args.train, "train.csv")
    val_path = os.path.join(args.val, "val.csv")

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    X_train = train_df["text"].astype(str)
    y_train = train_df["classification"].astype(str)

    X_val = val_df["text"].astype(str)
    y_val = val_df["classification"].astype(str)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_features=5000
        )),
        ("clf", LinearSVC())
    ])

    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_val)
    print("Validation accuracy:", accuracy_score(y_val, preds))
    print(classification_report(y_val, preds))

    os.makedirs(args.model_dir, exist_ok=True)
    joblib.dump(pipeline, os.path.join(args.model_dir, "model.joblib"))
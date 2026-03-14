import os
import json
import joblib

def model_fn(model_dir):
    model_path = os.path.join(model_dir, "model.joblib")
    return joblib.load(model_path)

def input_fn(request_body, content_type):
    if content_type != "application/json":
        raise ValueError(f"Unsupported content type: {content_type}")

    data = json.loads(request_body)

    if "text" in data:
        return [data["text"]]

    if "texts" in data:
        return data["texts"]

    raise ValueError("Payload must contain either 'text' or 'texts'")

def predict_fn(input_data, model):
    predictions = model.predict(input_data)
    return predictions.tolist()

def output_fn(prediction, accept):
    if accept not in ("application/json", "*/*"):
        raise ValueError(f"Unsupported accept type: {accept}")

    if len(prediction) == 1:
        return json.dumps({"prediction": prediction[0]}), "application/json"

    return json.dumps({"predictions": prediction}), "application/json"
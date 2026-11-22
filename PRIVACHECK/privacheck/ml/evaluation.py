import json
import joblib
from .train_model import METRICS_PATH, MODEL_PATH

def load_evaluation():
    if not METRICS_PATH.exists():
        return None
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))

def feature_importance(top_n=8):
    if not MODEL_PATH.exists():
        return []
    model = joblib.load(MODEL_PATH)
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    terms = vectorizer.get_feature_names_out()
    rows = []
    for label, weights in zip(classifier.classes_, classifier.coef_):
        indices = weights.argsort()[-top_n:][::-1]
        for index in indices:
            rows.append({"category": str(label), "term": str(terms[index]), "weight": float(weights[index])})
    return rows

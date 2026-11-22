from pathlib import Path
import joblib
from .preprocessing import clean_text, split_paragraphs
from .train_model import MODEL_PATH

def model_exists():
    return MODEL_PATH.exists()

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Aucun modèle entraîné. Lancez d'abord l'entraînement dans ML Analytics.")
    return joblib.load(MODEL_PATH)

def predict_texts(texts):
    model = load_model()
    cleaned = [clean_text(x) for x in texts]
    labels = model.predict(cleaned)
    classifier = model.named_steps["classifier"]
    scores = classifier.decision_function(model.named_steps["tfidf"].transform(cleaned))
    if getattr(scores, "ndim", 1) == 1:
        margins = [float(abs(x)) for x in scores]
    else:
        margins = [float(sorted(row)[-1] - sorted(row)[-2]) for row in scores]
    return [{"text": text, "category": str(label), "decision_margin": margin}
            for text, label, margin in zip(texts, labels, margins)]

def predict_document(text):
    paragraphs = split_paragraphs(text)
    return predict_texts(paragraphs) if paragraphs else []

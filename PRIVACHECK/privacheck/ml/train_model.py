from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from .preprocessing import clean_text

ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "datasets" / "gdpr_training_data.csv"
MODEL_PATH = ROOT / "models" / "gdpr_classifier.joblib"
METRICS_PATH = ROOT / "models" / "evaluation.json"

def train_model(dataset_path=None):
    path = Path(dataset_path) if dataset_path else DATASET_PATH
    if not path.exists():
        raise FileNotFoundError(f"Dataset introuvable: {path}")
    df = pd.read_csv(path)
    required = {"text", "label"}
    if not required.issubset(df.columns):
        raise ValueError("Le CSV doit contenir deux colonnes : text et label.")
    df = df[["text", "label"]].dropna()
    df["text"] = df["text"].map(clean_text)
    df["label"] = df["label"].astype(str).str.strip()
    df = df[(df["text"].str.len() > 10) & (df["label"] != "")]
    counts = df["label"].value_counts()
    if len(counts) < 2 or counts.min() < 4:
        raise ValueError("Il faut au moins 2 classes et 4 exemples par classe pour une évaluation stratifiée.")
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
    )
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=12000, sublinear_tf=True)),
        ("classifier", LinearSVC(class_weight="balanced", random_state=42))
    ])
    pipeline.fit(X_train, y_train)
    predicted = pipeline.predict(X_test)
    labels = sorted(df["label"].unique().tolist())
    report = classification_report(y_test, predicted, labels=labels, output_dict=True, zero_division=0)
    matrix = confusion_matrix(y_test, predicted, labels=labels)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    result = {
        "accuracy": float(accuracy_score(y_test, predicted)),
        "report": report,
        "labels": labels,
        "confusion_matrix": matrix.tolist(),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "dataset_size": int(len(df)),
        "source": path.name,
        "warning": "Le dataset de démonstration est illustratif. Les métriques ne démontrent pas une performance juridique ou une généralisation à des politiques réelles."
    }
    import json
    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result

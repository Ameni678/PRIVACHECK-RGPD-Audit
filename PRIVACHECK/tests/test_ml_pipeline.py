from pathlib import Path
import pandas as pd
from privacheck.ml.preprocessing import clean_text, split_paragraphs
from privacheck.ml.train_model import DATASET_PATH

def test_demo_dataset_has_required_columns_and_balanced_labels():
    df = pd.read_csv(DATASET_PATH)
    assert {"text", "label"}.issubset(df.columns)
    assert df["label"].nunique() >= 2
    assert df.groupby("label").size().min() >= 4

def test_preprocessing_normalizes_and_splits():
    assert clean_text("  GDPR   POLICY ") == "gdpr policy"
    paragraphs = split_paragraphs("A sufficiently long first paragraph about personal data and privacy.\n\nA sufficiently long second paragraph about retention periods and access rights.")
    assert len(paragraphs) == 2

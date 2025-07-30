from sklearn.linear_model import LogisticRegression
from transformers import DistilBertTokenizer, DistilBertModel
from sklearn.preprocessing import LabelEncoder
import torch
import joblib
import pandas as pd

class DistilBERTEmbedder:
    def __init__(self):
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        self.model = DistilBertModel.from_pretrained('distilbert-base-uncased').to("cuda" if torch.cuda.is_available() else "cpu")

    def encode(self, texts):
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :].cpu().numpy()

def train_model():
    df = pd.read_json("training.jsonl", lines=True)
    X = df["text"].tolist()
    y = df["label"].tolist()

    embedder = DistilBERTEmbedder()
    embeddings = embedder.encode(X)

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(embeddings, y_encoded)

    joblib.dump(clf, "../model/model.joblib")
    joblib.dump(encoder, "../model/label_encoder.joblib")
    print("✅ Model trained and saved.")

if __name__ == "__main__":
    train_model()

import yaml
from transformers import DistilBertTokenizer, DistilBertModel
import torch
import joblib
import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)

class EmailClassifier:
    def __init__(self, model_path, encoder_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.bert = DistilBertModel.from_pretrained('distilbert-base-uncased').to(self.device)
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        self.classifier = joblib.load(model_path)
        self.encoder = joblib.load(encoder_path)

    def embed(self, texts):
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.bert(**inputs)
        return outputs.last_hidden_state[:, 0, :].cpu().numpy()

    def predict(self, emails):
        texts = [e["text"] for e in emails]
        embeddings = self.embed(texts)
        preds = self.classifier.predict(embeddings)
        labels = self.encoder.inverse_transform(preds)
        return [dict(email, label=label) for email, label in zip(emails, labels)]

def load_from_s3(bucket, key, region):
    try:
        s3 = boto3.client('s3', region_name=region)
        obj = s3.get_object(Bucket=bucket, Key=key)
        logging.info(f"📥 Loaded input from s3://{bucket}/{key}")
        return [json.loads(line) for line in obj['Body'].read().decode('utf-8').splitlines()]
    except Exception as e:
        logging.error(f"❌ Failed to load from S3: {e}")
        raise

def save_to_s3(data, bucket, key, region):
    try:
        s3 = boto3.client('s3', region_name=region)
        output = '\n'.join(json.dumps(d) for d in data)
        s3.put_object(Bucket=bucket, Key=key, Body=output.encode('utf-8'))
        logging.info(f"✅ Saved output to s3://{bucket}/{key}")
    except Exception as e:
        logging.error(f"❌ Failed to save to S3: {e}")
        raise

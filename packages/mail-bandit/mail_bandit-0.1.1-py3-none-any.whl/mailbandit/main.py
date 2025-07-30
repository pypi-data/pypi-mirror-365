import logging
import yaml
from .distilbert import EmailClassifier, load_from_s3, save_to_s3

def main():
    with open("training/config.yaml") as f:
        config = yaml.safe_load(f)

    bucket = config["aws"]["bucket_name"]
    region = config["aws"]["region"]
    input_key = config["aws"]["input_key"]
    output_key = config["aws"]["output_key"]

    emails = load_from_s3(bucket, input_key, region)
    classifier = EmailClassifier(
        model_path=config["model"]["classifier_path"],
        encoder_path=config["model"]["label_encoder_path"]
    )
    predictions = classifier.predict(emails)
    save_to_s3(predictions, bucket, output_key, region)

if __name__ == "__main__":
    main()

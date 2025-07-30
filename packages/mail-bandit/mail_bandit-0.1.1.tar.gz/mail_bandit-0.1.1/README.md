# 📬 mail-bandit

**mail-bandit** is a plug-and-play email classifier that reads emails from an Amazon S3 bucket and classifies them into 5 categories using a fine-tuned DistilBERT model and XGBoost classifier.

---

## 🚀 Features

- ✅ Classifies emails into:
  - Offer Rollout
  - Rejection
  - Additional Information Required
  - General Communication
  - Unrelated to Application
- ✅ DistilBERT embeddings + XGBoost classifier
- ✅ Reads email data from `.jsonl` stored in S3
- ✅ Easy to train, deploy, and extend

---

## 🛠 Installation

```bash
pip install mail-bandit

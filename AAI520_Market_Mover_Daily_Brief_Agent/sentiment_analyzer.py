# data_processor/sentiment_analyzer.py

import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax


class DistilBERTSentimentAnalyzer:
    """
    Sentiment analyzer using the 'distilbert-base-uncased-finetuned-sst-2-english' model.
    Works without FinBERT and avoids PyTorch CVE issues.
    """

    def __init__(self):
        print("Loading DistilBERT sentiment model...")

        model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

        # Detect best available device (MPS for Apple Silicon, else CPU)
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("✅ Device set to use Apple MPS (Metal)")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            print("✅ Device set to use GPU (CUDA)")
        else:
            self.device = torch.device("cpu")
            print("✅ Device set to use CPU")

        self.model.to(self.device)
        self.model.eval()

        self.labels = ["negative", "positive"]

    def analyze_sentiment(self, texts):
        """
        Analyze sentiment for a list of text strings.
        Returns a DataFrame with sentiment label and scores.
        """
        results = []

        for text in texts:
            if not text.strip():
                results.append({"sentiment": "neutral", "positive_score": 0.5, "negative_score": 0.5})
                continue

            try:
                inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                with torch.no_grad():
                    logits = self.model(**inputs).logits

                probs = softmax(logits.cpu().numpy()[0])
                sentiment_label = self.labels[int(probs.argmax())]

                results.append({
                    "sentiment": sentiment_label,
                    "positive_score": float(probs[1]),
                    "negative_score": float(probs[0])
                })

            except Exception as e:
                print(f"⚠️ Error processing text: {e}")
                results.append({"sentiment": "error", "positive_score": None, "negative_score": None})

        return pd.DataFrame(results)

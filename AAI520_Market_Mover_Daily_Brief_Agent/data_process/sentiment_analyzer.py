"""
Sentiment analysis module for processing financial news and text data.
Uses DistilBERT model for efficient sentiment analysis.
"""

import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax


class DistilBERTSentimentAnalyzer:
    """
    Sentiment analyzer using the 'distilbert-base-uncased-finetuned-sst-2-english' model.
    Optimized for financial text analysis with support for batch processing.
    """

    def __init__(self):
        """Initialize the sentiment analyzer with the DistilBERT model."""
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
        
        Args:
            texts (list): List of text strings to analyze
            
        Returns:
            pd.DataFrame: DataFrame with columns:
                - sentiment: predicted sentiment label ('positive' or 'negative')
                - positive_score: probability score for positive sentiment
                - negative_score: probability score for negative sentiment
        """
        if not isinstance(texts, (list, tuple)):
            texts = [texts]
            
        results = []

        for text in texts:
            if not text or not str(text).strip():
                results.append({"sentiment": "neutral", "positive_score": 0.5, "negative_score": 0.5})
                continue

            try:
                inputs = self.tokenizer(
                    text, 
                    return_tensors="pt", 
                    truncation=True, 
                    padding=True, 
                    max_length=128
                )
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

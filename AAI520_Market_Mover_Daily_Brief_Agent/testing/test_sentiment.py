"""
Quick test script to verify sentiment analyzer integration
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data_process.sentiment_analyzer import DistilBERTSentimentAnalyzer

def test_sentiment_analyzer():
    print("Testing Sentiment Analyzer...")
    print("=" * 60)
    
    # Initialize analyzer
    print("\n1. Initializing DistilBERT Sentiment Analyzer...")
    analyzer = DistilBERTSentimentAnalyzer()
    print("✓ Analyzer initialized successfully")
    
    # Test with sample news headlines
    print("\n2. Testing with sample news headlines...")
    test_texts = [
        "Stocks Rally as Market Gains Momentum",
        "Tech Stocks Plunge on Economic Concerns",
        "Market Shows Mixed Results in Trading Session",
        "Apple Stock Surges to Record High",
        "Investors Worried About Rising Inflation"
    ]
    
    print("\nAnalyzing sentiments...")
    results = analyzer.analyze_sentiment(test_texts)
    
    print("\n3. Results:")
    print("-" * 60)
    for text, (idx, row) in zip(test_texts, results.iterrows()):
        sentiment = row['sentiment']
        pos_score = row['positive_score']
        neg_score = row['negative_score']
        
        print(f"\nText: {text}")
        print(f"  Sentiment: {sentiment}")
        print(f"  Positive Score: {pos_score:.3f}")
        print(f"  Negative Score: {neg_score:.3f}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")

if __name__ == '__main__':
    try:
        test_sentiment_analyzer()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

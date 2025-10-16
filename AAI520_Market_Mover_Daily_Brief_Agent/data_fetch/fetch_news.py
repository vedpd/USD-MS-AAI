"""
Fetch and process news articles related to stock movements.
Supports both real-time and mock data modes.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    """Fetches and processes news articles related to stock movements."""
    
    def __init__(self, use_mock: bool = False):
        """Initialize the news fetcher.
        
        Args:
            use_mock: If True, use mock data instead of making API calls
        """
        self.use_mock = use_mock
        self.api_key = os.getenv('NEWSAPI_API_KEY')
        self.base_url = os.getenv('NEWSAPI_BASE_URL', 'https://newsapi.org/v2')
    
    def get_news_for_tickers(self, tickers: List[str], days_back: int = 1) -> List[Dict[str, Any]]:
        """Get news articles related to the given stock tickers.
        
        Args:
            tickers: List of stock tickers to fetch news for
            days_back: Number of days to look back for news
            
        Returns:
            List of news articles with metadata
        """
        if self.use_mock or not self.api_key:
            return self._get_mock_news(tickers)
            
        try:
            # Format date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            # Format tickers for query
            ticker_query = ' OR '.join([f'({ticker} OR "{ticker}")' for ticker in tickers])
            
            # Make API request
            url = f"{self.base_url}/everything"
            params = {
                'q': ticker_query,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'sortBy': 'relevancy',
                'pageSize': 10 * len(tickers),  # Get more articles to ensure coverage
                'apiKey': self.api_key,
                'language': 'en',
                'searchIn': 'title,description,content'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            articles = response.json().get('articles', [])
            
            # Process and filter articles
            processed_articles = []
            for article in articles:
                # Skip articles without content
                if not article.get('content'):
                    continue
                    
                # Find which tickers are mentioned in the article
                mentioned_tickers = [
                    ticker for ticker in tickers 
                    if ticker.lower() in article.get('title', '').lower() or 
                       ticker.lower() in article.get('content', '').lower()
                ]
                
                if mentioned_tickers:
                    processed_articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'published_at': article.get('publishedAt', ''),
                        'tickers': mentioned_tickers
                    })
            
            return processed_articles
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return self._get_mock_news(tickers)
    
    def _get_mock_news(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Generate mock news data for testing."""
        logger.info("Using mock news data")
        
        # Create mock news data
        mock_news = [
            {
                'title': f"{tickers[0]} Reports Strong Quarterly Earnings",
                'description': f"{tickers[0]} reports better-than-expected earnings, beating analyst estimates.",
                'content': f"{tickers[0]} announced its quarterly earnings today, reporting strong growth across all business segments. The company's stock is up significantly in pre-market trading.",
                'url': f"https://example.com/news/{tickers[0].lower()}-earnings",
                'source': 'Mock Financial News',
                'published_at': datetime.utcnow().isoformat() + 'Z',
                'tickers': [tickers[0]]
            },
            {
                'title': f"Market Update: {tickers[1]} and {tickers[2]} Lead Tech Rally",
                'description': f"Tech stocks rally as {tickers[1]} and {tickers[2]} show strong performance.",
                'content': f"In today's trading session, technology stocks showed strong performance with {tickers[1]} and {tickers[2]} leading the charge. Analysts attribute this to positive market sentiment and strong earnings reports.",
                'url': 'https://example.com/news/tech-rally',
                'source': 'Mock Market Watch',
                'published_at': (datetime.utcnow() - timedelta(hours=2)).isoformat() + 'Z',
                'tickers': [tickers[1], tickers[2]]
            },
            {
                'title': f"{tickers[-1]} Faces Regulatory Challenges",
                'description': f"{tickers[-1]} stock drops amid new regulatory concerns.",
                'content': f"Shares of {tickers[-1]} fell sharply today after reports of increased regulatory scrutiny. Analysts are watching the situation closely as it develops.",
                'url': f'https://example.com/news/{tickers[-1].lower()}-regulatory',
                'source': 'Mock Business Daily',
                'published_at': (datetime.utcnow() - timedelta(hours=5)).isoformat() + 'Z',
                'tickers': [tickers[-1]]
            }
        ]
        
        # Save mock data for reference
        os.makedirs('data', exist_ok=True)
        with open('data/mock_news.json', 'w') as f:
            json.dump(mock_news, f, indent=2)
        
        return mock_news

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Simple sentiment analysis of news content.
        
        In a real implementation, this would use a more sophisticated NLP model.
        """
        positive_words = ['strong', 'growth', 'beat', 'up', 'gain', 'positive', 'profit', 'rise', 'surge', 'rally']
        negative_words = ['fall', 'drop', 'loss', 'down', 'negative', 'decline', 'concern', 'risk', 'volatile']
        
        text_lower = text.lower()
        
        pos_score = sum(1 for word in positive_words if word in text_lower)
        neg_score = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_score + neg_score
        
        if total > 0:
            sentiment = (pos_score - neg_score) / total
        else:
            sentiment = 0.0
            
        return {
            'score': sentiment,
            'magnitude': abs(sentiment),
            'positive': pos_score,
            'negative': neg_score
        }

if __name__ == "__main__":
    # Example usage
    fetcher = NewsFetcher(use_mock=True)  # Set to False to use real API with valid key
    news = fetcher.get_news_for_tickers(['AAPL', 'MSFT', 'GOOGL', 'TSLA'])
    
    print("\nLatest News:")
    for i, article in enumerate(news, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Tickers: {', '.join(article['tickers'])}")
        print(f"   Sentiment: {fetcher.analyze_sentiment(article['content'])['score']:.2f}")

"""
Generate concise summaries of market movements and news.
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketBriefGenerator:
    """Generates a daily market brief based on price movements and news."""
    
    def __init__(self, use_mock: bool = False):
        """Initialize the brief generator.
        
        Args:
            use_mock: If True, use mock data for demonstration
        """
        self.use_mock = use_mock
    
    def generate_daily_brief(self, movers_data: Dict[str, Any], news_data: List[Dict], 
                           routed_movements: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> Dict[str, Any]:
        """Generate a comprehensive daily market brief.
        
        Args:
            movers_data: Dictionary containing 'gainers' and 'losers' DataFrames
            news_data: List of news articles related to the movers
            routed_movements: Dictionary containing routed movements by category
            
        Returns:
            Dictionary containing the formatted brief
        """
        # Get current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Generate sections of the brief
        summary = self._generate_summary_section(movers_data)
        gainers_analysis = self._analyze_movers(movers_data.get('gainers', pd.DataFrame()), 'gainers', news_data)
        losers_analysis = self._analyze_movers(movers_data.get('losers', pd.DataFrame()), 'losers', news_data)
        market_sentiment = self._analyze_market_sentiment(movers_data, news_data)
        
        # Compile the full brief
        brief = {
            'date': current_date,
            'overview': summary,
            'top_gainers': gainers_analysis,
            'top_losers': losers_analysis,
            'market_sentiment': market_sentiment,
            'key_news': self._summarize_key_news(news_data) if news_data else []
        }
        
        # Add routing information if available
        if routed_movements is not None:
            brief['routed_movements'] = routed_movements
            
            # Add analysis summary
            analysis_summary = {}
            for category, items in routed_movements.items():
                if items:
                    analysis_summary[category] = {
                        'count': len(items),
                        'avg_confidence': sum(item.get('confidence', 0) for item in items) / len(items)
                    }
            brief['analysis_summary'] = analysis_summary
        
        return brief
    
    def _generate_summary_section(self, movers_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the summary section of the brief."""
        gainers = movers_data.get('gainers', pd.DataFrame())
        losers = movers_data.get('losers', pd.DataFrame())
        
        return {
            'total_gainers': len(gainers),
            'total_losers': len(losers),
            'market_breadth': self._calculate_market_breadth(gainers, losers),
            'notable_movers': self._get_notable_movers(gainers, losers)
        }
    
    def _calculate_market_breadth(self, gainers: pd.DataFrame, losers: pd.DataFrame) -> Dict[str, float]:
        """Calculate market breadth metrics."""
        total = len(gainers) + len(losers)
        if total == 0:
            return {'advance_decline_ratio': 0, 'market_health': 'neutral'}
            
        adv_decline_ratio = len(gainers) / total if len(losers) > 0 else float('inf')
        
        # Simple market health assessment
        if adv_decline_ratio > 0.6:
            health = 'bullish'
        elif adv_decline_ratio < 0.4:
            health = 'bearish'
        else:
            health = 'neutral'
            
        return {
            'advance_decline_ratio': round(adv_decline_ratio, 2),
            'market_health': health
        }
    
    def _get_notable_movers(self, gainers: pd.DataFrame, losers: pd.DataFrame) -> List[Dict]:
        """Identify and describe the most notable movers."""
        notable = []
        
        # Get top 3 gainers and losers
        for i, (_, row) in enumerate(gainers.head(3).iterrows(), 1):
            notable.append({
                'ticker': row['ticker'],
                'rank': i,
                'type': 'gainer',
                'pct_change': round(row['pct_change'], 2),
                'close': round(row['close'], 2)
            })
            
        for i, (_, row) in enumerate(losers.head(3).iterrows(), 1):
            notable.append({
                'ticker': row['ticker'],
                'rank': i,
                'type': 'loser',
                'pct_change': round(row['pct_change'], 2),
                'close': round(row['close'], 2)
            })
            
        return notable
    
    def _analyze_movers(self, movers: pd.DataFrame, mover_type: str, news_data: List[Dict]) -> List[Dict]:
        """Analyze and summarize movers of a specific type (gainers/losers)."""
        if movers.empty:
            return []
            
        analysis = []
        
        for _, row in movers.iterrows():
            ticker = row['ticker']
            
            # Find related news
            related_news = [
                news for news in news_data 
                if ticker in news.get('tickers', [])
            ]
            
            # Get potential reasons from news
            reasons = []
            for news in related_news[:2]:  # Limit to top 2 news items per stock
                reasons.append({
                    'headline': news.get('title', ''),
                    'source': news.get('source', 'Unknown'),
                    'sentiment': self._analyze_news_sentiment(news.get('content', ''))
                })
            
            analysis.append({
                'ticker': ticker,
                'price': round(row['close'], 2),
                'pct_change': round(row['pct_change'], 2),
                'volume': int(row.get('volume', 0)),
                'potential_reasons': reasons or [{'headline': 'No significant news found', 'source': 'N/A', 'sentiment': 'neutral'}],
                'sector': self._get_sector(ticker)
            })
            
        return analysis
    
    def _analyze_market_sentiment(self, movers_data: Dict[str, Any], news_data: List[Dict]) -> Dict[str, Any]:
        """Analyze overall market sentiment based on movers and news."""
        # Simple sentiment analysis
        sentiment_scores = []
        
        # Sentiment from price movements
        gainers = movers_data.get('gainers', pd.DataFrame())
        losers = movers_data.get('losers', pd.DataFrame())
        
        if not gainers.empty:
            avg_gain = gainers['pct_change'].mean()
            sentiment_scores.append(min(avg_gain / 5, 1))  # Normalize
            
        if not losers.empty:
            avg_loss = losers['pct_change'].mean()
            sentiment_scores.append(max(avg_loss / 5, -1))  # Normalize
        
        # Sentiment from news
        from fetch_news import NewsFetcher
        news_fetcher = NewsFetcher(use_mock=self.use_mock)
        
        news_sentiments = []
        for news in news_data:
            sentiment = news_fetcher.analyze_sentiment(news.get('content', ''))
            news_sentiments.append(sentiment['score'])
        
        if news_sentiments:
            avg_news_sentiment = sum(news_sentiments) / len(news_sentiments)
            sentiment_scores.append(avg_news_sentiment)
        
        # Calculate overall sentiment
        overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        return {
            'score': round(overall_sentiment, 2),
            'sentiment': self._get_sentiment_label(overall_sentiment),
            'factors_considered': ['price_movements', 'news_sentiment']
        }
    
    def _summarize_key_news(self, news_data: List[Dict]) -> List[Dict]:
        """Summarize key news items."""
        if not news_data:
            return []
            
        # Sort by recency and impact (simple heuristic based on ticker mentions and content length)
        sorted_news = sorted(
            news_data,
            key=lambda x: (
                -len(x.get('tickers', [])),  # More tickers mentioned
                len(x.get('content', ''))     # Longer content (more detailed)
            )
        )
        
        # Return top 5 news items
        return [
            {
                'headline': news.get('title', ''),
                'source': news.get('source', 'Unknown'),
                'tickers': news.get('tickers', []),
                'published_at': news.get('published_at', ''),
                'url': news.get('url', '')
            }
            for news in sorted_news[:5]
        ]
    
    def _get_sector(self, ticker: str) -> str:
        """Get sector for a ticker (mock implementation)."""
        # In a real implementation, this would come from a data source
        sector_map = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology',
            'AMZN': 'Consumer Cyclical', 'TSLA': 'Consumer Cyclical',
            'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial',
            'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'MRK': 'Healthcare'
        }
        return sector_map.get(ticker, 'Other')
    
    def _analyze_news_sentiment(self, text: str) -> str:
        """Simple sentiment analysis for news content."""
        positive_words = ['strong', 'growth', 'beat', 'up', 'gain', 'positive', 'profit', 'rise', 'surge', 'rally']
        negative_words = ['fall', 'drop', 'loss', 'down', 'negative', 'decline', 'concern', 'risk', 'volatile']
        
        text_lower = text.lower()
        
        pos_score = sum(1 for word in positive_words if word in text_lower)
        neg_score = sum(1 for word in negative_words if word in text_lower)
        
        if pos_score > neg_score:
            return 'positive'
        elif neg_score > pos_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label."""
        if score >= 0.3:
            return 'bullish'
        elif score <= -0.3:
            return 'bearish'
        else:
            return 'neutral'

if __name__ == "__main__":
    # Example usage
    from fetch_prices import StockPriceFetcher
    from fetch_news import NewsFetcher
    from identify_movers import MoverAnalyzer
    import json
    
    # Initialize components
    price_fetcher = StockPriceFetcher(use_mock=True)
    news_fetcher = NewsFetcher(use_mock=True)
    mover_analyzer = MoverAnalyzer(threshold=2.0)
    brief_generator = MarketBriefGenerator(use_mock=True)
    
    # Get data
    price_data = price_fetcher.get_top_movers(20)
    movers = mover_analyzer.identify_significant_movers(price_data)
    all_tickers = list(set(movers['all_movers']['ticker'].tolist()))
    news = news_fetcher.get_news_for_tickers(all_tickers)
    
    # Generate brief
    brief = brief_generator.generate_daily_brief(movers, news)
    
    # Print the brief in a readable format
    print("\n" + "="*50)
    print(f"MARKET BRIEF - {brief['date']}")
    print("="*50)
    
    # Overview
    print("\nOVERVIEW:")
    print(f"- {brief['overview']['total_gainers']} significant gainers | {brief['overview']['total_losers']} significant losers")
    print(f"- Market Health: {brief['overview']['market_breadth']['market_health'].upper()}")
    
    # Top movers
    print("\nTOP MOVERS:")
    for mover in brief['overview']['notable_movers'][:5]:  # Show top 5
        change_type = "↑ GAIN" if mover['type'] == 'gainer' else "↓ LOSS"
        print(f"- {mover['ticker']}: {change_type} {abs(mover['pct_change']):.2f}% (${mover['close']})")
    
    # Market sentiment
    print("\nMARKET SENTIMENT:")
    print(f"- Sentiment: {brief['market_sentiment']['sentiment'].upper()} ({brief['market_sentiment']['score']:.2f})")
    
    # Key news
    if brief['key_news']:
        print("\nKEY MARKET NEWS:")
        for i, news in enumerate(brief['key_news'][:3], 1):  # Show top 3
            tickers = ", ".join(news['tickers']) if news['tickers'] else "General Market"
            print(f"{i}. {news['headline']} ({tickers}) - {news['source']}")

"""
Data Fetcher Module
Handles fetching real market data from Yahoo Finance and NewsAPI
"""
import os
import yfinance as yf
import pandas as pd
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import random
import logging
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        """Initialize the DataFetcher with API clients and configuration"""
        self.newsapi = NewsApiClient(api_key=os.getenv('NEWSAPI_API_KEY'))
        self.tickers = os.getenv('YAHOO_FINANCE_TICKERS', 'AAPL,GOOGL,MSFT,AMZN,META,TSLA,NVDA,NFLX,AMD,INTC').split(',')
        self.news_page_size = int(os.getenv('NEWS_API_PAGE_SIZE', 5))
        
        # Cache for news data to avoid hitting API rate limits
        self.news_cache = {}
        self.news_last_fetched = {}
        self.news_cache_ttl = 3600  # 1 hour in seconds
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = None
        self._init_sentiment_analyzer()
    
    def _init_sentiment_analyzer(self):
        """Initialize the sentiment analyzer (lazy loading to avoid startup delays)"""
        try:
            from data_process.sentiment_analyzer import DistilBERTSentimentAnalyzer
            self.sentiment_analyzer = DistilBERTSentimentAnalyzer()
            logger.info("Sentiment analyzer initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize sentiment analyzer: {str(e)}. Will use fallback method.")
            self.sentiment_analyzer = None
    
    def get_stock_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Fetch stock data for all configured tickers and identify top movers"""
        try:
            tickers_data = {}
            
            # Use a more reliable list of tickers
            reliable_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'JNJ']
            
            # Fetch data in chunks to avoid timeouts
            chunk_size = 3  # Smaller chunk size for better reliability
            for i in range(0, len(reliable_tickers), chunk_size):
                chunk = reliable_tickers[i:i + chunk_size]
                try:
                    data = yf.download(
                        tickers=chunk,
                        period='1d',
                        interval='1d',
                        group_by='ticker',
                        progress=False,
                        auto_adjust=True  # Explicitly set to avoid warning
                    )
                    
                    # Process each ticker in the chunk
                    for ticker in chunk:
                        try:
                            if len(chunk) == 1:
                                # Single ticker case
                                ticker_data = data
                            else:
                                # Multiple tickers case
                                ticker_data = data[ticker] if ticker in data.columns.levels[0] else None
                            
                            if ticker_data is not None and not ticker_data.empty and len(ticker_data) >= 1:
                                current = ticker_data.iloc[-1]
                                prev_close = ticker_data['Close'].iloc[0] if len(ticker_data) > 1 else current['Open']
                                
                                # Skip if we don't have valid price data
                                if pd.isna(current['Close']) or pd.isna(prev_close):
                                    continue
                                    
                                change_pct = ((current['Close'] - prev_close) / prev_close) * 100
                                volume = int(current['Volume']) if not pd.isna(current['Volume']) else 0
                                
                                tickers_data[ticker] = {
                                    'symbol': ticker,
                                    'price': round(float(current['Close']), 2),
                                    'change': round(float(change_pct), 2),
                                    'volume': volume
                                }
                                
                        except Exception as e:
                            logger.warning(f"Error processing ticker {ticker}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error fetching data for tickers {chunk}: {str(e)}")
                    continue
                    
            # Separate gainers and losers
            all_tickers = list(tickers_data.values())
            
            # Sort gainers in descending order (highest gains first)
            gainers = sorted(
                [t for t in all_tickers if t['change'] > 0],
                key=lambda x: x['change'],
                reverse=True
            )
            
            # Sort losers in ascending order (biggest losses first)
            losers = sorted(
                [t for t in all_tickers if t['change'] < 0],
                key=lambda x: x['change']
            )
            
            logger.info(f"Found {len(gainers)} gainers and {len(losers)} losers")
            
            return gainers, losers
            
        except Exception as e:
            logger.error(f"Error in get_stock_data: {str(e)}")
            # Return empty lists in case of error
            return [], []
    
    def get_news(self, tickers: Optional[List[str]] = None) -> List[Dict]:
        """Fetch market news from NewsAPI
        
        Args:
            tickers: Optional list of ticker symbols to fetch news for.
                    If None, fetches general market news.
        """
        try:
            # Create cache key based on tickers
            cache_key = f"news_{'_'.join(tickers)}" if tickers else 'market_news'
            current_time = datetime.now()
            
            if (cache_key in self.news_cache and 
                cache_key in self.news_last_fetched and
                (current_time - self.news_last_fetched[cache_key]).total_seconds() < self.news_cache_ttl):
                return self.news_cache[cache_key]
            
            # If not in cache or cache expired, fetch from API
            news_items = []
            
            # Build search query
            if tickers:
                # Get company names for better search results
                ticker_names = self._get_company_names(tickers)
                # Build more specific query with stock/market context
                company_query = ' OR '.join([f'"{name}"' for name in ticker_names[:3]])
                query = f'({company_query}) AND (stock OR shares OR market OR trading OR price)'
                logger.info(f"Fetching news for tickers {tickers} with query: {query}")
            else:
                query = 'stocks OR market'
                logger.info(f"Fetching general market news with query: {query}")
            
            # Try to get business news first
            try:
                news = self.newsapi.get_everything(
                    q=query,
                    language='en',
                    sort_by='publishedAt',
                    page_size=self.news_page_size * 2,  # Fetch more to filter
                    page=1
                )
                
                if news['status'] == 'ok':
                    # Collect all articles first
                    articles_to_process = []
                    for article in news['articles']:
                        try:
                            # Filter articles to ensure relevance
                            title = article['title'].lower()
                            description = article.get('description', '').lower()
                            
                            # If we have specific tickers, verify article mentions them
                            if tickers:
                                ticker_names_lower = [name.lower() for name in self._get_company_names(tickers)]
                                # Check if any company name or ticker is mentioned
                                is_relevant = any(
                                    name in title or name in description or 
                                    ticker in title or ticker in description
                                    for name, ticker in zip(ticker_names_lower, tickers)
                                )
                                
                                # Skip if not relevant to our tickers
                                if not is_relevant:
                                    continue
                            
                            articles_to_process.append({
                                'title': article['title'],
                                'source': article['source']['name'],
                                'published_at': article['publishedAt'],
                                'url': article['url'],
                                'description': article.get('description', '')
                            })
                            
                            # Stop if we have enough relevant articles
                            if len(articles_to_process) >= self.news_page_size:
                                break
                                
                        except Exception as e:
                            logger.warning(f"Error collecting news article: {str(e)}")
                            continue
                    
                    # Log filtering results
                    if tickers:
                        logger.info(f"Found {len(articles_to_process)} relevant articles after filtering for {tickers}")
                    
                    # Perform sentiment analysis on all articles
                    if articles_to_process:
                        sentiments = self._analyze_news_sentiment(articles_to_process)
                        
                        # Combine articles with sentiment results
                        for article, sentiment_data in zip(articles_to_process, sentiments):
                            news_items.append({
                                'title': article['title'],
                                'source': article['source'],
                                'published_at': article['published_at'],
                                'url': article['url'],
                                'sentiment': sentiment_data['sentiment'],
                                'sentiment_score': sentiment_data['score'],
                                'positive_score': sentiment_data.get('positive_score', 0),
                                'negative_score': sentiment_data.get('negative_score', 0)
                            })
            except Exception as e:
                logger.error(f"Error fetching news from NewsAPI: {str(e)}")
                # Fall back to mock news if API fails
                return self._get_mock_news()
            
            # Cache the results
            self.news_cache[cache_key] = news_items
            self.news_last_fetched[cache_key] = current_time
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error in get_news: {str(e)}")
            # Fall back to mock news in case of error
            return self._get_mock_news()
    
    def _get_company_names(self, tickers: List[str]) -> List[str]:
        """Get company names from ticker symbols for better news search"""
        ticker_to_name = {
            'AAPL': 'Apple',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google',
            'AMZN': 'Amazon',
            'META': 'Meta',
            'TSLA': 'Tesla',
            'NVDA': 'NVIDIA',
            'JPM': 'JPMorgan',
            'V': 'Visa',
            'JNJ': 'Johnson',
            'NFLX': 'Netflix',
            'AMD': 'AMD',
            'INTC': 'Intel',
            'WMT': 'Walmart'
        }
        return [ticker_to_name.get(t, t) for t in tickers]
    
    def get_ticker_news(self, ticker: str) -> List[Dict]:
        """Fetch news for a specific ticker symbol
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            List of news articles with sentiment analysis
        """
        return self.get_news(tickers=[ticker])
    
    def _analyze_news_sentiment(self, articles: List[Dict]) -> List[Dict]:
        """Analyze sentiment for news articles using DistilBERT or fallback method"""
        sentiments = []
        
        if self.sentiment_analyzer:
            try:
                # Use DistilBERT sentiment analyzer
                texts = [f"{article['title']}. {article.get('description', '')}" for article in articles]
                results = self.sentiment_analyzer.analyze_sentiment(texts)
                
                for idx, row in results.iterrows():
                    sentiment_label = row['sentiment']
                    positive_score = row.get('positive_score', 0)
                    negative_score = row.get('negative_score', 0)
                    
                    # Convert to sentiment label and score
                    if sentiment_label == 'positive':
                        sentiment = 'positive'
                        score = positive_score
                    elif sentiment_label == 'negative':
                        sentiment = 'negative'
                        score = negative_score
                    else:
                        sentiment = 'neutral'
                        score = 0.5
                    
                    sentiments.append({
                        'sentiment': sentiment,
                        'score': round(score, 3),
                        'positive_score': round(positive_score, 3),
                        'negative_score': round(negative_score, 3)
                    })
                
                return sentiments
                
            except Exception as e:
                logger.warning(f"Error using sentiment analyzer: {str(e)}. Falling back to keyword-based method.")
        
        # Fallback: Simple keyword-based sentiment analysis
        for article in articles:
            title = article['title'].lower()
            content = article.get('description', '').lower()
            
            # Simple keyword-based sentiment
            positive_words = ['up', 'rise', 'gain', 'surge', 'rally', 'positive', 'profit', 'growth', 'bullish', 'strong']
            negative_words = ['down', 'fall', 'drop', 'plunge', 'decline', 'negative', 'loss', 'worry', 'bearish', 'weak']
            
            pos_count = sum(1 for word in positive_words if word in title or word in content)
            neg_count = sum(1 for word in negative_words if word in title or word in content)
            
            if pos_count > neg_count:
                sentiment = 'positive'
                score = min(0.5 + (pos_count * 0.1), 0.9)
            elif neg_count > pos_count:
                sentiment = 'negative'
                score = min(0.5 + (neg_count * 0.1), 0.9)
            else:
                sentiment = 'neutral'
                score = 0.5
            
            sentiments.append({
                'sentiment': sentiment,
                'score': round(score, 3),
                'positive_score': round(pos_count / max(pos_count + neg_count, 1), 3),
                'negative_score': round(neg_count / max(pos_count + neg_count, 1), 3)
            })
        
        return sentiments
    
    def _get_mock_news(self) -> List[Dict]:
        """Generate mock news data as fallback"""
        mock_news = [
            {
                'title': 'Stocks Rally as Market Gains Momentum',
                'source': 'Financial Times',
                'published_at': datetime.utcnow().isoformat() + 'Z',
                'sentiment': 'positive',
                'sentiment_score': 0.85,
                'positive_score': 0.85,
                'negative_score': 0.15
            },
            {
                'title': 'Tech Stocks Show Mixed Results in After-Hours Trading',
                'source': 'MarketWatch',
                'published_at': (datetime.utcnow() - timedelta(hours=2)).isoformat() + 'Z',
                'sentiment': 'neutral',
                'sentiment_score': 0.5,
                'positive_score': 0.5,
                'negative_score': 0.5
            },
            {
                'title': 'Investors Cautious as Market Volatility Rises',
                'source': 'Bloomberg',
                'published_at': (datetime.utcnow() - timedelta(hours=4)).isoformat() + 'Z',
                'sentiment': 'negative',
                'sentiment_score': 0.75,
                'positive_score': 0.25,
                'negative_score': 0.75
            }
        ]
        return mock_news

    def get_market_health(self, gainers: List[Dict], losers: List[Dict]) -> str:
        """Determine overall market health based on gainers and losers"""
        if not gainers and not losers:
            return 'neutral'
            
        total = len(gainers) + len(losers)
        if total == 0:
            return 'neutral'
            
        gainer_ratio = len(gainers) / total
        
        if gainer_ratio > 0.6:
            return 'bullish'
        elif gainer_ratio < 0.4:
            return 'bearish'
        else:
            return 'neutral'
            
    def get_historical_data(self, symbol: str, period: str = '1y', interval: str = '1d') -> Optional[Dict]:
        """Fetch historical price data for a symbol"""
        try:
            # Download historical data
            stock = yf.Ticker(symbol)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                return None
                
            # Reset index to make Date a column
            df = df.reset_index()
            
            # Convert datetime to string for JSON serialization
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            # Calculate simple moving averages
            sma_20 = SMAIndicator(close=df['Close'], window=20)
            sma_50 = SMAIndicator(close=df['Close'], window=50)
            df['SMA_20'] = sma_20.sma_indicator()
            df['SMA_50'] = sma_50.sma_indicator()
            
            # Calculate RSI
            rsi = RSIIndicator(close=df['Close'], window=14)
            df['RSI'] = rsi.rsi()
            
            # Convert to dictionary for JSON serialization
            data = {
                'dates': df['Date'].tolist(),
                'open': df['Open'].round(2).tolist(),
                'high': df['High'].round(2).tolist(),
                'low': df['Low'].round(2).tolist(),
                'close': df['Close'].round(2).tolist(),
                'volume': df['Volume'].astype(int).tolist(),
                'sma_20': df['SMA_20'].round(2).fillna('').astype(str).replace('nan', '').tolist(),
                'sma_50': df['SMA_50'].round(2).fillna('').astype(str).replace('nan', '').tolist(),
                'rsi': df['RSI'].round(2).fillna('').astype(str).replace('nan', '').tolist()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None

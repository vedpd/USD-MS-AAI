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
    
    def get_news(self) -> List[Dict]:
        """Fetch market news from NewsAPI"""
        try:
            # Check cache first
            cache_key = 'market_news'
            current_time = datetime.now()
            
            if (cache_key in self.news_cache and 
                cache_key in self.news_last_fetched and
                (current_time - self.news_last_fetched[cache_key]).total_seconds() < self.news_cache_ttl):
                return self.news_cache[cache_key]
            
            # If not in cache or cache expired, fetch from API
            news_items = []
            
            # Try to get business news first
            try:
                news = self.newsapi.get_everything(
                    q='stocks OR market',
                    language='en',
                    sort_by='publishedAt',
                    page_size=self.news_page_size,
                    page=1
                )
                
                if news['status'] == 'ok':
                    for article in news['articles']:
                        try:
                            # Basic sentiment analysis (very simple approach)
                            title = article['title'].lower()
                            content = article.get('description', '').lower()
                            
                            # Simple keyword-based sentiment
                            positive_words = ['up', 'rise', 'gain', 'surge', 'rally', 'positive', 'profit', 'growth']
                            negative_words = ['down', 'fall', 'drop', 'plunge', 'decline', 'negative', 'loss', 'worry']
                            
                            score = 0
                            for word in positive_words:
                                if word in title or word in content:
                                    score += 1
                            
                            for word in negative_words:
                                if word in title or word in content:
                                    score -= 1
                            
                            # Normalize score to -1 to 1 range
                            sentiment = max(-1, min(1, score / 3))
                            
                            news_items.append({
                                'title': article['title'],
                                'source': article['source']['name'],
                                'published_at': article['publishedAt'],
                                'url': article['url'],
                                'sentiment': sentiment
                            })
                        except Exception as e:
                            logger.warning(f"Error processing news article: {str(e)}")
                            continue
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
    
    def _get_mock_news(self) -> List[Dict]:
        """Generate mock news data as fallback"""
        mock_news = [
            {
                'title': 'Stocks Rally as Market Gains Momentum',
                'source': 'Financial Times',
                'published_at': datetime.utcnow().isoformat() + 'Z',
                'sentiment': 0.8
            },
            {
                'title': 'Tech Stocks Show Mixed Results in After-Hours Trading',
                'source': 'MarketWatch',
                'published_at': (datetime.utcnow() - timedelta(hours=2)).isoformat() + 'Z',
                'sentiment': 0.1
            },
            {
                'title': 'Investors Cautious as Market Volatility Rises',
                'source': 'Bloomberg',
                'published_at': (datetime.utcnow() - timedelta(hours=4)).isoformat() + 'Z',
                'sentiment': -0.5
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

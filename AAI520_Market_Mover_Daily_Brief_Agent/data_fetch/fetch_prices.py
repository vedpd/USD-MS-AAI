"""
Fetch stock price data from Yahoo Finance.
Supports both real-time and mock data modes.
"""
import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Union
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockPriceFetcher:
    """Fetches stock price data from Yahoo Finance."""
    
    def __init__(self, use_mock: bool = False):
        """Initialize the price fetcher.
        
        Args:
            use_mock: If True, use mock data instead of making API calls
        """
        self.use_mock = use_mock
        
    def get_top_movers(self, top_n: int = 10) -> pd.DataFrame:
        """Get top gainers and losers for the day.
        
        Args:
            top_n: Number of top gainers/losers to return
            
        Returns:
            DataFrame with top movers
        """
        if self.use_mock:
            return self._get_mock_movers(top_n)
            
        # Get S&P 500 tickers as our universe
        sp500_tickers = self._get_sp500_tickers()
        
        # Get price data for all tickers
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Get data for the past week
        
        try:
            data = yf.download(
                tickers=sp500_tickers,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                group_by='ticker',
                progress=False
            )
            
            # Process the data to find daily movers
            movers = self._process_price_data(data, sp500_tickers)
            
            # Get top gainers and losers
            top_gainers = movers.nlargest(top_n, 'pct_change')
            top_losers = movers.nsmallest(top_n, 'pct_change')
            
            # Combine and return
            return pd.concat([top_gainers, top_losers]).drop_duplicates()
            
        except Exception as e:
            logger.error(f"Error fetching price data: {e}")
            # Fall back to mock data on error
            return self._get_mock_movers(top_n)
    
    def _get_sp500_tickers(self) -> List[str]:
        """Get list of S&P 500 tickers."""
        try:
            table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            return table[0]['Symbol'].tolist()
        except:
            # Fallback to a small set of major tickers if the request fails
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'JPM', 'JNJ', 'V', 'PG']
    
    def _process_price_data(self, data: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
        """Process raw price data to calculate daily percentage changes."""
        movers = []
        
        for ticker in tickers:
            try:
                if ticker not in data.columns.get_level_values(0):
                    continue
                    
                df = data[ticker].copy()
                if df.empty:
                    continue
                    
                # Calculate daily percentage change
                df['pct_change'] = df['Close'].pct_change() * 100
                
                # Get most recent day's data
                latest = df.iloc[-1]
                
                movers.append({
                    'ticker': ticker,
                    'close': latest['Close'],
                    'pct_change': latest['pct_change'],
                    'volume': latest['Volume']
                })
                
            except Exception as e:
                logger.warning(f"Error processing {ticker}: {e}")
        
        return pd.DataFrame(movers)
    
    def _get_mock_movers(self, top_n: int) -> pd.DataFrame:
        """Generate mock data for testing."""
        logger.info("Using mock stock data")
        
        # Create mock data
        mock_data = {
            'ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA', 'AMD', 'INTC',
                      'JPM', 'BAC', 'WFC', 'C', 'GS', 'JNJ', 'PFE', 'MRK', 'ABT', 'GILD'],
            'close': [150.25, 305.42, 98.76, 112.34, 245.67, 320.98, 410.32, 290.76, 180.45, 42.31,
                     145.67, 32.45, 45.67, 67.89, 345.67, 165.43, 43.21, 98.76, 110.22, 78.90],
            'pct_change': [5.2, 3.8, 2.9, -1.2, 7.8, -2.4, 1.5, 4.3, -3.1, -5.6,
                          1.2, -0.8, 2.1, -1.9, 3.5, -2.2, 0.8, -1.5, 2.7, -4.3],
            'volume': [1000000, 2000000, 1500000, 3000000, 2500000, 1800000, 1200000, 900000, 1100000, 800000,
                      700000, 850000, 950000, 650000, 500000, 750000, 850000, 900000, 600000, 550000]
        }
        
        df = pd.DataFrame(mock_data)
        
        # Save mock data for reference
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/mock_prices.csv', index=False)
        
        # Return top gainers and losers
        top_gainers = df.nlargest(top_n, 'pct_change')
        top_losers = df.nsmallest(top_n, 'pct_change')
        
        return pd.concat([top_gainers, top_losers]).drop_duplicates()

if __name__ == "__main__":
    # Example usage
    fetcher = StockPriceFetcher(use_mock=True)  # Set to False for real data
    movers = fetcher.get_top_movers(5)
    print("\nTop Movers:")
    print(movers[['ticker', 'pct_change', 'close']])

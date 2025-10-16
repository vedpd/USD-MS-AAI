"""
Test script for live data integration.
"""
import os
import logging
from dotenv import load_dotenv
import yfinance as yf
import requests
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LiveDataTester:
    """Class to test live data integration."""
    
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_API_KEY')
        self.newsapi_base_url = os.getenv('NEWSAPI_BASE_URL', 'https://newsapi.org/v2')
        
        if not self.newsapi_key or self.newsapi_key == 'your_newsapi_key_here':
            logger.warning("NewsAPI key not found or using placeholder. Some features may be limited.")
    
    def test_yfinance(self, ticker: str = 'AAPL'):
        """Test Yahoo Finance API."""
        try:
            logger.info(f"Testing Yahoo Finance API for {ticker}...")
            stock = yf.Ticker(ticker)
            
            # Get today's date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)  # Get data for the last 7 days
            
            # Get historical market data
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"No data returned for {ticker}")
                return False
                
            logger.info(f"Successfully retrieved data for {ticker}")
            logger.info(f"Latest data (as of {hist.index[-1].date()}):")
            logger.info(f"  Open: {hist['Open'][-1]:.2f}")
            logger.info(f"  High: {hist['High'][-1]:.2f}")
            logger.info(f"  Low: {hist['Low'][-1]:.2f}")
            logger.info(f"  Close: {hist['Close'][-1]:.2f}")
            logger.info(f"  Volume: {hist['Volume'][-1]:,}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing Yahoo Finance API: {e}")
            return False
    
    def test_newsapi(self, query: str = 'stocks'):
        """Test NewsAPI."""
        if not self.newsapi_key or self.newsapi_key == 'your_newsapi_key_here':
            logger.error("Please set your NewsAPI key in the .env file")
            return False
            
        try:
            logger.info(f"Testing NewsAPI with query: {query}")
            
            # Calculate date range (last 7 days)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=7)
            
            # Make request to NewsAPI
            url = f"{self.newsapi_base_url}/everything"
            params = {
                'q': query,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'sortBy': 'publishedAt',
                'apiKey': self.newsapi_key,
                'pageSize': 3  # Just get 3 articles for testing
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'ok':
                logger.error(f"NewsAPI returned status: {data.get('message', 'Unknown error')}")
                return False
                
            articles = data.get('articles', [])
            
            if not articles:
                logger.warning("No articles found for the given query")
                return False
                
            logger.info(f"Successfully retrieved {len(articles)} articles:")
            for i, article in enumerate(articles[:3], 1):  # Show first 3 articles
                logger.info(f"\n{i}. {article.get('title', 'No title')}")
                logger.info(f"   Source: {article.get('source', {}).get('name', 'Unknown')}")
                logger.info(f"   Published: {article.get('publishedAt', 'Unknown')}")
                logger.info(f"   URL: {article.get('url', 'No URL')}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to NewsAPI: {e}")
            return False
        except Exception as e:
            logger.error(f"Error testing NewsAPI: {e}")
            return False

def main():
    """Run tests for live data integration."""
    tester = LiveDataTester()
    
    print("\n" + "="*60)
    print("TESTING LIVE DATA INTEGRATION")
    print("="*60)
    
    # Test Yahoo Finance
    print("\n[1/2] Testing Yahoo Finance API...")
    yfinance_success = tester.test_yfinance('AAPL')
    
    # Test NewsAPI
    print("\n[2/2] Testing NewsAPI...")
    newsapi_success = tester.test_newsapi('stocks')
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Yahoo Finance: {'SUCCESS' if yfinance_success else 'FAILED'}")
    print(f"NewsAPI: {'SUCCESS' if newsapi_success else 'FAILED'}")
    
    if not yfinance_success or not newsapi_success:
        print("\nTroubleshooting Tips:")
        if not yfinance_success:
            print("- Check your internet connection")
            print("- Verify that yfinance package is installed (pip install yfinance)")
        if not newsapi_success:
            print("- Make sure you've set a valid NewsAPI key in the .env file")
            print("- Check that your NewsAPI key has the correct permissions")
            print("- Visit https://newsapi.org/ to check your account status")
    else:
        print("\nAll tests passed! You can now run the agent with live data.")
        print("To run the agent, use: python run_agent.py")

if __name__ == "__main__":
    main()

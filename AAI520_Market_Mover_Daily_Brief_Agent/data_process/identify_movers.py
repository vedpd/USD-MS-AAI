"""
Identify and analyze significant stock price movements.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoverAnalyzer:
    """Analyzes stock price movements to identify significant movers."""
    
    def __init__(self, threshold: float = 2.0):
        """Initialize the mover analyzer.
        
        Args:
            threshold: Percentage threshold to consider a stock a significant mover
        """
        self.threshold = threshold
    
    def identify_significant_movers(self, price_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Identify significant movers from price data.
        
        Args:
            price_data: DataFrame containing price data with 'pct_change' column
            
        Returns:
            Dictionary containing DataFrames for gainers and losers
        """
        if price_data.empty:
            return {'gainers': pd.DataFrame(), 'losers': pd.DataFrame()}
        
        # Ensure we have the required columns
        required_columns = ['ticker', 'pct_change', 'close']
        missing_columns = [col for col in required_columns if col not in price_data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in price data: {', '.join(missing_columns)}")
        
        # Filter for significant movers
        gainers = price_data[price_data['pct_change'] >= self.threshold].copy()
        losers = price_data[price_data['pct_change'] <= -self.threshold].copy()
        
        # Sort by absolute percentage change
        gainers = gainers.sort_values('pct_change', ascending=False)
        losers = losers.sort_values('pct_change')
        
        # Add additional metrics
        for df in [gainers, losers]:
            if not df.empty:
                df['abs_change'] = (df['pct_change'] / 100) * df['close']
        
        return {
            'gainers': gainers,
            'losers': losers,
            'all_movers': pd.concat([gainers, losers])
        }
    
    def get_movement_summary(self, movers_data: Dict[str, pd.DataFrame]) -> Dict[str, any]:
        """Generate a summary of the market movements.
        
        Args:
            movers_data: Dictionary containing 'gainers' and 'losers' DataFrames
            
        Returns:
            Dictionary with summary statistics
        """
        gainers = movers_data.get('gainers', pd.DataFrame())
        losers = movers_data.get('losers', pd.DataFrame())
        
        summary = {
            'total_gainers': len(gainers),
            'total_losers': len(losers),
            'top_gainer': gainers.iloc[0].to_dict() if not gainers.empty else None,
            'top_loser': losers.iloc[0].to_dict() if not losers.empty else None,
            'avg_gain': gainers['pct_change'].mean() if not gainers.empty else 0,
            'avg_loss': losers['pct_change'].mean() if not losers.empty else 0,
            'total_volume': {
                'gainers': gainers['volume'].sum() if not gainers.empty else 0,
                'losers': losers['volume'].sum() if not losers.empty else 0
            },
            'sector_breakdown': {
                'gainers': self._get_sector_breakdown(gainers),
                'losers': self._get_sector_breakdown(losers)
            }
        }
        
        return summary
    
    def _get_sector_breakdown(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get sector breakdown of movers.
        
        In a real implementation, this would map tickers to sectors.
        For now, we'll use a simple mock implementation.
        """
        if df.empty:
            return {}
            
        # Mock sector mapping (in a real app, this would come from a data source)
        sector_map = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology',
            'AMZN': 'Consumer Cyclical', 'TSLA': 'Consumer Cyclical',
            'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial',
            'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'MRK': 'Healthcare'
        }
        
        # Count by sector
        sectors = [sector_map.get(ticker, 'Other') for ticker in df['ticker']]
        return pd.Series(sectors).value_counts().to_dict()

if __name__ == "__main__":
    # Example usage
    from fetch_prices import StockPriceFetcher
    
    # Get some price data
    fetcher = StockPriceFetcher(use_mock=True)
    price_data = fetcher.get_top_movers(20)  # Get top 20 movers
    
    # Analyze movers
    analyzer = MoverAnalyzer(threshold=2.0)
    movers = analyzer.identify_significant_movers(price_data)
    
    # Print results
    print("\nSignificant Gainers:")
    print(movers['gainers'][['ticker', 'pct_change', 'close', 'volume']])
    
    print("\nSignificant Losers:")
    print(movers['losers'][['ticker', 'pct_change', 'close', 'volume']])
    
    # Print summary
    summary = analyzer.get_movement_summary(movers)
    print("\nMarket Movement Summary:")
    print(f"Total Gainers: {summary['total_gainers']}")
    print(f"Total Losers: {summary['total_losers']}")
    
    if summary['top_gainer']:
        print(f"\nTop Gainer: {summary['top_gainer']['ticker']} ({summary['top_gainer']['pct_change']:.2f}%)")
    if summary['top_loser']:
        print(f"Top Loser: {summary['top_loser']['ticker']} ({summary['top_loser']['pct_change']:.2f}%)")

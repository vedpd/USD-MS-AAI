"""
Routing system for directing market movers to appropriate analysis agents.
"""
import logging
from typing import Dict, Any, Tuple, List
import re
from dataclasses import dataclass
from enum import Enum, auto
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of analysis that can be performed on a stock movement."""
    EARNINGS = auto()
    MACRO = auto()
    NEWS = auto()
    UNKNOWN = auto()

@dataclass
class MoveAnalysis:
    """Container for analysis results of a stock movement."""
    ticker: str
    move_type: str  # 'gainer' or 'loser'
    pct_change: float
    analysis_type: AnalysisType
    confidence: float
    reasons: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'ticker': self.ticker,
            'move_type': self.move_type,
            'pct_change': self.pct_change,
            'analysis_type': self.analysis_type.name,
            'confidence': self.confidence,
            'reasons': self.reasons
        }

class Router:
    """Routes stock movements to appropriate analysis agents."""
    
    def __init__(self):
        # Keywords that indicate earnings-related news
        self.earnings_keywords = [
            'earnings', 'profit', 'revenue', 'eps', 'ebitda', 'quarterly results',
            'annual report', 'beats estimates', 'misses estimates', 'guidance',
            'raised forecast', 'lowered forecast', 'quarterly report', 'financial results'
        ]
        
        # Keywords that indicate macroeconomic news
        self.macro_keywords = [
            'fed', 'interest rate', 'inflation', 'unemployment', 'gdp', 'economic growth',
            'central bank', 'policy', 'trade war', 'tariff', 'economic data', 'jobs report',
            'manufacturing index', 'retail sales', 'housing market', 'consumer confidence'
        ]
    
    def analyze_movement(self, ticker: str, move_type: str, pct_change: float, 
                        related_news: List[Dict[str, Any]]) -> MoveAnalysis:
        """Analyze a stock movement and determine the most likely cause."""
        # Initialize analysis
        analysis = MoveAnalysis(
            ticker=ticker,
            move_type=move_type,
            pct_change=pct_change,
            analysis_type=AnalysisType.UNKNOWN,
            confidence=0.0,
            reasons=[]
        )
        
        # Analyze each news item
        for news in related_news:
            content = f"{news.get('title', '')} {news.get('description', '')} {news.get('content', '')}".lower()
            
            # Check for earnings-related content
            earnings_score = sum(1 for kw in self.earnings_keywords if kw in content)
            macro_score = sum(1 for kw in self.macro_keywords if kw in content)
            
            if earnings_score > 0 or macro_score > 0:
                reason = {
                    'headline': news.get('title', ''),
                    'source': news.get('source', 'Unknown'),
                    'earnings_score': earnings_score,
                    'macro_score': macro_score,
                    'published_at': news.get('published_at', '')
                }
                analysis.reasons.append(reason)
        
        # Determine the most likely cause
        if analysis.reasons:
            total_earnings = sum(r['earnings_score'] for r in analysis.reasons)
            total_macro = sum(r['macro_score'] for r in analysis.reasons)
            
            if total_earnings > total_macro * 1.5:  # Significant earnings focus
                analysis.analysis_type = AnalysisType.EARNINGS
                analysis.confidence = min(1.0, total_earnings / 5.0)  # Cap at 1.0
            elif total_macro > total_earnings * 1.5:  # Significant macro focus
                analysis.analysis_type = AnalysisType.MACRO
                analysis.confidence = min(1.0, total_macro / 5.0)  # Cap at 1.0
            else:  # Mixed or unclear
                analysis.analysis_type = AnalysisType.NEWS
                analysis.confidence = min(0.7, max(total_earnings, total_macro) / 5.0)
        
        return analysis

    def route_movements(self, movers: Dict[str, Any], news_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Route all movers to appropriate analysis types."""
        results = {
            'earnings': [],
            'macro': [],
            'news': [],
            'unknown': []
        }
        
        # Process gainers
        for _, row in movers.get('gainers', pd.DataFrame()).iterrows():
            ticker = row['ticker']
            related_news = [n for n in news_data if ticker in n.get('tickers', [])]
            
            analysis = self.analyze_movement(
                ticker=ticker,
                move_type='gainer',
                pct_change=row['pct_change'],
                related_news=related_news
            )
            
            # Route to appropriate category
            if analysis.analysis_type == AnalysisType.EARNINGS:
                results['earnings'].append(analysis.to_dict())
            elif analysis.analysis_type == AnalysisType.MACRO:
                results['macro'].append(analysis.to_dict())
            elif analysis.analysis_type == AnalysisType.NEWS:
                results['news'].append(analysis.to_dict())
            else:
                results['unknown'].append(analysis.to_dict())
        
        # Process losers (similar to gainers)
        for _, row in movers.get('losers', pd.DataFrame()).iterrows():
            ticker = row['ticker']
            related_news = [n for n in news_data if ticker in n.get('tickers', [])]
            
            analysis = self.analyze_movement(
                ticker=ticker,
                move_type='loser',
                pct_change=row['pct_change'],
                related_news=related_news
            )
            
            # Route to appropriate category
            if analysis.analysis_type == AnalysisType.EARNINGS:
                results['earnings'].append(analysis.to_dict())
            elif analysis.analysis_type == AnalysisType.MACRO:
                results['macro'].append(analysis.to_dict())
            elif analysis.analysis_type == AnalysisType.NEWS:
                results['news'].append(analysis.to_dict())
            else:
                results['unknown'].append(analysis.to_dict())
        
        return results

# Example usage
if __name__ == "__main__":
    import pandas as pd
    
    # Example data
    movers = {
        'gainers': pd.DataFrame([
            {'ticker': 'AAPL', 'pct_change': 5.2, 'close': 150.25, 'volume': 1000000},
            {'ticker': 'TSLA', 'pct_change': 7.8, 'close': 245.67, 'volume': 2500000}
        ]),
        'losers': pd.DataFrame([
            {'ticker': 'INTC', 'pct_change': -5.6, 'close': 42.31, 'volume': 800000}
        ])
    }
    
    news_data = [
        {
            'title': 'AAPL Reports Record Quarterly Earnings',
            'description': 'Apple beats earnings estimates with strong iPhone sales',
            'content': 'Apple reported better-than-expected earnings for Q2 2025...',
            'source': 'Financial Times',
            'published_at': '2025-09-13T10:30:00Z',
            'tickers': ['AAPL']
        },
        {
            'title': 'Fed Signals Possible Rate Hike',
            'description': 'Federal Reserve indicates potential interest rate increase',
            'content': 'The Federal Reserve signaled it may raise interest rates...',
            'source': 'Wall Street Journal',
            'published_at': '2025-09-13T11:15:00Z',
            'tickers': []
        },
        {
            'title': 'TSLA Stock Soars on New Model Announcement',
            'description': 'Tesla shares jump after unveiling new electric vehicle model',
            'content': 'Tesla announced a new electric vehicle model...',
            'source': 'Tech News',
            'published_at': '2025-09-13T12:00:00Z',
            'tickers': ['TSLA']
        }
    ]
    
    # Create router and process movements
    router = Router()
    results = router.route_movements(movers, news_data)
    
    # Print results
    for category, items in results.items():
        if items:
            print(f"\n{category.upper()} MOVEMENTS:")
            for item in items:
                print(f"- {item['ticker']}: {item['move_type'].title()} {abs(item['pct_change']):.2f}%")
                for reason in item['reasons']:
                    print(f"  - {reason['headline']} ({reason['source']})")

#!/usr/bin/env python3
"""
Market Movers Daily Brief Generator
Generates comprehensive daily market briefs with AI-powered sentiment analysis
and saves results in multiple formats (JSON, Markdown, HTML, CSV)
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json
import csv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data_fetch.data_fetcher import DataFetcher
from data_process.evaluator import EvaluatorOptimizer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketBriefAgent:
    """AI-Powered Market Brief Generator"""
    
    def __init__(self, output_dir: str = './output', enable_evaluation: bool = True):
        self.data_fetcher = DataFetcher()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize evaluator for performance tracking
        self.enable_evaluation = enable_evaluation
        if enable_evaluation:
            eval_dir = self.output_dir / 'eval_data'
            eval_dir.mkdir(exist_ok=True)
            self.evaluator = EvaluatorOptimizer(data_dir=str(eval_dir))
            logger.info("Evaluator initialized for performance tracking")
        else:
            self.evaluator = None
        
        self.sector_map = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology',
            'AMZN': 'Consumer Cyclical', 'META': 'Technology', 'TSLA': 'Consumer Cyclical',
            'NVDA': 'Technology', 'JPM': 'Financial Services', 'V': 'Financial Services',
            'JNJ': 'Healthcare', 'WMT': 'Consumer Defensive', 'NFLX': 'Communication Services',
            'AMD': 'Technology', 'INTC': 'Technology'
        }
    
    def generate_daily_brief(self, save_outputs: bool = True, evaluate_previous: bool = True) -> Dict[str, Any]:
        """Generate comprehensive daily market brief
        
        Args:
            save_outputs: Whether to save outputs to files
            evaluate_previous: Whether to evaluate previous day's predictions
        """
        logger.info("=" * 70)
        logger.info("Starting Daily Market Brief Generation")
        logger.info("=" * 70)
        
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')
        
        # Fetch data
        logger.info("Fetching market data...")
        gainers, losers = self.data_fetcher.get_stock_data()
        
        if not gainers and not losers:
            return {"error": "No market data available"}
        
        market_health = self.data_fetcher.get_market_health(gainers, losers)
        
        # Get news
        top_tickers = []
        if gainers:
            top_tickers.extend([g['symbol'] for g in gainers[:3]])
        if losers:
            top_tickers.extend([l['symbol'] for l in losers[:2]])
        
        news = self.data_fetcher.get_news(tickers=top_tickers if top_tickers else None)
        
        # Evaluate previous day's predictions (if enabled)
        evaluation_results = None
        if evaluate_previous and self.evaluator:
            evaluation_results = self._evaluate_previous_predictions(date_str)
        
        # Generate brief
        brief = {
            'metadata': {
                'generated_at': timestamp.isoformat(),
                'date': date_str,
                'version': '3.1',
                'evaluation_enabled': self.enable_evaluation
            },
            'market_overview': self._generate_overview(gainers, losers, market_health),
            'top_gainers': self._analyze_movers(gainers[:10], 'gainer'),
            'top_losers': self._analyze_movers(losers[:10], 'loser'),
            'news_analysis': self._analyze_news(news),
            'sector_analysis': self._analyze_sectors(gainers, losers),
            'key_insights': self._generate_insights(gainers, losers, news, market_health),
            'recommendations': self._generate_recommendations(gainers, losers, market_health)
        }
        
        # Add evaluation results if available
        if evaluation_results:
            brief['evaluation'] = evaluation_results
            logger.info(f"📊 Previous predictions accuracy: {evaluation_results.get('accuracy', 0):.1%}")
        
        if save_outputs:
            self._save_all_formats(brief, date_str)
        
        logger.info("Brief generation complete!")
        return brief
    
    def _generate_overview(self, gainers, losers, market_health):
        total = len(gainers) + len(losers)
        return {
            'market_health': market_health,
            'total_gainers': len(gainers),
            'total_losers': len(losers),
            'advance_decline_ratio': round(len(gainers) / total, 2) if total > 0 else 0,
            'biggest_gainer': max(gainers, key=lambda x: x['change']) if gainers else None,
            'biggest_loser': min(losers, key=lambda x: x['change']) if losers else None
        }
    
    def _analyze_movers(self, movers, mover_type):
        return [{
            'rank': i + 1,
            'symbol': m['symbol'],
            'price': m['price'],
            'change_percent': m['change'],
            'volume': m['volume'],
            'sector': self.sector_map.get(m['symbol'], 'Other'),
            'type': mover_type
        } for i, m in enumerate(movers)]
    
    def _analyze_news(self, news):
        if not news:
            return {'total_articles': 0, 'articles': []}
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for a in news:
            sentiment_counts[a.get('sentiment', 'neutral')] += 1
        
        return {
            'total_articles': len(news),
            'sentiment_distribution': sentiment_counts,
            'articles': news
        }
    
    def _analyze_sectors(self, gainers, losers):
        sector_perf = {}
        for m in gainers + losers:
            sector = self.sector_map.get(m['symbol'], 'Other')
            if sector not in sector_perf:
                sector_perf[sector] = {'gainers': 0, 'losers': 0}
            if m in gainers:
                sector_perf[sector]['gainers'] += 1
            else:
                sector_perf[sector]['losers'] += 1
        return {'sector_performance': sector_perf}
    
    def _generate_insights(self, gainers, losers, news, market_health):
        insights = []
        total = len(gainers) + len(losers)
        if total > 0:
            insights.append(f"Market shows {market_health} sentiment with {len(gainers)}/{total} stocks advancing")
        if gainers:
            top = max(gainers, key=lambda x: x['change'])
            insights.append(f"{top['symbol']} led with +{top['change']:.2f}%")
        return insights
    
    def _generate_recommendations(self, gainers, losers, market_health):
        recs = []
        if market_health == 'bullish':
            recs.append("✅ Bullish market - Consider long positions")
        elif market_health == 'bearish':
            recs.append("⚠️ Bearish market - Exercise caution")
        else:
            recs.append("➖ Neutral market - Wait for clear signals")
        return recs
    
    def _save_all_formats(self, brief, date_str):
        logger.info("Saving outputs...")
        
        # JSON
        json_path = self.output_dir / f"market_brief_{date_str}.json"
        with open(json_path, 'w') as f:
            json.dump(brief, f, indent=2)
        logger.info(f"✅ Saved: {json_path}")
        
        # Markdown
        md_path = self.output_dir / f"market_brief_{date_str}.md"
        with open(md_path, 'w') as f:
            f.write(self._format_markdown(brief))
        logger.info(f"✅ Saved: {md_path}")
        
        # CSV
        csv_path = self.output_dir / f"movers_{date_str}.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['rank', 'symbol', 'type', 'price', 'change_percent', 'volume', 'sector'])
            writer.writeheader()
            writer.writerows(brief['top_gainers'] + brief['top_losers'])
        logger.info(f"✅ Saved: {csv_path}")
    
    def _format_markdown(self, brief):
        md = [f"# Market Brief - {brief['metadata']['date']}\n"]
        
        overview = brief['market_overview']
        md.append(f"## Market Overview\n")
        md.append(f"- Health: **{overview['market_health'].upper()}**")
        md.append(f"- Gainers: {overview['total_gainers']} | Losers: {overview['total_losers']}\n")
        
        md.append("## Top Gainers\n")
        for g in brief['top_gainers'][:5]:
            md.append(f"{g['rank']}. **{g['symbol']}** - ${g['price']} (+{g['change_percent']}%)")
        
        md.append("\n## Top Losers\n")
        for l in brief['top_losers'][:5]:
            md.append(f"{l['rank']}. **{l['symbol']}** - ${l['price']} ({l['change_percent']}%)")
        
        md.append("\n## Key Insights\n")
        for insight in brief['key_insights']:
            md.append(f"- {insight}")
        
        return "\n".join(md)
    
    def _evaluate_previous_predictions(self, current_date_str: str) -> Dict[str, Any]:
        """Evaluate previous day's predictions against actual movements"""
        from datetime import datetime, timedelta
        
        try:
            # Calculate previous trading day (skip weekends)
            current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
            days_back = 3 if current_date.weekday() == 0 else 1  # Monday looks back 3 days
            previous_date = current_date - timedelta(days=days_back)
            previous_date_str = previous_date.strftime('%Y-%m-%d')
            
            # Load previous day's brief
            previous_brief_path = self.output_dir / f"market_brief_{previous_date_str}.json"
            if not previous_brief_path.exists():
                logger.info(f"No previous brief found for {previous_date_str}, skipping evaluation")
                return None
            
            with open(previous_brief_path, 'r') as f:
                previous_brief = json.load(f)
            
            # Get current actual movements
            gainers, losers = self.data_fetcher.get_stock_data()
            actual_movements = {}
            for mover in gainers + losers:
                actual_movements[mover['symbol']] = mover['change']
            
            # Build analysis results from previous brief
            analysis_results = {
                'earnings': [],
                'macro': [],
                'news': [],
                'unknown': []
            }
            
            # Categorize previous predictions
            for gainer in previous_brief.get('top_gainers', []):
                category = self._categorize_movement(gainer, previous_brief.get('news_analysis', {}))
                analysis_results[category].append({
                    'ticker': gainer['symbol'],
                    'move_type': 'gainer',
                    'pct_change': gainer['change_percent'],
                    'reasons': [{'headline': f"Predicted as top gainer", 'source': 'System'}]
                })
            
            for loser in previous_brief.get('top_losers', []):
                category = self._categorize_movement(loser, previous_brief.get('news_analysis', {}))
                analysis_results[category].append({
                    'ticker': loser['symbol'],
                    'move_type': 'loser',
                    'pct_change': loser['change_percent'],
                    'reasons': [{'headline': f"Predicted as top loser", 'source': 'System'}]
                })
            
            # Evaluate predictions
            evaluation = self.evaluator.evaluate(analysis_results, actual_movements)
            
            # Optimize weights based on evaluation
            self.evaluator.optimize_weights()
            
            # Get performance summary
            performance = self.evaluator.get_performance_summary()
            
            logger.info("✅ Evaluation complete")
            logger.info(f"   Accuracy: {evaluation.get('accuracy', 0):.1%}")
            logger.info(f"   Precision: {evaluation.get('precision', 0):.1%}")
            logger.info(f"   Recall: {evaluation.get('recall', 0):.1%}")
            
            return {
                'previous_date': previous_date_str,
                'current_metrics': {
                    'accuracy': evaluation.get('accuracy', 0),
                    'precision': evaluation.get('precision', 0),
                    'recall': evaluation.get('recall', 0),
                    'f1_score': evaluation.get('f1_score', 0)
                },
                'historical_performance': performance,
                'predictions_evaluated': len(evaluation.get('details', [])),
                'correct_predictions': evaluation.get('true_positives', 0)
            }
            
        except Exception as e:
            logger.warning(f"Error during evaluation: {str(e)}")
            return None
    
    def _categorize_movement(self, mover: Dict, news_analysis: Dict) -> str:
        """Categorize a stock movement based on available information"""
        # Simple categorization logic
        # In a real system, this would be more sophisticated
        articles = news_analysis.get('articles', [])
        
        # Check if there's news about this ticker
        has_news = any(
            mover['symbol'].lower() in article.get('title', '').lower()
            for article in articles
        )
        
        if has_news:
            return 'news'
        else:
            return 'unknown'


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("📊 MARKET MOVERS DAILY BRIEF GENERATOR")
    print("=" * 70 + "\n")
    
    agent = MarketBriefAgent()
    brief = agent.generate_daily_brief(save_outputs=True)
    
    if 'error' in brief:
        print(f"❌ Error: {brief['error']}")
        return
    
    # Print summary
    print("\n" + "=" * 70)
    print("📋 BRIEF SUMMARY")
    print("=" * 70)
    
    overview = brief['market_overview']
    print(f"\n🎯 Market Health: {overview['market_health'].upper()}")
    print(f"📈 Gainers: {overview['total_gainers']}")
    print(f"📉 Losers: {overview['total_losers']}")
    
    print("\n🚀 Top 3 Gainers:")
    for g in brief['top_gainers'][:3]:
        print(f"   {g['rank']}. {g['symbol']} - ${g['price']} (+{g['change_percent']}%)")
    
    print("\n📉 Top 3 Losers:")
    for l in brief['top_losers'][:3]:
        print(f"   {l['rank']}. {l['symbol']} - ${l['price']} ({l['change_percent']}%)")
    
    print("\n💡 Key Insights:")
    for insight in brief['key_insights']:
        print(f"   • {insight}")
    
    print("\n🎯 Recommendations:")
    for rec in brief['recommendations']:
        print(f"   • {rec}")
    
    print("\n" + "=" * 70)
    print("✅ Brief generation complete! Check ./output/ for files.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

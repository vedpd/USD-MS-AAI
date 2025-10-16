"""
Main orchestrator for the Market Movers Daily Brief Agent.
"""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd

# Import local modules
from data_fetch.fetch_prices import StockPriceFetcher
from data_fetch.fetch_news import NewsFetcher
from data_process.identify_movers import MoverAnalyzer
from data_visualization.summarize import MarketBriefGenerator
from data_process.routing import Router, AnalysisType
from data_process.evaluator import EvaluatorOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketMoversAgent:
    """Main agent class for generating daily market briefs."""
    
    def __init__(self, use_mock: bool = False, output_dir: str = 'output'):
        """Initialize the market movers agent.
        
        Args:
            use_mock: If True, use mock data instead of real APIs
            output_dir: Directory to save output files
        """
        self.use_mock = use_mock
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        self.price_fetcher = StockPriceFetcher(use_mock=use_mock)
        self.news_fetcher = NewsFetcher(use_mock=use_mock)
        self.mover_analyzer = MoverAnalyzer(threshold=2.0)  # 2% threshold for significant moves
        self.brief_generator = MarketBriefGenerator(use_mock=use_mock)
        self.router = Router()
        self.evaluator = EvaluatorOptimizer(data_dir=os.path.join(output_dir, 'eval_data'))
        
        logger.info(f"Market Movers Agent initialized in {'MOCK' if use_mock else 'LIVE'} mode")
    
    def run(self) -> Dict[str, Any]:
        """Run the complete market analysis pipeline."""
        logger.info("Starting market analysis...")
        
        try:
            # Step 1: Fetch price data
            logger.info("Fetching stock price data...")
            price_data = self.price_fetcher.get_top_movers(30)  # Get top 30 movers
            
            # Step 2: Identify significant movers
            logger.info("Identifying significant movers...")
            movers = self.mover_analyzer.identify_significant_movers(price_data)
            
            # Get all unique tickers from movers
            all_tickers = list(set(movers['all_movers']['ticker'].tolist()))
            
            # Step 3: Fetch news for the movers
            logger.info("Fetching relevant news...")
            news = []
            if all_tickers:  # Only fetch news if we have tickers to look up
                news = self.news_fetcher.get_news_for_tickers(all_tickers)
            
            # Step 4: Route movements to appropriate analysis paths
            logger.info("Routing market movements...")
            routed_movements = self.router.route_movements(movers, news)
            
            # Step 5: Evaluate the analysis against actual movements
            logger.info("Evaluating analysis...")
            actual_movements = dict(zip(
                movers['all_movers']['ticker'], 
                movers['all_movers']['pct_change']
            ))
            evaluation = self.evaluator.evaluate(routed_movements, actual_movements)
            
            # Step 6: Optimize weights based on evaluation
            self.evaluator.optimize_weights()
            
            # Step 7: Generate the daily brief with routing information
            logger.info("Generating daily brief...")
            brief = self.brief_generator.generate_daily_brief(movers, news, routed_movements)
            
            # Step 8: Save the results
            self._save_results(brief, movers, news, routed_movements, evaluation)
            
            logger.info("Market analysis completed successfully!")
            return brief
            
        except Exception as e:
            logger.error(f"Error running market analysis: {e}", exc_info=True)
            raise
    
    def _save_results(self, brief: Dict[str, Any], movers: Dict[str, Any], 
                     news: list, routed_movements: Dict[str, List[Dict[str, Any]]],
                     evaluation: Dict[str, Any]) -> None:
        """Save the analysis results to files."""
        try:
            # Save the brief as JSON
            brief_file = os.path.join(self.output_dir, f"market_brief_{brief['date']}.json")
            with open(brief_file, 'w') as f:
                json.dump(brief, f, indent=2)
            logger.info(f"Saved brief to {brief_file}")
            
            # Save movers data
            movers_file = os.path.join(self.output_dir, f"movers_{brief['date']}.csv")
            movers['all_movers'].to_csv(movers_file, index=False)
            
            # Save news data
            if news:
                news_file = os.path.join(self.output_dir, f"news_{brief['date']}.json")
                with open(news_file, 'w') as f:
                    json.dump(news, f, indent=2)
            
            # Save routed movements
            routed_file = os.path.join(self.output_dir, f"routed_movements_{brief['date']}.json")
            with open(routed_file, 'w') as f:
                json.dump(routed_movements, f, indent=2)
            
            # Save evaluation
            eval_file = os.path.join(self.output_dir, f"evaluation_{brief['date']}.json")
            with open(eval_file, 'w') as f:
                json.dump(evaluation, f, indent=2)
            
            # Generate a human-readable report
            self._generate_report(brief, movers_file, brief_file, routed_movements, evaluation)
            
        except Exception as e:
            logger.error(f"Error saving results: {e}", exc_info=True)
    
    def _generate_report(self, brief: Dict[str, Any], movers_file: str, brief_file: str,
                        routed_movements: Dict[str, List[Dict[str, Any]]],
                        evaluation: Dict[str, Any]) -> None:
        """Generate a human-readable report."""
        try:
            report_file = os.path.join(self.output_dir, f"market_report_{brief['date']}.txt")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                # Header
                f.write("=" * 60 + "\n")
                f.write(f"MARKET MOVERS DAILY BRIEF - {brief['date']}\n")
                f.write("=" * 60 + "\n\n")
                
                # Overview
                f.write("MARKET OVERVIEW\n")
                f.write("-" * 60 + "\n")
                f.write(f"Significant Gainers: {brief['overview']['total_gainers']}\n")
                f.write(f"Significant Losers: {brief['overview']['total_losers']}\n")
                f.write(f"Market Health: {brief['overview']['market_breadth']['market_health'].upper()}\n\n")
                
                # Top Movers
                f.write("TOP MOVERS\n")
                f.write("-" * 60 + "\n")
                for i, mover in enumerate(brief['overview']['notable_movers'][:5], 1):
                    change_type = "↑ GAIN" if mover['type'] == 'gainer' else "↓ LOSS"
                    f.write(f"{i}. {mover['ticker']}: {change_type} {abs(mover['pct_change']):.2f}% (${mover['close']:.2f})\n")
                
                # Market Sentiment
                f.write("\nMARKET SENTIMENT\n")
                f.write("-" * 60 + "\n")
                f.write(f"Overall Sentiment: {brief['market_sentiment']['sentiment'].upper()} ({brief['market_sentiment']['score']:.2f})\n")
                
                # Routed Movements Summary
                f.write("\nMOVEMENT ANALYSIS\n")
                f.write("-" * 60 + "\n")
                for category, items in routed_movements.items():
                    if items:
                        f.write(f"{category.upper()} MOVEMENTS ({len(items)}):\n")
                        for item in items[:5]:  # Show top 5 in each category
                            change_type = "GAIN" if item['pct_change'] > 0 else "LOSS"
                            f.write(f"- {item['ticker']}: {change_type} {abs(item['pct_change']):.2f}%")
                            if item.get('reasons'):
                                f.write(f" (Reason: {item['reasons'][0].get('headline', 'No reason provided')[:60]}...)")
                            f.write("\n")
                        if len(items) > 5:
                            f.write(f"  ... and {len(items) - 5} more\n")
                        f.write("\n")
                
                # Key News
                if brief.get('key_news'):
                    f.write("\nKEY MARKET NEWS\n")
                    f.write("-" * 60 + "\n")
                    for i, news in enumerate(brief['key_news'][:3], 1):
                        tickers = ", ".join(news['tickers']) if news['tickers'] else "General Market"
                        f.write(f"{i}. {news['headline']}\n   ({tickers} - {news['source']})\n\n")
                
                # Evaluation Summary
                f.write("\nANALYSIS EVALUATION\n")
                f.write("-" * 60 + "\n")
                if 'accuracy' in evaluation:
                    f.write(f"Model Performance (based on {evaluation.get('true_positives', 0) + evaluation.get('false_positives', 0) + evaluation.get('false_negatives', 0)} samples):\n")
                    f.write(f"- Accuracy: {evaluation.get('accuracy', 0):.2f}\n")
                    f.write(f"- Precision: {evaluation.get('precision', 0):.2f}\n")
                    f.write(f"- Recall: {evaluation.get('recall', 0):.2f}\n")
                    f.write(f"- F1 Score: {evaluation.get('f1_score', 0):.2f}\n")
                else:
                    f.write("Evaluation metrics not available for this run.\n")
                
                # Footer
                f.write("\n" + "=" * 60 + "\n")
                f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Data sources: {'Mock Data' if self.use_mock else 'Yahoo Finance, NewsAPI'}\n")
                f.write("=" * 60 + "\n")
            
            logger.info(f"Generated report at {report_file}")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Market Movers Daily Brief Agent')
    parser.add_argument('--mock', action='store_true', help='Use mock data instead of real APIs')
    parser.add_argument('--output-dir', type=str, default='output', help='Directory to save output files')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Initialize and run the agent
        agent = MarketMoversAgent(
            use_mock=args.mock,
            output_dir=args.output_dir
        )
        
        # Run the analysis
        brief = agent.run()
        
        # Print a success message with the location of the output
        print("\n" + "="*60)
        print("MARKET MOVERS DAILY BRIEF GENERATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nThe daily brief has been saved to: {os.path.abspath(args.output_dir)}")
        print("\nKey Highlights:")
        print(f"- {brief['overview']['total_gainers']} significant gainers | {brief['overview']['total_losers']} significant losers")
        print(f"- Market Health: {brief['overview']['market_breadth']['market_health'].upper()}")
        print(f"- Overall Sentiment: {brief['market_sentiment']['sentiment'].upper()}")
        
        # Print the top mover
        if brief['overview']['notable_movers']:
            top_mover = brief['overview']['notable_movers'][0]
            change_type = "GAIN" if top_mover['type'] == 'gainer' else "LOSS"
            print(f"- Top Mover: {top_mover['ticker']} with {change_type} of {abs(top_mover['pct_change']):.2f}%")
        
        print("\nCheck the output directory for the full report and data files.")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        print("\nPlease check the logs for more details.")

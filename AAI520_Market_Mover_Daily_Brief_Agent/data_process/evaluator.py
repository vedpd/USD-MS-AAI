"""
Evaluator-Optimizer for validating detected reasons against market consensus.
"""
import logging
from typing import Dict, List, Any, Tuple
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluatorOptimizer:
    """
    Evaluates the accuracy of detected reasons for stock movements
    and optimizes the analysis process over time.
    """
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, 'evaluation_history.json')
        self.performance_metrics = self._load_performance_metrics()
        
        # Initialize default weights for different analysis types
        self.weights = {
            'earnings': 1.0,
            'macro': 1.0,
            'news': 0.7,
            'unknown': 0.3
        }
        
        # Load historical data if available
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load evaluation history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load evaluation history: {e}")
        return []
    
    def _save_history(self):
        """Save evaluation history to file."""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump(self.history[-100:], f)  # Keep only last 100 entries
        except Exception as e:
            logger.error(f"Failed to save evaluation history: {e}")
    
    def _load_performance_metrics(self) -> Dict[str, Dict[str, float]]:
        """Load or initialize performance metrics."""
        metrics_file = os.path.join(self.data_dir, 'performance_metrics.json')
        try:
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load performance metrics: {e}")
        
        # Default metrics
        return {
            'accuracy': {'value': 0.0, 'count': 0},
            'precision': {'value': 0.0, 'count': 0},
            'recall': {'value': 0.0, 'count': 0},
            'f1_score': {'value': 0.0, 'count': 0}
        }
    
    def _save_performance_metrics(self):
        """Save performance metrics to file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            metrics_file = os.path.join(self.data_dir, 'performance_metrics.json')
            with open(metrics_file, 'w') as f:
                json.dump(self.performance_metrics, f)
        except Exception as e:
            logger.error(f"Failed to save performance metrics: {e}")
    
    def _calculate_metrics(self, true_positives: int, false_positives: int, 
                         false_negatives: int) -> Dict[str, float]:
        """Calculate performance metrics."""
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = true_positives / (true_positives + false_positives + false_negatives) if (true_positives + false_positives + false_negatives) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'accuracy': accuracy
        }
    
    def _update_metrics(self, metrics: Dict[str, float]):
        """Update running average of performance metrics."""
        for metric, value in metrics.items():
            if metric in self.performance_metrics:
                current = self.performance_metrics[metric]
                n = current['count']
                current['value'] = (current['value'] * n + value) / (n + 1)
                current['count'] = n + 1
    
    def evaluate(self, analysis_results: Dict[str, Any], 
                actual_movements: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluate the accuracy of the analysis results against actual market movements.
        
        Args:
            analysis_results: Results from the router
            actual_movements: Dictionary mapping tickers to actual price changes
            
        Returns:
            Dictionary containing evaluation results
        """
        evaluation = {
            'timestamp': datetime.utcnow().isoformat(),
            'true_positives': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'details': []
        }
        
        # Check each predicted movement
        for category in ['earnings', 'macro', 'news', 'unknown']:
            for item in analysis_results.get(category, []):
                ticker = item['ticker']
                predicted_move = item['pct_change']
                actual_move = actual_movements.get(ticker, 0)
                
                # Determine if prediction was correct
                is_positive_move = predicted_move > 0
                is_actual_positive = actual_move > 0
                
                detail = {
                    'ticker': ticker,
                    'predicted_move': predicted_move,
                    'actual_move': actual_move,
                    'category': category,
                    'correct_direction': (is_positive_move == is_actual_positive),
                    'reasons': item.get('reasons', [])
                }
                
                # Update evaluation metrics
                if is_positive_move and is_actual_positive:
                    evaluation['true_positives'] += 1
                elif is_positive_move and not is_actual_positive:
                    evaluation['false_positives'] += 1
                elif not is_positive_move and is_actual_positive:
                    evaluation['false_negatives'] += 1
                
                evaluation['details'].append(detail)
        
        # Calculate metrics
        metrics = self._calculate_metrics(
            evaluation['true_positives'],
            evaluation['false_positives'],
            evaluation['false_negatives']
        )
        
        # Update running metrics
        self._update_metrics(metrics)
        
        # Add metrics to evaluation
        evaluation.update(metrics)
        
        # Save evaluation to history
        self.history.append(evaluation)
        self._save_history()
        self._save_performance_metrics()
        
        return evaluation
    
    def optimize_weights(self):
        """
        Optimize the weights for different analysis types based on historical performance.
        """
        if not self.history:
            return
        
        # Simple optimization: increase weights for categories with high accuracy
        category_scores = {}
        
        # Analyze history to find which categories perform best
        for category in ['earnings', 'macro', 'news']:
            correct = 0
            total = 0
            
            for eval_item in self.history:
                for detail in eval_item.get('details', []):
                    if detail.get('category') == category:
                        total += 1
                        if detail.get('correct_direction', False):
                            correct += 1
            
            if total > 0:
                accuracy = correct / total
                category_scores[category] = accuracy
        
        # Update weights based on performance
        if category_scores:
            max_score = max(category_scores.values())
            if max_score > 0:
                for category, score in category_scores.items():
                    # Normalize to 0.5-1.5 range
                    self.weights[category] = 0.5 + (score / max_score)
        
        logger.info(f"Updated analysis weights: {self.weights}")
        return self.weights
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of model performance."""
        return {
            'metrics': {k: v['value'] for k, v in self.performance_metrics.items()},
            'sample_size': self.performance_metrics['accuracy']['count'],
            'current_weights': self.weights
        }

# Example usage
if __name__ == "__main__":
    # Example data
    analysis_results = {
        'earnings': [
            {
                'ticker': 'AAPL',
                'move_type': 'gainer',
                'pct_change': 5.2,
                'reasons': [
                    {'headline': 'AAPL beats earnings estimates', 'source': 'CNBC'}
                ]
            }
        ],
        'macro': [
            {
                'ticker': 'JPM',
                'move_type': 'gainer',
                'pct_change': 2.1,
                'reasons': [
                    {'headline': 'Fed signals dovish stance', 'source': 'WSJ'}
                ]
            }
        ]
    }
    
    actual_movements = {
        'AAPL': 4.8,  # Correct direction (positive)
        'JPM': -1.2    # Incorrect direction (predicted up, actual down)
    }
    
    # Create and use evaluator
    evaluator = EvaluatorOptimizer()
    
    # Evaluate the analysis
    evaluation = evaluator.evaluate(analysis_results, actual_movements)
    print("\nEvaluation Results:")
    print(f"Accuracy: {evaluation['accuracy']:.2f}")
    print(f"Precision: {evaluation['precision']:.2f}")
    print(f"Recall: {evaluation['recall']:.2f}")
    print(f"F1 Score: {evaluation['f1_score']:.2f}")
    
    # Optimize weights
    evaluator.optimize_weights()
    
    # Get performance summary
    summary = evaluator.get_performance_summary()
    print("\nPerformance Summary:")
    print(f"Sample Size: {summary['sample_size']}")
    print(f"Current Weights: {summary['current_weights']}")

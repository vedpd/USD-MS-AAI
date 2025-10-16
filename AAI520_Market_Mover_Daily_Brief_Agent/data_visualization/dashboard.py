"""
Market Movers Dashboard - Real-time Web Application
"""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import json
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import random
import threading
import eventlet

# Import our existing modules
from data_fetch.fetch_prices import StockPriceFetcher
from data_fetch.fetch_news import NewsFetcher
from data_process.identify_movers import MoverAnalyzer
from data_process.routing import Router
from data_process.evaluator import EvaluatorOptimizer
from data_visualization.summarize import MarketBriefGenerator

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize components
price_fetcher = StockPriceFetcher(use_mock=False)
news_fetcher = NewsFetcher()
mover_analyzer = MoverAnalyzer(threshold=2.0)  # 2% threshold for significant moves
router = Router()
evaluator = EvaluatorOptimizer()
brief_generator = MarketBriefGenerator()

# Global state to store the latest data
current_state = {
    'market_health': 'neutral',
    'overall_sentiment': 0.0,
    'gainers': [],
    'losers': [],
    'news': [],
    'last_updated': None,
    'metrics': {}
}

# Track connected clients
connected_clients = 0

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/api/market-data')
def get_market_data():
    """API endpoint to get current market data."""
    return jsonify({
        'status': 'success',
        'data': current_state
    })

def fetch_and_update_market_data():
    """Fetch market data and update the current state."""
    try:
        logger.info("Fetching market data...")
        
        # 1. Fetch stock prices and identify movers
        price_data = price_fetcher.get_top_movers(top_n=20)
        movers = mover_analyzer.identify_significant_movers(price_data)
        
        # 2. Get news for the movers
        tickers = list(set(movers['gainers']['symbol'].tolist() + movers['losers']['symbol'].tolist()))
        news_items = news_fetcher.get_news_for_tickers(tickers)
        
        # 3. Route the movements
        routed_movements = {
            'earnings': [],
            'macro': [],
            'news': [],
            'unknown': []
        }
        
        # Process gainers
        for _, row in movers['gainers'].iterrows():
            ticker = row['symbol']
            ticker_news = [n for n in news_items if ticker in n.get('tickers', [])]
            
            # Get the most relevant news for this ticker
            relevant_news = ticker_news[0] if ticker_news else None
            
            # Route the movement
            movement = {
                'symbol': ticker,
                'price': row['price'],
                'change': row['pct_change'],
                'volume': row['volume'],
                'news': relevant_news
            }
            
            if relevant_news:
                category, confidence, reason = router.analyze_movement(
                    ticker, 
                    row['pct_change'], 
                    relevant_news['title'] + ' ' + (relevant_news.get('description') or '')
                )
                movement.update({
                    'category': category,
                    'confidence': confidence,
                    'reason': reason
                })
                
                # Add to the appropriate category
                if category == 'earnings':
                    routed_movements['earnings'].append(movement)
                elif category == 'macro':
                    routed_movements['macro'].append(movement)
                elif category == 'news':
                    routed_movements['news'].append(movement)
                else:
                    routed_movements['unknown'].append(movement)
            else:
                # No news, categorize as unknown
                movement.update({
                    'category': 'unknown',
                    'confidence': 0.0,
                    'reason': 'No relevant news found'
                })
                routed_movements['unknown'].append(movement)
        
        # Process losers (similar to gainers)
        for _, row in movers['losers'].iterrows():
            ticker = row['symbol']
            ticker_news = [n for n in news_items if ticker in n.get('tickers', [])]
            relevant_news = ticker_news[0] if ticker_news else None
            
            movement = {
                'symbol': ticker,
                'price': row['price'],
                'change': row['pct_change'],
                'volume': row['volume'],
                'news': relevant_news
            }
            
            if relevant_news:
                category, confidence, reason = router.analyze_movement(
                    ticker, 
                    row['pct_change'], 
                    relevant_news['title'] + ' ' + (relevant_news.get('description') or '')
                )
                movement.update({
                    'category': category,
                    'confidence': confidence,
                    'reason': reason
                })
                
                if category == 'earnings':
                    routed_movements['earnings'].append(movement)
                elif category == 'macro':
                    routed_movements['macro'].append(movement)
                elif category == 'news':
                    routed_movements['news'].append(movement)
                else:
                    routed_movements['unknown'].append(movement)
            else:
                movement.update({
                    'category': 'unknown',
                    'confidence': 0.0,
                    'reason': 'No relevant news found'
                })
                routed_movements['unknown'].append(movement)
        
        # 4. Evaluate and optimize
        metrics = evaluator.evaluate_performance(routed_movements)
        evaluator.optimize_weights()
        
        # 5. Update current state
        current_state.update({
            'market_health': 'bullish' if len(movers['gainers']) > len(movers['losers']) else 'bearish',
            'overall_sentiment': metrics.get('average_sentiment', 0.0),
            'gainers': movers['gainers'].to_dict('records'),
            'losers': movers['losers'].to_dict('records'),
            'news': news_items,
            'routed_movements': routed_movements,
            'metrics': metrics,
            'last_updated': datetime.utcnow().isoformat()
        })
        
        logger.info("Market data updated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error updating market data: {e}", exc_info=True)
        return False

def broadcast_market_update():
    """Broadcast the current market data to all connected clients."""
    try:
        if not current_state.get('last_updated'):
            return
            
        # Prepare data for the frontend
        data = {
            'overview': {
                'market_health': current_state['market_health'],
                'gainers_count': len(current_state['gainers']),
                'losers_count': len(current_state['losers']),
                'overall_sentiment': current_state['overall_sentiment']
            },
            'movers': current_state['gainers'] + current_state['losers'],
            'news': current_state['news'],
            'metrics': current_state['metrics']
        }
        
        # Emit the update
        socketio.emit('market_update', data)
        logger.debug("Market update broadcasted to clients")
        
    except Exception as e:
        logger.error(f"Error broadcasting market update: {e}")

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    global connected_clients
    connected_clients += 1
    logger.info(f"Client connected. Total clients: {connected_clients}")
    
    # Send current data to the newly connected client
    if current_state.get('last_updated'):
        socketio.emit('market_update', {
            'overview': {
                'market_health': current_state['market_health'],
                'gainers_count': len(current_state['gainers']),
                'losers_count': len(current_state['losers']),
                'overall_sentiment': current_state['overall_sentiment']
            },
            'movers': current_state['gainers'] + current_state['losers'],
            'news': current_state['news'],
            'metrics': current_state['metrics']
        })

@socketio.on('disconnect')
def handle_disconnect():
    global connected_clients
    connected_clients = max(0, connected_clients - 1)
    logger.info(f"Client disconnected. Total clients: {connected_clients}")

@socketio.on('request_initial_data')
def handle_initial_data_request():
    """Send the current market data to the client."""
    if current_state.get('last_updated'):
        socketio.emit('market_update', {
            'overview': {
                'market_health': current_state['market_health'],
                'gainers_count': len(current_state['gainers']),
                'losers_count': len(current_state['losers']),
                'overall_sentiment': current_state['overall_sentiment']
            },
            'movers': current_state['gainers'] + current_state['losers'],
            'news': current_state['news'],
            'metrics': current_state['metrics']
        })

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update requests from clients."""
    logger.info("Manual update requested by client")
    fetch_and_update_market_data()
    broadcast_market_update()

def background_task():
    """Background task to periodically update market data."""
    while True:
        try:
            # Update market data
            success = fetch_and_update_market_data()
            
            # Broadcast update if we have connected clients
            if connected_clients > 0 and success:
                broadcast_market_update()
                
            # Wait before next update (5 minutes)
            eventlet.sleep(300)
            
        except Exception as e:
            logger.error(f"Error in background task: {e}")
            eventlet.sleep(60)  # Wait a minute before retrying

if __name__ == '__main__':
    # Load environment variables
    load_dotenv()
    
    # Initial data fetch
    fetch_and_update_market_data()
    
    # Start background task
    eventlet.spawn(background_task)
    
    # Run the Flask app with SocketIO
    logger.info("Starting Market Movers Dashboard...")
    socketio.run(app, 
                host='0.0.0.0', 
                port=5000, 
                debug=True, 
                use_reloader=False,
                log_output=True)

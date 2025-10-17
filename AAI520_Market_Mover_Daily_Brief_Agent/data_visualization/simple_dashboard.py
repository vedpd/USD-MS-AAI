"""
Market Movers Dashboard
A real-time dashboard showing stock market movers and news
"""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import os
from datetime import datetime
import time
from threading import Thread, Lock
import logging
from data_fetch.data_fetcher import DataFetcher

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize Socket.IO with CORS enabled
socketio = SocketIO(app, 
                   async_mode='threading',
                   cors_allowed_origins="*",
                   logger=True,
                   engineio_logger=True)

# Initialize data fetcher
data_fetcher = DataFetcher()

# Global variable to store market data

# Global state with thread safety
global market_data
market_data = {
    'gainers': [],
    'losers': [],
    'market_health': 'neutral',
    'last_updated': None,
    'news': []
}

# Thread lock for thread safety
data_lock = Lock()

def fetch_market_data():
    """Fetch real market data from APIs"""
    try:
        # Fetch stock data
        gainers, losers = data_fetcher.get_stock_data()
        
        # Ensure we have some data
        if not gainers and not losers:
            logger.warning("No stock data available, using mock data")
            # Return some mock data if API fails
            gainers = [
                {'symbol': 'AAPL', 'price': 175.50, 'change': 2.5, 'volume': 5000000},
                {'symbol': 'MSFT', 'price': 320.25, 'change': 1.8, 'volume': 3500000},
                {'symbol': 'GOOGL', 'price': 2750.75, 'change': 1.2, 'volume': 2000000}
            ]
            losers = [
                {'symbol': 'TSLA', 'price': 650.80, 'change': -3.2, 'volume': 8000000},
                {'symbol': 'AMZN', 'price': 3100.25, 'change': -1.8, 'volume': 4500000},
                {'symbol': 'META', 'price': 180.50, 'change': -2.1, 'volume': 3000000}
            ]
        
        # Fetch news for top movers (gainers and losers)
        # Get tickers from top gainers and losers
        top_tickers = []
        if gainers:
            top_tickers.extend([g['symbol'] for g in gainers[:3]])  # Top 3 gainers
        if losers:
            top_tickers.extend([l['symbol'] for l in losers[:2]])  # Top 2 losers
        
        # Fetch news related to these tickers
        news = data_fetcher.get_news(tickers=top_tickers if top_tickers else None)
        
        if not news:
            news = [
                {
                    'title': 'Market Update: Major indices show mixed results',
                    'description': 'Stocks showed mixed results in today\'s trading session...',
                    'url': '#',
                    'publishedAt': datetime.now().isoformat(),
                    'source': {'name': 'Market News'},
                    'sentiment': 'neutral',
                    'sentiment_score': 0.5,
                    'positive_score': 0.5,
                    'negative_score': 0.5
                }
            ]
        
        # Get market health
        market_health = data_fetcher.get_market_health(gainers, losers)
        
        # Prepare response
        return {
            'gainers': gainers[:10],  # Limit to top 10
            'losers': losers[:10],    # Limit to top 10
            'market_health': market_health,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'news': news[:5]  # Limit to 5 news items
        }
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        # Return current data if available, or empty data if not
        with data_lock:
            return market_data if any(market_data.values()) else {
                'gainers': [],
                'losers': [],
                'market_health': 'neutral',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'news': []
            }

def background_thread():
    """Background thread to update market data"""
    while True:
        try:
            # Fetch new data
            new_data = fetch_market_data()
            
            # Update global state with thread safety
            with data_lock:
                global market_data
                market_data = new_data
            
            # Emit update to all connected clients
            socketio.emit('market_update', new_data)
            logger.info(f"Market data updated at {datetime.now().strftime('%H:%M:%S')}")
            
            # Wait for next update (5 minutes)
            time.sleep(300)
            
        except Exception as e:
            logger.error(f"Error in background thread: {str(e)}")
            # Wait a bit before retrying
            time.sleep(60)

@app.route('/')
def index():
    """Render the dashboard"""
    return render_template('simple_dashboard.html')

@app.route('/api/historical-data')
def get_historical_data():
    """API endpoint to fetch historical price data for a symbol"""
    symbol = request.args.get('symbol', '').upper()
    period = request.args.get('period', '1mo')  # Default to 1 month
    
    if not symbol:
        return jsonify({'error': 'Symbol parameter is required'}), 400
    
    try:
        # Fetch historical data
        data = data_fetcher.get_historical_data(symbol, period=period)
        
        if not data:
            return jsonify({'error': f'No data available for {symbol}'}), 404
            
        return jsonify(data)
        
    except Exception as e:
        app.logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return jsonify({'error': 'Failed to fetch historical data'}), 500

@app.route('/api/market-data')
def get_market_data():
    """API endpoint to get current market data"""
    with data_lock:
        return jsonify(market_data)

@app.route('/api/ticker-news')
def get_ticker_news():
    """API endpoint to fetch news for a specific ticker with sentiment analysis"""
    ticker = request.args.get('ticker', '').upper()
    
    if not ticker:
        return jsonify({'error': 'Ticker parameter is required'}), 400
    
    try:
        # Fetch news for the specific ticker
        news = data_fetcher.get_ticker_news(ticker)
        
        return jsonify({
            'ticker': ticker,
            'news': news,
            'count': len(news)
        })
        
    except Exception as e:
        app.logger.error(f"Error fetching news for {ticker}: {str(e)}")
        return jsonify({'error': 'Failed to fetch ticker news'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection"""
    print('Client connected')
    # Send current market data to the newly connected client
    with data_lock:
        socketio.emit('market_update', market_data)

@socketio.on('request_initial_data')
def handle_initial_data():
    """Handle initial data request from client"""
    print('Initial data requested by client')
    with data_lock:
        socketio.emit('initial_data', market_data)

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update requests"""
    print('Update requested by client')
    # Fetch fresh data and send update
    try:
        new_data = fetch_market_data()
        with data_lock:
            global market_data
            market_data = new_data
        socketio.emit('market_update', new_data)
    except Exception as e:
        print(f'Error handling update request: {str(e)}')
        with data_lock:
            socketio.emit('market_update', market_data)

# Initialize data and background thread when module is loaded
def initialize_dashboard():
    """Initialize the dashboard with data and background thread"""
    try:
        # Fetch initial data
        logger.info("Fetching initial market data...")
        initial_data = fetch_market_data()
        with data_lock:
            global market_data
            market_data = initial_data
            logger.info(f"Initial data loaded: {len(market_data.get('gainers', []))} gainers, {len(market_data.get('losers', []))} losers")
        
        # Start background thread
        logger.info("Starting background thread...")
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
        logger.info("Dashboard initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing dashboard: {str(e)}")

# Initialize when module is imported
initialize_dashboard()

if __name__ == '__main__':
    try:
        # Run the app
        logger.info("Starting Socket.IO server...")
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=5000, 
                    debug=True, 
                    use_reloader=False,
                    allow_unsafe_werkzeug=True)
        
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

# 📈 Market Movers Dashboard

> **AI-Powered Real-Time Stock Market Analysis with DistilBERT Sentiment Analysis**

A sophisticated web dashboard that tracks stock market movements in real-time and analyzes market sentiment using state-of-the-art AI. Built with Flask, PyTorch, and Hugging Face Transformers.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)
![PyTorch](https://img.shields.io/badge/pytorch-2.2.2-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## ✨ Features

### 📊 Real-Time Stock Data
- **Live Market Updates** - Automatic refresh every 5 minutes
- **Top Gainers & Losers** - Track the biggest movers in the market
- **Price & Volume Data** - Real-time pricing with trading volumes
- **WebSocket Integration** - Instant updates without page reload

### 🤖 AI-Powered Sentiment Analysis
- **DistilBERT Model** - Fine-tuned for financial sentiment analysis
- **Apple MPS Acceleration** - GPU-accelerated inference on Apple Silicon
- **Confidence Scores** - Detailed positive/negative sentiment breakdown
- **Visual Indicators** - Color-coded badges and progress bars
- **Real-Time Analysis** - Every news article analyzed automatically

### 📰 News Integration
- **NewsAPI Integration** - Latest market news from multiple sources
- **Automatic Categorization** - Sentiment-based article classification
- **Source Attribution** - Track news sources and publication dates
- **Direct Links** - Quick access to full articles

### 🎨 Modern UI/UX
- **Responsive Design** - Works on all screen sizes
- **Bootstrap 5** - Clean, professional interface
- **Real-Time Updates** - Live data without page refresh
- **Interactive Charts** - Plotly.js visualizations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- NewsAPI Key ([Get one free](https://newsapi.org/))

### Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd market_movers
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create .env file
cp .env.template .env

# Edit .env and add your NewsAPI key
NEWS_API_KEY=your_newsapi_key_here
```

5. **Run the dashboard**
```bash
python main.py
```

6. **Open in browser**
```
http://localhost:5001
```

---

## 🎯 Usage

### Running the Dashboard

```bash
# Start the server
python main.py

# The dashboard will be available at:
# http://localhost:5001
```

### Testing Sentiment Analysis

```bash
# Test the DistilBERT sentiment analyzer
python testing/test_sentiment.py

# Verify all dashboard features
python testing/verify_dashboard.py
```

### Configuration

Edit `.env` file to customize:

```bash
# NewsAPI Configuration
NEWS_API_KEY=your_api_key_here

# Flask Configuration
FLASK_PORT=5001
FLASK_DEBUG=False

# Tokenizers (for DistilBERT)
TOKENIZERS_PARALLELISM=false

# Stock Tickers to Track
YAHOO_FINANCE_TICKERS=AAPL,MSFT,GOOGL,AMZN,TSLA,META,NVDA,V,JNJ,WMT
```

---

## 🏗️ Architecture

### Project Structure

```
market_movers/
├── data_fetch/              # Data fetching module
│   ├── data_fetcher.py     # Main data fetcher
│   ├── fetch_news.py       # NewsAPI integration
│   └── fetch_prices.py     # Yahoo Finance integration
│
├── data_process/            # Data processing module
│   ├── sentiment_analyzer.py  # DistilBERT sentiment analysis
│   ├── identify_movers.py  # Identify gainers/losers
│   └── routing.py          # Movement categorization
│
├── data_visualization/      # Visualization module
│   ├── simple_dashboard.py # Flask dashboard
│   └── templates/          # HTML templates
│
├── testing/                 # Testing module
│   ├── test_sentiment.py   # Sentiment analyzer tests
│   ├── test_ticker_news.py # Ticker news tests
│   ├── test_live_data.py   # Live data tests
│   └── verify_dashboard.py # Dashboard verification
│
├── main.py                  # Entry point
├── generate_brief.py        # Brief generator
├── agentic_flow.py          # Agent workflow
└── visualize_agentic_flow.py # Workflow visualization
```

### Technology Stack

**Backend:**
- Flask 2.3.3 - Web framework
- Flask-SocketIO 5.3.5 - WebSocket support
- PyTorch 2.2.2 - Deep learning framework
- Transformers 4.57.1 - Hugging Face models

**Data Sources:**
- yfinance 0.2.33 - Stock market data
- newsapi-python 0.2.7 - News articles

**AI/ML:**
- DistilBERT - Sentiment analysis model
- Apple MPS - GPU acceleration (Mac)
- NumPy 1.26.4 - Numerical computing

**Frontend:**
- Bootstrap 5 - UI framework
- Socket.IO - Real-time updates
- Plotly.js - Interactive charts

---

## 🛠️ Development Guide

### Adding New Features

#### 1. New Data Source

Create a new file in `data_fetch/`:

```python
# data_fetch/fetch_crypto.py
class CryptoFetcher:
    def __init__(self):
        self.api_key = os.getenv('CRYPTO_API_KEY')
    
    def fetch_prices(self, symbols):
        # Your implementation
        return data
```

Update `data_fetch/__init__.py`:
```python
from .fetch_crypto import CryptoFetcher
__all__ = [..., 'CryptoFetcher']
```

#### 2. New Processing Logic

Create a new file in `data_process/`:

```python
# data_process/technical_indicators.py
class TechnicalAnalyzer:
    def calculate_rsi(self, prices, period=14):
        # RSI calculation
        return rsi_values
    
    def calculate_macd(self, prices):
        # MACD calculation
        return macd_line, signal_line
```

Update `data_process/__init__.py`:
```python
from .technical_indicators import TechnicalAnalyzer
__all__ = [..., 'TechnicalAnalyzer']
```

#### 3. New Dashboard Route

Add to `data_visualization/simple_dashboard.py`:

```python
@app.route('/api/technical-indicators')
def get_technical_indicators():
    from data_process.technical_indicators import TechnicalAnalyzer
    
    analyzer = TechnicalAnalyzer()
    indicators = analyzer.calculate_rsi(prices)
    
    return jsonify({
        'rsi': indicators,
        'timestamp': datetime.now().isoformat()
    })
```

### Import Guidelines

**Standard Import Pattern:**
```python
# All imports from project root
from data_fetch.data_fetcher import DataFetcher
from data_process.sentiment_analyzer import DistilBERTSentimentAnalyzer
from data_visualization.simple_dashboard import app
```

**For Standalone Scripts:**
```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Then import normally
from data_fetch.data_fetcher import DataFetcher
```

### Module Capabilities

#### 📥 Data Fetch Module
- **Real-time stock prices** - Yahoo Finance API integration
- **Market news** - NewsAPI with sentiment analysis
- **Ticker-specific news** - Fetch news for individual stocks
- **Intelligent caching** - 1-hour TTL to avoid rate limits
- **Rate limit management** - Automatic retry with exponential backoff
- **Error handling** - Graceful fallbacks for API failures

#### ⚙️ Data Process Module
- **Top movers identification** - Automatic detection of gainers/losers
- **Movement categorization** - Classify by earnings, macro, news
- **Performance tracking** - Accuracy, precision, recall, F1 metrics
- **Self-optimization** - Automatic weight adjustment based on performance
- **DistilBERT sentiment** - AI-powered financial sentiment analysis
- **GPU acceleration** - Apple MPS support for faster inference
- **Confidence scoring** - Detailed positive/negative breakdown (0-1 scale)

#### 📊 Data Visualization Module
- **Real-time updates** - WebSocket-based live data (5-minute intervals)
- **Interactive charts** - Plotly.js candlestick visualizations
- **Technical indicators** - Volume, SMA 20, SMA 50, RSI
- **Period selector** - 1D, 5D, 1M, 3M, 1Y views
- **Market health** - Bullish/bearish indicators
- **Sentiment badges** - Color-coded positive/negative/neutral
- **Responsive UI** - Bootstrap 5 mobile-friendly design

### Code Style Guidelines

- **PEP 8** - Follow Python style guide
- **Type hints** - Use for function parameters and returns
- **Docstrings** - Document all classes and functions
- **Error handling** - Use try/except with specific exceptions
- **Logging** - Use Python logging module, not print statements

```python
import logging

logger = logging.getLogger(__name__)

def fetch_data():
    try:
        # Your code
        logger.info("Data fetched successfully")
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise
```

---

## 🤖 AI Sentiment Analysis

### How It Works

1. **Model**: DistilBERT fine-tuned for financial sentiment
   - Lightweight transformer model (66M parameters)
   - Fast inference with high accuracy
   - Optimized for financial text

2. **Hardware Acceleration**:
   - Apple MPS (Metal Performance Shaders) on Mac
   - CPU fallback for other systems
   - Automatic device selection

3. **Analysis Output**:
   - Sentiment label (Positive/Negative/Neutral)
   - Confidence score (0-1)
   - Positive percentage
   - Negative percentage

### Example Output

```python
{
    "sentiment": "positive",
    "sentiment_score": 0.997,
    "positive_score": 0.997,
    "negative_score": 0.003
}
```

---

## 📊 Dashboard Features

### Stock Cards
- **Color-coded cards** - Green for gainers, red for losers
- **Real-time prices** - Updated every 5 minutes
- **Percentage changes** - Visual indicators
- **Trading volumes** - Market activity metrics

### News Section
- **Sentiment badges** - Color-coded (green/red/gray)
- **Confidence scores** - Progress bars showing strength
- **Detailed breakdown** - Positive vs negative percentages
- **Article metadata** - Source, date, and links

### Live Updates
- **WebSocket connection** - Real-time data push
- **Auto-refresh** - Every 5 minutes
- **Status indicators** - Last update timestamp
- **Connection status** - Visual feedback

---

## 🧪 Testing

### Run All Tests

```bash
# Test sentiment analyzer
python testing/test_sentiment.py

# Verify dashboard functionality
python testing/verify_dashboard.py
```

### Expected Output

```
✅ Sentiment Analyzer Test
   - Model loaded successfully
   - Positive sentiment detected: 0.997
   - Negative sentiment detected: 0.978

✅ Dashboard Verification
   - Homepage accessible
   - API endpoints working
   - Stock data fetching
   - News sentiment analysis active
```

---

## 🔧 Troubleshooting

### NumPy Compatibility Issue

**Problem**: "Numpy is not available" error

**Solution**: 
```bash
# NumPy 1.26.4 is required for PyTorch 2.2.2
pip install "numpy==1.26.4" --force-reinstall
```

**Important**: Do not upgrade to NumPy 2.x - it's incompatible with PyTorch 2.2.2

### Port Already in Use

**Problem**: Port 5001 is busy

**Solution**:
```bash
# Kill existing process
lsof -ti:5001 | xargs kill -9

# Restart server
python main.py
```

### Sentiment Analysis Not Working

**Problem**: Sentiment scores showing as None

**Solution**:
```bash
# Test sentiment analyzer
python testing/test_sentiment.py

# Check PyTorch and NumPy versions
pip list | grep -E "(numpy|torch)"
```

### News Not Loading

**Problem**: No news articles appearing

**Solution**:
- Verify NewsAPI key in `.env`
- Check API quota (free tier: 100 requests/day)
- Ensure internet connection is active

---

## 📈 Performance

- **Response Time**: < 1 second for API calls
- **Update Frequency**: Every 5 minutes
- **Sentiment Analysis**: ~100ms per article (with MPS)
- **Concurrent Users**: Supports multiple WebSocket connections

---

## 📊 Performance Metrics & Evaluation System

### Overview

The system includes an **automatic evaluation system** that tracks prediction accuracy and continuously improves over time. Starting from Day 2, the system evaluates previous day's predictions against actual market movements.

### Metrics Tracked

| Metric | Description | Formula | Good Score |
|--------|-------------|---------|------------|
| **Accuracy** | Overall correctness of predictions | Correct / Total | > 70% |
| **Precision** | Correct predictions / Total predictions | TP / (TP + FP) | > 75% |
| **Recall** | Predicted moves / Actual moves | TP / (TP + FN) | > 65% |
| **F1 Score** | Balance of precision & recall | 2 * (P * R) / (P + R) | > 70% |

### Output Structure

#### Brief JSON with Evaluation Metrics

```json
{
  "metadata": {
    "generated_at": "2025-10-17T18:55:00.123456",
    "date": "2025-10-17",
    "version": "3.1",
    "evaluation_enabled": true
  },
  "market_overview": {
    "market_health": "bullish",
    "total_gainers": 6,
    "total_losers": 3,
    "advance_decline_ratio": 0.67,
    "biggest_gainer": {
      "symbol": "NVDA",
      "price": 182.5,
      "change": 3.45,
      "volume": 180000000
    },
    "biggest_loser": {
      "symbol": "V",
      "price": 335.4,
      "change": -2.78,
      "volume": 6231200
    }
  },
  "top_gainers": [
    {
      "rank": 1,
      "symbol": "NVDA",
      "price": 182.5,
      "change_percent": 3.45,
      "volume": 180000000,
      "sector": "Technology",
      "type": "gainer"
    }
  ],
  "top_losers": [
    {
      "rank": 1,
      "symbol": "V",
      "price": 335.4,
      "change_percent": -2.78,
      "volume": 6231200,
      "sector": "Financial Services",
      "type": "loser"
    }
  ],
  "news_analysis": {
    "total_articles": 5,
    "sentiment_distribution": {
      "positive": 3,
      "negative": 2,
      "neutral": 0
    },
    "articles": [
      {
        "title": "NVIDIA Announces New AI Chip",
        "source": "TechCrunch",
        "published_at": "2025-10-17T10:30:00Z",
        "url": "https://...",
        "sentiment": "positive",
        "sentiment_score": 0.987,
        "positive_score": 0.987,
        "negative_score": 0.013
      }
    ]
  },
  "sector_analysis": {
    "sector_performance": {
      "Technology": {
        "gainers": 4,
        "losers": 2
      },
      "Financial Services": {
        "gainers": 0,
        "losers": 2
      }
    }
  },
  "key_insights": [
    "Market shows bullish sentiment with 6/9 stocks advancing",
    "NVDA led with +3.45%"
  ],
  "recommendations": [
    "✅ Bullish market - Consider long positions"
  ],
  "evaluation": {
    "previous_date": "2025-10-16",
    "current_metrics": {
      "accuracy": 0.778,
      "precision": 0.850,
      "recall": 0.700,
      "f1_score": 0.768
    },
    "historical_performance": {
      "metrics": {
        "accuracy": 0.735,
        "precision": 0.790,
        "recall": 0.690,
        "f1_score": 0.737
      },
      "sample_size": 45,
      "current_weights": {
        "earnings": 1.2,
        "macro": 1.0,
        "news": 0.85,
        "unknown": 0.3
      }
    },
    "predictions_evaluated": 9,
    "correct_predictions": 7
  }
}
```

### Console Output with Metrics

```bash
$ python generate_brief.py

======================================================================
📊 MARKET MOVERS DAILY BRIEF GENERATOR
======================================================================

INFO:__main__:Evaluator initialized for performance tracking
INFO:__main__:Starting Daily Market Brief Generation
INFO:__main__:Fetching market data...
INFO:data_fetch.data_fetcher:Found 6 gainers and 3 losers
INFO:data_fetch.data_fetcher:Fetching news for tickers ['NVDA', 'GOOGL', 'AMZN', 'V', 'JPM']
INFO:data_fetch.data_fetcher:Found 5 relevant articles after filtering

INFO:__main__:✅ Evaluation complete
INFO:__main__:   Accuracy: 77.8%
INFO:__main__:   Precision: 85.0%
INFO:__main__:   Recall: 70.0%
INFO:__main__:📊 Previous predictions accuracy: 77.8%

INFO:__main__:Saving outputs...
INFO:__main__:✅ Saved: output/market_brief_2025-10-17.json
INFO:__main__:✅ Saved: output/market_brief_2025-10-17.md
INFO:__main__:✅ Saved: output/movers_2025-10-17.csv
INFO:__main__:Brief generation complete!

======================================================================
📋 BRIEF SUMMARY
======================================================================

🎯 Market Health: BULLISH
📈 Gainers: 6
📉 Losers: 3

📊 Performance Metrics (Yesterday's Predictions):
   • Accuracy: 77.8%
   • Precision: 85.0%
   • Recall: 70.0%
   • F1 Score: 76.8%
   • Trend: 📈 Improving (Historical avg: 73.5%)

🚀 Top 3 Gainers:
   1. NVDA - $182.5 (+3.45%)
   2. GOOGL - $251.46 (+2.15%)
   3. AMZN - $214.47 (+1.82%)

📉 Top 3 Losers:
   1. V - $335.4 (-2.78%)
   2. JPM - $298.54 (-2.23%)
   3. TSLA - $428.75 (-1.38%)

💡 Key Insights:
   • Market shows bullish sentiment with 6/9 stocks advancing
   • NVDA led with +3.45%

🎯 Recommendations:
   • ✅ Bullish market - Consider long positions

======================================================================
✅ Brief generation complete! Check ./output/ for files.
======================================================================
```

### Evaluation Data Files

```
output/
├── market_brief_2025-10-17.json    # Today's brief with evaluation
├── market_brief_2025-10-16.json    # Yesterday's brief (used for eval)
├── movers_2025-10-17.csv           # CSV export
└── eval_data/                       # Evaluation tracking
    ├── evaluation_history.json      # Last 100 evaluations
    └── performance_metrics.json     # Running averages
```

#### Evaluation History Format

```json
[
  {
    "timestamp": "2025-10-17T18:55:00.123456",
    "true_positives": 7,
    "false_positives": 2,
    "false_negatives": 0,
    "accuracy": 0.778,
    "precision": 0.778,
    "recall": 1.0,
    "f1_score": 0.875,
    "details": [
      {
        "ticker": "NVDA",
        "predicted_move": 3.45,
        "actual_move": 2.89,
        "category": "news",
        "correct_direction": true,
        "reasons": [
          {
            "headline": "Predicted as top gainer",
            "source": "System"
          }
        ]
      }
    ]
  }
]
```

#### Performance Metrics Format

```json
{
  "accuracy": {
    "value": 0.735,
    "count": 45
  },
  "precision": {
    "value": 0.790,
    "count": 45
  },
  "recall": {
    "value": 0.690,
    "count": 45
  },
  "f1_score": {
    "value": 0.737,
    "count": 45
  }
}
```

### How Evaluation Works

#### Day 1 (Baseline):
```
1. Generate brief with predictions
2. Save to output/market_brief_2025-10-17.json
3. No evaluation (no previous data)
```

#### Day 2 (First Evaluation):
```
1. Load Day 1 predictions from output/market_brief_2025-10-16.json
2. Fetch today's actual movements
3. Compare predictions vs actuals
4. Calculate accuracy, precision, recall, F1
5. Optimize weights based on performance
6. Save evaluation to eval_data/evaluation_history.json
7. Generate today's brief with evaluation metrics
```

#### Day 3+ (Continuous Learning):
```
1. Evaluate previous day
2. Track performance trends
3. Optimize weights automatically
4. System improves over time
```

### Expected Performance Trends

| Period | Accuracy | Notes |
|--------|----------|-------|
| **Week 1** | 65-70% | Baseline, learning patterns |
| **Week 2-4** | 75-80% | Weights optimized, patterns recognized |
| **Month 2+** | 80-85% | Mature predictions, consistent performance |

### Configuration

```python
# Enable evaluation (default)
agent = MarketBriefAgent(enable_evaluation=True)

# Disable evaluation
agent = MarketBriefAgent(enable_evaluation=False)

# Skip one evaluation
agent = MarketBriefAgent()
brief = agent.generate_daily_brief(evaluate_previous=False)
```

### API Access to Metrics

```python
from generate_brief import MarketBriefAgent

# Generate brief
agent = MarketBriefAgent()
brief = agent.generate_daily_brief()

# Access evaluation metrics
if 'evaluation' in brief:
    metrics = brief['evaluation']['current_metrics']
    print(f"Accuracy: {metrics['accuracy']:.1%}")
    print(f"Precision: {metrics['precision']:.1%}")
    print(f"Recall: {metrics['recall']:.1%}")
    print(f"F1 Score: {metrics['f1_score']:.1%}")
    
    # Historical performance
    historical = brief['evaluation']['historical_performance']
    print(f"Historical Average: {historical['metrics']['accuracy']:.1%}")
    print(f"Sample Size: {historical['sample_size']} days")
```

---

## 🔐 Security

- API keys stored in `.env` (not in version control)
- Environment variables loaded securely
- No sensitive data exposed in frontend
- CORS configured for localhost

---

## 🛣️ Roadmap

### Planned Features
- [ ] Historical price charts
- [ ] Portfolio tracking
- [ ] Email/SMS alerts
- [ ] Technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Multi-language support
- [ ] User authentication
- [ ] Customizable watchlists
- [ ] Export to CSV/Excel

---

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_SUCCESS.md) - Production deployment
- [Agentic Workflow v3.1](AGENTIC_WORKFLOW_V3.1.md) - Complete workflow with evaluator
- [Evaluation Feature](EVALUATION_FEATURE.md) - Performance tracking guide
- [Brief Generation Guide](BRIEF_GENERATION_GUIDE.md) - Daily brief generation
- [Ticker News Feature](TICKER_NEWS_FEATURE.md) - Ticker-specific news
- [API Documentation](docs/api.md) - REST API reference (coming soon)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Hugging Face** - For the Transformers library and DistilBERT model
- **NewsAPI** - For providing news data
- **Yahoo Finance** - For stock market data
- **Flask Team** - For the excellent web framework

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check [Troubleshooting](#-troubleshooting) section
- Review [Documentation](#-documentation)

---

**Built with ❤️ using Flask, PyTorch, and DistilBERT**

**Last Updated**: October 17, 2025  
**Version**: 3.1 (AI-Powered with Continuous Learning)

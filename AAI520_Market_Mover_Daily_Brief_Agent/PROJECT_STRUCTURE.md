# Market Movers Dashboard - Project Structure

## 📁 Project Organization

The project has been restructured into four main modules:

```
Module3 - NLP with Gen AI project/
│
├── data_fetch/              # 📥 Data Fetching Module
│   ├── __init__.py
│   ├── data_fetcher.py     # Main data fetcher class
│   ├── fetch_news.py       # NewsAPI integration
│   └── fetch_prices.py     # Yahoo Finance integration
│
├── data_process/            # ⚙️ Data Processing Module
│   ├── __init__.py
│   ├── identify_movers.py  # Identify top gainers/losers
│   ├── routing.py          # Route movements by category
│   └── evaluator.py        # Evaluate and optimize routing
│
├── data_visualization/      # 📊 Visualization Module
│   ├── __init__.py
│   ├── simple_dashboard.py # Main dashboard application
│   ├── dashboard.py        # Alternative dashboard
│   ├── summarize.py        # Generate market summaries
│   ├── templates/          # HTML templates
│   │   ├── simple_dashboard.html
│   │   └── index.html
│   └── static/             # CSS, JS, images
│       ├── css/
│       ├── js/
│       └── images/
│
├── testing/                 # 🧪 Testing Module
│   ├── __init__.py
│   ├── test_live_data.py   # Test live data integration
│   └── run_agent.py        # Run the full agent pipeline
│
├── data/                    # 💾 Data Storage
│   └── (raw/processed data files)
│
├── output/                  # 📄 Output Files
│   └── (generated reports and summaries)
│
├── main.py                  # 🚀 Main Entry Point
├── requirements.txt         # 📦 Python Dependencies
├── .env                     # 🔐 Environment Variables
├── .env.template            # 📝 Environment Template
├── Readme.md                # 📖 Project README
└── PROJECT_STRUCTURE.md     # 📋 This file

```

## 🚀 Quick Start

### Running the Dashboard

```bash
# From project root
python main.py
```

The dashboard will be available at:
- http://localhost:5000
- http://127.0.0.1:5000

### Running from Module Directory

```bash
# From data_visualization directory
cd data_visualization
python simple_dashboard.py
```

### Running the Agent

```bash
# From testing directory
cd testing
python run_agent.py
```

## 📦 Module Details

### 1. Data Fetch Module (`data_fetch/`)

**Purpose:** Fetch real-time market data and news

**Files:**
- `data_fetcher.py` - Main class combining all data sources
- `fetch_news.py` - Fetch news from NewsAPI
- `fetch_prices.py` - Fetch stock prices from Yahoo Finance

**Key Features:**
- Real-time stock price data
- Market news with sentiment analysis
- Caching to avoid API rate limits
- Error handling and fallback mechanisms

### 2. Data Process Module (`data_process/`)

**Purpose:** Analyze and categorize market movements

**Files:**
- `identify_movers.py` - Identify significant gainers and losers
- `routing.py` - Route movements by category (earnings, macro, news)
- `evaluator.py` - Evaluate routing accuracy and optimize

**Key Features:**
- Top 10 gainers and losers identification
- Movement categorization
- Performance metrics
- Self-optimization

### 3. Data Visualization Module (`data_visualization/`)

**Purpose:** Present data through interactive dashboards

**Files:**
- `simple_dashboard.py` - Main Flask dashboard
- `dashboard.py` - Alternative advanced dashboard
- `summarize.py` - Generate market summaries
- `templates/` - HTML templates
- `static/` - Frontend assets

**Key Features:**
- Real-time WebSocket updates
- Interactive candlestick charts (Plotly.js)
- Period selector (1D, 5D, 1M, 3M, 1Y)
- Toggle indicators (Volume, SMA 20, SMA 50, RSI)
- Market health indicator
- Latest news with sentiment

### 4. Testing Module (`testing/`)

**Purpose:** Test and validate system components

**Files:**
- `test_live_data.py` - Test live API integrations
- `run_agent.py` - Run complete agent pipeline

**Key Features:**
- API connectivity tests
- End-to-end workflow testing
- Performance benchmarking

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Yahoo Finance Configuration
YAHOO_FINANCE_TICKERS=AAPL,MSFT,GOOGL,AMZN,...

# NewsAPI Configuration
NEWSAPI_API_KEY=your_api_key_here
NEWS_API_PAGE_SIZE=5

# Logging
LOG_LEVEL=INFO

# Output
OUTPUT_DIR=./output
```

## 📊 Dashboard Features

### Real-time Data
- Updates every 5 minutes via WebSocket
- Manual refresh button available

### Stock Charts
- Candlestick visualization
- Volume bars
- Technical indicators (SMA 20, SMA 50, RSI)
- Multiple time periods

### Market Overview
- Top 10 Gainers (sorted by % gain)
- Top 10 Losers (sorted by % loss)
- Market health indicator
- Latest market news

## 🛠️ Development

### Adding New Features

1. **New Data Source:**
   - Add file to `data_fetch/`
   - Update `data_fetch/__init__.py`

2. **New Processing Logic:**
   - Add file to `data_process/`
   - Update `data_process/__init__.py`

3. **New Visualization:**
   - Add template to `data_visualization/templates/`
   - Add route in `simple_dashboard.py`

### Import Guidelines

All modules use relative imports from project root:

```python
from data_fetch.data_fetcher import DataFetcher
from data_process.identify_movers import MoverAnalyzer
from data_visualization.summarize import MarketBriefGenerator
```

Each file adds project root to `sys.path`:

```python
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

## 📝 Dependencies

See `requirements.txt` for complete list. Key dependencies:
- Flask & Flask-SocketIO (Web framework)
- yfinance (Stock data)
- newsapi-python (News data)
- pandas & numpy (Data processing)
- plotly (Interactive charts)
- scikit-learn & nltk (ML & NLP)

## 🔒 Security

- API keys stored in `.env` (not committed to git)
- `.env.template` provided for reference
- CORS enabled for WebSocket (localhost only recommended for production)

## 📈 Performance

- News caching (1 hour TTL)
- Batch stock data fetching
- WebSocket for real-time updates
- Background thread for data updates

## 🐛 Troubleshooting

### Import Errors
- Ensure project root is in `PYTHONPATH`
- Run from `main.py` or include path setup in script

### API Errors
- Check `.env` file configuration
- Verify API keys are valid
- Check rate limits

### Chart Not Loading
- Verify Plotly.js CDN is accessible
- Check browser console for errors
- Ensure WebSocket connection is established

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Yahoo Finance API](https://python-yahoofinance.readthedocs.io/)
- [NewsAPI Documentation](https://newsapi.org/docs)
- [Plotly.js Documentation](https://plotly.com/javascript/)

---

**Last Updated:** October 16, 2025
**Version:** 2.0 (Restructured)

# Market Movers Daily Brief Agent

## Overview
The **Market Movers Daily Brief Agent** automatically generates a daily summary of top stock price movements and their likely drivers (earnings, macroeconomic news, or other events).  
It integrates **Yahoo Finance** for stock data and **NewsAPI** (or similar sources) for market news.  

**Workflow:**
1. Fetch daily stock price data.
2. Identify top gainers and losers.
3. Retrieve related news.
4. Route price movements:
   - Earnings-driven → earnings agent
   - Macro-driven → macro agent
   - Other → noise filter
5. Summarize insights into a structured daily brief.
6. Evaluator validates reasons against actual market commentary.

The agent can run in two modes:
- **Demo mode**: Uses mock data (no API keys required).
- **Live mode**: Uses real-time APIs (requires API keys).

---

## Repository Structure
market-movers-agent/
│
├── data/ # Mock data for demo runs
│ ├── mock_prices.csv
│ └── mock_news.json
│
├── output/ # Generated daily briefs
│
├── fetch_prices.py # Fetches stock prices
├── identify_movers.py # Identifies top movers
├── fetch_news.py # Retrieves related news
├── route_news.py # Routes articles (earnings/macro/other)
├── summarize.py # Summarizes reasons
├── evaluator.py # Evaluates reason vs consensus
├── run_agent.py # Main orchestrator (entrypoint)
│
├── requirements.txt # Python dependencies
├── .env.template # Environment variable template
└── README.md # Documentation


---

## Virtual Environment Setup

### 1. Clone the Repository
```bash
git clone <repo-url>
cd market-movers-agent

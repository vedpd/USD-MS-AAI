#!/usr/bin/env python3
"""
Market Movers Agentic Flow Definition
Defines the complete workflow graph for the Market Movers Daily Brief Agent
"""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import operator


# Define the state that flows through the graph
class MarketMoversState(TypedDict):
    """State object that flows through the agent workflow"""
    # Input
    date: str
    tickers: list[str]
    
    # Data collection
    stock_data: dict
    gainers: list[dict]
    losers: list[dict]
    
    # News & sentiment
    news_articles: list[dict]
    sentiment_analysis: dict
    
    # Analysis
    market_health: str
    sector_analysis: dict
    
    # Output
    brief_data: dict
    insights: list[str]
    recommendations: list[str]
    
    # Control flow
    tasks_completed: Annotated[list[str], operator.add]
    needs_refinement: bool
    iteration_count: int


# ============================================================================
# AGENT NODES
# ============================================================================

def data_fetcher_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Data Fetcher
    Fetches real-time stock data from Yahoo Finance
    """
    from data_fetch.data_fetcher import DataFetcher
    
    print("🔄 [Data Fetcher Agent] Fetching stock market data...")
    
    fetcher = DataFetcher()
    gainers, losers = fetcher.get_stock_data()
    
    state['gainers'] = gainers
    state['losers'] = losers
    state['stock_data'] = {
        'gainers': gainers,
        'losers': losers,
        'total_movers': len(gainers) + len(losers)
    }
    state['tasks_completed'].append('fetch_stock_data')
    
    print(f"✅ [Data Fetcher Agent] Found {len(gainers)} gainers, {len(losers)} losers")
    return state


def market_analyzer_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Market Analyzer
    Analyzes market health and identifies top movers
    """
    from data_fetch.data_fetcher import DataFetcher
    
    print("🔄 [Market Analyzer Agent] Analyzing market conditions...")
    
    fetcher = DataFetcher()
    gainers = state['gainers']
    losers = state['losers']
    
    # Calculate market health
    market_health = fetcher.get_market_health(gainers, losers)
    
    # Identify top movers for news fetching
    top_tickers = []
    if gainers:
        top_tickers.extend([g['symbol'] for g in gainers[:3]])
    if losers:
        top_tickers.extend([l['symbol'] for l in losers[:2]])
    
    state['market_health'] = market_health
    state['tickers'] = top_tickers
    state['tasks_completed'].append('analyze_market')
    
    print(f"✅ [Market Analyzer Agent] Market health: {market_health.upper()}")
    print(f"   Top movers to track: {', '.join(top_tickers)}")
    return state


def news_router_agent(state: MarketMoversState) -> Literal['fetch_news', 'skip_news']:
    """
    Router: News Decision
    Decides whether to fetch news based on available tickers
    """
    print("🔀 [News Router] Checking if news fetching is needed...")
    
    if state.get('tickers') and len(state['tickers']) > 0:
        print("✅ [News Router] Routing to news fetcher")
        return 'fetch_news'
    else:
        print("⚠️  [News Router] No tickers available, skipping news")
        return 'skip_news'


def news_fetcher_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: News Fetcher
    Fetches ticker-specific news from NewsAPI
    """
    from data_fetch.data_fetcher import DataFetcher
    
    print("🔄 [News Fetcher Agent] Fetching news for top movers...")
    
    fetcher = DataFetcher()
    tickers = state['tickers']
    
    # Fetch news for specific tickers
    news = fetcher.get_news(tickers=tickers)
    
    state['news_articles'] = news
    state['tasks_completed'].append('fetch_news')
    
    print(f"✅ [News Fetcher Agent] Retrieved {len(news)} articles")
    return state


def sentiment_analyzer_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Sentiment Analyzer
    Analyzes news sentiment using DistilBERT AI model
    """
    print("🔄 [Sentiment Analyzer Agent] Analyzing news sentiment with DistilBERT...")
    
    news = state.get('news_articles', [])
    
    if not news:
        print("⚠️  [Sentiment Analyzer Agent] No news to analyze")
        state['sentiment_analysis'] = {
            'total_articles': 0,
            'sentiment_distribution': {}
        }
        return state
    
    # Count sentiments (already analyzed by DistilBERT in news fetcher)
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    for article in news:
        sentiment = article.get('sentiment', 'neutral')
        sentiment_counts[sentiment] += 1
    
    avg_sentiment = sum(a.get('sentiment_score', 0) for a in news) / len(news)
    
    state['sentiment_analysis'] = {
        'total_articles': len(news),
        'sentiment_distribution': sentiment_counts,
        'average_sentiment': avg_sentiment
    }
    state['tasks_completed'].append('analyze_sentiment')
    
    print(f"✅ [Sentiment Analyzer Agent] Sentiment: {sentiment_counts}")
    return state


def sector_analyzer_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Sector Analyzer
    Analyzes performance by market sector
    """
    print("🔄 [Sector Analyzer Agent] Analyzing sector performance...")
    
    sector_map = {
        'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology',
        'AMZN': 'Consumer Cyclical', 'META': 'Technology', 'TSLA': 'Consumer Cyclical',
        'NVDA': 'Technology', 'JPM': 'Financial Services', 'V': 'Financial Services',
        'JNJ': 'Healthcare', 'WMT': 'Consumer Defensive'
    }
    
    sector_perf = {}
    for mover in state['gainers'] + state['losers']:
        sector = sector_map.get(mover['symbol'], 'Other')
        if sector not in sector_perf:
            sector_perf[sector] = {'gainers': 0, 'losers': 0}
        
        if mover in state['gainers']:
            sector_perf[sector]['gainers'] += 1
        else:
            sector_perf[sector]['losers'] += 1
    
    state['sector_analysis'] = sector_perf
    state['tasks_completed'].append('analyze_sectors')
    
    print(f"✅ [Sector Analyzer Agent] Analyzed {len(sector_perf)} sectors")
    return state


def insight_generator_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Insight Generator
    Generates key insights from all collected data
    """
    print("🔄 [Insight Generator Agent] Generating market insights...")
    
    insights = []
    
    # Market breadth insight
    total = len(state['gainers']) + len(state['losers'])
    if total > 0:
        gainer_pct = (len(state['gainers']) / total) * 100
        insights.append(
            f"Market breadth shows {gainer_pct:.1f}% advancing, "
            f"indicating {state['market_health']} sentiment"
        )
    
    # Top mover insights
    if state['gainers']:
        top = max(state['gainers'], key=lambda x: x['change'])
        insights.append(f"{top['symbol']} led gainers with +{top['change']:.2f}%")
    
    if state['losers']:
        top = min(state['losers'], key=lambda x: x['change'])
        insights.append(f"{top['symbol']} biggest loser at {top['change']:.2f}%")
    
    # News sentiment insight
    sentiment = state.get('sentiment_analysis', {})
    if sentiment.get('total_articles', 0) > 0:
        dist = sentiment['sentiment_distribution']
        if dist.get('positive', 0) > dist.get('negative', 0):
            insights.append("News sentiment predominantly positive")
        elif dist.get('negative', 0) > dist.get('positive', 0):
            insights.append("News sentiment predominantly negative")
    
    state['insights'] = insights
    state['tasks_completed'].append('generate_insights')
    
    print(f"✅ [Insight Generator Agent] Generated {len(insights)} insights")
    return state


def recommendation_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Recommendation Generator
    Generates actionable recommendations
    """
    print("🔄 [Recommendation Agent] Generating recommendations...")
    
    recommendations = []
    market_health = state['market_health']
    
    # Market-based recommendations
    if market_health == 'bullish':
        recommendations.append("✅ Bullish market - Consider maintaining long positions")
    elif market_health == 'bearish':
        recommendations.append("⚠️ Bearish market - Exercise caution and defensive positioning")
    else:
        recommendations.append("➖ Neutral market - Wait for clearer directional signals")
    
    # Volatility recommendation
    if state['gainers'] and state['losers']:
        avg_change = sum(abs(g['change']) for g in state['gainers'][:5]) / 5
        if avg_change > 3:
            recommendations.append("⚡ High volatility - Consider tighter stop-losses")
    
    state['recommendations'] = recommendations
    state['tasks_completed'].append('generate_recommendations')
    
    print(f"✅ [Recommendation Agent] Generated {len(recommendations)} recommendations")
    return state


def brief_compiler_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Brief Compiler
    Compiles all data into structured brief
    """
    from datetime import datetime
    
    print("🔄 [Brief Compiler Agent] Compiling final brief...")
    
    brief = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'date': state.get('date', datetime.now().strftime('%Y-%m-%d')),
            'version': '3.0'
        },
        'market_overview': {
            'market_health': state['market_health'],
            'total_gainers': len(state['gainers']),
            'total_losers': len(state['losers'])
        },
        'top_gainers': state['gainers'][:10],
        'top_losers': state['losers'][:10],
        'news_analysis': state.get('sentiment_analysis', {}),
        'sector_analysis': state.get('sector_analysis', {}),
        'key_insights': state.get('insights', []),
        'recommendations': state.get('recommendations', [])
    }
    
    state['brief_data'] = brief
    state['tasks_completed'].append('compile_brief')
    
    print("✅ [Brief Compiler Agent] Brief compiled successfully")
    return state


def quality_evaluator_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Quality Evaluator
    Evaluates brief quality and decides if refinement needed
    """
    print("🔄 [Quality Evaluator Agent] Evaluating brief quality...")
    
    brief = state['brief_data']
    needs_refinement = False
    
    # Check if we have sufficient data
    if len(state['gainers']) + len(state['losers']) < 3:
        print("⚠️  [Quality Evaluator] Insufficient market data")
        needs_refinement = True
    
    # Check if we have insights
    if len(state.get('insights', [])) < 2:
        print("⚠️  [Quality Evaluator] Insufficient insights")
        needs_refinement = True
    
    # Check iteration count (max 2 refinements)
    if state.get('iteration_count', 0) >= 2:
        needs_refinement = False
        print("ℹ️  [Quality Evaluator] Max iterations reached, proceeding")
    
    state['needs_refinement'] = needs_refinement
    state['iteration_count'] = state.get('iteration_count', 0) + 1
    
    if needs_refinement:
        print("🔄 [Quality Evaluator] Refinement needed")
    else:
        print("✅ [Quality Evaluator] Quality acceptable, proceeding to output")
    
    return state


def evaluation_router(state: MarketMoversState) -> Literal['refine', 'output']:
    """
    Router: Quality Decision
    Routes to refinement or output based on quality evaluation
    """
    if state.get('needs_refinement', False):
        print("🔀 [Evaluation Router] Routing to refinement")
        return 'refine'
    else:
        print("🔀 [Evaluation Router] Routing to output")
        return 'output'


def output_generator_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Output Generator
    Saves brief in multiple formats (JSON, Markdown, CSV)
    """
    from generate_brief import MarketBriefAgent
    from datetime import datetime
    
    print("🔄 [Output Generator Agent] Generating output files...")
    
    agent = MarketBriefAgent()
    date_str = state.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Save in all formats
    agent._save_all_formats(state['brief_data'], date_str)
    
    state['tasks_completed'].append('generate_output')
    
    print("✅ [Output Generator Agent] All output files saved")
    return state


def finalize_agent(state: MarketMoversState) -> MarketMoversState:
    """
    Agent: Finalizer
    Final processing and cleanup
    """
    print("🔄 [Finalizer Agent] Finalizing workflow...")
    print(f"✅ [Finalizer Agent] Completed tasks: {', '.join(state['tasks_completed'])}")
    print("🎉 [Finalizer Agent] Market Movers Brief Generation Complete!")
    return state


# ============================================================================
# BUILD THE AGENTIC WORKFLOW GRAPH
# ============================================================================

def build_market_movers_graph():
    """
    Build the complete agentic workflow graph for Market Movers
    """
    # Initialize the graph
    workflow = StateGraph(MarketMoversState)
    
    # ========================================================================
    # ADD NODES (Agents)
    # ========================================================================
    
    workflow.add_node('data_fetcher', data_fetcher_agent)
    workflow.add_node('market_analyzer', market_analyzer_agent)
    workflow.add_node('news_router', news_router_agent)
    workflow.add_node('news_fetcher', news_fetcher_agent)
    workflow.add_node('sentiment_analyzer', sentiment_analyzer_agent)
    workflow.add_node('sector_analyzer', sector_analyzer_agent)
    workflow.add_node('insight_generator', insight_generator_agent)
    workflow.add_node('recommendation_agent', recommendation_agent)
    workflow.add_node('brief_compiler', brief_compiler_agent)
    workflow.add_node('quality_evaluator', quality_evaluator_agent)
    workflow.add_node('output_generator', output_generator_agent)
    workflow.add_node('finalizer', finalize_agent)
    
    # ========================================================================
    # SET ENTRY POINT
    # ========================================================================
    
    workflow.set_entry_point('data_fetcher')
    
    # ========================================================================
    # ADD EDGES (Sequential Flow)
    # ========================================================================
    
    # Main sequential flow
    workflow.add_edge('data_fetcher', 'market_analyzer')
    workflow.add_edge('market_analyzer', 'news_router')
    
    # ========================================================================
    # ADD CONDITIONAL EDGES (Routing Logic)
    # ========================================================================
    
    # News routing decision
    workflow.add_conditional_edges(
        'news_router',
        news_router_agent,
        {
            'fetch_news': 'news_fetcher',
            'skip_news': 'sentiment_analyzer'
        }
    )
    
    # After news fetching, continue to sentiment analysis
    workflow.add_edge('news_fetcher', 'sentiment_analyzer')
    
    # Continue sequential flow after sentiment analysis
    workflow.add_edge('sentiment_analyzer', 'sector_analyzer')
    workflow.add_edge('sector_analyzer', 'insight_generator')
    workflow.add_edge('insight_generator', 'recommendation_agent')
    workflow.add_edge('recommendation_agent', 'brief_compiler')
    workflow.add_edge('brief_compiler', 'quality_evaluator')
    
    # Quality evaluation routing
    workflow.add_conditional_edges(
        'quality_evaluator',
        evaluation_router,
        {
            'refine': 'insight_generator',  # Loop back for refinement
            'output': 'output_generator'     # Proceed to output
        }
    )
    
    # Final steps
    workflow.add_edge('output_generator', 'finalizer')
    workflow.add_edge('finalizer', END)
    
    # ========================================================================
    # COMPILE THE GRAPH
    # ========================================================================
    
    app = workflow.compile()
    
    return app


# ============================================================================
# VISUALIZATION
# ============================================================================

def visualize_graph():
    """
    Generate a visual representation of the workflow graph
    """
    print("\n" + "=" * 80)
    print("MARKET MOVERS AGENTIC WORKFLOW GRAPH")
    print("=" * 80 + "\n")
    
    print("📊 WORKFLOW STRUCTURE:\n")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                         ENTRY POINT                                  │")
    print("│                      [Data Fetcher Agent]                            │")
    print("│                  Fetches stock market data                           │")
    print("└────────────────────────┬────────────────────────────────────────────┘")
    print("                         │")
    print("                         ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                   [Market Analyzer Agent]                            │")
    print("│              Analyzes market health & top movers                     │")
    print("└────────────────────────┬────────────────────────────────────────────┘")
    print("                         │")
    print("                         ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                     [News Router] 🔀                                 │")
    print("│                  Decision: Fetch news?                               │")
    print("└─────────┬───────────────────────────────────────────┬───────────────┘")
    print("          │ YES                                       │ NO")
    print("          ▼                                           ▼")
    print("┌──────────────────────┐                   ┌──────────────────────────┐")
    print("│ [News Fetcher Agent] │                   │  [Skip to Sentiment]     │")
    print("│ Fetches ticker news  │                   │                          │")
    print("└──────────┬───────────┘                   └────────────┬─────────────┘")
    print("           │                                            │")
    print("           └────────────────────┬───────────────────────┘")
    print("                                ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                [Sentiment Analyzer Agent] 🤖                         │")
    print("│           AI-powered sentiment analysis (DistilBERT)                 │")
    print("└────────────────────────┬────────────────────────────────────────────┘")
    print("                         │")
    print("                         ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                  [Sector Analyzer Agent]                             │")
    print("│                Analyzes sector performance                           │")
    print("└────────────────────────┬────────────────────────────────────────────┘")
    print("                         │")
    print("                         ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                 [Insight Generator Agent] 💡                         │")
    print("│                  Generates key insights                              │")
    print("└────────────────────────┬────────────────────────────────────────────┘")
    print("                         │")
    print("                         ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                [Recommendation Agent] 🎯                             │")
    print("│              Generates actionable recommendations                    │")
    print("└────────────────────────┬────────────────────────────────────────────┘")
    print("                         │")
    print("                         ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                  [Brief Compiler Agent]                              │")
    print("│              Compiles all data into brief                            │")
    print("└────────────────────────┬────────────────────────────────────────────┘")
    print("                         │")
    print("                         ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                [Quality Evaluator Agent] ✓                           │")
    print("│                 Evaluates brief quality                              │")
    print("└─────────┬───────────────────────────────────────────┬───────────────┘")
    print("          │ NEEDS REFINEMENT                          │ QUALITY OK")
    print("          │ (Loop back)                               │")
    print("          ▼                                           ▼")
    print("    ┌─────────────┐                         ┌──────────────────────┐")
    print("    │   REFINE    │                         │ [Output Generator]   │")
    print("    │ (Max 2x)    │                         │ Saves JSON/MD/CSV    │")
    print("    └──────┬──────┘                         └──────────┬───────────┘")
    print("           │                                           │")
    print("           └──────────► [Insight Generator]            │")
    print("                                                       ▼")
    print("                                           ┌──────────────────────┐")
    print("                                           │   [Finalizer Agent]  │")
    print("                                           │   Cleanup & Summary  │")
    print("                                           └──────────┬───────────┘")
    print("                                                      │")
    print("                                                      ▼")
    print("                                                    [END]")
    print("\n" + "=" * 80)
    print("AGENT TYPES:")
    print("=" * 80)
    print("🔄 Worker Agents: Execute specific tasks")
    print("🔀 Router Agents: Make routing decisions")
    print("🤖 AI Agents: Use machine learning models")
    print("✓ Evaluator Agents: Quality control")
    print("💡 Generator Agents: Create insights/recommendations")
    print("=" * 80 + "\n")


def print_workflow_summary():
    """Print a summary of the workflow"""
    print("\n" + "=" * 80)
    print("WORKFLOW SUMMARY")
    print("=" * 80 + "\n")
    
    print("📋 TOTAL AGENTS: 12")
    print("\n1. Data Fetcher Agent - Fetches stock market data")
    print("2. Market Analyzer Agent - Analyzes market health")
    print("3. News Router Agent - Routes news fetching decision")
    print("4. News Fetcher Agent - Fetches ticker-specific news")
    print("5. Sentiment Analyzer Agent - AI sentiment analysis (DistilBERT)")
    print("6. Sector Analyzer Agent - Analyzes sector performance")
    print("7. Insight Generator Agent - Generates key insights")
    print("8. Recommendation Agent - Creates actionable recommendations")
    print("9. Brief Compiler Agent - Compiles final brief")
    print("10. Quality Evaluator Agent - Evaluates brief quality")
    print("11. Output Generator Agent - Saves outputs (JSON/MD/CSV)")
    print("12. Finalizer Agent - Final cleanup and summary")
    
    print("\n🔀 ROUTING DECISIONS: 2")
    print("\n1. News Router - Decides whether to fetch news")
    print("2. Quality Evaluator - Decides refinement or output")
    
    print("\n🔄 LOOPS: 1")
    print("\n1. Quality Refinement Loop - Max 2 iterations")
    print("   From: Quality Evaluator → Back to: Insight Generator")
    
    print("\n📤 OUTPUTS: 3 formats")
    print("\n1. JSON - Structured data")
    print("2. Markdown - Readable report")
    print("3. CSV - Spreadsheet data")
    
    print("\n" + "=" * 80 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Visualize the graph structure
    visualize_graph()
    print_workflow_summary()
    
    print("\n" + "=" * 80)
    print("To run the actual workflow, use:")
    print("  python generate_brief.py")
    print("=" * 80 + "\n")

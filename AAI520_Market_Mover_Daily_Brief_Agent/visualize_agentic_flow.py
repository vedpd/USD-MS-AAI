#!/usr/bin/env python3
"""
Market Movers Agentic Flow Visualization
Shows the complete workflow graph for the Market Movers Daily Brief Agent
"""


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
    print("│              [Previous Day Evaluator Agent] 📊                       │")
    print("│         Evaluates yesterday's predictions vs actuals                 │")
    print("└────────────────────────┬────────────────────────────────────────────┘")
    print("                         │")
    print("                         ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                [Performance Tracker Agent] 📈                        │")
    print("│           Tracks accuracy, precision, recall, F1 score               │")
    print("└────────────────────────┬────────────────────────────────────────────┘")
    print("                         │")
    print("                         ▼")
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│                [Weight Optimizer Agent] ⚙️                           │")
    print("│            Optimizes analysis weights based on accuracy              │")
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
    
    print("📋 TOTAL AGENTS: 15")
    print("\n1. Data Fetcher Agent - Fetches stock market data")
    print("2. Market Analyzer Agent - Analyzes market health")
    print("3. News Router Agent - Routes news fetching decision")
    print("4. News Fetcher Agent - Fetches ticker-specific news")
    print("5. Sentiment Analyzer Agent - AI sentiment analysis (DistilBERT)")
    print("6. Sector Analyzer Agent - Analyzes sector performance")
    print("7. Insight Generator Agent - Generates key insights")
    print("8. Recommendation Agent - Creates actionable recommendations")
    print("9. Brief Compiler Agent - Compiles final brief")
    print("10. Previous Day Evaluator Agent - Evaluates yesterday's predictions")
    print("11. Performance Tracker Agent - Tracks accuracy metrics")
    print("12. Weight Optimizer Agent - Optimizes analysis weights")
    print("13. Quality Evaluator Agent - Evaluates brief quality")
    print("14. Output Generator Agent - Saves outputs (JSON/MD/CSV)")
    print("15. Finalizer Agent - Final cleanup and summary")
    
    print("\n🔀 ROUTING DECISIONS: 2")
    print("\n1. News Router - Decides whether to fetch news")
    print("2. Quality Evaluator - Decides refinement or output")
    
    print("\n🔄 LOOPS: 1")
    print("\n1. Quality Refinement Loop - Max 2 iterations")
    print("   From: Quality Evaluator → Back to: Insight Generator")
    print("\n📊 EVALUATION SYSTEM: 3 agents")
    print("\n1. Previous Day Evaluator - Compares predictions vs actuals")
    print("2. Performance Tracker - Calculates accuracy/precision/recall")
    print("3. Weight Optimizer - Learns and improves over time")
    
    print("\n📤 OUTPUTS: 3 formats")
    print("\n1. JSON - Structured data")
    print("2. Markdown - Readable report")
    print("3. CSV - Spreadsheet data")
    
    print("\n" + "=" * 80 + "\n")


def print_graph_code():
    """Print the graph building code"""
    print("\n" + "=" * 80)
    print("GRAPH BUILDING CODE (LangGraph Style)")
    print("=" * 80 + "\n")
    
    code = '''
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

# Continue sequential flow
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
'''
    
    print(code)
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    # Visualize the graph structure
    visualize_graph()
    print_workflow_summary()
    print_graph_code()
    
    print("\n" + "=" * 80)
    print("To run the actual workflow, use:")
    print("  python generate_brief.py")
    print("=" * 80 + "\n")

import pandas as pd
from crewai.tools import tool
import os
from pathlib import Path

# Resolve the absolute path to the portfolio CSV
# This tool file is in src/utils/, so project root is two levels up.
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
PORTFOLIO_PATH = os.path.join(PROJECT_ROOT, "data", "test_data", "sample_portfolio.csv")

@tool("read_portfolio_data")
def read_portfolio_data() -> str:
    """
    Reads the user's portfolio data and returns a highly detailed list of holdings.
    Use this to find specific quantities, purchase prices, or categories for tickers in the user's account.
    """
    try:
        if not os.path.exists(PORTFOLIO_PATH):
            return f"Error: Portfolio file not found at {PORTFOLIO_PATH}"
            
        df = pd.read_csv(PORTFOLIO_PATH)
        holdings = []
        for _, row in df.iterrows():
            holdings.append(f"Ticker: {row['ticker']}, Quantity: {row['quantity']}, Purchase Price: ${row['purchase_price']}, Category: {row['category']}")
        
        return "Current Portfolio Holdings:\n" + "\n".join(holdings)
    except Exception as e:
        return f"Error reading portfolio file: {e}"

@tool("analyze_portfolio_diversification")
def analyze_portfolio_diversification() -> str:
    """
    Analyzes the diversification of the user's portfolio by category and returns the percentage breakdown.
    """
    try:
        if not os.path.exists(PORTFOLIO_PATH):
            return f"Error: Portfolio file not found at {PORTFOLIO_PATH}"

        df = pd.read_csv(PORTFOLIO_PATH)
        # Calculate total value per row (approximation using purchase_price)
        df['total_value'] = df['quantity'] * df['purchase_price']
        total_portfolio_value = df['total_value'].sum()
        
        # Group by category
        category_breakdown = df.groupby('category')['total_value'].sum() / total_portfolio_value * 100
        
        result = "Portfolio Diversification Breakdown:\n"
        for category, percentage in category_breakdown.items():
            result += f"- {category}: {percentage:.2f}%\n"
        
        return result
    except Exception as e:
        return f"Error analyzing portfolio: {e}"

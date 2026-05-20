import pandas as pd
from crewai.tools import tool
import os
from pathlib import Path

def get_actual_portfolio_path():
    """
    Robustly finds the sample_portfolio.csv file regardless of environment.
    """
    # Try relative to this file
    base_path = Path(__file__).parent.parent.parent.resolve()
    path = os.path.join(base_path, "data", "test_data", "sample_portfolio.csv")
    if os.path.exists(path):
        return path
    
    # Fallback: Try current working directory
    fallback_path = os.path.join(os.getcwd(), "data", "test_data", "sample_portfolio.csv")
    if os.path.exists(fallback_path):
        return fallback_path
    
    return path # Return the first one anyway if both fail

@tool("read_portfolio_data")
def read_portfolio_data(**kwargs) -> str:
    """
    Reads the user's REAL portfolio holdings. It takes NO parameters.
    """
    target_path = get_actual_portfolio_path()
    print(f"DEBUG: Portfolio tool is attempting to read facts from: {target_path}")
    
    try:
        if not os.path.exists(target_path):
            return f"Error: The portfolio data file was not found at {target_path}. Please ensure data/test_data/sample_portfolio.csv exists."
            
        df = pd.read_csv(target_path)
        holdings = []
        for _, row in df.iterrows():
            holdings.append(f"Ticker: {row['ticker']}, Quantity: {row['quantity']}, Category: {row['category']}")
        
        return "Actual Portfolio Data Found:\n" + "\n".join(holdings)
    except Exception as e:
        return f"Error reading portfolio facts: {e}"

@tool("analyze_portfolio_diversification")
def analyze_portfolio_diversification(**kwargs) -> str:
    """
    Analyzes the REAL user's portfolio diversification. It takes NO parameters.
    """
    target_path = get_actual_portfolio_path()
    try:
        if not os.path.exists(target_path):
            return f"Error: Portfolio facts not found at {target_path}"

        df = pd.read_csv(target_path)
        df['total_value'] = df['quantity'] * df['purchase_price']
        total_portfolio_value = df['total_value'].sum()
        
        category_breakdown = df.groupby('category')['total_value'].sum() / total_portfolio_value * 100
        
        result = "Portfolio Diversification Breakdown:\n"
        for category, percentage in category_breakdown.items():
            result += f"- {category}: {percentage:.2f}%\n"
        
        return result
    except Exception as e:
        return f"Error analyzing portfolio facts: {e}"

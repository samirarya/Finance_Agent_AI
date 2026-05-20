import pandas as pd
from crewai.tools import tool
import os
from pathlib import Path

# Paths configured for your specific environments
LOCAL_HARDCODED_PATH = "/Users/samirarya/Desktop/ai_projects/Capstone_Project/Finance_Agent_AI/data/test_data/sample_portfolio.csv"
CLOUD_PATH = "/mount/src/finance_agent_ai/data/test_data/sample_portfolio.csv"

def get_final_data_path():
    """
    Checks for the existence of the hardcoded local path, then the cloud path, 
    then falls back to relative resolution.
    """
    if os.path.exists(LOCAL_HARDCODED_PATH):
        return LOCAL_HARDCODED_PATH
    if os.path.exists(CLOUD_PATH):
        return CLOUD_PATH
        
    # Relative fallback logic
    base_path = Path(__file__).parent.parent.parent.resolve()
    return os.path.join(base_path, "data", "test_data", "sample_portfolio.csv")

@tool("read_portfolio_data")
def read_portfolio_data(file_path: str = LOCAL_HARDCODED_PATH) -> str:
    """
    Reads the user's REAL portfolio holdings. 
    The portfolio data is located at /Users/samirarya/Desktop/ai_projects/Capstone_Project/Finance_Agent_AI/data/test_data/sample_portfolio.csv
    Use the default path and do NOT hallucinate other paths.
    """
    # We ignore whatever 'file_path' the model might pass if it looks like a hallucination
    # and instead use our verified detection logic.
    target_path = get_final_data_path()
    
    print(f"DEBUG: Portfolio tool is using path: {target_path}")
    
    try:
        if not os.path.exists(target_path):
            return f"Error: Portfolio file not found at {target_path}."
            
        df = pd.read_csv(target_path)
        holdings = []
        for _, row in df.iterrows():
            holdings.append(f"Ticker: {row['ticker']}, Quantity: {row['quantity']}, Category: {row['category']}")
        
        return "Portfolio Facts Found:\n" + "\n".join(holdings)
    except Exception as e:
        return f"Error reading portfolio facts: {e}"

@tool("analyze_portfolio_diversification")
def analyze_portfolio_diversification(**kwargs) -> str:
    """
    Analyzes the REAL user's portfolio diversification.
    Uses the data at /Users/samirarya/Desktop/ai_projects/Capstone_Project/Finance_Agent_AI/data/test_data/sample_portfolio.csv
    """
    target_path = get_final_data_path()
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

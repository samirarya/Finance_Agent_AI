import pandas as pd
from crewai.tools import tool

@tool("read_portfolio_data")
def read_portfolio_data(file_path: str = "data/test_data/sample_portfolio.csv") -> str:
    """
    Reads portfolio data from a CSV file and returns it as a formatted string.
    The CSV should have columns: ticker, quantity, purchase_price, purchase_date, category.
    """
    try:
        df = pd.read_csv(file_path)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error reading portfolio file: {e}"

@tool("analyze_portfolio_diversification")
def analyze_portfolio_diversification(file_path: str = "data/test_data/sample_portfolio.csv") -> str:
    """
    Analyzes the diversification of the portfolio by category and returns the percentage breakdown.
    """
    try:
        df = pd.read_csv(file_path)
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

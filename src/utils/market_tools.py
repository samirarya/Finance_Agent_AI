import os
import requests
import yfinance as yf
from crewai.tools import tool

@tool("get_stock_quote")
def get_stock_quote(symbol: str) -> str:
    """
    Retrieves the current stock price and change information for a given ticker symbol.
    Uses yfinance for reliability.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Use fast_info or basic info
        info = ticker.fast_info
        price = info.last_price
        
        # Get change info from history if needed, but fast_info is quicker
        # For a full quote, we can use the regular info but it's slower
        return f"Stock: {symbol}, Price: ${price:.2f}"
            
    except Exception as e:
        return f"Error fetching data for {symbol}: {e}"

def get_current_price(symbol: str) -> float:
    """
    Retrieves the current stock price for a given ticker symbol as a float using yfinance.
    This avoids Alpha Vantage rate limits.
    """
    try:
        # Ticker symbols like BRK.B need to be handled for yfinance (BRK-B)
        yf_symbol = symbol.replace(".", "-")
        ticker = yf.Ticker(yf_symbol)
        
        # Using fast_info for performance
        price = ticker.fast_info.last_price
        
        if price is None or price == 0:
            # Fallback to regular info if fast_info fails
            price = ticker.info.get('regularMarketPrice') or ticker.info.get('currentPrice')
            
        return float(price) if price else 0.0
    except Exception:
        return 0.0

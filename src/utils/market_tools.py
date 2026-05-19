import os
import requests
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool("get_stock_quote")
def get_stock_quote(symbol: str) -> str:
    """
    Retrieves the current stock price and change information for a given ticker symbol using Alpha Vantage.
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            price = quote.get("05. price")
            change = quote.get("09. change")
            percent_change = quote.get("10. change percent")
            return f"Stock: {symbol}, Price: ${float(price):.2f}, Change: {change} ({percent_change})"
        else:
            return f"Could not fetch data for {symbol}. Response: {data}"
            
    except Exception as e:
        return f"Error fetching data for {symbol}: {e}"

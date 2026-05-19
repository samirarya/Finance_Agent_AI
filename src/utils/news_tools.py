import yfinance as yf
from crewai.tools import tool

@tool("get_stock_news")
def get_stock_news(symbol: str) -> str:
    """
    Retrieves the latest news headlines and summaries for a given stock ticker symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if not news:
            return f"No recent news found for {symbol}."
        
        result = f"Latest News for {symbol}:\n"
        for item in news[:5]: # Get top 5 news items
            title = item.get('content', {}).get('title', 'No Title')
            summary = item.get('content', {}).get('summary', 'No Summary')
            pub_date = item.get('content', {}).get('pubDate', 'No Date')
            result += f"- {title} ({pub_date})\n  Summary: {summary}\n"
        
        return result
    except Exception as e:
        return f"Error fetching news for {symbol}: {e}"

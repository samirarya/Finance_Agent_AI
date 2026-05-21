import sys
import os
from pathlib import Path

# Standardize pathing for Streamlit Cloud
# Add current directory and project root to sys.path
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Fix for ChromaDB / Pydantic v1 validation error on Python 3.14+
os.environ["CHROMA_SERVER_NOFILE"] = os.environ.get("CHROMA_SERVER_NOFILE", "100")

import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
# Import workflow after path setup
from src.workflow.crew_setup import run_sammy_workflow
from src.utils.market_tools import get_current_price

@st.cache_data(ttl=600)
def get_portfolio_prices(tickers):
    """Fetch current prices for all tickers in the portfolio using batch download."""
    try:
        # Convert list to string for yfinance batch download
        # Also handle tickers like BRK.B -> BRK-B for yfinance
        yf_tickers = [t.replace(".", "-") for t in tickers]
        data = yf.download(yf_tickers, period="1d", interval="1m", progress=False)
        
        prices = {}
        if not data.empty and 'Adj Close' in data:
            for ticker in tickers:
                yf_t = ticker.replace(".", "-")
                try:
                    # Get the last valid price from Adj Close
                    price = data['Adj Close'][yf_t].iloc[-1]
                    prices[ticker] = float(price)
                except Exception:
                    prices[ticker] = 0.0
        else:
            # Fallback if download fails
            for ticker in tickers:
                prices[ticker] = get_current_price(ticker)
        return prices
    except Exception:
        # Fallback to individual calls if batch fails
        prices = {}
        for ticker in tickers:
            prices[ticker] = get_current_price(ticker)
        return prices

st.set_page_config(page_title="Sammy - Your Personal Finance Agent", page_icon="💰", layout="wide")

# Sidebar for Portfolio and Settings
with st.sidebar:
    st.title("💰 Sammy AI")
    st.markdown("---")
    
    st.subheader("Your Portfolio")
    portfolio_path = "data/test_data/sample_portfolio.csv"
    if os.path.exists(portfolio_path):
        df = pd.read_csv(portfolio_path)
        
        # Fetch current prices
        with st.spinner("Updating prices..."):
            prices = get_portfolio_prices(df['ticker'].tolist())
            df['current_price'] = df['ticker'].map(prices)
            df['current_value'] = df['quantity'] * df['current_price']
            
            # Format price as currency for display
            df['price_display'] = df['current_price'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
            
        # Shift index to start from 1
        df.index = df.index + 1
        # Include 'price_display' column next to 'quantity'
        df_display = df[['ticker', 'quantity', 'price_display', 'category']]
        df_display.columns = ['ticker', 'quantity', 'price', 'category'] # Rename for display
        
        # Dynamically calculate height to be more compact: (rows + 1) * 35 + 2
        # For 15 rows, this is roughly 16 * 35 + 2 = 562
        table_height = (len(df_display) + 1) * 35 + 2
        st.dataframe(df_display, use_container_width=True, height=table_height)
        
        # Quick Stats (Compact)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Holdings", len(df))
        with col2:
            st.metric("Net Value", f"${df['current_value'].sum():,.0f}")
            
        # Portfolio Composition Pie Chart (Miniaturized to fit)
        fig = px.pie(df, values='current_value', names='category', 
                     hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5, font=dict(size=10)),
            margin=dict(t=0, b=0, l=0, r=0),
            height=200 # Further reduced to accommodate the taller table
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No portfolio data found. Create a sample_portfolio.csv in data/test_data/")


# Main Chat Interface
st.title("Sammy - Personal Finance Agent")
st.markdown("Democratizing financial literacy through multi-agent AI.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me about your portfolio, market news, or financial concepts..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 *Sammy is thinking and coordinating agents...*")
        
        try:
            # Run the CrewAI workflow
            response = run_sammy_workflow(prompt)
            
            # Display assistant response
            message_placeholder.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                user_friendly_error = "⚠️ **Sammy is experiencing high demand right now.** \n\nThe underlying AI model has reached its temporary limit. Please wait about 60 seconds and try your request again. We appreciate your patience!"
                message_placeholder.markdown(user_friendly_error)
                st.session_state.messages.append({"role": "assistant", "content": user_friendly_error})
            else:
                error_msg = f"❌ **An unexpected error occurred:** \n\n{error_str}"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.caption("Powered by CrewAI, Pinecone, and Google Gemini. For educational purposes only.")

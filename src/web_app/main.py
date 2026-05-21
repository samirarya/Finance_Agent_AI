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
# Import workflow after path setup
from src.workflow.crew_setup import run_sammy_workflow

st.set_page_config(page_title="Sammy - Your Personal Finance Agent", page_icon="💰", layout="wide")

# Sidebar for Portfolio and Settings
with st.sidebar:
    st.title("💰 Sammy AI")
    st.markdown("---")
    
    st.subheader("Your Portfolio")
    portfolio_path = "data/test_data/sample_portfolio.csv"
    if os.path.exists(portfolio_path):
        df = pd.read_csv(portfolio_path)
        
        # Shift index to start from 1
        df.index = df.index + 1
        
        # Select columns to display (Removing Price)
        df_display = df[['ticker', 'quantity', 'category']]
        
        # Dynamically calculate height to be more compact: (rows + 1) * 35 + 2
        table_height = (len(df_display) + 1) * 35 + 2
        # Fixed: use width='stretch' instead of use_container_width=True
        st.dataframe(df_display, width='stretch', height=table_height)
        
        # Quick Stats (Removing Net Value)
        st.metric("Total Holdings", len(df))
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

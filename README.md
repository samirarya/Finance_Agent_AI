# Finnie - Personal Finance Agent 💰

Finnie is a multi-agent conversational AI system designed to democratize financial literacy. It provides personalized financial education, portfolio analysis, and goal planning using real-time market data and a curated knowledge base.

## 🚀 Key Features

- **Multi-Agent Orchestration:** Powered by CrewAI with a hierarchical (Manager-led) architecture.
- **6 Specialized Agents:**
  - **Finance Q&A Agent:** General education via Pinecone RAG.
  - **Portfolio Analysis Agent:** Reviews diversification and risk in your holdings.
  - **Market Analysis Agent:** Real-time stock quotes via Alpha Vantage.
  - **Goal Planning Agent:** Retirement and savings goal calculations.
  - **News Synthesizer Agent:** Contextualizes market news via Yahoo Finance.
  - **Tax Education Agent:** Explains complex tax concepts and account types.
- **RAG Knowledge Base:** 110+ curated articles indexed in a high-dimensional Pinecone vector store.
- **Observability:** Full tracing and monitoring integrated with LangSmith.

## 🛠️ Project Structure

- `src/agents/`: Specialized agent definitions (managed via `crew_setup.py`).
- `src/core/`: Core logic and shared base classes.
- `src/data/`: Educational articles, glossary, and sample portfolio.
- `src/rag/`: Pinecone indexer and search logic.
- `src/web_app/`: Streamlit dashboard interface.
- `src/utils/`: Custom tools for market data, news, and goal planning.
- `src/workflow/`: CrewAI hierarchical orchestration.

## ⚙️ Setup Instructions

1. **Environment Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **API Configuration:**
   Create a `.env` file based on `.env.example`:
   - `GOOGLE_API_KEY`: For Gemini and Embeddings.
   - `ALPHA_VANTAGE_API_KEY`: For real-time market data.
   - `PINECONE_API_KEY` & `PINECONE_INDEX_NAME`: For the vector store.
   - `LANGCHAIN_API_KEY` (Optional): For LangSmith tracing.

3. **Initialize Knowledge Base:**
   If the Pinecone index is not yet populated:
   ```bash
   python3 src/rag/indexer.py
   ```

4. **Run the Application:**
   ```bash
   streamlit run src/web_app/main.py
   ```

## 🌐 Deployment

Finnie is designed to be hosted on **Streamlit Community Cloud** and integrated into your portfolio at **samiraryamane.com**.

1. Push your code to a GitHub repository.
2. Connect the repository to [Streamlit Cloud](https://share.streamlit.io/).
3. Add your environment variables to the "Secrets" dashboard in Streamlit Cloud.
4. Link the deployment URL to your portfolio website.

---
*Disclaimer: For educational purposes only. Not financial advice.*

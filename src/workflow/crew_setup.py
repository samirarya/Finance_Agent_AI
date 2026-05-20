import os
import time
import re
from crewai import Agent, Task, Crew, Process
from src.rag.search import financial_knowledge_base_search
from src.utils.market_tools import get_stock_quote
from src.utils.portfolio_tools import read_portfolio_data, analyze_portfolio_diversification
from src.utils.news_tools import get_stock_news
from src.utils.goal_tools import calculate_retirement_savings, calculate_savings_goal

# --- LLM Configurations ---
PRIMARY_LLM = "gemini/gemini-2.5-flash"
SECONDARY_LLM = "gpt-4o"
TERTIARY_LLM = "ollama/llama3.1"

def create_hierarchical_crew(user_query, model_name):
    """
    Creates a full hierarchical Crew for high-performance cloud models.
    """
    qa_agent = Agent(
        role='Finance Q&A Agent',
        goal='Handle general financial education queries accurately.',
        backstory='Financial literacy advocate with RAG access.',
        llm=model_name,
        tools=[financial_knowledge_base_search],
        max_iter=3
    )

    portfolio_agent = Agent(
        role='Portfolio Analysis Agent',
        goal='Analyze user portfolios for risk and diversification.',
        backstory='Quantitative investment analyst.',
        llm=model_name,
        tools=[read_portfolio_data, analyze_portfolio_diversification],
        max_iter=3
    )

    market_agent = Agent(
        role='Market Analysis Agent',
        goal='Provide real-time market insights and quotes.',
        backstory='Market strategist tracking real-time data.',
        llm=model_name,
        tools=[get_stock_quote],
        max_iter=3
    )

    goal_agent = Agent(
        role='Goal Planning Agent',
        goal='Assist with financial goal setting and calculations.',
        backstory='Certified financial planner.',
        llm=model_name,
        tools=[calculate_retirement_savings, calculate_savings_goal],
        max_iter=3
    )

    news_agent = Agent(
        role='News Synthesizer Agent',
        goal='Summarize and contextualize financial news.',
        backstory='Financial journalist.',
        llm=model_name,
        tools=[get_stock_news],
        max_iter=3
    )

    tax_agent = Agent(
        role='Tax Education Agent',
        goal='Explain tax concepts and account types.',
        backstory='Tax education specialist.',
        llm=model_name,
        tools=[financial_knowledge_base_search],
        max_iter=3
    )

    main_task = Task(
        description=f"Process the user query: {user_query}. Gather information and provide a final response.",
        expected_output="A comprehensive and helpful financial response.",
    )

    return Crew(
        agents=[qa_agent, portfolio_agent, market_agent, goal_agent, news_agent, tax_agent],
        tasks=[main_task],
        process=Process.hierarchical,
        manager_llm=model_name,
        verbose=True
    )

def clean_fallback_output(text):
    """
    Strips out internal agent dialogue, tool calls (JSON), and metadata from the final string.
    """
    # Remove any JSON code blocks
    text = re.sub(r'```json.*?```', '', text, flags=re.DOTALL)
    # Remove raw JSON objects if not in code blocks
    text = re.sub(r'\{"name":.*?"parameters":.*?\}', '', text, flags=re.DOTALL)
    # Remove common internal headers
    text = re.sub(r'(To determine the best course of action|I will call|Tool response:|The .* Agent responds with:)', '', text, flags=re.IGNORECASE)
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

def create_fallback_crew(user_query, model_name):
    """
    Creates a simplified Sequential Crew for models that might struggle with complex hierarchy 
    or when running as a last resort.
    """
    generalist_agent = Agent(
        role='Sammy Generalist',
        goal='Provide accurate and honest financial answers. If you are unsure or the data is unclear, say so. Do NOT make up numbers.',
        backstory='You are a meticulous financial assistant. You provide only the final answer in clean language.',
        llm=model_name,
        tools=[
            financial_knowledge_base_search,
            get_stock_quote,
            get_stock_news,
            read_portfolio_data,
            analyze_portfolio_diversification,
            calculate_retirement_savings,
            calculate_savings_goal
        ],
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )

    task = Task(
        description=f"Answer the user query: {user_query}. If the query is about the user's specific holdings, you MUST call the 'read_portfolio_data' tool. Present ONLY the final answer. NO JSON.",
        agent=generalist_agent,
        expected_output="A direct, human-friendly final answer grounded in the tool data."
    )

    return Crew(
        agents=[generalist_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

def run_sammy_workflow(user_query):
    """
    Orchestrates the Sammy Agent workflow with three-tier fallback logic:
    Gemini -> OpenAI -> Local Llama
    """
    # 1. Attempt Gemini (Primary)
    print(f"--- Tier 1: Attempting Gemini Workflow ({PRIMARY_LLM}) ---")
    try:
        crew = create_hierarchical_crew(user_query, PRIMARY_LLM)
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        error_str = str(e)
        if any(kw in error_str for kw in ["429", "RESOURCE_EXHAUSTED", "quota"]):
            # 2. Fallback to OpenAI (Secondary)
            print(f"⚠️ Gemini limit hit. Tier 2: Falling back to OpenAI ({SECONDARY_LLM})...")
            time.sleep(1)
            try:
                # OpenAI is capable enough for hierarchy
                crew = create_hierarchical_crew(user_query, SECONDARY_LLM)
                result = crew.kickoff()
                return "*(Note: This response was generated by OpenAI as a secondary fallback)*\n\n" + str(result)
            except Exception as e2:
                # 3. Fallback to Local Llama (Tertiary)
                print(f"⚠️ OpenAI also hit an issue: {e2}. Tier 3: Falling back to Local Llama ({TERTIARY_LLM})...")
                time.sleep(1)
                try:
                    # Use simplified sequential crew for local fallback
                    fallback_crew = create_fallback_crew(user_query, TERTIARY_LLM)
                    result = fallback_crew.kickoff()
                    final_answer = clean_fallback_output(str(result))
                    if not final_answer: final_answer = str(result)
                    return "*(Note: This response was generated by your local Llama 3.1 model as a final fallback)*\n\n" + final_answer
                except Exception as e3:
                    return f"❌ All tiers failed. Final error: {e3}"
        else:
            raise e

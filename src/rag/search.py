import os
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from crewai.tools import tool

@tool("financial_knowledge_base_search")
def financial_knowledge_base_search(query: str) -> str:
    """
    Useful for answering financial education, tax, and general finance questions. 
    Searches a curated library of 110+ articles.
    """
    index_name = os.getenv("PINECONE_INDEX_NAME")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings
    )
    
    docs = vector_store.similarity_search(query, k=3)
    context = "\n---\n".join([doc.page_content for doc in docs])
    return context

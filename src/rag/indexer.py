import os
import sys
from pathlib import Path

# Add the project root to sys.path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

def run_indexing():
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    articles_dir = "data/education/articles/"
    
    if not api_key or not index_name:
        print("❌ Error: PINECONE_API_KEY or PINECONE_INDEX_NAME not found in .env")
        return

    pc = Pinecone(api_key=api_key)
    
    if index_name not in pc.list_indexes().names():
        print(f"Creating Pinecone index: {index_name} with dimension 3072...")
        pc.create_index(
            name=index_name,
            dimension=3072,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        # Wait for index to be ready
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
    else:
        print(f"Index {index_name} already exists.")

    loader = DirectoryLoader(articles_dir, glob="*.md", loader_cls=TextLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)

    print(f"Upserting {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        success = False
        retries = 0
        while not success and retries < 3:
            try:
                vector_store.add_documents([chunk])
                success = True
                if (i + 1) % 10 == 0:
                    print(f"✅ Indexed {i + 1}/{len(chunks)}")
                time.sleep(1)
            except Exception as e:
                if "429" in str(e):
                    time.sleep(65)
                else:
                    time.sleep(5)
                retries += 1
    print("✅ Indexing complete!")

if __name__ == "__main__":
    run_indexing()

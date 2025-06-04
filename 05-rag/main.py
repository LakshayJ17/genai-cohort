from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore

load_dotenv()

pdf_path = Path(__file__).parent / "nodejs.pdf"
api_key = os.getenv("GEMINI_API_KEY")

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

split_docs = text_splitter.split_documents(documents=docs)

embedding_model = genai.embed_content(
    model="models/embedding-001",                                  # Specify the embedding model
    content=split_docs
)

vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)

print("Indexing of Documents done..")

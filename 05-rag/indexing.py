import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Indexing / Ingestion - Loading data
pdf_path = Path(__file__).parent / "nodejs.pdf"

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()  # Read PDF File


# Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

split_docs = text_splitter.split_documents(documents=docs)


# Vector embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=api_key
)

# Using [embedding_model] , create embeddings of [split_docs] and store in db

vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url="http://vector-db:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)

print("Indexing of Documents done..")

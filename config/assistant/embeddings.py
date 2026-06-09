from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "chroma_db"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def store_embeddings(chunks):
    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"[ChromaDB] Stored {len(chunks)} vectors")
    return vectordb

def load_vectordb():
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
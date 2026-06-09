import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from .embeddings import load_vectordb

load_dotenv("config.env")

def get_llm():
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",
        temperature=0
    )

def ask_question_with_history(question: str, chat_history: list) -> str:
    try:
        vectordb = load_vectordb()
        retriever = vectordb.as_retriever(search_kwargs={"k": 4})
        llm = get_llm()

        # Get relevant docs
        docs = retriever.invoke(question)

        # If no docs found at all
        if not docs:
            return "I could not find any relevant information in the uploaded documents."

        context = "\n\n".join([doc.page_content for doc in docs])

        # Build conversation history string
        history_text = ""
        for msg in chat_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

        # Strict PDF only prompt
        prompt = f"""You are a document assistant. You ONLY answer questions based on the provided document context below.

STRICT RULES:
- ONLY use information from the Document Context below
- If the answer is NOT found in the Document Context, say exactly: "This information is not available in the uploaded document."
- Do NOT use your own knowledge
- Do NOT make up answers
- Do NOT answer general knowledge questions

Document Context:
{context}

Conversation History:
{history_text}

Current Question: {question}

Answer (only from document):"""

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Error: {str(e)}"
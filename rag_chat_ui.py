import warnings
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")

from surrealdb import Surreal
from langchain_surrealdb.vectorstores import SurrealDBVectorStore
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from nicegui import ui
from typing import List

# Initialize SurrealDB connection
conn = Surreal("ws://localhost:8000")
conn.signin({"username": "root", "password": "root"})
conn.use("whatsapp", "chats")

# Initialize embeddings and vector store
embeddings = OllamaEmbeddings(model="all-minilm:22m")
vector_store = SurrealDBVectorStore(embeddings, conn)

# Initialize LLM for generating answers
llm = ChatOllama(model="llama3.2:latest", temperature=0.7)

# Chat history
chat_history: List = []

def search_and_answer(question: str) -> tuple:
    """Search vector store and generate answer using LLM
    Returns: (answer, sources) tuple"""
    # Search for relevant documents
    results = vector_store.similarity_search_with_score(question, k=3)
    
    if not results:
        return "No relevant information found in the knowledge base.", []
    
    # Build context and sources
    context_lines = []
    sources = []
    
    for doc, score in results:
        context_lines.append(f"- {doc.page_content}")
        # Extract metadata if available
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        sources.append({
            "content": doc.page_content,
            "score": score,
            "sender": metadata.get("sender", "Unknown"),
            "timestamp": metadata.get("timestamp", "N/A")
        })
    
    context = "\n".join(context_lines)
    
    # Create a prompt with context
    prompt = f"""Based on the following information from the chat history:

{context}

Please answer this question: {question}

Provide a concise and helpful answer."""
    
    # Generate answer
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content, sources

def send_message() -> None:
    """Handle sending a message"""
    if not input_field.value.strip():
        return
    
    question = input_field.value
    input_field.value = ""
    
    # Add user message to chat
    with chat_container:
        with ui.chat_message(name="You", sent=True):
            ui.label(question)
    
    chat_history.append({"role": "user", "content": question})
    
    # Generate and display answer with sources
    answer, sources = search_and_answer(question)
    
    with chat_container:
        with ui.chat_message(name="RAG Bot", sent=False):
            # Display the answer
            ui.label(answer).classes("text-base font-semibold mb-3")
            
            # Display sources
            if sources:
                ui.label("📚 Sources:").classes("text-sm font-bold mt-3 mb-2 text-gray-600")
                for i, source in enumerate(sources, 1):
                    with ui.card().classes("w-full bg-gray-100 p-3 rounded"):
                        ui.label(f"Source {i} - {source['sender']}").classes("text-xs font-bold text-blue-600")
                        ui.label(f"Confidence: {source['score']:.1%}").classes("text-xs text-gray-500")
                        if source['timestamp'] != 'N/A':
                            ui.label(f"Time: {source['timestamp']}").classes("text-xs text-gray-500")
                        ui.label(source['content'][:150] + "...").classes("text-sm text-gray-700 mt-1")
    
    chat_history.append({"role": "assistant", "content": answer, "sources": sources})

# Build UI
ui.page_title("WhatsApp RAG Chat")

# Header (top-level)
with ui.header().classes("bg-blue-600 text-white"):
    ui.label("WhatsApp RAG Chat").classes("text-2xl font-bold")
    ui.label("Ask questions about your WhatsApp conversations").classes("text-sm opacity-80")

# Main content area
with ui.column().classes("w-full"):
    # Chat display area
    chat_container = ui.column().classes("flex-grow overflow-y-auto p-4 bg-gray-50")
    
    # Welcome message
    with chat_container:
        with ui.chat_message(name="RAG Bot", sent=False):
            ui.label("👋 Hello! I'm your WhatsApp RAG assistant. Ask me anything about your conversations!")
    
    # Input area
    with ui.row().classes("w-full p-4 bg-white border-t"):
        input_field = ui.input(
            placeholder="Ask a question about your WhatsApp chats...",
            on_change=lambda: None
        ).classes("flex-grow")
        
        send_button = ui.button(
            "Send",
            on_click=send_message,
            icon="send"
        ).classes("ml-2 bg-blue-600 text-white")
        
        # Allow Enter key to send
        input_field.on("keydown.enter", send_message)

ui.run(host="0.0.0.0", port=8080, title="WhatsApp RAG Chat")

import warnings
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")
from surrealdb import Surreal
from langchain_surrealdb.vectorstores import SurrealDBVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# Export your WhatsApp chat:
# Open WhatsApp → Chat → More → Export Chat → Without Media

conn = Surreal("ws://localhost:8000")
conn.signin({"username": "root", "password": "root"})
conn.use("whatsapp", "chats")

# Load WhatsApp chat file
with open("./whatsappChatExport.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Parse WhatsApp messages manually
messages = []
for line in lines:
    line = line.strip()
    if not line:
        continue
    
    # WhatsApp format: [DD/MM/YYYY, HH:MM:SS] Sender: Message
    try:
        # Find the closing bracket
        bracket_idx = line.find("]")
        if bracket_idx == -1:
            continue
        
        timestamp = line[1:bracket_idx]  # Get timestamp
        rest = line[bracket_idx+2:]  # Skip "] "
        
        # Find the colon that separates sender from message
        colon_idx = rest.find(":")
        if colon_idx == -1:
            continue
        
        sender = rest[:colon_idx]
        content = rest[colon_idx+2:]  # Skip ": "
        
        if content:  # Only add non-empty messages
            messages.append(
                Document(
                    page_content=content,
                    metadata={"sender": sender, "timestamp": timestamp}
                )
            )
    except Exception as e:
        print(f"Error parsing line: {line} - {e}")
        continue

# Create vector store and add messages
embeddings = OllamaEmbeddings(model="all-minilm:22m")
vector_store = SurrealDBVectorStore(embeddings, conn)
vector_store.add_documents(messages)

print(f"✓ Loaded {len(messages)} messages into SurrealDB")
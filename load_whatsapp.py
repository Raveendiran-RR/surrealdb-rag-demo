import warnings
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")
from surrealdb import Surreal
from langchain_surrealdb.vectorstores import SurrealDBVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
import requests
import time

# Configuration for Embeddings and LLM
# Embeddings: Ollama (port 11434) - Docker Model Runner doesn't support embedding models
# LLM: Docker Model Runner (port 12434) - for chat/generation models
EMBEDDING_SERVER_URL = "http://localhost:11434"
EMBEDDING_MODEL = "all-minilm:22m"

# Wait for Ollama embedding server to be ready
print("⏳ Waiting for Ollama embedding server to be ready...")
max_retries = 30
retries = 0
while retries < max_retries:
    try:
        response = requests.get(f"{EMBEDDING_SERVER_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            print("✓ Ollama embedding server is ready")
            break
    except requests.exceptions.RequestException:
        pass
    retries += 1
    time.sleep(1)

if retries == max_retries:
    print("❌ Ollama is not responding.")
    print("Please ensure Ollama is running:")
    print("  Option 1: Install Ollama from https://ollama.ai")
    print("  Option 2: Run 'ollama serve' in a terminal")
    exit(1)

# Initialize SurrealDB connection
conn = Surreal("ws://localhost:8000")
conn.signin({"username": "root", "password": "root"})
conn.use("whatsapp", "chats")

print("✓ Connected to SurrealDB")

# Initialize embeddings using Ollama
embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=EMBEDDING_SERVER_URL
)

print(f"✓ Embeddings initialized (Model: {EMBEDDING_MODEL})")

# Create vector store
vector_store = SurrealDBVectorStore(embeddings, conn)

print("✓ Vector store created")

# Export your WhatsApp chat:
# Open WhatsApp → Chat → More → Export Chat → Without Media

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

# Add messages to vector store
vector_store.add_documents(messages)

print(f"✓ Loaded {len(messages)} messages into SurrealDB")

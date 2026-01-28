import warnings
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")
from surrealdb import Surreal
from langchain_surrealdb.vectorstores import SurrealDBVectorStore
from docker_model_runner_embeddings import DockerModelRunnerEmbeddings
from langchain_core.documents import Document
import requests
import time

# Configuration for Embeddings and LLM
# Both using Docker Model Runner (port 12434)
# Using OpenAI-compatible API for embeddings
EMBEDDING_SERVER_URL = "http://localhost:12434"
EMBEDDING_MODEL = "embeddinggemma"

# Wait for Docker Model Runner to be ready
print("⏳ Waiting for Docker Model Runner to be ready...")
max_retries = 30
retries = 0
while retries < max_retries:
    try:
        response = requests.get(f"{EMBEDDING_SERVER_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            print("✓ Docker Model Runner is ready")
            break
    except requests.exceptions.RequestException:
        pass
    retries += 1
    time.sleep(1)

if retries == max_retries:
    print("❌ Docker Model Runner is not responding.")
    print("Please ensure Docker Model Runner is enabled in Docker Desktop:")
    print("  Settings → Features in development → Enable Docker Model Runner")
    exit(1)

# Initialize SurrealDB connection
conn = Surreal("ws://localhost:8002")
conn.signin({"username": "root", "password": "root"})
conn.use("whatsapp", "chats")

print("✓ Connected to SurrealDB")

# Initialize embeddings using Docker Model Runner (OpenAI-compatible API)
embeddings = DockerModelRunnerEmbeddings(
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

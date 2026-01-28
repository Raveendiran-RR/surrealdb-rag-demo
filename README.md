# WhatsApp RAG Chat with SurrealDB

A Retrieval-Augmented Generation (RAG) chatbot that analyzes your WhatsApp conversations using vector embeddings and LLMs.

## 🏗️ Architecture

This project uses **Docker Model Runner exclusively** for all AI operations:
- **Docker Model Runner** (port 12434) - For both embeddings and LLM
  - Embeddings via OpenAI-compatible API (`/v1/embeddings`)
  - LLM via Ollama-compatible API (`/api/generate`)
- **SurrealDB** (port 8002) - Vector database for storing embeddings

```mermaid
graph TB
    subgraph AI["🤖 AI Infrastructure - Docker Model Runner Only"]
        direction TB
        subgraph DMR["Docker Model Runner (Port 12434)"]
            D1["Embeddings API<br/>/v1/embeddings<br/>Model: embeddinggemma<br/>768 dimensions"]
            D2["LLM API<br/>/api/generate<br/>Model: ai/llama3.2:3B-Q4_0"]
        end
    end
    
    App["Python Application<br/>(Custom Embeddings + Chat)"] -.->|Embedding Requests<br/>OpenAI API| D1
    App -.->|LLM Requests<br/>DockerModelRunner API| D2
    
    style AI fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style DMR fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style App fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
```

## 📋 Requirements

- **Python 3.14+**
- **Docker Desktop** with Docker Model Runner enabled
- **SurrealDB** running via Docker Desktop Extension (port 8002)

## 🚀 Setup Instructions

### 1. Create Virtual Environment
```bash
python3.14 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare Your WhatsApp Chat

1. Open WhatsApp on your phone
2. Go to Chat → More options (⋮) → Export Chat
3. Select a chat and choose "Without Media"
4. Save the file as `whatsappChatExport.txt` in the project directory

### 4. Enable Docker Model Runner

Docker Model Runner will handle both embeddings and LLM models.

1. Open **Docker Desktop**
2. Go to **Settings** → **Features in development**
3. Enable **Docker Model Runner**
4. Restart Docker Desktop if prompted

### 5. Pull Required Models

```bash
# Pull the embedding model
docker model pull embeddinggemma

# Pull the LLM model for chat/generation
docker model pull ai/llama3.2:3B-Q4_0
```

To verify models are available:
```bash
docker model ls
```

You should see:
- `embeddinggemma` (302.86M parameters, Q8_0, 768 dimensions)
- `ai/llama3.2:3B-Q4_0` (3.21B parameters)

### 6. Start SurrealDB via Docker Desktop
1. Open **Docker Desktop**
2. Go to **Extensions**
3. Find and start **SurrealDB** extension
4. Configure it to run on port **8002** (Settings in the extension)
5. Ensure it's running on `ws://localhost:8002`

### 7. Load WhatsApp Messages into SurrealDB
```bash
./venv/bin/python load_whatsapp.py
```

You should see: `✓ Loaded X messages into SurrealDB`

## 💻 Usage

### Quick Start (Recommended)
```bash
# Make sure SurrealDB is running via Docker Desktop Extension first!
# Then:

# Step 1: Load your WhatsApp messages
./venv/bin/python load_whatsapp.py

# Step 2: Start the web UI
./venv/bin/python rag_chat_ui.py
```

Then open your browser to: **http://localhost:8080**

---

### Web UI with NiceGUI (Primary Interface)
```bash
./venv/bin/python rag_chat_ui.py
```

**Features:**
- Beautiful interactive chat interface
- Full source citations with metadata
- Confidence scores for each match
- Sender information & timestamps
- Complete conversation history

### Alternative: Interactive Terminal Chat
```bash
./venv/bin/python rag_chat_interactive.py
```

**Features:**
- Command-line interface
- Relevant source message display
- Confidence scores
- Quick testing without web browser

## 📁 Project Files

- `load_whatsapp.py` - Loads WhatsApp messages into SurrealDB
- `rag_chat_interactive.py` - Terminal-based interactive chat
- `rag_chat_ui.py` - Web UI with NiceGUI frontend
- `whatsappChatExport.txt` - Your exported WhatsApp chat
- `requirements.txt` - Python dependencies

## 🔧 Configuration

### Current Setup
```python
# Both using Docker Model Runner (port 12434)
EMBEDDING_SERVER_URL = "http://localhost:12434"
EMBEDDING_MODEL = "embeddinggemma"  # 768-dimensional embeddings

LLM_SERVER_URL = "http://localhost:12434"
LLM_MODEL = "ai/llama3.2:3B-Q4_0"

# SurrealDB
SURREALDB_URL = "ws://localhost:8002"
```

### Environment Details

- **Python Version**: 3.14.2
- **Main Dependencies**:
  - `langchain-community` - LLM framework
  - `langchain-ollama` - Ollama-compatible API integration
  - `surrealdb` - Vector database
  - `nicegui` - Web UI framework
- **AI Infrastructure**:
  - Docker Model Runner - Both embedding and LLM serving (port 12434)
    - Embeddings: OpenAI-compatible API (`/v1/embeddings`)
    - LLM: Ollama-compatible API (`/api/generate`)

## 🔄 How It Works

1. **Load**: WhatsApp messages are parsed and stored in SurrealDB with embeddings
2. **Search**: User questions are converted to vectors and searched against stored messages
3. **Generate**: Relevant messages are used as context for the LLM
4. **Answer**: LLM generates an answer with source citations

<img width="1920" height="1080" alt="Screenshot 2026-01-28 at 12 51 13 AM" src="https://github.com/user-attachments/assets/9237de74-6800-4087-ae29-6b2fc3117553" />


### Architecture Diagram

```mermaid
graph TD
    A["📱 WhatsApp Chat Export"] -->|Parse & Extract| B["📝 Raw Messages"]
    B -->|Embed with DMR<br/>embeddinggemma 768D| C["🔢 Vector Embeddings"]
    C -->|Store| D["🗄️ SurrealDB (8002)<br/>Vector Store"]
    
    E["👤 User Question"] -->|Embed| F["🔢 Query Vector"]
    F -->|Similarity Search<br/>k=3| D
    D -->|Retrieve Top Matches| G["📚 Relevant Context<br/>+ Metadata"]
    
    G -->|With Context| H["🤖 Docker Model Runner<br/>ai/llama3.2"]
    H -->|Generate Answer| I["💬 AI Response"]
    
    I -->|Display with<br/>Citations| J["🌐 NiceGUI Web Interface<br/>or Terminal"]
    
    G -.->|Show Sources| K["📖 Source Citations<br/>Sender, Timestamp,<br/>Confidence Score"]
    K -->|Display| J
```

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as NiceGUI<br/>Web Interface
    participant VectorStore as SurrealDB<br/>Vector Store
    participant Embedder as Docker Model Runner<br/>Embeddings (12434)
    participant LLM as Docker Model Runner<br/>LLM (12434)

    User->>UI: Ask a question
    UI->>Embedder: Convert question to vector
    Embedder-->>UI: Return question vector
    UI->>VectorStore: Search similar messages
    VectorStore-->>UI: Return top 3 matches<br/>with scores
    UI->>LLM: Generate answer<br/>with context
    LLM-->>UI: Return AI response
    UI->>User: Display answer<br/>+ source citations
```

### Component Architecture

```mermaid
graph LR
    subgraph "Data Processing"
        A["WhatsApp<br/>Chat Export"] -->|load_whatsapp.py| B["Parse &<br/>Embed"]
    end
    
    subgraph "Storage Layer"
        B -->|Store| C["SurrealDB<br/>Vector DB"]
    end
    
    subgraph "AI Layer"
        D["Question"] -->|Embedding| E["Docker Model Runner<br/>embeddinggemma"]
        C -->|Vector<br/>Search| F["Similarity<br/>Match"]
        E -.-> F
        F -->|Context| G["Docker Model Runner<br/>ai/llama3.2"]
    end
    
    subgraph "Interface Layer"
        G -->|Answer| H["Web UI<br/>NiceGUI"]
        H -->|Display| I["Sources<br/>Citations"]
    end
```

## 🐛 Troubleshooting

### Docker Model Runner Not Responding
```bash
# Check if enabled in Docker Desktop
# Settings → Features in development → Docker Model Runner

# Verify models
docker model ls

# Test endpoint
curl http://localhost:12434/api/tags
```

### Error: `{"error": "unknown error"}` or 404 errors

This usually means:
1. **Incorrect model name** - Use exact name from `docker model ls`
2. **Model not pulled** - Run `docker model pull <model-name>`
3. **Wrong API endpoint** - Embeddings use `/v1/embeddings`, LLM uses `/api/generate`

### Connection Refused to SurrealDB
- **Solution**: Make sure Docker Desktop is running and SurrealDB extension is started on port 8002
  - Open Docker Desktop → Extensions → SurrealDB → Start
  - Check port configuration in extension settings

### `ModuleNotFoundError` when running scripts
- **Solution**: Make sure virtual environment is activated: `source venv/bin/activate`
- Or use full path: `./venv/bin/python script.py`

### "No relevant information found"
- **Solution**: Make sure WhatsApp messages are loaded first
- Run: `./venv/bin/python load_whatsapp.py`

### Web UI won't start
- **Solution**: Check if port 8080 is available
- Or modify the port in `rag_chat_ui.py`: `ui.run(port=8081)`

## 📊 Port Reference

| Service | Port | Purpose | Model/Details |
|---------|------|---------|---------------|
| **Docker Model Runner** | 12434 | Embeddings | `embeddinggemma` (768D, OpenAI API) |
| **Docker Model Runner** | 12434 | LLM/Chat | `ai/llama3.2:3B-Q4_0` (Ollama API) |
| **SurrealDB** | 8002 | Vector DB | 768-dimensional index |
| **Web UI** | 8080 | Interface | NiceGUI |

## 🔍 Verify Your Setup

### Check All Services
```bash
# 1. Check Docker Model Runner
curl http://localhost:12434/api/tags

# 2. Check SurrealDB (should be running in Docker Desktop on port 8002)
# Look for SurrealDB in Docker Desktop Extensions

# 3. List available models
docker model ls

# 4. Verify data in SurrealDB
python3 verify_surrealdb.py
```

### Test Embeddings (OpenAI API)
```bash
curl http://localhost:12434/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "embeddinggemma",
    "input": "test"
  }'
```

### Test LLM
```bash
curl http://localhost:12434/api/generate -d '{
  "model": "ai/llama3.2:3B-Q4_0",
  "prompt": "Hello",
  "stream": false
}'
```

## 🎯 Alternative Models

### Embedding Models (Docker Model Runner)
```bash
# Current (recommended)
docker model pull embeddinggemma  # 768D, 302M params

# Alternative from HuggingFace
docker model pull hf.co/mungert/all-minilm-l6-v2-gguf  # 384D, 22M params
```

### LLM Models (Docker Model Runner)
```bash
# Meta's Llama 3.2 (recommended)
docker model pull ai/llama3.2:3B-Q4_0

# Coding assistant
docker model pull ai/qwen2.5-coder

# Microsoft's Phi-3
docker model pull ai/phi3

# Small, fast model
docker model pull ai/smollm2
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Getting Started
1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/surrealdb-rag-demo.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Follow the setup instructions in the README

### Development Guidelines

**Code Style:**
- Follow PEP 8 conventions
- Use meaningful variable and function names
- Add docstrings to functions
- Keep functions focused and modular

**Before Submitting:**
1. Test your changes thoroughly
2. Run the scripts to ensure no errors
3. Update documentation if adding new features
4. Include descriptive commit messages

### Areas for Contribution

- **Features**: New chat models, database backends, enhanced UI components
- **Improvements**: Performance optimization, code refactoring, dependency updates
- **Documentation**: Better guides, API documentation, usage examples
- **Bug Fixes**: Report or fix issues you find
- **Tests**: Add unit tests and integration tests

### Submitting Changes

1. Push to your fork
2. Create a Pull Request with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots for UI changes (if applicable)
3. Wait for review and address feedback

### Reporting Issues

When reporting bugs, include:
- Python version and OS
- Steps to reproduce
- Error messages and stack traces
- Your environment details

### Questions?

Open an issue with the label `question` or start a discussion.

## 📝 License

MIT

---

## 📚 Additional Resources


- [Install the SurrealDB Docker Desktop Extension](https://open.docker.com/extensions/marketplace?extensionId=raveendiranrr/surrealdb-docker-extension)
- [Docker Model Runner Documentation](https://docs.docker.com/ai/model-runner/)
- [SurrealDB Documentation](https://surrealdb.com/docs)
- [LangChain Documentation](https://python.langchain.com/)

## 🎉 Quick Tips

1. **First time setup**: Allow 10-15 minutes for model downloads
2. **Performance**: Embeddings are fast, LLM responses may take 5-30 seconds
3. **Model size**: Larger models = better quality but slower responses
4. **Context**: The system retrieves top 3 most relevant messages for context
5. **Privacy**: Everything runs locally - your data never leaves your machine

---

**Made with ❤️ using Docker Model Runner and SurrealDB**

## 🆕 Recent Updates

- ✅ **Simplified Architecture**: Now uses Docker Model Runner exclusively (no Ollama required)
- ✅ **Better Embeddings**: Upgraded to `embeddinggemma` (768D, 302M parameters)
- ✅ **OpenAI API Support**: Custom embeddings class using Docker Model Runner's OpenAI-compatible endpoint
- ✅ **Single Service**: Everything runs on port 12434
- ✅ **Utility Scripts**: Added verification and reset scripts for easier debugging

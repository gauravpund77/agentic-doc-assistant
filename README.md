# 🤖 Agentic AI Document Assistant

A RAG-based PDF Q&A chatbot with User Authentication and Chat History — built with 100% free tools.

![Banner](assets/banner.png)

---

## 🚀 Features

- 📄 PDF Upload & Processing
- 🔍 RAG-based Question Answering (answers only from your PDF)
- 💬 Chat History & Memory (remembers conversation)
- 🔐 JWT User Authentication (Login / Signup)
- 🧠 Context-aware AI Responses
- 🆓 100% Free Stack

---

## 🛠️ Tech Stack

| Technology | Purpose | Cost |
|------------|---------|------|
| Django + DRF | Backend REST API | Free |
| LangChain | AI Framework | Free |
| Groq (llama-3.1) | LLM Model | Free |
| HuggingFace | Embeddings | Free |
| ChromaDB | Vector Database | Free |
| JWT | Authentication | Free |
| SQLite | Database | Free |

---

## 📁 Project Structure

agentic-doc-assistant/
├── config/
│   ├── manage.py
│   ├── assistant/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── ingestion.py
│   │   ├── embeddings.py
│   │   └── rag_chain.py
│   └── config/
│       ├── settings.py
│       └── urls.py
├── requirements.txt
├── .gitignore
└── README.md


---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/gauravpund77/agentic-doc-assistant.git
cd agentic-doc-assistant
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create config.env file
```bash
GROQ_API_KEY=your_groq_api_key_here
DJANGO_SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 5. Run migrations
```bash
cd config
python manage.py migrate
```

### 6. Start server
```bash
python manage.py runserver
```

---

## 📡 API Endpoints

### Auth APIs
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | ❌ |
| POST | `/api/auth/login/` | Login & get tokens | ❌ |
| POST | `/api/auth/refresh/` | Refresh access token | ❌ |
| POST | `/api/auth/logout/` | Logout user | ✅ |
| GET  | `/api/auth/profile/` | Get user profile | ✅ |

### Document APIs
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/upload/` | Upload PDF file | ✅ |

### Chat APIs
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/session/new/` | Create new chat session | ✅ |
| POST | `/api/ask/` | Ask question from PDF | ✅ |
| GET  | `/api/history/<session_id>/` | Get chat history | ✅ |

### Health
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/health/` | Health check | ❌ |

---

## 🧪 How to Test (curl)

### Register
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@gmail.com", "password": "test123", "password2": "test123"}'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}'
```

### Upload PDF
```bash
curl -X POST http://127.0.0.1:8000/api/upload/ \
  -H "Authorization: Bearer your_access_token" \
  -F "file=@document.pdf"
```

### Ask Question
```bash
curl -X POST http://127.0.0.1:8000/api/ask/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "session_id": "your_session_id"}'
```

---

## 🔄 How It Works

User registers / logs in → gets JWT token
User uploads PDF → stored in media/ folder
PDF is chunked → embeddings stored in ChromaDB
User asks question → relevant chunks retrieved
Groq LLM answers → only from PDF content
Answer + history saved → in SQLite DB

# Company Chatbot

A production-ready RAG (Retrieval-Augmented Generation) chatbot that lets your team ask questions in plain English and get accurate answers grounded in your company's own documents — with citations back to the source.

---

## What does it do?

1. An admin uploads documents (PDFs, Markdown, CSVs, text files).
2. The system chunks and indexes them into a vector database.
3. Users ask questions through a chat interface.
4. The AI retrieves the most relevant document chunks, then generates a grounded answer with source citations.

No hallucinations about things your documents don't cover. No sharing company knowledge with third-party training pipelines beyond the embedding call.

---

## Features

- **Chat with your documents** — RAG-powered Q&A using OpenAI `gpt-4o-mini`
- **Role-based access control** — superadmin, admin, and user roles
- **Group-based document isolation** — HR sees HR docs, Engineering sees Engineering docs
- **Dual login** — email/password or Google OAuth2
- **Persistent chat history** — sessions survive page reloads
- **Flexible storage** — MinIO locally, swap to AWS S3/DynamoDB in the admin panel
- **Fully containerised** — one `docker compose up` to run everything

---

## Architecture

```
Browser
  └── React 18 / TypeScript / Tailwind (port 80)
        └── FastAPI backend (port 8000)
              ├── PostgreSQL  — users, groups, document metadata
              ├── Qdrant      — vector store for semantic search (port 6333)
              ├── DynamoDB    — chat sessions & message history (port 8001)
              └── MinIO       — raw document storage (port 9000)
```

| Component | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui |
| Backend | FastAPI (Python 3.12) |
| Auth | JWT (email/password) + Google OAuth2 |
| User & document DB | PostgreSQL (SQLAlchemy + Alembic) |
| Vector store | Qdrant |
| Chat history | DynamoDB Local / AWS DynamoDB |
| Document storage | MinIO (local) / AWS S3 |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | OpenAI `gpt-4o-mini` |

---

## User roles

| Role | What they can do |
|---|---|
| **superadmin** | Everything — system settings, create/manage groups, promote admins, mark documents public |
| **admin** | Upload documents, manage members in their own groups |
| **user** | Chat only — queries documents in their groups plus any public documents |

### Document access model

Documents belong to **groups** (e.g. HR, Engineering, Finance). Users are members of groups. When a user sends a message, the RAG search is scoped only to their groups plus documents marked **public** by a superadmin. Admins cannot see groups they don't manage.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Google OAuth2 Client ID](https://console.cloud.google.com/) *(optional — email/password login works without it)*

---

## Quick start

### 1. Clone and configure

```bash
git clone <repo-url>
cd <repo-directory>
cp .env.example .env
```

Open `.env` and fill in the three required values:

```env
SECRET_KEY=          # any long random string — run: openssl rand -hex 32
OPENAI_API_KEY=      # sk-...

SUPERADMIN_EMAIL=    # your email
SUPERADMIN_USERNAME= # your chosen username
SUPERADMIN_PASSWORD= # your chosen password
```

Everything else can stay as-is for local development.

### 2. Start everything

```bash
docker compose up --build
```

First boot takes a few minutes while Docker pulls images and npm installs packages. Subsequent starts are fast.

### 3. Open the app

| What | URL |
|---|---|
| **Chatbot** | http://localhost |
| **API docs** (Swagger) | http://localhost:8000/docs |
| **MinIO console** | http://localhost:9001 |
| **Qdrant dashboard** | http://localhost:6333/dashboard |

Log in with the superadmin credentials you set in `.env`. The superadmin account is created automatically on first boot.

---

## Uploading documents and making them available

1. Log in as superadmin (or a group admin).
2. Go to **Admin panel → Documents** and upload a file.  
   Supported formats: PDF, TXT, Markdown, CSV.
3. Wait for the status to change `pending → indexed` — this means the document has been chunked and embedded into Qdrant.
4. Go to **Admin panel → Groups**, select a group, and assign the document to it.  
   Alternatively, mark it **public** (superadmin only) to make it available to all users.

Users in that group can now ask questions about the document.

---

## Google OAuth setup (optional)

1. Open [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials.
2. Create an **OAuth 2.0 Client ID** (Web application).
3. Add `http://localhost` to **Authorized JavaScript origins**.
4. Copy the Client ID into `.env`:
   ```env
   GOOGLE_CLIENT_ID=<your-client-id>
   VITE_GOOGLE_CLIENT_ID=<same-value>
   GOOGLE_CLIENT_SECRET=<your-client-secret>
   ```
5. Rebuild the frontend:
   ```bash
   docker compose build --no-cache frontend && docker compose up -d
   ```

---

## Switching to AWS storage (production)

By default everything runs locally. When you're ready to move to the cloud:

1. Log in as superadmin and go to **Admin panel → Settings**.
2. Switch **Storage backend** from MinIO to **AWS S3**.
3. Switch **DynamoDB mode** from Local to **AWS**.

Add your AWS credentials to `.env`:

```env
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_S3_BUCKET=
AWS_DYNAMO_REGION=us-east-1
```

Changes take effect immediately for new requests. Existing data is not migrated automatically.

---

## Development without Docker

If you want to iterate faster on the backend or frontend without rebuilding containers:

```bash
# Start only the infrastructure services
docker compose up postgres qdrant dynamodb minio

# Backend (in a separate terminal)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

The frontend dev server runs on http://localhost:5173 and proxies API calls to the backend.

---

## Project structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/        # Route handlers — auth, users, documents, groups, chat, settings
│   │   ├── core/          # Config, JWT security, dependency injection
│   │   ├── db/            # SQLAlchemy models, session factory, seed data
│   │   ├── schemas/       # Pydantic request/response models
│   │   └── services/      # Business logic — RAG pipeline, ingest, vector search,
│   │                      #   storage, chat history, access control
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/           # Axios API clients
│       ├── components/    # Chat UI, Admin panel, shadcn/ui primitives
│       ├── pages/         # LoginPage, ChatPage, AdminPage
│       ├── store/         # Zustand auth store
│       └── types/         # TypeScript interfaces
├── docker-compose.yaml
└── .env.example           # Copy this to .env and fill in your values
```

---

## Exercises

The `exercises/` directory contains standalone scripts from an earlier exploration phase of this project. They demonstrate individual OpenAI API features (text completions, image understanding, JSON mode, PDF parsing, chatbots) and are useful as reference or learning material but are not part of the main application.

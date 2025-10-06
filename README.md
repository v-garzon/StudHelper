# StudHelper - AI Study Assistant

## Project Overview

**Problem:** Saiera.com charges $10K-50K/month for AI tutoring
**Solution:** DIY alternative using OpenAI APIs for $15-30/month
**Savings:** 300x cost reduction

### Core Concept

Class-based AI learning platform where students upload study materials (PDFs, docs, videos) and chat with an AI tutor that has knowledge of their specific content using RAG (Retrieval Augmented Generation).

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                  Vue 3 + Tailwind + Pinia                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/REST
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AUTHENTICATION                              │
│              Firebase (OAuth + Email/Password)                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ JWT Token
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API                                │
│                  FastAPI + PostgreSQL                           │
└─────┬──────────────┬──────────────┬─────────────────────────────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────────┐  ┌─────────────────┐
│ OpenAI   │  │ Vector Store │  │ File Storage    │
│ GPT-4o   │  │ ChromaDB     │  │ Local/S3        │
└──────────┘  └──────────────┘  └─────────────────┘
```

---

## Database Schema

```
┌──────────────┐
│    USERS     │
├──────────────┤
│ id           │──┐
│ email        │  │
│ name         │  │
│ surname      │  │
│ alias        │  │
│ firebase_uid │  │
│ auth_provider│  │
│ email_verified│ │
└──────────────┘  │
                  │
       ┌──────────┴──────────┬─────────────┬──────────────┐
       │                     │             │              │
       ▼                     ▼             ▼              ▼
┌──────────────┐      ┌─────────────┐  ┌──────────┐  ┌────────────────┐
│   CLASSES    │      │  DOCUMENTS  │  │CHAT_MSGS │  │ USAGE_RECORDS  │
├──────────────┤      ├─────────────┤  ├──────────┤  ├────────────────┤
│ id           │──┐   │ id          │  │ id       │  │ id             │
│ name         │  │   │ filename    │  │ session_id│ │ user_id        │
│ class_code   │  │   │ scope       │  │ content  │  │ tokens_used    │
│ owner_id     │──┘   │ class_id    │  │ is_user  │  │ cost           │
└──────────────┘      │ uploaded_by │  └──────────┘  │ is_sponsored   │
       │              └─────────────┘                 └────────────────┘
       │
       ▼
┌──────────────────────┐
│ CLASS_MEMBERSHIPS    │
├──────────────────────┤
│ id                   │
│ user_id              │
│ class_id             │
│ is_manager           │
│ can_chat             │
│ daily_token_limit    │
│ is_sponsored         │
└──────────────────────┘
```

---

## Backend Folder Structure

```
Backend/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Environment configuration
│   ├── database.py                # DB connection
│   ├── firebase_admin.py          # Firebase token verification
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   └── __init__.py            # User, Class, Document, etc.
│   │
│   ├── schemas/                   # Pydantic validation schemas
│   │   └── __init__.py            # Request/Response models
│   │
│   ├── routes/                    # API endpoints
│   │   ├── auth.py                # Authentication routes
│   │   ├── classes.py             # Class management
│   │   ├── permissions.py         # Permission management
│   │   ├── chat.py                # Chat with AI
│   │   ├── documents.py           # Document upload/management
│   │   └── usage.py               # Usage tracking
│   │
│   ├── services/                  # Business logic
│   │   ├── auth_service.py        # User auth & management
│   │   ├── permission_service.py  # Permission checks
│   │   ├── chat_service.py        # AI chat orchestration
│   │   ├── document_service.py    # Document processing
│   │   ├── openai_service.py      # OpenAI API integration
│   │   └── usage_service.py       # Token tracking
│   │
│   ├── utils/                     # Helper functions
│   │   ├── security.py            # JWT, password hashing
│   │   ├── file_processing.py     # PDF/Doc extraction
│   │   └── vector_operations.py   # Embedding & search
│   │
│   └── migrations/                # Alembic database migrations
│       └── versions/
│
├── uploads/                       # Temporary file storage
├── requirements.txt
├── .env
└── firebase-credentials.json
```

---

## Frontend Folder Structure

```
Vue-Frontend/
├── src/
│   ├── main.js
│   ├── App.vue
│   │
│   ├── config/
│   │   └── firebase.js            # Firebase SDK initialization
│   │
│   ├── views/                     # Page components
│   │   ├── LandingView.vue        # Login/Register
│   │   ├── DashboardView.vue      # Main dashboard
│   │   └── HelpView.vue           # Documentation
│   │
│   ├── components/
│   │   ├── features/
│   │   │   ├── landing/
│   │   │   │   ├── LoginForm.vue
│   │   │   │   └── RegisterForm.vue
│   │   │   │
│   │   │   └── dashboard/
│   │   │       ├── Sidebar.vue
│   │   │       ├── UserMenu.vue
│   │   │       ├── ChatInterface.vue
│   │   │       ├── WelcomeScreen.vue
│   │   │       └── VerificationBanner.vue
│   │   │
│   │   ├── ui/                    # Reusable UI components
│   │   │   ├── ModalWrapper.vue
│   │   │   └── SlideOutWrapper.vue
│   │   │
│   │   └── shared/                # Base components
│   │       ├── BaseButton.vue
│   │       ├── BaseInput.vue
│   │       └── LoadingSpinner.vue
│   │
│   ├── stores/                    # Pinia state management
│   │   ├── auth.js                # User authentication
│   │   ├── classes.js             # Class data
│   │   └── ui.js                  # UI state (modals, etc.)
│   │
│   ├── services/                  # API communication
│   │   ├── api.js                 # Axios configuration
│   │   └── auth/
│   │       └── authService.js     # Auth API calls
│   │
│   ├── router/
│   │   └── index.js               # Vue Router
│   │
│   ├── composables/               # Reusable composition functions
│   ├── utils/                     # Helper functions
│   └── assets/                    # Static assets
│
├── package.json
├── vite.config.js
├── tailwind.config.js
└── .env
```

---

## API Endpoints

### Authentication

```
POST   /api/v1/auth/register              # Email/password registration
POST   /api/v1/auth/login                 # Email/password login
POST   /api/v1/auth/firebase-login        # Firebase OAuth login
POST   /api/v1/auth/logout                # Logout
GET    /api/v1/auth/me                    # Get current user
PUT    /api/v1/auth/profile               # Update profile
DELETE /api/v1/auth/account               # Delete account
```

### Classes

```
POST   /api/v1/classes                    # Create class
GET    /api/v1/classes                    # List user's classes
POST   /api/v1/classes/join               # Join class by code
GET    /api/v1/classes/{id}               # Get class details
DELETE /api/v1/classes/{id}               # Delete class
```

### Permissions

```
GET    /api/v1/classes/{id}/members       # List class members
PUT    /api/v1/classes/{id}/members/{uid} # Update permissions
PUT    /api/v1/classes/{id}/sponsorship   # Toggle sponsorship
```

### Documents

```
POST   /api/v1/documents/classes/{id}/upload     # Upload class doc
POST   /api/v1/documents/sessions/{id}/upload    # Upload chat doc
GET    /api/v1/documents/classes/{id}            # List class docs
GET    /api/v1/documents/sessions/{id}           # List session docs
DELETE /api/v1/documents/{id}                    # Delete document
```

### Chat

```
POST   /api/v1/chat/sessions                     # Create chat session
GET    /api/v1/chat/sessions                     # List sessions
GET    /api/v1/chat/sessions/{id}                # Get session
POST   /api/v1/chat/sessions/{id}/messages       # Send message
GET    /api/v1/chat/sessions/{id}/messages       # Get history
```

### Usage Tracking

```
GET    /api/v1/usage/my-usage                    # Personal usage
GET    /api/v1/usage/classes/{id}/members        # Class usage (managers)
GET    /api/v1/usage/classes/{id}/limits         # Current limits
PUT    /api/v1/usage/classes/{id}/limits/{uid}   # Update limits
```

---

## Tech Stack

### Frontend

- **Framework:** Vue 3 (Composition API)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State:** Pinia
- **Routing:** Vue Router
- **HTTP:** Axios
- **Auth:** Firebase SDK

### Backend

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migration:** Alembic
- **Auth:** Firebase Admin SDK + JWT
- **AI:** OpenAI GPT-4o-mini
- **Embeddings:** OpenAI text-embedding-3-small
- **Vectors:** ChromaDB / FAISS

---

## Authentication Flow

```
┌──────────┐
│  USER    │
└────┬─────┘
     │
     ├─ Email/Password ─────────────────────┐
     │                                       │
     │  1. Register with Firebase            │
     │  2. Firebase sends verification email │
     │  3. Firebase returns idToken          │
     │                                       │
     └─ OAuth (Google/Microsoft) ────────────┤
        1. Firebase handles OAuth popup      │
        2. Firebase returns idToken          │
                                             ▼
                                    ┌────────────────┐
                                    │   FRONTEND     │
                                    │ Send idToken   │
                                    └────────┬───────┘
                                             │
                                             ▼
                                    ┌────────────────┐
                                    │    BACKEND     │
                                    │ Verify Token   │
                                    │ Create/Get User│
                                    │ Return JWT     │
                                    └────────┬───────┘
                                             │
                                             ▼
                                    ┌────────────────┐
                                    │  POSTGRESQL    │
                                    │ Store User Data│
                                    └────────────────┘
```

---

## RAG Pipeline

```
┌─────────────────┐
│ Document Upload │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Extraction │  (PyPDF2, python-docx, Whisper)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Chunking     │  (1000-1500 chars, 200 overlap)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Embedding     │  (OpenAI text-embedding-3-small)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │  (ChromaDB/FAISS)
└─────────────────┘

┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Embedding │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Similarity Search│ (Top-K relevant chunks)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GPT-4o-mini     │  (Question + Context → Answer)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Response   │
└─────────────────┘
```

---

## Frontend - Completed Features

### Landing Page

- [X] Login form with Firebase OAuth (Google, Microsoft)
- [X] Register form with email/password
- [X] Password strength indicator (red/yellow/green)
- [X] Password requirements validation (6 chars, 1 uppercase, 1 number)
- [X] Password confirmation matching
- [X] Password visibility toggle (hold to show)
- [X] Detailed error messages
- [X] Email verification flow

### Dashboard

- [X] Responsive layout (sidebar + main content)
- [X] User menu with alias/name display
- [X] Email verification banner (floating, non-intrusive)
- [X] Welcome screen
- [X] Route guards (auth protection)

### State Management

- [X] Auth store (user, token, authentication)
- [X] UI store (sidebar, modals, slide-outs)
- [X] Class store structure

---

## Frontend - Planned Features

### Class Management

- [ ] Create class wizard (3-step modal)
  - [ ] Upload knowledge base
  - [ ] Set permissions
  - [ ] Configure billing/limits
- [ ] Join class by code
- [ ] Class list view
- [ ] Class settings panel (slide-out)

### Document Management

- [ ] Drag-and-drop file upload
- [ ] Upload progress tracking
- [ ] Document list view
- [ ] Document preview
- [ ] YouTube video integration
- [ ] Processing status indicators

### Chat Interface

- [ ] Real-time chat UI
- [ ] Message history
- [ ] Context indicators (which documents used)
- [ ] Token usage display
- [ ] Export chat history

### User Settings

- [ ] Profile editor (name, surname, alias)
- [ ] Change password
- [ ] Link/unlink OAuth accounts
- [ ] Delete account

### Analytics

- [ ] Personal usage dashboard
- [ ] Class usage overview (for managers)
- [ ] Token consumption charts
- [ ] Cost tracking

---

## Backend - Completed Features

### Core Infrastructure

- [X] FastAPI application setup
- [X] PostgreSQL database connection
- [X] SQLAlchemy ORM models
- [X] Alembic migrations
- [X] CORS configuration

### Authentication

- [X] Firebase Admin SDK integration
- [X] Firebase token verification
- [X] Email/password registration
- [X] Email/password login
- [X] Firebase OAuth integration
- [X] JWT token generation
- [X] Password strength validation
- [X] User CRUD operations

### Database Models

- [X] User model (with Firebase integration)
- [X] Class model
- [X] ClassMembership model
- [X] Document model (dual-scope: class/chat)
- [X] ChatSession model
- [X] ChatMessage model
- [X] UsageRecord model
- [X] ClassUsageTracker model

---

## Backend - Planned Features

### Class Management

- [ ] Class creation endpoint
- [ ] Class code generation
- [ ] Join class validation
- [ ] List user classes
- [ ] Delete class (owner only)

### Permission System

- [ ] Permission middleware
- [ ] Update member permissions
- [ ] Sponsorship toggle
- [ ] Token limit management
- [ ] Manager dashboard data

### Document Processing

- [ ] PDF text extraction (PyPDF2)
- [ ] Word document processing (python-docx)
- [ ] PowerPoint processing (python-pptx)
- [ ] YouTube transcription (Whisper)
- [ ] Text chunking (LangChain)
- [ ] Embedding generation (OpenAI)
- [ ] Vector storage (ChromaDB)

### Chat System

- [ ] Create chat session
- [ ] Send message endpoint
- [ ] Retrieve context from vectors
- [ ] OpenAI chat integration
- [ ] Stream responses (SSE)
- [ ] Message history retrieval

### Usage Tracking

- [ ] Token counting per request
- [ ] Daily/weekly/monthly tracking
- [ ] Limit enforcement
- [ ] Usage reset (midnight CET)
- [ ] Sponsorship billing logic
- [ ] Overflow detection

---

## Development Phases

### Phase 1: Foundation (Completed)

- Authentication system
- Database schema
- Basic frontend structure
- Firebase integration

### Phase 2: Class System (Current)

- Class creation/joining
- Permission management
- Member management
- UI components for class management

### Phase 3: Document Processing

- File upload endpoints
- Text extraction pipeline
- Vector embedding generation
- ChromaDB integration

### Phase 4: Chat & AI

- Chat interface
- OpenAI integration
- RAG implementation
- Context retrieval
- Streaming responses

### Phase 5: Usage & Limits

- Token tracking
- Usage analytics
- Limit enforcement
- Billing logic

### Phase 6: Polish & Deploy

- Error handling
- Loading states
- Testing
- Documentation
- Deployment

---

## Environment Variables

### Backend (.env)

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/studhelper
SECRET_KEY=your-jwt-secret-key
OPENAI_API_KEY=your-openai-key
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

---

## Running the Project

### Backend

```bash
cd Backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd Vue-Frontend
npm install
npm run dev
```

---

## Cost Estimates (Monthly)

**OpenAI API:**

- GPT-4o-mini: $0.15 input / $0.60 output per 1M tokens
- Embeddings: $0.02 per 1M tokens

**Usage Example (Single User):**

- 100 documents (~1M tokens) → $0.02 embedding cost
- 1000 questions (~500K input, 1M output) → $0.075 + $0.60 = $0.68
- **Total: ~$5-15/month** (vs $10K-50K for Saiera)

---

## Security Features

- Firebase authentication (OAuth + Email)
- JWT token authorization
- Password hashing (bcrypt)
- Firebase token verification
- Route guards
- CORS protection
- SQL injection prevention (ORM)
- XSS protection
- Rate limiting (Firebase built-in)

---

## Future Enhancements

- Mobile app (React Native)
- Real-time collaboration
- Advanced analytics
- AI model selection (GPT-4, Claude, etc.)
- Custom AI personalities
- Multi-language support
- Voice chat
- Study group features
- Flashcard generation
- Quiz creation from documents

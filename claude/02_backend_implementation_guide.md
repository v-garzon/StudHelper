# StudHelper Backend: Technical Implementation Guide

**Phase 1 - Core Platform (2-4 Week Sprint)**

## **Project Overview**

StudHelper is a class-based AI learning platform with flexible permissions and granular usage tracking. This implementation focuses on** ****core functionality** with** ****rapid deployment** capabilities.

 **Timeline** : 2-4 weeks for MVP** ** **Focus** : Technical foundation, not business features** ** **Architecture** : Scalable, testable, production-ready

---

## **Requirements Specification**

### **Core Features**

1. **User Management** : Register, login, logout, profile management
2. **Class System** : Create/join classes with unique codes
3. **Permission Management** : Granular class-based permissions
4. **Dual-Document System** : Class-wide + chat-specific documents
5. **AI Chat** : Context-aware conversations with document integration
6. **Usage Tracking** : Per-class, per-user token limits and monitoring

### **Technical Constraints**

* **Single AI Model** : ChatGPT-4o-mini only (no tier selection)
* **Single Embedder** : Small embedding model for RAG
* **No Payment Integration** : Usage limits only, no billing
* **Madrid Timezone** : Usage resets at 00:00 CET
* **PostgreSQL** : Primary database
* **FastAPI** : REST API framework

---

## **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (Future)      │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   OpenAI API    │    │   Vector Store  │
                       │   (GPT-4o-mini) │    │   (Chroma/FAISS)│
                       └─────────────────┘    └─────────────────┘
```

### **Data Flow Pipeline**

```
Document Upload → Text Extraction → Chunking → Vectorization → Storage
                                                                  │
Chat Message → Permission Check → Context Retrieval → AI Response ←┘
                     │                                      │
             Usage Tracking ←──────────────────────── Token Counting
```

---

## **Folder Structure**

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── database.py             # Database configuration
│   ├── config.py               # Environment configuration
│   │
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── class_models.py
│   │   ├── chat_models.py
│   │   └── document_models.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── classes.py
│   │   ├── chat.py
│   │   └── documents.py
│   │
│   ├── routes/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── classes.py
│   │   ├── permissions.py
│   │   ├── chat.py
│   │   ├── documents.py
│   │   └── usage.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── permission_service.py
│   │   ├── chat_service.py
│   │   ├── document_service.py
│   │   ├── openai_service.py
│   │   └── usage_service.py
│   │
│   ├── utils/                  # Helper functions
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── file_processing.py
│   │   └── vector_operations.py
│   │
│   └── migrations/             # Database migrations
│       ├── versions/
│       └── alembic.ini
│
├── tests/                      # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py            # Test configuration
│   ├── test_auth.py
│   ├── test_classes.py
│   ├── test_permissions.py
│   ├── test_chat.py
│   ├── test_documents.py
│   ├── test_usage.py
│   └── test_integration.py
│
├── uploads/                    # Document storage
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── docker-compose.yml        # Local development
├── Dockerfile                # Production build
└── README.md                 # Setup instructions
```

---

## **API Endpoints Specification**

### **Authentication (`/api/v1/auth`)**

```
POST   /register              # Create user account
POST   /login                 # JWT authentication
POST   /logout                # Invalidate token
GET    /me                    # Current user profile
PUT    /profile               # Update profile
DELETE /account               # Delete account
```

### **Class Management (`/api/v1/classes`)**

```
POST   /                      # Create new class
GET    /                      # List user's classes
POST   /join                  # Join class by code
GET    /{class_id}            # Class details
DELETE /{class_id}            # Delete class (owner only)
```

### **Permission Management (`/api/v1/classes/{class_id}`)**

```
GET    /members               # List class members
PUT    /members/{user_id}     # Update member permissions
PUT    /sponsorship           # Enable/disable sponsorship
GET    /permissions           # Get permission templates
```

### **Document System (`/api/v1/documents`)**

```
POST   /classes/{class_id}/upload       # Upload class document
POST   /sessions/{session_id}/upload    # Upload chat document
GET    /classes/{class_id}              # List class documents
GET    /sessions/{session_id}           # List session documents
DELETE /documents/{doc_id}              # Delete document
```

### **Chat System (`/api/v1/chat`)**

```
POST   /sessions              # Create chat session
GET    /sessions              # List user sessions
GET    /sessions/{session_id} # Session details
POST   /sessions/{session_id}/messages # Send message
GET    /sessions/{session_id}/messages # Message history
```

### **Usage Tracking (`/api/v1/usage`)**

```
GET    /my-usage              # Personal usage stats
GET    /classes/{class_id}/members # Class usage overview (managers)
GET    /classes/{class_id}/limits  # Current limits and usage
PUT    /classes/{class_id}/limits/{user_id} # Update user limits
```

---

## **Database Schema**

### **Core Models**

```python
User
├── id, email, username, hashed_password
├── full_name, preferred_ai_tier
├── created_at, is_active

Class
├── id, name, description, class_code
├── owner_id, created_at, is_active

ClassMembership
├── id, user_id, class_id, joined_at
├── is_manager, can_read, can_chat
├── max_concurrent_chats, can_share_class
├── is_sponsored, daily/weekly/monthly_token_limits

ClassUsageTracker
├── id, user_id, class_id
├── daily/weekly/monthly_tokens_used
├── last_daily/weekly/monthly_reset

Document
├── id, filename, file_path, file_type
├── scope (CLASS/CHAT), class_id, session_id
├── uploaded_by, processing_status

ChatSession
├── id, title, user_id, class_id
├── ai_tier, created_at, updated_at

ChatMessage
├── id, session_id, content, is_user
├── timestamp, response_time_ms, context_used

UsageRecord
├── id, user_id, model_name, operation_type
├── input_tokens, output_tokens, cost
├── billed_to_user_id, is_sponsored, is_overflow
```

---

## **Development Timeline (2-4 Weeks)**

### **Week 1: Foundation**

* Database models and migrations
* User authentication system
* Basic class creation/joining
* Core test infrastructure

### **Week 2: Permissions & Documents**

* Permission service implementation
* Class membership management
* Document upload and processing
* Vector store integration

### **Week 3: Chat System**

* Chat session creation
* AI integration (ChatGPT-4o-mini)
* Document context retrieval (RAG)
* Message persistence

### **Week 4: Usage & Polish**

* Usage tracking implementation
* Limit enforcement
* Manager dashboard endpoints
* Integration testing and deployment

---

## **Scalability Considerations**

### **Database Optimization**

```python
# Essential indexes
CREATE INDEX idx_class_memberships_user_class ON class_memberships(user_id, class_id);
CREATE INDEX idx_usage_tracker_user_class ON class_usage_trackers(user_id, class_id);
CREATE INDEX idx_chat_sessions_class ON chat_sessions(class_id, created_at);
CREATE INDEX idx_documents_class_scope ON documents(class_id, scope);
```

### **Caching Strategy**

* **Redis** : Session storage, permission caching
* **Application** : Class membership lookup caching
* **Database** : Connection pooling, prepared statements

### **File Storage**

* **Local** : Development and small deployments
* **S3/MinIO** : Production scalability
* **CDN** : Static document serving

---

## **Testing Strategy**

### **Test Coverage Goals**

```
Unit Tests:        80%+ coverage
Integration Tests: All API endpoints
End-to-End Tests:  Critical user flows
Performance Tests: Chat response times
Load Tests:        Concurrent user handling
```

### **Test Structure**

```python
# Example test organization
tests/
├── unit/          # Service and utility tests
├── integration/   # API endpoint tests
├── fixtures/      # Test data and mocks
└── performance/   # Load and stress tests
```

### **Rapid Testing Features**

* **Pytest fixtures** : Database and user setup
* **Factory patterns** : Test data generation
* **Mock services** : OpenAI API responses
* **Test database** : Isolated test environment
* **CI/CD pipeline** : Automated testing on commits

---

## **Production Deployment**

### **Environment Configuration**

```bash
# Required environment variables
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
UPLOAD_PATH=/app/uploads
REDIS_URL=redis://localhost:6379
```

### **Docker Deployment**

```yaml
# docker-compose.production.yml
version: '3.8'
services:
  backend:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/studhelper
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: studhelper
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

---

## **Key Implementation Decisions**

### **Simplified for Speed**

* **Single AI model** : No tier complexity
* **Basic file storage** : Local filesystem initially
* **JWT authentication** : No OAuth complexity
* **PostgreSQL only** : No multi-database complexity

### **Extensibility Built-In**

* **Service pattern** : Easy to add new AI models
* **Permission system** : Ready for complex workflows
* **Document scoping** : Supports advanced features
* **Usage tracking** : Ready for billing integration

### **Performance Focus**

* **Async FastAPI** : High concurrency
* **Efficient vector operations** : Fast document search
* **Connection pooling** : Database optimization
* **Structured logging** : Production monitoring

---

This implementation provides a** ****solid foundation** that can be built in 2-4 weeks while maintaining** ****production readiness**and** ****clear extension points** for future features. The architecture supports rapid iteration and testing while remaining scalable for growth.

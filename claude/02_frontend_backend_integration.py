# StudHelper Frontend-Backend Integration Files

## 1. NEW FILE: utils/config.py
"""Configuration management for StudHelper frontend."""

import os
from typing import Optional

class Config:
    """Application configuration."""
    
    # Backend API settings
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    API_BASE_URL: str = f"{BACKEND_URL}/api/v1"
    
    # API endpoints
    AUTH_LOGIN_URL: str = f"{API_BASE_URL}/auth/login"
    AUTH_REGISTER_URL: str = f"{API_BASE_URL}/auth/register"
    AUTH_ME_URL: str = f"{API_BASE_URL}/auth/me"
    
    DOCUMENTS_UPLOAD_URL: str = f"{API_BASE_URL}/documents/upload"
    DOCUMENTS_YOUTUBE_URL: str = f"{API_BASE_URL}/documents/youtube"
    DOCUMENTS_LIST_URL: str = f"{API_BASE_URL}/documents/"
    
    AI_CHAT_URL: str = f"{API_BASE_URL}/ai/chat"
    AI_CHAT_STREAM_URL: str = f"{API_BASE_URL}/ai/chat/stream"
    AI_SESSIONS_URL: str = f"{API_BASE_URL}/ai/sessions"
    
    RAG_SEARCH_URL: str = f"{API_BASE_URL}/rag/search"
    USAGE_ANALYTICS_URL: str = f"{API_BASE_URL}/usage/analytics"
    
    # Frontend settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    SUPPORTED_FILE_TYPES: list = ['.pdf', '.docx', '.pptx', '.txt', '.md']
    
    # Session settings
    TOKEN_KEY: str = "studhelper_token"
    USER_KEY: str = "studhelper_user"
    
    @classmethod
    def get_headers(cls, token: Optional[str] = None) -> dict:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    @classmethod
    def get_file_headers(cls, token: Optional[str] = None) -> dict:
        """Get headers for file upload requests."""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

## 2. NEW FILE: utils/api_client.py
"""API client for backend communication."""

import streamlit as st
import requests
import json
from typing import Dict, Any, Optional, List
from .config import Config

class APIClient:
    """Client for backend API communication."""
    
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
    
    def _get_token(self) -> Optional[str]:
        """Get authentication token from session state."""
        return st.session_state.get(self.config.TOKEN_KEY)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response."""
        try:
            if response.status_code == 401:
                # Clear invalid token
                if self.config.TOKEN_KEY in st.session_state:
                    del st.session_state[self.config.TOKEN_KEY]
                if self.config.USER_KEY in st.session_state:
                    del st.session_state[self.config.USER_KEY]
                return {"success": False, "error": "Authentication required"}
            
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid response format"}
    
    # Authentication methods
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user."""
        try:
            response = self.session.post(
                self.config.AUTH_LOGIN_URL,
                json={"email": email, "password": password},
                headers=self.config.get_headers()
            )
            
            result = self._handle_response(response)
            
            if result["success"]:
                token = result["data"]["access_token"]
                user = result["data"]["user"]
                
                # Store in session state
                st.session_state[self.config.TOKEN_KEY] = token
                st.session_state[self.config.USER_KEY] = user
            
            return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def register(self, email: str, username: str, password: str) -> Dict[str, Any]:
        """Register new user."""
        try:
            response = self.session.post(
                self.config.AUTH_REGISTER_URL,
                json={"email": email, "username": username, "password": password},
                headers=self.config.get_headers()
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user info."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "No authentication token"}
        
        try:
            response = self.session.get(
                self.config.AUTH_ME_URL,
                headers=self.config.get_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def logout(self):
        """Logout user."""
        if self.config.TOKEN_KEY in st.session_state:
            del st.session_state[self.config.TOKEN_KEY]
        if self.config.USER_KEY in st.session_state:
            del st.session_state[self.config.USER_KEY]
    
    # Document methods
    def upload_document(self, file_data: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Upload document to backend."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            files = {"file": (filename, file_data, content_type)}
            response = self.session.post(
                self.config.DOCUMENTS_UPLOAD_URL,
                files=files,
                headers=self.config.get_file_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_youtube_video(self, url: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Add YouTube video."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            data = {"url": url}
            if title:
                data["title"] = title
            
            response = self.session.post(
                self.config.DOCUMENTS_YOUTUBE_URL,
                json=data,
                headers=self.config.get_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_documents(self) -> Dict[str, Any]:
        """Get user documents."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            response = self.session.get(
                self.config.DOCUMENTS_LIST_URL,
                headers=self.config.get_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_document(self, document_id: int) -> Dict[str, Any]:
        """Delete document."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            response = self.session.delete(
                f"{self.config.DOCUMENTS_LIST_URL}{document_id}",
                headers=self.config.get_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Chat methods
    def send_chat_message(self, message: str, mode: str = "economic", session_id: Optional[int] = None) -> Dict[str, Any]:
        """Send chat message."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            data = {
                "message": message,
                "mode": mode,
                "include_context": True
            }
            if session_id:
                data["session_id"] = session_id
            
            response = self.session.post(
                self.config.AI_CHAT_URL,
                json=data,
                headers=self.config.get_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_chat_sessions(self) -> Dict[str, Any]:
        """Get chat sessions."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            response = self.session.get(
                self.config.AI_SESSIONS_URL,
                headers=self.config.get_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_chat_history(self, session_id: int) -> Dict[str, Any]:
        """Get chat history for session."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            response = self.session.get(
                f"{self.config.AI_SESSIONS_URL}/{session_id}/history",
                headers=self.config.get_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # RAG methods
    def search_documents(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search documents."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            data = {
                "query": query,
                "limit": limit
            }
            
            response = self.session.post(
                self.config.RAG_SEARCH_URL,
                json=data,
                headers=self.config.get_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Usage methods
    def get_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics."""
        token = self._get_token()
        if not token:
            return {"success": False, "error": "Authentication required"}
        
        try:
            response = self.session.get(
                f"{self.config.USAGE_ANALYTICS_URL}?days={days}",
                headers=self.config.get_headers(token)
            )
            return self._handle_response(response)
        
        except Exception as e:
            return {"success": False, "error": str(e)}

## 3. NEW FILE: components/auth_components.py
"""Authentication components for Streamlit frontend."""

import streamlit as st
from utils.api_client import APIClient
from utils.config import Config

def render_auth_page():
    """Render authentication page (login/register)."""
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #667eea; font-size: 3rem; margin-bottom: 0;'>
            🎓 StudHelper
        </h1>
        <h3 style='color: #764ba2; margin-top: 0; font-weight: 300;'>
            Your Personal AI Study Assistant
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Auth tabs
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_register_form()

def render_login_form():
    """Render login form."""
    
    st.markdown("### Welcome Back!")
    st.markdown("Sign in to access your study materials and AI tutor.")
    
    with st.form("login_form"):
        email = st.text_input(
            "Email",
            placeholder="your@email.com",
            help="Enter your registered email address"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_button = st.form_submit_button(
                "🔑 Sign In",
                type="primary",
                use_container_width=True
            )
        
        if login_button:
            if not email or not password:
                st.error("Please enter both email and password.")
                return
            
            # Attempt login
            api_client = APIClient()
            
            with st.spinner("Signing in..."):
                result = api_client.login(email, password)
            
            if result["success"]:
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error(f"Login failed: {result['error']}")
    
    # Demo credentials info
    with st.expander("🔧 Demo Credentials", expanded=False):
        st.info("""
        **Demo Account:**
        - Email: default@studhelper.local
        - Password: default_password_change_me
        
        *This account is created automatically by the backend for testing.*
        """)

def render_register_form():
    """Render registration form."""
    
    st.markdown("### Create Account")
    st.markdown("Join StudHelper to start building your personalized AI tutor.")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "Username",
                placeholder="Choose a username",
                help="3-30 characters, letters and numbers only"
            )
        
        with col2:
            email = st.text_input(
                "Email",
                placeholder="your@email.com",
                help="We'll use this for account recovery"
            )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a strong password",
            help="Minimum 6 characters"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            register_button = st.form_submit_button(
                "📝 Create Account",
                type="primary",
                use_container_width=True
            )
        
        if register_button:
            # Validation
            if not all([username, email, password, confirm_password]):
                st.error("Please fill in all fields.")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters.")
                return
            
            if len(username) < 3 or len(username) > 30:
                st.error("Username must be 3-30 characters.")
                return
            
            # Attempt registration
            api_client = APIClient()
            
            with st.spinner("Creating account..."):
                result = api_client.register(email, username, password)
            
            if result["success"]:
                st.success("Account created successfully! Please log in.")
                st.balloons()
            else:
                st.error(f"Registration failed: {result['error']}")

def render_user_menu():
    """Render user menu in sidebar."""
    
    user = st.session_state.get(Config.USER_KEY)
    
    if not user:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Account")
        
        # User info
        st.markdown(f"**{user.get('username', 'User')}**")
        st.markdown(f"*{user.get('email', '')}*")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            api_client = APIClient()
            api_client.logout()
            st.rerun()
        
        # Usage info
        with st.expander("📊 Usage Stats", expanded=False):
            api_client = APIClient()
            usage_result = api_client.get_usage_analytics(days=7)
            
            if usage_result["success"]:
                usage_data = usage_result["data"]
                
                st.metric("Tokens Used", usage_data.get("total_tokens", 0))
                st.metric("Total Cost", f"${usage_data.get('total_cost', 0):.4f}")
                st.metric("Requests", usage_data.get("total_requests", 0))
            else:
                st.info("Usage data not available")

def check_authentication() -> bool:
    """Check if user is authenticated."""
    token = st.session_state.get(Config.TOKEN_KEY)
    user = st.session_state.get(Config.USER_KEY)
    
    if not token or not user:
        return False
    
    # Verify token is still valid
    api_client = APIClient()
    result = api_client.get_current_user()
    
    if not result["success"]:
        # Clear invalid session
        api_client.logout()
        return False
    
    return True

## 4. MODIFIED FILE: components/chat_interface.py
"""Modified chat interface to use backend API."""

import streamlit as st
from datetime import datetime
from utils.api_client import APIClient

def render_chat_interface():
    """Render the chat interface for interacting with the AI tutor"""
    
    api_client = APIClient()
    
    # Get documents to check if user has knowledge base
    docs_result = api_client.get_documents()
    
    if not docs_result["success"]:
        st.error(f"❌ Error loading documents: {docs_result['error']}")
        return
    
    documents = docs_result["data"]
    
    if not documents:
        st.error("❌ No documents found. Please upload some study materials first.")
        return
    
    # Header
    st.markdown("## 💬 Chat with AI Tutor")
    
    # Knowledge base info
    with st.expander("📚 Knowledge Base Info", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Documents", len(documents))
        with col2:
            total_pages = sum(doc.get('page_count', 0) for doc in documents)
            st.metric("📰 Pages", total_pages)
        with col3:
            processed_docs = len([doc for doc in documents if doc.get('status') == 'completed'])
            st.metric("✅ Processed", processed_docs)
        with col4:
            st.metric("💾 Status", "Ready" if processed_docs > 0 else "Processing")
    
    # Get chat sessions
    sessions_result = api_client.get_chat_sessions()
    
    if sessions_result["success"]:
        sessions = sessions_result["data"]
        
        # Session selector
        if sessions:
            session_options = {
                f"Session {i+1}: {session.get('created_at', '')[:10]}": session['id'] 
                for i, session in enumerate(sessions)
            }
            session_options["➕ New Session"] = None
            
            selected_session_key = st.selectbox(
                "Chat Session",
                options=list(session_options.keys()),
                index=0
            )
            
            selected_session_id = session_options[selected_session_key]
        else:
            selected_session_id = None
        
        # Display chat history
        if selected_session_id:
            display_chat_history(selected_session_id, api_client)
        else:
            st.info("Starting a new chat session. Send a message to begin!")
        
        # Chat input
        render_chat_input(selected_session_id, api_client)
    
    else:
        st.error(f"❌ Error loading chat sessions: {sessions_result['error']}")

def display_chat_history(session_id: int, api_client: APIClient):
    """Display chat history for session."""
    
    history_result = api_client.get_chat_history(session_id)
    
    if not history_result["success"]:
        st.error(f"Error loading chat history: {history_result['error']}")
        return
    
    messages = history_result["data"]
    
    # Display messages
    for message in messages:
        role = message.get('role', 'user')
        content = message.get('content', '')
        created_at = message.get('created_at', '')
        sources = message.get('sources', [])
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00') if created_at.endswith('Z') else created_at)
            time_str = dt.strftime("%H:%M")
        except:
            time_str = ""
        
        if role == 'user':
            with st.chat_message("user"):
                st.markdown(content)
                if time_str:
                    st.caption(f"You • {time_str}")
        
        elif role == 'assistant':
            with st.chat_message("assistant"):
                st.markdown(content)
                
                # Show sources if available
                if sources:
                    with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
                        for i, source in enumerate(sources):
                            st.markdown(f"**{i+1}.** {source.get('filename', 'Unknown')}")
                
                if time_str:
                    st.caption(f"AI Tutor • {time_str}")

def render_chat_input(session_id: Optional[int], api_client: APIClient):
    """Render chat input and handle user messages"""
    
    # Chat mode selector
    col1, col2 = st.columns([3, 1])
    
    with col2:
        chat_mode = st.selectbox(
            "Mode",
            options=["economic", "standard", "turbo"],
            index=0,
            help="Economic: Fast & cheap, Standard: Balanced, Turbo: Advanced reasoning"
        )
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your study materials...")
    
    if user_input:
        send_message(user_input, chat_mode, session_id, api_client)

def send_message(user_message: str, mode: str, session_id: Optional[int], api_client: APIClient):
    """Process and send a user message"""
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_message)
        st.caption(f"You • {datetime.now().strftime('%H:%M')}")
    
    # Send to backend
    with st.chat_message("assistant"):
        with st.spinner("🤔 AI Tutor is thinking..."):
            result = api_client.send_chat_message(
                message=user_message,
                mode=mode,
                session_id=session_id
            )
        
        if result["success"]:
            response_data = result["data"]
            content = response_data.get("content", "")
            sources = response_data.get("sources", [])
            cost = response_data.get("cost", 0)
            
            # Display response
            st.markdown(content)
            
            # Show sources if available
            if sources:
                with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
                    for i, source in enumerate(sources):
                        st.markdown(f"**{i+1}.** {source.get('filename', 'Unknown')}")
            
            # Show cost info
            st.caption(f"AI Tutor • {datetime.now().strftime('%H:%M')} • ${cost:.4f}")
        
        else:
            st.error(f"❌ Error: {result['error']}")
    
    # Rerun to update chat history
    st.rerun()

## 5. MODIFIED FILE: components/knowledge_upload.py
"""Modified knowledge upload to use backend API."""

import streamlit as st
from utils.api_client import APIClient
from utils.youtube_handler import is_valid_youtube_url

def render_knowledge_upload():
    """Render the knowledge upload interface"""
    
    api_client = APIClient()
    
    st.markdown("## 📤 Upload Study Materials")
    st.markdown("""
    Upload your study materials to create a personalized AI tutor. The more comprehensive 
    your materials, the better your AI assistant will be at answering questions.
    """)
    
    # Create tabs for different upload types
    tab1, tab2, tab3 = st.tabs(["📄 Documents", "🎥 YouTube Videos", "📊 Summary"])
    
    with tab1:
        render_document_upload(api_client)
    
    with tab2:
        render_youtube_upload(api_client)
    
    with tab3:
        render_knowledge_summary(api_client)

def render_document_upload(api_client: APIClient):
    """Render document upload section"""
    
    st.markdown("### 📄 Upload Documents")
    st.markdown("""
    Upload PDFs, Word documents, PowerPoint presentations, and other text files. 
    These will be analyzed and used to answer your questions.
    """)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=['pdf', 'docx', 'pptx', 'txt', 'md'],
        accept_multiple_files=True,
        help="Supported formats: PDF, Word (.docx), PowerPoint (.pptx), Text (.txt), Markdown (.md)"
    )
    
    # File size warning
    if uploaded_files:
        total_size = sum(file.size for file in uploaded_files)
        total_size_mb = total_size / (1024 * 1024)
        
        if total_size_mb > 100:
            st.warning(f"⚠️ Total file size: {total_size_mb:.1f}MB. Consider uploading files in smaller batches for better performance.")
        else:
            st.info(f"📊 Total file size: {total_size_mb:.1f}MB")
        
        # Show file details
        with st.expander("📋 File Details", expanded=True):
            for i, file in enumerate(uploaded_files):
                file_size_mb = file.size / (1024 * 1024)
                st.write(f"**{i+1}.** {file.name} ({file_size_mb:.1f}MB)")
        
        # Process files button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                f"🚀 Upload {len(uploaded_files)} File(s)",
                type="primary",
                use_container_width=True
            ):
                upload_documents(uploaded_files, api_client)

def render_youtube_upload(api_client: APIClient):
    """Render YouTube upload section"""
    
    st.markdown("### 🎥 YouTube Videos")
    st.markdown("""
    Add YouTube video links to extract and analyze the audio content. 
    Great for lectures, tutorials, and educational videos.
    """)
    
    # YouTube URL input
    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        help="Paste a YouTube video link here"
    )
    
    # Optional title
    video_title = st.text_input(
        "Title (Optional)",
        placeholder="Give this video a custom title",
        help="Leave blank to use the video's original title"
    )
    
    # Validate and show video info
    if youtube_url:
        if is_valid_youtube_url(youtube_url):
            # Show video preview
            col1, col2 = st.columns([1, 2])
            
            with col1:
                try:
                    st.video(youtube_url)
                except:
                    st.info("Video preview not available")
            
            with col2:
                st.markdown("#### Video Preview")
                st.info("👆 This video will be processed to extract audio and create a transcript for your AI tutor.")
                
                if st.button(
                    "🎵 Add Video to Knowledge Base",
                    type="primary",
                    use_container_width=True
                ):
                    upload_youtube_video(youtube_url, video_title, api_client)
        else:
            st.error("❌ Please enter a valid YouTube URL")

def render_knowledge_summary(api_client: APIClient):
    """Render knowledge summary and processing status"""
    
    st.markdown("### 📊 Knowledge Base Summary")
    
    # Get documents from backend
    docs_result = api_client.get_documents()
    
    if not docs_result["success"]:
        st.error(f"❌ Error loading documents: {docs_result['error']}")
        return
    
    documents = docs_result["data"]
    
    # Statistics
    total_files = len(documents)
    completed_docs = len([doc for doc in documents if doc.get('status') == 'completed'])
    processing_docs = len([doc for doc in documents if doc.get('status') == 'processing'])
    failed_docs = len([doc for doc in documents if doc.get('status') == 'failed'])
    total_pages = sum(doc.get('page_count', 0) for doc in documents)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Documents", total_files)
    with col2:
        st.metric("✅ Completed", completed_docs)
    with col3:
        st.metric("⏳ Processing", processing_docs)
    with col4:
        st.metric("📰 Total Pages", total_pages)
    
    # Document list
    if documents:
        st.markdown("#### 📋 Your Documents")
        
        for doc in documents:
            with st.expander(f"{doc['filename']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Type:** {doc.get('file_type', 'Unknown')}")
                    st.write(f"**Size:** {doc.get('file_size', 0) / (1024*1024):.1f}MB")
                    st.write(f"**Pages:** {doc.get('page_count', 'N/A')}")
                    st.write(f"**Status:** {doc.get('status', 'Unknown')}")
                    st.write(f"**Uploaded:** {doc.get('created_at', 'Unknown')[:10]}")
                
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_doc_{doc['id']}"):
                        delete_document(doc['id'], api_client)
    
    else:
        st.info("👆 Upload some documents or add YouTube videos to get started!")

def upload_documents(uploaded_files, api_client: APIClient):
    """Upload documents to backend"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    success_count = 0
    error_count = 0
    
    for i, file in enumerate(uploaded_files):
        status_text.text(f"Uploading {file.name}...")
        progress_bar.progress((i + 1) / len(uploaded_files))
        
        # Upload to backend
        result = api_client.upload_document(
            file_data=file.getvalue(),
            filename=file.name,
            content_type=file.type
        )
        
        if result["success"]:
            success_count += 1
        else:
            error_count += 1
            st.error(f"Failed to upload {file.name}: {result['error']}")
    
    status_text.text("✅ Upload complete!")
    
    if success_count > 0:
        st.success(f"🎉 Successfully uploaded {success_count} file(s)!")
    
    if error_count > 0:
        st.warning(f"⚠️ {error_count} file(s) failed to upload")
    
    # Refresh the page
    st.rerun()

def upload_youtube_video(url: str, title: str, api_client: APIClient):
    """Upload YouTube video to backend"""
    
    with st.spinner("🎵 Adding YouTube video..."):
        result = api_client.add_youtube_video(url, title if title else None)
    
    if result["success"]:
        st.success("🎥 YouTube video added successfully!")
        st.rerun()
    else:
        st.error(f"❌ Error adding video: {result['error']}")

def delete_document(document_id: int, api_client: APIClient):
    """Delete a document"""
    
    result = api_client.delete_document(document_id)
    
    if result["success"]:
        st.success("🗑️ Document deleted successfully!")
        st.rerun()
    else:
        st.error(f"❌ Error deleting document: {result['error']}")

## 6. MODIFIED FILE: main.py
"""Modified main application with authentication."""

import streamlit as st
import os
from datetime import datetime

# Import our custom components
from components.sidebar import render_sidebar
from components.welcome import render_welcome_page
from components.knowledge_upload import render_knowledge_upload
from components.chat_interface import render_chat_interface
from components.auth_components import render_auth_page, check_authentication, render_user_menu
from utils.api_client import APIClient
from utils.config import Config

# Page configuration
st.set_page_config(
    page_title="StudHelper - AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application logic"""
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background: #f8f9fa;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stFileUploader > div > div > div {
        background-color: #f8f9fa;
        border: 2px dashed #dee2e6;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if not check_authentication():
        # Show authentication page
        render_auth_page()
        return
    
    # User is authenticated - show main app
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 StudHelper</h1>
        <p>Your AI-Powered Study Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render user menu in sidebar
    render_user_menu()
    
    # Main content - show navigation
    render_main_navigation()

def render_main_navigation():
    """Render main navigation and content."""
    
    # Navigation
    page = st.sidebar.selectbox(
        "📖 Navigation",
        options=["📤 Upload Materials", "💬 Chat with AI", "📊 Analytics"],
        index=0
    )
    
    if page == "📤 Upload Materials":
        render_knowledge_upload()
    elif page == "💬 Chat with AI":
        render_chat_interface()
    elif page == "📊 Analytics":
        render_analytics_page()

def render_analytics_page():
    """Render analytics page."""
    
    st.markdown("## 📊 Usage Analytics")
    
    api_client = APIClient()
    
    # Get usage analytics
    usage_result = api_client.get_usage_analytics(days=30)
    
    if usage_result["success"]:
        usage_data = usage_result["data"]
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tokens", f"{usage_data.get('total_tokens', 0):,}")
        
        with col2:
            st.metric("Total Cost", f"${usage_data.get('total_cost', 0):.4f}")
        
        with col3:
            st.metric("Total Requests", usage_data.get('total_requests', 0))
        
        with col4:
            avg_cost = usage_data.get('avg_cost_per_request', 0)
            st.metric("Avg Cost/Request", f"${avg_cost:.4f}")
        
        # Usage by model
        st.markdown("### 🤖 Usage by Model")
        model_usage = usage_data.get('usage_by_model', [])
        
        if model_usage:
            for model_data in model_usage:
                with st.expander(f"Model: {model_data['model']}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Tokens", f"{model_data['tokens']:,}")
                    
                    with col2:
                        st.metric("Cost", f"${model_data['cost']:.4f}")
                    
                    with col3:
                        st.metric("Requests", model_data['requests'])
        
        # Daily breakdown
        st.markdown("### 📅 Daily Usage")
        daily_data = usage_data.get('daily_breakdown', [])
        
        if daily_data:
            for day_data in daily_data[-7:]:  # Last 7 days
                date = day_data['date']
                with st.expander(f"📅 {date}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Tokens", day_data['tokens_used'])
                        st.progress(day_data['tokens_used'] / max(day_data.get('tokens_remaining', 1) + day_data['tokens_used'], 1))
                    
                    with col2:
                        st.metric("Cost", f"${day_data['cost_incurred']:.4f}")
                        cost_progress = day_data['cost_incurred'] / max(day_data.get('cost_remaining', 0.01) + day_data['cost_incurred'], 0.01)
                        st.progress(min(cost_progress, 1.0))
                    
                    with col3:
                        st.metric("Requests", day_data['requests_made'])
                        req_progress = day_data['requests_made'] / max(day_data.get('requests_remaining', 1) + day_data['requests_made'], 1)
                        st.progress(req_progress)
        
    else:
        st.error(f"❌ Error loading analytics: {usage_result['error']}")
    
    # Get documents
    docs_result = api_client.get_documents()
    
    if docs_result["success"]:
        documents = docs_result["data"]
        
        st.markdown("### 📄 Document Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Documents", len(documents))
        
        with col2:
            completed = len([doc for doc in documents if doc.get('status') == 'completed'])
            st.metric("Processed", completed)
        
        with col3:
            total_pages = sum(doc.get('page_count', 0) for doc in documents)
            st.metric("Total Pages", total_pages)

if __name__ == "__main__":
    main()

## 7. MODIFIED FILE: requirements.txt
"""Updated requirements with API client dependencies."""

# StudHelper Streamlit Frontend Requirements

# Core Streamlit
streamlit==1.28.1

# API Communication
requests==2.31.0
httpx==0.25.2

# File Processing (keeping for any local processing)
PyPDF2==3.0.1
pdfplumber==0.10.3
python-docx==1.1.0
python-pptx==0.6.23
openpyxl==3.1.2

# Authentication & Security
python-jose[cryptography]==3.3.0

# Utilities
python-dotenv==1.0.0
regex==2023.10.3

# Data Handling
pandas==2.1.3
numpy==1.25.2

# Development and Testing
pytest==7.4.3
black==23.11.0
isort==5.12.0

## 8. NEW FILE: .env.example
"""Environment configuration example."""

# Backend API Configuration
BACKEND_URL=http://localhost:8000

# Optional: Override individual endpoints
# API_BASE_URL=http://localhost:8000/api/v1

# Development Settings
DEBUG=true

# Frontend Settings
MAX_FILE_SIZE=52428800
SUPPORTED_FILE_TYPES=pdf,docx,pptx,txt,md


### readme.md
## Summary of Changes

The frontend has been modified to integrate with the FastAPI backend:

### New Files:
1. **utils/config.py** - Configuration management for API endpoints
2. **utils/api_client.py** - HTTP client for backend communication
3. **components/auth_components.py** - Login/register UI components
4. **.env.example** - Environment configuration template

### Modified Files:
1. **components/chat_interface.py** - Now calls backend chat API instead of mock responses
2. **components/knowledge_upload.py** - Uploads files to backend API
3. **main.py** - Added authentication flow and navigation
4. **requirements.txt** - Added requests and authentication dependencies

### Key Features Added:
- ✅ User authentication (login/register)
- ✅ Real document upload to backend
- ✅ Real AI chat with backend integration
- ✅ Usage analytics from backend
- ✅ Document management through backend API
- ✅ YouTube video processing through backend
- ✅ Error handling and user feedback

### To Use:
1. Start the FastAPI backend: `uvicorn src.main:app --reload`
2. Update frontend environment: `cp .env.example .env`
3. Install new requirements: `pip install -r requirements.txt`
4. Run frontend: `streamlit run main.py`
5. Use demo credentials: `default@studhelper.local` / `default_password_change_me`

The frontend now provides a complete interface to the StudHelper backend!

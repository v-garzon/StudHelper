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


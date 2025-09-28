"""
Python client example for StudHelper Backend API
"""

import requests
import json
from typing import Optional, Dict, Any

class StudHelperClient:
    """Python client for StudHelper Backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request"""
        url = f"{self.base_url}{endpoint}"
        
        if self.token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.token}'
            kwargs['headers'] = headers
        
        return self.session.request(method, url, **kwargs)
    
    def register(self, email: str, username: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Register a new user"""
        data = {
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name
        }
        response = self._request('POST', '/api/v1/auth/register', json=data)
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and store token"""
        data = {"username": username, "password": password}
        response = self._request('POST', '/api/v1/auth/login', json=data)
        response.raise_for_status()
        
        result = response.json()
        self.token = result['access_token']
        return result
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        response = self._request('GET', '/api/v1/auth/me')
        response.raise_for_status()
        return response.json()
    
    def create_class(self, name: str, description: str = None) -> Dict[str, Any]:
        """Create a new class"""
        data = {"name": name, "description": description}
        response = self._request('POST', '/api/v1/classes/', json=data)
        response.raise_for_status()
        return response.json()
    
    def join_class(self, class_code: str) -> Dict[str, Any]:
        """Join a class by code"""
        data = {"class_code": class_code}
        response = self._request('POST', '/api/v1/classes/join', json=data)
        response.raise_for_status()
        return response.json()
    
    def get_classes(self) -> list:
        """Get user's classes"""
        response = self._request('GET', '/api/v1/classes/')
        response.raise_for_status()
        return response.json()
    
    def create_chat_session(self, class_id: int, title: str) -> Dict[str, Any]:
        """Create a chat session"""
        data = {"class_id": class_id, "title": title}
        response = self._request('POST', '/api/v1/chat/sessions', json=data)
        response.raise_for_status()
        return response.json()
    
    def send_message(self, session_id: int, content: str) -> Dict[str, Any]:
        """Send a message in a chat session"""
        data = {"content": content}
        response = self._request('POST', f'/api/v1/chat/sessions/{session_id}/messages', json=data)
        response.raise_for_status()
        return response.json()
    
    def upload_class_document(self, class_id: int, file_path: str) -> Dict[str, Any]:
        """Upload a document to a class"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self._request('POST', f'/api/v1/documents/classes/{class_id}/upload', files=files)
            response.raise_for_status()
            return response.json()
    
    def get_usage_stats(self) -> list:
        """Get usage statistics"""
        response = self._request('GET', '/api/v1/usage/my-usage')
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    client = StudHelperClient()
    
    # Register and login
    try:
        user = client.register(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            full_name="Test User"
        )
        print("User registered:", user['username'])
    except requests.exceptions.HTTPError:
        print("User might already exist, trying to login...")
    
    # Login
    login_result = client.login("testuser", "testpass123")
    print("Logged in as:", login_result['user']['username'])
    
    # Create a class
    new_class = client.create_class("Test Class", "A test class for the API")
    print("Created class:", new_class['name'], "Code:", new_class['class_code'])
    
    # Create chat session
    session = client.create_chat_session(new_class['id'], "Test Chat")
    print("Created chat session:", session['title'])
    
    # Send a message
    chat_response = client.send_message(session['id'], "Hello, can you help me with physics?")
    print("AI Response:", chat_response['ai_response']['content'])


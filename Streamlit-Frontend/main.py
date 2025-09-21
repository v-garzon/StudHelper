import streamlit as st
import os
from datetime import datetime
from typing import Dict, List, Optional
import uuid

# Import our custom components
from components.sidebar import render_sidebar
from components.welcome import render_welcome_page
from components.knowledge_upload import render_knowledge_upload
from components.chat_interface import render_chat_interface
from utils.session_state import initialize_session_state, get_current_class_data
from utils.file_processing import process_uploaded_files
from utils.youtube_handler import process_youtube_video

# Page configuration
st.set_page_config(
    page_title="StudHelper - AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application logic"""
    
    # Initialize session state
    initialize_session_state()
    
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
    
    .class-status {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .knowledge-stats {
        background: #e3f2fd;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    .chat-message {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 10px;
    }
    
    .user-message {
        background: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: #f3e5f5;
        margin-right: 2rem;
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
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 StudHelper</h1>
        <p>Your AI-Powered Study Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render sidebar (class selection and creation)
    render_sidebar()
    
    # Main content area - render based on current state
    current_class = st.session_state.get('current_class')
    
    if not current_class:
        # No class selected - show welcome page
        render_welcome_page()
    else:
        # Class is selected - check if knowledge has been added
        class_data = get_current_class_data()
        
        if not class_data.get('has_knowledge', False):
            # Show knowledge upload interface
            render_knowledge_upload()
        else:
            # Show chat interface
            render_chat_interface()

if __name__ == "__main__":
    main()
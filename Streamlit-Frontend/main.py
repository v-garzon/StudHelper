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


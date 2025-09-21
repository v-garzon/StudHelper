"""Modified chat interface to use backend API."""

import streamlit as st
from datetime import datetime
from utils.api_client import APIClient

from typing import Optional

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


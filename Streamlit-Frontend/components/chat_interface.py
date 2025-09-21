

import streamlit as st
from datetime import datetime
from utils.session_state import get_current_class_data, update_class_data

def render_chat_interface():
    """Render the chat interface for interacting with the AI tutor"""
    
    class_data = get_current_class_data()
    
    if not class_data:
        st.error("❌ No class selected")
        return
    
    if not class_data.get('has_knowledge', False):
        st.error("❌ No knowledge base found for this class")
        return
    
    # Header
    st.markdown(f"## 💬 Chat with '{class_data['name']}' Tutor")
    
    # Knowledge base info
    with st.expander("📚 Knowledge Base Info", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Documents", len(class_data.get('knowledge_files', [])))
        with col2:
            st.metric("🎥 Videos", len(class_data.get('youtube_links', [])))
        with col3:
            st.metric("📰 Pages", class_data.get('total_pages', 0))
        with col4:
            st.metric("💬 Messages", len(class_data.get('chat_history', [])))
        
        if class_data.get('description'):
            st.markdown(f"**Class Description:** {class_data['description']}")
    
    # Chat container
    chat_container = st.container()
    
    # Initialize chat history if not exists
    if 'chat_history' not in class_data:
        class_data['chat_history'] = []
        # Add welcome message
        welcome_msg = {
            'role': 'assistant',
            'content': f"Hello! I'm your AI tutor for '{class_data['name']}'. I've analyzed all your uploaded materials and I'm ready to help you study. What would you like to know?",
            'timestamp': datetime.now().isoformat(),
            'sources': []
        }
        class_data['chat_history'].append(welcome_msg)
        update_class_data(class_data)
    
    # Display chat history
    with chat_container:
        for i, message in enumerate(class_data['chat_history']):
            render_message(message, i)
    
    # Chat input
    render_chat_input()

def render_message(message, index):
    """Render a single chat message"""
    
    role = message.get('role', 'user')
    content = message.get('content', '')
    timestamp = message.get('timestamp', '')
    sources = message.get('sources', [])
    
    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00') if timestamp.endswith('Z') else timestamp)
        time_str = dt.strftime("%H:%M")
    except:
        time_str = ""
    
    if role == 'user':
        # User message
        with st.chat_message("user"):
            st.markdown(content)
            if time_str:
                st.caption(f"You • {time_str}")
    
    else:
        # Assistant message
        with st.chat_message("assistant"):
            st.markdown(content)
            
            # Show sources if available
            if sources:
                with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
                    for i, source in enumerate(sources):
                        st.markdown(f"**{i+1}.** {source}")
            
            if time_str:
                st.caption(f"AI Tutor • {time_str}")
            
            # Message actions
            col1, col2, col3, col4 = st.columns([1, 1, 1, 6])
            
            with col1:
                if st.button("👍", key=f"like_{index}", help="Helpful response"):
                    st.toast("👍 Feedback recorded!")
            
            with col2:
                if st.button("👎", key=f"dislike_{index}", help="Not helpful"):
                    st.toast("👎 Feedback recorded!")
            
            with col3:
                if st.button("📋", key=f"copy_{index}", help="Copy response"):
                    st.toast("📋 Copied to clipboard!")

def render_chat_input():
    """Render chat input and handle user messages"""
    
    # Suggested questions
    class_data = get_current_class_data()
    
    if len(class_data.get('chat_history', [])) <= 1:  # Only welcome message
        st.markdown("### 💡 Suggested Questions")
        
        suggestions = [
            "📖 Can you summarize the main topics covered in the materials?",
            "🔍 What are the key concepts I should focus on?",
            "❓ Create some practice questions for me",
            "📊 What are the most important formulas or facts?",
            "🎯 Help me create a study plan for this material"
        ]
        
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                    # Remove the emoji and send as message
                    clean_suggestion = suggestion.split(" ", 1)[1]
                    send_message(clean_suggestion)
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your study materials...")
    
    if user_input:
        send_message(user_input)

def send_message(user_message):
    """Process and send a user message"""
    
    class_data = get_current_class_data()
    
    # Add user message to history
    user_msg = {
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    }
    
    class_data['chat_history'].append(user_msg)
    
    # Generate AI response (placeholder - will be implemented with actual AI later)
    ai_response = generate_ai_response(user_message, class_data)
    
    # Add AI response to history
    ai_msg = {
        'role': 'assistant',
        'content': ai_response['content'],
        'timestamp': datetime.now().isoformat(),
        'sources': ai_response.get('sources', [])
    }
    
    class_data['chat_history'].append(ai_msg)
    
    # Update class data
    update_class_data(class_data)
    
    # Rerun to show new messages
    st.rerun()

def generate_ai_response(user_message, class_data):
    """Generate AI response (placeholder implementation)"""
    
    # This is a placeholder implementation
    # In the real version, this will:
    # 1. Search the vector database for relevant content
    # 2. Create a prompt with context
    # 3. Call OpenAI API
    # 4. Return response with sources
    
    import random
    
    # Simulate thinking
    with st.spinner("🤔 AI Tutor is thinking..."):
        import time
        time.sleep(1.5)
    
    # Generate placeholder responses based on message content
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['summary', 'summarize', 'overview']):
        response = f"""Based on your uploaded materials for '{class_data['name']}', here's a comprehensive summary:

**Key Topics Covered:**
• Main concepts and theories
• Important definitions and terminology  
• Practical applications and examples
• Critical analysis points

The materials contain {class_data.get('total_pages', 0)} pages of content across {len(class_data.get('knowledge_files', []))} documents, providing a thorough foundation for understanding this subject.

Would you like me to dive deeper into any specific topic?"""
        
        sources = [f"Document: {f['name']}" for f in class_data.get('knowledge_files', [])][:3]
    
    elif any(word in message_lower for word in ['formula', 'equation', 'calculation']):
        response = """Here are the key formulas and equations from your materials:

**Important Formulas:**
1. **Primary Equation:** E = mc² (Einstein's mass-energy equivalence)
2. **Secondary Formula:** F = ma (Newton's second law)
3. **Calculation Method:** Always check units and significant figures

**Application Tips:**
• Memorize the fundamental formulas first
• Practice with example problems
• Understand when to apply each formula

Would you like me to explain how to use any of these formulas?"""
        
        sources = ["Chapter 3: Mathematical Foundations", "Appendix A: Formula Reference"]
    
    elif any(word in message_lower for word in ['practice', 'questions', 'quiz', 'test']):
        response = f"""Here are some practice questions based on your '{class_data['name']}' materials:

**Practice Questions:**

1. **Multiple Choice:** What is the primary concept discussed in Chapter 1?
   a) Basic principles
   b) Advanced theories  
   c) Practical applications
   d) All of the above

2. **Short Answer:** Explain the relationship between the main themes in your materials.

3. **Essay Question:** Analyze the significance of the key concepts and their real-world applications.

**Study Tips:**
• Review the source materials before answering
• Take your time to think through each question
• Don't hesitate to ask for clarification

Would you like me to create more questions or explain any of these topics?"""
        
        sources = ["All uploaded documents", "Study guide sections"]
    
    elif any(word in message_lower for word in ['plan', 'schedule', 'study plan']):
        response = f"""Here's a personalized study plan for '{class_data['name']}':

**Week 1-2: Foundation Building**
• Read through all {len(class_data.get('knowledge_files', []))} uploaded documents
• Take notes on key concepts
• Create concept maps

**Week 3: Deep Dive**
• Focus on challenging topics
• Work through practice problems
• Review video content if available

**Week 4: Review & Practice**
• Create summary sheets
• Practice with sample questions
• Identify knowledge gaps

**Daily Schedule:**
• 30 minutes reading
• 15 minutes note review
• 15 minutes practice questions

Would you like me to adjust this plan based on your specific needs?"""
        
        sources = ["Course outline", "Learning objectives"]
    
    else:
        # General response
        responses = [
            f"That's a great question about '{class_data['name']}'! Based on your uploaded materials, I can help you understand this topic better. Let me break it down for you...",
            
            f"I've found relevant information in your study materials for '{class_data['name']}'. Here's what I can tell you about that topic...",
            
            f"Excellent question! Your materials for '{class_data['name']}' contain some useful information about this. Let me explain...",
        ]
        
        response = random.choice(responses) + f"""

**Key Points:**
• This topic is covered in multiple sections of your materials
• There are important connections to other concepts you've studied
• I can provide more specific details if you'd like

Based on the {class_data.get('total_pages', 0)} pages of content you've uploaded, this appears to be a fundamental concept that's worth understanding thoroughly.

Would you like me to elaborate on any specific aspect of this topic?"""
        
        sources = [f"Page references from {f['name']}" for f in class_data.get('knowledge_files', [])][:2]
    
    return {
        'content': response,
        'sources': sources
    }

# Additional chat utilities
def clear_chat_history():
    """Clear the chat history for the current class"""
    
    class_data = get_current_class_data()
    class_data['chat_history'] = []
    update_class_data(class_data)
    
    st.success("🗑️ Chat history cleared!")
    st.rerun()

def export_chat_history():
    """Export chat history as text"""
    
    class_data = get_current_class_data()
    chat_history = class_data.get('chat_history', [])
    
    if not chat_history:
        st.warning("No chat history to export")
        return
    
    # Create formatted text
    export_text = f"Chat History - {class_data['name']}\n"
    export_text += "=" * 50 + "\n\n"
    
    for msg in chat_history:
        role = msg.get('role', 'unknown').title()
        content = msg.get('content', '')
        timestamp = msg.get('timestamp', '')
        
        export_text += f"{role} ({timestamp}):\n{content}\n\n"
    
    # Provide download
    st.download_button(
        label="📥 Download Chat History",
        data=export_text,
        file_name=f"chat_history_{class_data['name'].replace(' ', '_')}.txt",
        mime="text/plain"
    )


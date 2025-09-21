import streamlit as st

def render_welcome_page():
    """Render the welcome page when no class is selected"""
    
    # Main welcome content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #667eea; font-size: 3rem; margin-bottom: 0;'>
                🎓 Welcome to StudHelper
            </h1>
            <h3 style='color: #764ba2; margin-top: 0; font-weight: 300;'>
                Your Personal AI Study Assistant
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Hero image or illustration (using emoji for now)
        st.markdown("""
        <div style='text-align: center; font-size: 8rem; margin: 2rem 0;'>
            📚🤖💡
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; font-size: 1.2rem; color: #555; line-height: 1.6;'>
            Transform your study materials into an intelligent tutor that knows everything 
            about your documents and can answer your questions instantly.
        </div>
        """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("---")
    st.markdown("## ✨ What StudHelper Can Do")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📄 Smart Document Processing
        Upload PDFs, Word docs, PowerPoints, and even YouTube videos. 
        StudHelper will read and understand all your study materials.
        """)
        
        st.markdown("""
        **Supported formats:**
        - 📄 PDF documents
        - 📝 Word documents (.docx)
        - 📊 PowerPoint presentations
        - 🎥 YouTube video links
        """)
    
    with col2:
        st.markdown("""
        ### 🤖 AI-Powered Chat
        Ask questions about your materials and get accurate, contextual answers. 
        It's like having a personal tutor who has read all your documents.
        """)
        
        st.markdown("""
        **Ask things like:**
        - "Summarize chapter 3"
        - "What are the key formulas?"
        - "Explain this concept simply"
        - "Create practice questions"
        """)
    
    with col3:
        st.markdown("""
        ### 🎓 Organized Learning
        Create separate classes for different subjects. Each class has its own 
        knowledge base and chat history.
        """)
        
        st.markdown("""
        **Stay organized:**
        - 📚 Multiple study classes
        - 🔍 Subject-specific knowledge
        - 📝 Persistent chat history
        - 📊 Progress tracking
        """)
    
    # Getting started section
    st.markdown("---")
    st.markdown("## 🚀 Getting Started")
    
    steps_col1, steps_col2 = st.columns([2, 1])
    
    with steps_col1:
        st.markdown("""
        ### Follow these simple steps:
        
        1. **📚 Create a Class** - Use the sidebar to create a new study class
        2. **📤 Upload Knowledge** - Add your PDFs, documents, or YouTube links  
        3. **⏳ Wait for Processing** - Let the AI analyze your materials
        4. **💬 Start Chatting** - Ask questions and get intelligent answers!
        """)
        
        # Call-to-action
        st.markdown("""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; 
                    color: white; margin: 2rem 0;'>
            <h3 style='margin: 0; color: white;'>Ready to get started?</h3>
            <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
                👈 Create your first class in the sidebar!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with steps_col2:
        st.markdown("""
        <div style='text-align: center; font-size: 6rem; color: #667eea;'>
            🎯
        </div>
        """, unsafe_allow_html=True)
    
    # Tips section
    st.markdown("---")
    st.markdown("## 💡 Pro Tips")
    
    tip_col1, tip_col2 = st.columns(2)
    
    with tip_col1:
        st.info("""
        **📚 For better results:**
        - Upload related documents to the same class
        - Use clear, descriptive class names
        - Include lecture notes, textbooks, and slides together
        """)
    
    with tip_col2:
        st.info("""
        **💬 When chatting:**
        - Ask specific questions for better answers
        - Reference page numbers or chapters when possible
        - Use follow-up questions to dive deeper
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9rem; padding: 2rem 0;'>
        StudHelper uses advanced AI to help you study more effectively.<br>
        Your documents are processed securely and used only for your personal study sessions.
    </div>
    """, unsafe_allow_html=True)
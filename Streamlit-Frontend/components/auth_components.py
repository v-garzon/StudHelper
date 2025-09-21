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


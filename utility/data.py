import streamlit as st
from streamlit_cookies_manager import CookieManager
import time
import hashlib

# Initialize cookie manager
cookies = CookieManager()
# Configuration
SESSION_COOKIE_NAME = "auth_session"
SESSION_DURATION = 86400  # 24 hours in seconds
USER_CREDENTIALS = {
    "admin": hashlib.sha256("password123".encode()).hexdigest()  # Store hashed passwords
}


def login_page():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if authenticate_user(username, password):
                # Create session
                session_id = create_session(username)
                # Set cookie
                cookies.set(SESSION_COOKIE_NAME, session_id, max_age=SESSION_DURATION)
                st.success("Logged in successfully!")
                st.session_state.logged_in = True
                st.session_state.username = username
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password")


def authenticate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return USER_CREDENTIALS.get(username) == hashed_password


def create_session(username):
    # Create a simple session ID (in real application, use more secure method)
    return f"{username}-{time.time()}"


def validate_session(session_id):
    if not session_id:
        return False
    # Basic validation (extend with proper session validation in production)
    username_part = session_id.split("-")[0]
    return username_part in USER_CREDENTIALS


def logout():
    cookies.remove(SESSION_COOKIE_NAME)
    st.session_state.clear()
    st.success("Logged out successfully!")
    time.sleep(1)
    st.rerun()


def main_app():
    st.title("Your RAG Application")
    st.write(f"Welcome {st.session_state.username}!")
    # Add your existing RAG application components here
    # Logout button
    st.sidebar.button("Logout", on_click=logout)


# Check authentication state
if not hasattr(st.session_state, 'logged_in'):
    # Check for existing valid cookie
    session_cookie = cookies.get(SESSION_COOKIE_NAME)
    if validate_session(session_cookie):
        st.session_state.logged_in = True
        st.session_state.username = session_cookie.split("-")[0]
    else:
        st.session_state.logged_in = False
# Routing
if st.session_state.logged_in:
    main_app()
else:
    login_page()

# utils/auth.py
import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client (cached to avoid reconnecting)
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def get_supabase() -> Client:
    """Return the cached Supabase client."""
    return init_supabase()

def login(email: str, password: str) -> bool:
    """Attempt to log in with email/password. Returns True on success."""
    supabase = get_supabase()
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        # Store user and session in session_state
        st.session_state.user = auth_response.user
        st.session_state.session = auth_response.session
        return True
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

def logout():
    """Sign out the current user and clear session state."""
    supabase = get_supabase()
    try:
        supabase.auth.sign_out()
    except:
        pass  # Ignore errors if session already expired
    # Clear all auth-related keys from session_state
    for key in ["user", "session"]:
        if key in st.session_state:
            del st.session_state[key]

def is_authenticated() -> bool:
    """Return True if a user is logged in."""
    return "user" in st.session_state and st.session_state.user is not None

def require_auth():
    """
    Use on every protected page.
    If not authenticated, show a login form and stop execution of the rest of the page.
    """
    if not is_authenticated():
        show_login_form()
        st.stop()  # Stop further execution of the script

def show_login_form():
    """Display a login form in the sidebar (or main area)."""
    with st.sidebar:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log in", key="login_button"):
            if login(email, password):
                st.success("Logged in successfully!")
                st.rerun()  # Rerun to update the UI
            else:
                st.error("Invalid credentials. Please try again.")

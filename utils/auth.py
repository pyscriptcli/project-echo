# utils/auth.py
import streamlit as st
import bcrypt
from supabase import create_client, Client
from typing import List, Dict, Any
from datetime import datetime

# -------------------------------------------------------------------
# Supabase client initialization (cached)
# -------------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    """Return a cached Supabase client using credentials from secrets."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def get_supabase() -> Client:
    """Return the cached Supabase client."""
    return init_supabase()

# -------------------------------------------------------------------
# Authentication functions
# -------------------------------------------------------------------
def login(username: str, password: str) -> bool:
    """
    Check username and password against the admin_users table.
    If successful, store user info in session state and return True.
    """
    supabase = get_supabase()
    try:
        # Query the admin_users table for the given username
        response = supabase.table("admin_users") \
                           .select("*") \
                           .eq("username", username) \
                           .limit(1) \
                           .execute()

        if not response.data:
            return False  # username not found

        user_record = response.data[0]
        stored_hash = user_record["password_hash"]

        # Verify password using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            # Store user info in session state (excluding password hash)
            st.session_state.user = {
                "id": user_record["id"],
                "username": user_record["username"]
            }
            return True
        else:
            return False  # wrong password

    except Exception as e:
        st.error(f"Login error: {e}")
        return False

def logout():
    """Clear the current user from session state."""
    if "user" in st.session_state:
        del st.session_state.user

def is_authenticated() -> bool:
    """Return True if a user is logged in."""
    return "user" in st.session_state and st.session_state.user is not None

def get_current_user():
    """Return the current user dict or None."""
    return st.session_state.get("user", None)

def require_auth():
    """If not authenticated, stop execution with a message."""
    if not is_authenticated():
        st.error("Please log in to access this page.")
        st.stop()

# -------------------------------------------------------------------
# Admin management functions
# -------------------------------------------------------------------
def add_admin_user(username: str, password: str) -> bool:
    """
    Create a new admin user with hashed password.
    Returns True if successful, False if username exists or error.
    """
    supabase = get_supabase()
    # Check if username already exists
    existing = supabase.table("admin_users").select("id").eq("username", username).execute()
    if existing.data:
        return False  # username taken

    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Insert new user
    try:
        supabase.table("admin_users").insert({
            "username": username,
            "password_hash": hashed
        }).execute()
        return True
    except Exception as e:
        st.error(f"Failed to create user: {e}")
        return False

def get_all_users() -> List[Dict[str, Any]]:
    """Return all admin users (id, username, created_at)."""
    supabase = get_supabase()
    response = supabase.table("admin_users").select("id, username, created_at").order("created_at").execute()
    return response.data if response.data else []

def get_user_usage() -> List[Dict[str, Any]]:
    """
    Return aggregated usage per user:
    - user_id, username, total_tokens, total_events, last_active
    """
    supabase = get_supabase()
    # Fetch all usage rows
    usage_response = supabase.table("user_usage").select("*").execute()
    usage_data = usage_response.data if usage_response.data else []

    users = get_all_users()
    user_dict = {u["id"]: u for u in users}

    # Aggregate in Python
    agg = {}
    for row in usage_data:
        uid = row["user_id"]
        if uid not in agg:
            agg[uid] = {
                "user_id": uid,
                "username": user_dict.get(uid, {}).get("username", "Unknown"),
                "total_tokens": 0,
                "total_events": 0,
                "last_active": None
            }
        agg[uid]["total_tokens"] += row.get("tokens_used", 0)
        agg[uid]["total_events"] += 1
        timestamp = row.get("created_at")
        if timestamp:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if agg[uid]["last_active"] is None or dt > agg[uid]["last_active"]:
                agg[uid]["last_active"] = dt

    # Convert to list and sort by username
    result = list(agg.values())
    result.sort(key=lambda x: x["username"])
    return result

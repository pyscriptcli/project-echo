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
def login(username: str, password: str):
    """
    Authenticate a user against the admin_users table.

    Returns:
        tuple (bool, str, dict | None)
        - success flag
        - error message (empty string on success)
        - user dict (None on failure)
    """
    supabase = get_supabase()
    try:
        response = supabase.table("admin_users") \
                           .select("*") \
                           .eq("username", username) \
                           .limit(1) \
                           .execute()

        if not response.data:
            return False, "Invalid username or password.", None

        user_record = response.data[0]
        stored_hash = user_record["password_hash"]

        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            user = {
                "id": user_record["id"],
                "username": user_record["username"]
            }
            st.session_state.user = user
            return True, "", user
        else:
            return False, "Invalid username or password.", None

    except Exception as e:
        # Generic error for security — don't leak internals to the login UI
        return False, "Authentication error. Please try again.", None

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

# -------------------------------------------------------------------
# UPDATED: DISABLED REDIRECT FOR DIRECT URL ACCESS
# -------------------------------------------------------------------
def require_auth():
    """If not authenticated, redirect to the main app (login page)."""
    if not is_authenticated():
        # TEMPORARILY DISABLED TO ALLOW DIRECT /admin ACCESS
        # st.switch_page("app.py")  <-- Commented out
        pass 
        # SECURITY NOTE: Re-enable this (uncomment the line above) 
        # and require login on the main page before going live.

# -------------------------------------------------------------------
# Admin management functions
# -------------------------------------------------------------------
def add_admin_user(username: str, password: str) -> bool:
    """Create a new admin user with hashed password."""
    supabase = get_supabase()
    existing = supabase.table("admin_users").select("id").eq("username", username).execute()
    if existing.data:
        return False

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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
    """Return aggregated usage per user."""
    supabase = get_supabase()
    usage_response = supabase.table("user_usage").select("*").execute()
    usage_data = usage_response.data if usage_response.data else []

    users = get_all_users()
    user_dict = {u["id"]: u for u in users}

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

    result = list(agg.values())
    result.sort(key=lambda x: x["username"])
    return result

# utils/auth.py (additions)

import bcrypt
from supabase import create_client, Client
import streamlit as st
from typing import List, Dict, Any
from datetime import datetime, timedelta

# ... existing init_supabase, get_supabase, login, logout, is_authenticated, get_current_user ...

def require_auth():
    """If not authenticated, stop execution with a message."""
    if not is_authenticated():
        st.error("Please log in to access this page.")
        st.stop()

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
    # Join user_usage with admin_users and aggregate
    # We'll use a raw SQL query via supabase.rpc or just fetch and aggregate in Python
    # For simplicity, fetch all usage rows and aggregate in Python.
    usage_response = supabase.table("user_usage").select("*").execute()
    usage_data = usage_response.data if usage_response.data else []

    users = get_all_users()
    user_dict = {u["id"]: u for u in users}

    # Aggregate
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

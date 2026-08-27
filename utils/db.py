import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
    """Initializes and caches the Supabase client."""
    url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
    if url.endswith("/rest/v1"):
        url = url[:-8]
    key = "".join(str(st.secrets.get("SUPABASE_KEY", "")).split())
    
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase connection failed: {e}")
        return None

def fetch_meeting_archives(limit: int = 100):
    """Fetches meeting records from the meeting_archives table."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        resp = client.table("meeting_archives").select("*").order("meeting_date", desc=True).limit(limit).execute()
        return resp.data if resp and resp.data else []
    except Exception as e:
        st.warning(f"Could not retrieve meeting archives: {e}")
        return []

def fetch_echo_context():
    """Fetches all context entries from echo_context table and formats them for the AI."""
    client = get_supabase_client()
    if not client:
        return {"team": [], "jargon": {}, "projects": []}
    
    try:
        # Fetch all entries ordered by priority (highest first)
        resp = client.table("echo_context").select("*").order("priority", desc=True).execute()
        data = resp.data if resp.data else []
        
        context = {"team": [], "jargon": {}, "projects": []}
        
        for item in data:
            cat = item.get("category")
            k = item.get("key")
            v = item.get("value")
            
            if cat == "team":
                context["team"].append(v) # Storing the full role/name in value
            elif cat == "jargon":
                context["jargon"][k] = v
            elif cat == "projects":
                context["projects"].append(v)
                
        return context
    except Exception as e:
        st.warning(f"Could not load Echo Context: {e}")
        return {"team": [], "jargon": {}, "projects": []}

def upsert_echo_context(category: str, key: str, value: str, priority: int = 1):
    """Adds or updates a context entry in the echo_context table."""
    client = get_supabase_client()
    if not client:
        return False
    try:
        client.table("echo_context").upsert({
            "category": category,
            "key": key,
            "value": value,
            "priority": priority
        }, on_conflict="category,key").execute()
        return True
    except Exception as e:
        st.error(f"Failed to update context: {e}")
        return False

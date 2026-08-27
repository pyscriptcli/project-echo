import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
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
    client = get_supabase_client()
    if not client:
        return []
    try:
        resp = client.table("meeting_archives").select("*").order("meeting_date", desc=True).limit(limit).execute()
        return resp.data if resp and resp.data else []
    except Exception as e:
        st.warning(f"Could not retrieve meeting archives: {e}")
        return []

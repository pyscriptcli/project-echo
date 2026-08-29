import json
import logging
import streamlit as st
from supabase import create_client, Client

logger = logging.getLogger(__name__)


@st.cache_resource
def get_supabase_client() -> Client | None:
    """Initializes and caches the Supabase client."""
    url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
    if url.endswith("/rest/v1"):
        url = url[:-8]
    key = "".join(str(st.secrets.get("SUPABASE_KEY", "")).split())

    if not url or not key:
        logger.error("Supabase URL or Key configuration missing in secrets.")
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        logger.exception("Supabase client initialization failed: %s", e)
        st.error(f"Supabase connection failed: {e}")
        return None


def fetch_meeting_archives(limit: int = 100) -> list:
    """Fetches meeting records from the meeting_archives table."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        resp = (
            client.table("meeting_archives")
            .select("*")
            .order("meeting_date", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data if resp and resp.data else []
    except Exception as e:
        logger.warning("Could not retrieve meeting archives: %s", e)
        return []


@st.cache_data(ttl=300, show_spinner=False)
def fetch_echo_context() -> dict:
    """
    Fetches all context entries from the echo_context table and structures
    them into team, jargon, projects, and enterprise knowledge maps.
    """
    client = get_supabase_client()
    default_context = {"team": [], "jargon": {}, "projects": [], "knowledge": {}}
    if not client:
        return default_context

    try:
        resp = (
            client.table("echo_context")
            .select("*")
            .order("priority", desc=True)
            .execute()
        )
        data = resp.data if resp and resp.data else []

        context = {"team": [], "jargon": {}, "projects": [], "knowledge": {}}

        for item in data:
            cat = str(item.get("category", "")).strip().lower()
            k = str(item.get("key", "")).strip()
            v_raw = item.get("value")

            # Deserialize JSON strings if stored as JSON payloads
            v = v_raw
            if isinstance(v_raw, str):
                v_trimmed = v_raw.strip()
                if (v_trimmed.startswith("{") and v_trimmed.endswith("}")) or (
                    v_trimmed.startswith("[") and v_trimmed.endswith("]")
                ):
                    try:
                        v = json.loads(v_trimmed)
                    except Exception:
                        v = v_raw

            if cat == "team":
                context["team"].append(v)
            elif cat == "jargon":
                context["jargon"][k] = v
            elif cat == "projects":
                context["projects"].append(v)
            elif cat == "knowledge":
                context["knowledge"][k] = v
            else:
                # Fallback capture for dynamic custom categories
                if cat not in context:
                    context[cat] = {}
                context[cat][k] = v

        return context
    except Exception as e:
        logger.exception("Could not load Echo Context: %s", e)
        st.warning(f"Could not load Echo Context: {e}")
        return default_context


def upsert_echo_context(
    category: str, key: str, value: any, priority: int = 2
) -> bool:
    """
    Adds or updates an entry in the echo_context table and purges
    the cached context map for immediate retrieval.
    """
    client = get_supabase_client()
    if not client:
        logger.error("Database upsert failed: Supabase client is uninitialized.")
        return False

    c_clean = str(category).strip().lower()
    k_clean = str(key).strip()
    p_clean = int(priority) if priority is not None else 2

    if isinstance(value, (dict, list)):
        v_payload = json.dumps(value)
    else:
        v_payload = str(value).strip()

    row_data = {
        "category": c_clean,
        "key": k_clean,
        "value": v_payload,
        "priority": p_clean,
    }

    try:
        resp = (
            client.table("echo_context")
            .upsert(row_data, on_conflict="category,key")
            .execute()
        )

        if resp.data:
            # Clear Streamlit cache so next fetch immediately reflects changes
            fetch_echo_context.clear()
            return True
        else:
            logger.error("Supabase upsert executed without returned records: %s", resp)
            return False
    except Exception as e:
        logger.exception("Failed to upsert knowledge context entry for key '%s': %s", k_clean, e)
        st.error(f"Database write error on '{k_clean}': {e}")
        return False

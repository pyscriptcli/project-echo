"""Central page catalog and per-user page access policy."""

from typing import Any, Dict, Iterable, List, Set, Tuple

import streamlit as st

from utils.auth import get_current_user, get_supabase, is_admin


PAGE_CATALOG: Dict[str, Dict[str, str]] = {
    "dashboard": {"label": "Dashboard", "path": "app.py", "icon": ":material/dashboard:"},
    "ask_echo": {"label": "Ask Echo.ai", "path": "pages/3_echo_ai.py", "icon": ":material/smart_toy:"},
    "tasks": {"label": "Tasks & Calendar", "path": "pages/4_tasks.py", "icon": ":material/calendar_month:"},
    "meetings": {"label": "Meetings", "path": "pages/2_meeting_details.py", "icon": ":material/menu_book:"},
    "minutes": {"label": "Minutes of the Meeting", "path": "pages/1_minutes_of_the_meeting.py", "icon": ":material/edit_note:"},
    "notebook": {"label": "Notebook", "path": "pages/6_notebook.py", "icon": ":material/edit_note:"},
    "documents": {"label": "Documents", "path": "pages/8_documents.py", "icon": ":material/description:"},
    "admin": {"label": "Admin Console", "path": "pages/0_admin.py", "icon": ":material/admin_panel_settings:"},
}

MEMBER_PAGE_KEYS = tuple(key for key in PAGE_CATALOG if key != "admin")
PAGE_ACCESS_TABLE = "user_page_access"
_CURRENT_ACCESS_KEY = "_current_page_access"


def _normalise_page_keys(page_keys: Iterable[str]) -> Set[str]:
    """Keep only known member pages and return a stable set."""
    return {str(key) for key in page_keys if str(key) in MEMBER_PAGE_KEYS}


def get_page_catalog(include_admin: bool = False) -> Dict[str, Dict[str, str]]:
    """Return a copy of the navigation catalog for admin or member UI."""
    if include_admin:
        return dict(PAGE_CATALOG)
    return {key: value for key, value in PAGE_CATALOG.items() if key != "admin"}


def get_all_page_access() -> Tuple[Dict[str, Set[str]], bool]:
    """Load saved access policies and report whether storage is available."""
    try:
        response = get_supabase().table(PAGE_ACCESS_TABLE).select("user_id, allowed_pages").execute()
        policies = {}
        for row in response.data or []:
            user_id = row.get("user_id")
            if user_id:
                policies[str(user_id)] = _normalise_page_keys(row.get("allowed_pages") or [])
        return policies, True
    except Exception:
        return {}, False


def get_user_page_access(user_id: Any) -> Set[str]:
    """Return a user's allowlist, defaulting existing users to all member pages."""
    if not user_id:
        return set()
    try:
        response = (
            get_supabase()
            .table(PAGE_ACCESS_TABLE)
            .select("allowed_pages")
            .eq("user_id", str(user_id))
            .limit(1)
            .execute()
        )
        if response.data:
            return _normalise_page_keys(response.data[0].get("allowed_pages") or [])
    except Exception:
        pass
    return set(MEMBER_PAGE_KEYS)


def get_current_page_access() -> Set[str]:
    """Return current user's access, cached for this Streamlit session."""
    user = get_current_user() or {}
    user_id = str(user.get("id") or "")
    if is_admin():
        return set(MEMBER_PAGE_KEYS)
    cached = st.session_state.get(_CURRENT_ACCESS_KEY)
    if cached and cached.get("user_id") == user_id:
        return set(cached.get("pages") or [])
    pages = get_user_page_access(user_id)
    st.session_state[_CURRENT_ACCESS_KEY] = {"user_id": user_id, "pages": sorted(pages)}
    return pages


def clear_current_page_access() -> None:
    """Clear the current user's session access cache after a policy change."""
    st.session_state.pop(_CURRENT_ACCESS_KEY, None)


def can_access_page(page_key: str) -> bool:
    """Return whether current user can open a known page."""
    if page_key == "admin":
        return is_admin()
    return page_key in get_current_page_access()


def set_user_page_access(user_id: Any, page_keys: Iterable[str], updated_by: Any = None) -> bool:
    """Persist a member page allowlist and clear affected session cache."""
    if not user_id:
        return False
    payload: Dict[str, Any] = {
        "user_id": str(user_id),
        "allowed_pages": sorted(_normalise_page_keys(page_keys)),
    }
    if updated_by:
        payload["updated_by"] = str(updated_by)
    try:
        response = get_supabase().table(PAGE_ACCESS_TABLE).upsert(payload, on_conflict="user_id").execute()
        if str(user_id) == str((get_current_user() or {}).get("id") or ""):
            clear_current_page_access()
        return bool(response.data is not None)
    except Exception:
        return False

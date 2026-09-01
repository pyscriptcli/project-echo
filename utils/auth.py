# utils/auth.py
"""
Project Echo — Authentication & Authorization.

Single source of truth for login, sessions, and role-based access control.

Every page must call ``require_login()`` (optionally ``require_login(require_admin=True)``)
immediately after ``st.set_page_config()``. This renders the shared login screen and
``st.stop()`` when the user is not authenticated, so no page can be reached without a
valid, non-expired session — including when a page is opened directly by URL.

Session policy (industry standard):
  * Absolute timeout  — session must be refreshed by re-login after SESSION_ABSOLUTE_MINUTES.
  * Idle timeout      — session expires after SESSION_IDLE_MINUTES of inactivity.

RBAC:
  * Users carry a ``role`` column (``admin`` / ``member``) on ``admin_users``.
  * ``require_login(require_admin=True)`` blocks non-admin users.
  * Bootstrap: a username declared as ``SUPER_ADMIN_USERNAME`` in secrets is always admin,
    so an owner is never locked out before the ``role`` column is populated.
"""
import streamlit as st
import bcrypt
from datetime import datetime, timezone
from typing import List, Dict, Any
from supabase import create_client, Client

# -------------------------------------------------------------------
# Session policy
# -------------------------------------------------------------------
SESSION_IDLE_MINUTES = 30
SESSION_ABSOLUTE_MINUTES = 8 * 60  # 8 hours

_AUTH_KEY = "user"
_AUTH_LOGIN_AT = "_auth_login_at"
_AUTH_LAST_ACTIVE = "_auth_last_active"
_AUTH_EXPIRED_MSG = "_auth_expired_msg"

PASSWORD_MIN_LENGTH = 8


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


# -------------------------------------------------------------------
# Supabase client initialization (cached)
# -------------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    """Return a cached Supabase client using credentials from secrets."""
    url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
    if url.endswith("/rest/v1"):
        url = url[:-8]
    key = "".join(str(st.secrets.get("SUPABASE_KEY", "")).split())
    if not url or not key:
        raise RuntimeError("Supabase URL or Key configuration missing in secrets.")
    return create_client(url, key)


def get_supabase() -> Client:
    """Return the cached Supabase client."""
    return init_supabase()


# -------------------------------------------------------------------
# Authentication core
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
    try:
        supabase = get_supabase()
        response = (
            supabase.table("admin_users")
            .select("*")
            .eq("username", username)
            .limit(1)
            .execute()
        )

        if not response.data:
            return False, "Invalid username or password.", None

        user_record = response.data[0]
        stored_hash = user_record.get("password_hash") or ""
        if not stored_hash:
            return False, "Invalid username or password.", None

        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            return False, "Invalid username or password.", None

        user = {
            "id": user_record.get("id"),
            "username": user_record.get("username"),
            "role": str(user_record.get("role") or "member").strip() or "member",
        }
        return True, "", user
    except Exception:
        # Generic error for security — don't leak internals to the login UI.
        return False, "Authentication error. Please try again.", None


def _open_session(user: dict):
    """Establish a fresh authenticated session with expiry timestamps."""
    st.session_state[_AUTH_KEY] = user
    now = _now_utc()
    st.session_state[_AUTH_LOGIN_AT] = now
    st.session_state[_AUTH_LAST_ACTIVE] = now


def logout():
    """Clear the current user and all auth-related session state."""
    for key in [_AUTH_KEY, _AUTH_LOGIN_AT, _AUTH_LAST_ACTIVE, _AUTH_EXPIRED_MSG]:
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    """Return True if a user is currently logged in (expiry checked separately)."""
    return st.session_state.get(_AUTH_KEY) is not None


def get_current_user():
    """Return the current user dict or None."""
    return st.session_state.get(_AUTH_KEY, None)


def is_admin() -> bool:
    """Return True if the current user holds the admin role."""
    user = st.session_state.get(_AUTH_KEY)
    if not user:
        return False
    role = str(user.get("role", "")).strip()
    if role == "admin":
        return True
    # Bootstrap: a username declared as SUPER_ADMIN_USERNAME is always admin.
    super_admin = str(st.secrets.get("SUPER_ADMIN_USERNAME", "")).strip()
    if super_admin and user.get("username") == super_admin:
        return True
    return False


def _expire_if_timed_out() -> bool:
    """Expire the current session if any timeout elapsed. Returns True if expired."""
    if not is_authenticated():
        return False
    now = _now_utc()
    login_at = st.session_state.get(_AUTH_LOGIN_AT)
    last_active = st.session_state.get(_AUTH_LAST_ACTIVE)

    if login_at and (now - login_at).total_seconds() > SESSION_ABSOLUTE_MINUTES * 60:
        st.session_state[_AUTH_EXPIRED_MSG] = "Your session expired. Please sign in again."
        logout()
        return True
    if last_active and (now - last_active).total_seconds() > SESSION_IDLE_MINUTES * 60:
        st.session_state[_AUTH_EXPIRED_MSG] = "You were idle too long. Please sign in again."
        logout()
        return True

    # Refresh the idle timestamp on any authenticated interaction.
    st.session_state[_AUTH_LAST_ACTIVE] = now
    return False


# -------------------------------------------------------------------
# Shared login screen UI
# -------------------------------------------------------------------
LOGIN_CSS = """
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.06) !important;
    border-radius: 12px !important;
    border-top: 3px solid #C1BAA1 !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08) !important;
    padding: 2rem !important;
    margin: 2rem auto !important;
    max-width: 450px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-brand {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 2rem;
    font-weight: 600;
    color: #0D1B3E;
    text-align: center;
}
.login-tagline {
    font-size: 0.9rem;
    color: #6E6A6A;
    text-align: center;
    margin-bottom: 1.5rem;
}

.stTextInput input {
    background-color: #FAFAFA !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
    border-radius: 0 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 0.75rem !important;
}
.stTextInput input:focus {
    border-color: #C1BAA1 !important;
    box-shadow: 0 0 0 2px rgba(212,175,55,0.15) !important;
    background: #FFFFFF !important;
}

.stFormSubmitButton > button {
    background-color: #D7D3BF !important;
    color: #0D1B3E !important;
    border: 0 none !important;
    border-radius: 0 !important;
    font-weight: 600 !important;
    min-height: 36px !important;
    width: 100% !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}

.login-error {
    background: #FDF0EF;
    border-left: 3px solid #E74C3C;
    color: #9B1C1C;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    font-size: 0.8rem;
    margin-top: 0.75rem;
}
.login-warning {
    background: #FFFBEB;
    border-left: 3px solid #F59E0B;
    color: #92400E;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    font-size: 0.8rem;
    margin-top: 0.5rem;
}
</style>
"""


def render_login():
    """Render the shared login screen (must be followed by st.stop() in the caller)."""
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    # Show a session-expiry notice if the previous run timed the session out.
    expired_msg = st.session_state.pop(_AUTH_EXPIRED_MSG, None)
    if expired_msg:
        st.markdown(f'<div class="login-warning">{expired_msg}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown(
                '<div class="login-brand">Project Echo</div>'
                '<div class="login-tagline">Sign in to your AI Assistant</div>',
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    key="login_username",
                    placeholder="Enter your username",
                    autocomplete="username",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                    placeholder="Enter your password",
                    autocomplete="current-password",
                )
                submitted = st.form_submit_button(
                    "Sign In",
                    use_container_width=True,
                    type="primary",
                )

            if submitted:
                errors = []
                if not (username or "").strip():
                    errors.append("Username is required.")
                if not (password or "").strip():
                    errors.append("Password is required.")
                if errors:
                    for e in errors:
                        st.markdown(f'<div class="login-error">{e}</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Signing in..."):
                        success, error_msg, user = login(username, password)
                    if success:
                        _open_session(user)
                        st.rerun()
                    else:
                        st.markdown(f'<div class="login-error">{error_msg}</div>', unsafe_allow_html=True)

            if password and password.isalpha() and password.isupper():
                st.markdown(
                    '<div class="login-warning">Caps Lock is on.</div>',
                    unsafe_allow_html=True,
                )


# -------------------------------------------------------------------
# Page gate — call at the top of every page
# -------------------------------------------------------------------
def require_login(require_admin: bool = False):
    """
    Enforce authentication (and optionally the admin role) on the current page.

    If the user is not authenticated, renders the shared login screen and stops the
    script so no protected content is ever rendered. If ``require_admin`` is True and
    the user is not an admin, shows an access-denied message and stops.
    """
    if is_authenticated():
        _expire_if_timed_out()

    if not is_authenticated():
        render_login()
        st.stop()

    if require_admin and not is_admin():
        st.error("You do not have permission to access this page.")
        st.stop()


# -------------------------------------------------------------------
# Deprecated alias — kept so existing callers keep working.
# -------------------------------------------------------------------
def require_auth():
    """Deprecated alias of require_login()."""
    require_login()


# -------------------------------------------------------------------
# Admin / user management
# -------------------------------------------------------------------
def validate_password_strength(password: str) -> List[str]:
    """Return a list of password-policy violations (empty when the password is OK)."""
    problems = []
    if len(password) < PASSWORD_MIN_LENGTH:
        problems.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long.")
    if not any(c.islower() for c in password):
        problems.append("Password must include at least one lowercase letter.")
    if not any(c.isupper() for c in password):
        problems.append("Password must include at least one uppercase letter.")
    if not any(c.isdigit() for c in password):
        problems.append("Password must include at least one number.")
    return problems


def add_admin_user(username: str, password: str, role: str = "member") -> bool:
    """Create a new admin user with hashed password and an optional role."""
    username = (username or "").strip()
    if not username:
        st.error("Username is required.")
        return False

    problems = validate_password_strength(password or "")
    if problems:
        st.error(" ".join(problems))
        return False

    supabase = get_supabase()
    try:
        existing = supabase.table("admin_users").select("id").eq("username", username).execute()
    except Exception:
        st.error("User creation failed. Please try again.")
        return False

    if existing.data:
        st.error("Username already exists.")
        return False

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    payload = {"username": username, "password_hash": hashed}
    if role in ("admin", "member"):
        payload["role"] = role

    try:
        supabase.table("admin_users").insert(payload).execute()
        return True
    except Exception:
        # Legacy schema without a role column: retry without it so creation still works.
        try:
            supabase.table("admin_users").insert(
                {"username": username, "password_hash": hashed}
            ).execute()
            return True
        except Exception:
            st.error("User creation failed. Please try again.")
            return False


def get_all_users() -> List[Dict[str, Any]]:
    """Return all admin users (id, username, created_at, can_use_agent)."""
    supabase = get_supabase()
    response = supabase.table("admin_users").select("id, username, created_at, can_use_agent").order("created_at").execute()
    return response.data if response.data else []


def can_use_agent(user_id) -> bool:
    """RBAC gate: is this user granted agent-mode access?"""
    if not user_id:
        return False
    try:
        supabase = get_supabase()
        resp = supabase.table("admin_users").select("can_use_agent").eq("id", user_id).limit(1).execute()
        if not resp.data:
            return False
        return bool(resp.data[0].get("can_use_agent", False))
    except Exception:  # noqa: BLE001
        return False


def set_agent_access(user_id, allowed: bool) -> bool:
    """Grant or revoke agent-mode access for a user."""
    supabase = get_supabase()
    try:
        resp = supabase.table("admin_users").update({"can_use_agent": bool(allowed)}).eq("id", user_id).execute()
        return bool(resp.data)
    except Exception:  # noqa: BLE001
        return False


def set_user_password(user_id, new_password: str) -> bool:
    """Reset a user's password. Plaintext is passed in the UI, stored bcrypt-hashed."""
    problems = validate_password_strength(new_password or "")
    if problems:
        st.error(" ".join(problems))
        return False
    hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    supabase = get_supabase()
    try:
        resp = supabase.table("admin_users").update({"password_hash": hashed}).eq("id", user_id).execute()
        return bool(resp.data)
    except Exception:  # noqa: BLE001
        st.error("Password update failed. Please try again.")
        return False


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
                "last_active": None,
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

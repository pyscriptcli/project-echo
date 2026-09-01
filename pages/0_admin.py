# pages/admin.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.auth import (
    require_login, add_admin_user, get_all_users, get_user_usage, logout,
    set_agent_access, set_user_password,
)
from utils.limits import set_user_limits, get_user_limits, DEFAULT_DAILY_LIMIT, DEFAULT_WEEKLY_LIMIT

# -------------------------------
# Page configuration & styling
# -------------------------------
st.set_page_config(
    page_title="Admin Console",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500;1,600&family=Inter:wght@400;500;600;700&display=swap');

.stApp > header { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }

html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    overflow: auto !important;
    padding-top: 1.5rem !important;
    padding-bottom: 1.5rem !important;
    padding-right: 2.2rem !important;
    padding-left: 2.2rem !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

[data-testid="stAppViewContainer"], .stApp {
    background-color: #F5F1E8 !important;
    background-image:
        linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px) !important;
    background-size: 80px 80px !important;
    background-position: 0 0 !important;
    color: #1A1A1A;
}

.section-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    font-weight: 600 !important;
    color: #1A2B4C !important;
    font-size: 1.2rem !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}
.section-caption {
    font-size: 0.72rem;
    color: #6C727A;
    margin: 0 0 0.35rem 0 !important;
}

.admin-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 0;
    border: 1px solid rgba(26, 43, 76, 0.14);
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: none;
}

.stButton > button {
    background-color: #111A2B !important;
    color: #FFFFFF !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 20px !important;
    font-size: 0.72rem !important;
    padding: 0.2rem 0.75rem !important;
    min-height: 26px !important;
    height: 26px !important;
    box-shadow: 0 4px 10px rgba(26, 43, 76, 0.18) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    border-color: #F1C40F !important;
    background-color: #1A263D !important;
    box-shadow: 0 0 6px rgba(212, 175, 55, 0.3) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 1px solid #D1D5DB !important;
    border-radius: 0.375rem !important;
}

[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 6px;
    border: 1px solid rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Authentication check
# -------------------------------
require_login(require_admin=True)

# Apply the shared flat & edgy theme (large gridlines, 0 radius) to the admin page
from components.theme import inject_global_css
inject_global_css()

# Sidebar: logout
with st.sidebar:
    st.markdown("---")
    if st.button("Logout", key="admin_logout"):
        logout()
        st.rerun()

st.markdown('<p class="section-title">Admin Console</p>', unsafe_allow_html=True)
st.markdown('<p class="section-caption">Manage accounts, monitor telemetry, configure agent access & rate limits.</p>', unsafe_allow_html=True)

all_users = get_all_users()

tab_accounts, tab_telemetry, tab_agent, tab_limits = st.tabs([
    "Accounts", "Telemetry", "Agent Access", "Rate Limits",
])

# ============================================================
# TAB: ACCOUNTS  (create user + manage passwords)
# ============================================================
with tab_accounts:
    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown("### Create New Account")
    with st.form("create_user_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            new_username = st.text_input("Username", placeholder="e.g., jdoe")
        with col2:
            new_password = st.text_input("Password", type="password", placeholder="Min 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
        new_role = st.selectbox("Role", options=["member", "admin"], index=0,
                                help="Admins can create users and access the Admin Console.")
        submitted = st.form_submit_button("Create User")
        if submitted:
            if not new_username or not new_password:
                st.error("Username and password are required.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success = add_admin_user(new_username, new_password, role=new_role)
                if success:
                    st.success(f"User '{new_username}' created successfully.")
                else:
                    st.error("User creation failed. Check the username is unique and the password meets the policy.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown("### Manage Passwords")
    st.markdown("Enter a new password in plaintext below. It is stored as a bcrypt hash in Supabase — plaintext is never saved.")
    pwd_all_users = all_users or get_all_users()
    if not pwd_all_users:
        st.info("No users found.")
    else:
        pwd_user = st.selectbox(
            "Select user", options=pwd_all_users,
            format_func=lambda u: str(u.get("username") or "unknown"),
            key="pwd_select",
        )
        new_pw = st.text_input("New Password", type="password", key="pwd_new", placeholder="Min 8 characters, uppercase+lowercase+number")
        confirm_pw = st.text_input("Confirm New Password", type="password", key="pwd_confirm")
        if st.button("Update Password", key="pwd_update"):
            if not new_pw:
                st.error("Password is required.")
            elif new_pw != confirm_pw:
                st.error("Passwords do not match.")
            else:
                ok = set_user_password(pwd_user.get("id"), new_pw)
                if ok:
                    st.success(f"Password updated for '{pwd_user.get('username')}'.")
                else:
                    st.error("Password update failed. Check the policy (min 8 chars, lower+upper+number).")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB: TELEMETRY  (usage dashboard)
# ============================================================
with tab_telemetry:
    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown("### User Usage Telemetry")
    if st.button("Refresh Data", key="refresh_usage"):
        st.rerun()

    usage_data = get_user_usage()
    if not usage_data:
        st.info("No usage data recorded yet. Telemetry fills as users interact with Ask Echo / Agent mode.")
    else:
        df = pd.DataFrame(usage_data)
        if "last_active" in df.columns:
            df["last_active"] = df["last_active"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M") if x else "Never")

        total_tokens = df["total_tokens"].sum()
        total_events = df["total_events"].sum()
        total_users = len(df)
        active_7d = sum(1 for x in df["last_active"] if x != "Never"
                        and (datetime.now() - datetime.strptime(x, "%Y-%m-%d %H:%M")) <= timedelta(days=7))

        kpi_cols = st.columns(4)
        kpi_cols[0].metric("Total Users", total_users)
        kpi_cols[1].metric("Total Tokens", f"{total_tokens:,}")
        kpi_cols[2].metric("Total Events", total_events)
        kpi_cols[3].metric("Active (7d)", active_7d)

        st.markdown("#### Tokens per User")
        chart_data = df[["username", "total_tokens"]].set_index("username")
        st.bar_chart(chart_data)

        st.markdown("#### Detailed Usage")
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB: AGENT ACCESS  (RBAC grant/revoke)
# ============================================================
with tab_agent:
    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown("### Agentic AI Access")
    st.markdown("Control which users can enable **Agent mode** in Ask Echo. Users without access see a \"contact the developer\" notice in chat settings.")
    agent_users = all_users or get_all_users()
    if not agent_users:
        st.info("No users found.")
    else:
        for u in agent_users:
            uname = str(u.get("username") or "unknown")
            uid = u.get("id")
            cur = bool(u.get("can_use_agent", False))
            c1, c2 = st.columns([3, 7])
            with c1:
                granted = st.checkbox("Enable Agent mode", value=cur, key=f"agent_gr_{uid}")
            with c2:
                st.markdown(f"<b>{uname}</b> <span style='color:#888;font-size:0.8rem'>({uid})</span>", unsafe_allow_html=True)
            if granted != cur:
                if set_agent_access(uid, granted):
                    st.caption(f"{uname}: access {'granted' if granted else 'revoked'}")
                    st.rerun()
                else:
                    st.warning(f"Could not update access for {uname}. Check that agent_rbac_ddl.sql has been run.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB: RATE LIMITS  (per-user daily/weekly token budgets)
# ============================================================
with tab_limits:
    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown("### Per-User Token Rate Limits")
    st.markdown("Set daily/weekly token budgets for Ask Echo. The app enforces these per user. Default is 50k daily / 250k weekly.")
    st.caption("Requires the `usage_limits` table — run `supabase/usage_limits_ddl.sql` if you haven't.")
    limits_users = all_users or get_all_users()
    if not limits_users:
        st.info("No users found.")
    else:
        for u in limits_users:
            uname = str(u.get("username") or "unknown")
            uid = u.get("id")
            lim = get_user_limits(uid)
            col_a, col_b, col_c = st.columns([3, 2, 2])
            with col_a:
                st.markdown(f"<b>{uname}</b>", unsafe_allow_html=True)
            with col_b:
                daily = st.number_input("Daily limit", min_value=1000, step=5000,
                                        value=int(lim["daily_limit"]), key=f"lim_d_{uid}")
            with col_c:
                weekly = st.number_input("Weekly limit", min_value=2000, step=10000,
                                         value=int(lim["weekly_limit"]), key=f"lim_w_{uid}")
            col_s, _ = st.columns([2, 8])
            with col_s:
                if st.button("Save", key=f"lim_save_{uid}"):
                    if set_user_limits(uid, int(daily), int(weekly)):
                        st.success(f"Saved limits for {uname}")
                        st.rerun()
                    else:
                        st.error("Could not save limits.")
            st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)

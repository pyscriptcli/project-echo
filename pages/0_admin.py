# pages/admin.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.auth import require_login, add_admin_user, get_all_users, get_user_usage, logout, set_agent_access

# -------------------------------
# Page configuration & styling
# -------------------------------
st.set_page_config(
    page_title="Admin Console",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Reuse the global CSS from app.py? We'll include a condensed version for this page.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500;1,600&family=Inter:wght@400;500;600;700&display=swap');

.stApp > header { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }

html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    overflow: auto !important;
    padding-top: 0.8rem !important;
    padding-bottom: 0.5rem !important;
    padding-right: 1.5rem !important;
    padding-left: 1.5rem !important;
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

/* Container styling */
.admin-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

/* Buttons – same pill style as main app */
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

/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 1px solid #D1D5DB !important;
    border-radius: 0.375rem !important;
}

/* Dataframe styling */
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

# -------------------------------
# Sidebar: logout button
# -------------------------------
with st.sidebar:
    st.markdown("---")
    if st.button("Logout", key="admin_logout"):
        logout()
        st.rerun()

# -------------------------------
# Main content
# -------------------------------
st.markdown('<p class="section-title">Admin Console</p>', unsafe_allow_html=True)
st.markdown('<p class="section-caption">Manage admin accounts and monitor user activity.</p>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# 1. Account Creation Section
# ------------------------------------------------------------------
st.markdown('<div class="admin-card">', unsafe_allow_html=True)
st.markdown("### Create New Admin")
with st.form("create_user_form", clear_on_submit=True):
    col1, col2 = st.columns([1, 1])
    with col1:
        new_username = st.text_input("Username", placeholder="e.g., jdoe")
    with col2:
        new_password = st.text_input("Password", type="password", placeholder="Min 8 characters")
        confirm_password = st.text_input("Confirm Password", type="password")

    new_role = st.selectbox(
        "Role",
        options=["member", "admin"],
        index=0,
        help="Admins can create users and access the Admin Console.",
    )

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

# ------------------------------------------------------------------
# 2. Telemetry / Usage Dashboard
# ------------------------------------------------------------------
st.markdown('<div class="admin-card">', unsafe_allow_html=True)
st.markdown("### User Usage Telemetry")

# Fetch usage data
usage_data = get_user_usage()
all_users = get_all_users()

# Refresh button
if st.button("Refresh Data", key="refresh_usage"):
    st.rerun()

if not usage_data:
    st.info("No usage data recorded yet.")
else:
    df = pd.DataFrame(usage_data)
    # Format last_active
    if "last_active" in df.columns:
        df["last_active"] = df["last_active"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M") if x else "Never")

    # KPI cards
    total_tokens = df["total_tokens"].sum()
    total_events = df["total_events"].sum()
    total_users = len(df)
    active_7d = sum(1 for x in df["last_active"] if x != "Never" and (datetime.now() - datetime.strptime(x, "%Y-%m-%d %H:%M")) <= timedelta(days=7))

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total Users", total_users)
    kpi_cols[1].metric("Total Tokens", f"{total_tokens:,}")
    kpi_cols[2].metric("Total Events", f"{total_events:,}")
    kpi_cols[3].metric("Active (7d)", active_7d)

    # Bar chart: tokens per user
    st.markdown("#### Tokens Used per User")
    chart_data = df[["username", "total_tokens"]].set_index("username")
    st.bar_chart(chart_data)

    # Detailed table
    st.markdown("#### Detailed Usage")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Agentic AI Access (RBAC) — grant users the right to enable Agent mode
# ------------------------------------------------------------------
st.markdown('<div class="admin-card">', unsafe_allow_html=True)
st.markdown("### Agentic AI Access")
st.markdown("Control which users can enable **Agent mode** in Ask Echo. Users without access will see a \"contact the developer\" notice in the chat settings.")
all_users = get_all_users()
if not all_users:
    st.info("No users found.")
else:
    for u in all_users:
        uname = str(u.get("username") or "unknown")
        uid = u.get("id")
        cur = bool(u.get("can_use_agent", False))
        c1, c2 = st.columns([3, 7])
        with c1:
            granted = st.checkbox("Enable Agent mode", value=cur, key=f"agent_gr_{uname}_{uid}")
        with c2:
            st.markdown(f"<b>{uname}</b> <span style='color:#888;font-size:0.8rem'>({uid})</span>", unsafe_allow_html=True)
        if granted != cur:
            if set_agent_access(uid, granted):
                st.caption(f"{uname}: access {'granted' if granted else 'revoked'}")
                st.rerun()
            else:
                st.warning(f"Could not update access for {uname}. Check that the agent_rbac_ddl.sql has been run.")
st.markdown('</div>', unsafe_allow_html=True)

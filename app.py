import streamlit as st

def render_global_navbar(page_title="Project Echo"):
    # 1. Global Layout CSS & Topbar Header
    custom_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif !important;
    }}

    /* Global Grid Background */
    .stApp {{
        background-color: #F3EFE6; 
        background-image: 
            linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
        background-size: 80px 80px;
        color: #2D2D2D;
    }}

    .stApp > header {{ display: none !important; }}

    /* Layout Spacing */
    .block-container {{ 
        padding-top: 5.5rem !important; 
        padding-left: 6.2rem !important;
        padding-right: 2rem !important;
        max-width: 98% !important;
    }}

    /* Fixed Topbar Header */
    .echo-topbar-wrapper {{
        position: fixed; 
        top: 0; 
        left: 0; 
        right: 0; 
        height: 60px;
        background-color: #161616;
        border-bottom: 1px solid #333333;
        z-index: 999990; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        display: flex; 
        align-items: center; 
        justify-content: flex-start;
        padding: 0 2rem;
    }}

    .echo-title {{
        font-family: 'Playfair Display', serif !important;
        font-style: italic !important; 
        font-weight: 400 !important;
        font-size: 1.35rem !important; 
        color: #FFFFFF !important; 
        margin: 0 !important;
    }}
    .echo-title span {{ color: #D4AF37 !important; }}

    h3 {{
        font-family: 'Playfair Display', serif !important;
        font-style: italic !important; 
        font-weight: 400 !important; 
        color: #1A2B4C !important; 
        letter-spacing: 0.02em; 
        margin-bottom: 0.25rem; 
        font-size: 1.25rem !important;
    }}

    .playfair-label {{
        font-family: 'Playfair Display', serif !important;
        font-style: italic !important;
        font-weight: 400 !important;
        color: #1A2B4C !important;
        font-size: 1.05rem !important;
        margin-bottom: 0.25rem !important;
        display: block;
    }}

    /* Streamlit Sidebar Configured as Permanent Left Icon Rail */
    section[data-testid="stSidebar"] {{
        position: fixed !important;
        top: 60px !important;
        left: 0 !important;
        bottom: 0 !important;
        width: 68px !important;
        min-width: 68px !important;
        max-width: 68px !important;
        background-color: #161616 !important;
        border-right: 1px solid #2B2B2B !important;
        box-shadow: 4px 0 15px rgba(0,0,0,0.2) !important;
        z-index: 999980 !important;
        transform: none !important;
        margin-left: 0 !important;
        visibility: visible !important;
        display: block !important;
    }}

    button[data-testid="stSidebarCollapseButton"],
    div[data-testid="stSidebarHeader"],
    div[data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {{
        padding: 1.25rem 0.6rem !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{
        gap: 1rem !important;
        align-items: center !important;
    }}

    /* Native Streamlit Sidebar Icon Buttons */
    section[data-testid="stSidebar"] .stButton > button {{
        width: 44px !important;
        height: 44px !important;
        min-height: 44px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        background-color: #222222 !important;
        border: 1px solid #333333 !important;
        color: #C5A059 !important;
        font-size: 1.3rem !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: #D4AF37 !important;
        color: #161616 !important;
        border-color: #D4AF37 !important;
        transform: translateY(-1px);
    }}

    /* Main Content Containers & Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #FFFFFF !important; 
        border-radius: 12px !important;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1), 0 4px 10px -2px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important; 
        padding: 1.5rem !important; 
        margin-bottom: 1.25rem !important;
    }}

    /* Form Fields */
    .stTextArea textarea, .stTextInput input, div[data-baseweb="select"] > div {{
        background-color: #FAFAFA !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        border-radius: 8px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
        font-size: 0.92rem !important;
        line-height: 1.45 !important;
    }}
    .stTextArea textarea:focus, .stTextInput input:focus, div[data-baseweb="select"] > div:focus-within {{
        background-color: #FFFFFF !important;
        border-color: #D4AF37 !important;
    }}

    /* Action Buttons */
    .block-container .stButton > button, .block-container .stDownloadButton > button {{
        background-color: #222222 !important; 
        color: #FFFFFF !important;
        border: none !important; 
        border-radius: 50px !important; 
        font-family: 'Montserrat', sans-serif !important; 
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.5px; 
        padding: 0.4rem 1.2rem !important;
        height: 36px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.2s ease !important; 
        width: 100% !important;
    }}

    .block-container .stButton > button:hover, .block-container .stDownloadButton > button:hover {{
        background-color: #D4AF37 !important;
        color: #161616 !important;
        transform: translateY(-1px);
    }}

    button[key^="del_"], button[key^="del_md_"] {{
        background-color: #FDF9F9 !important;
        color: #B23A3A !important;
        border: 1px solid rgba(178, 58, 58, 0.25) !important;
    }}

    button[key^="del_"]:hover, button[key^="del_md_"]:hover {{
        background-color: #B23A3A !important;
        color: #FFFFFF !important;
        border-color: #B23A3A !important;
    }}

    /* Minimalist Chat */
    .chat-container {{ display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem; padding-bottom: 1rem; }}
    .chat-ai {{
        align-self: flex-start;
        color: #1A1A1A;
        padding: 0.2rem;
        max-width: 95%;
        font-size: 0.88rem;
        line-height: 1.5;
    }}
    .chat-user-wrap {{ display: flex; justify-content: flex-end; width: 100%; margin-bottom: 0.2rem; }}
    .chat-user {{
        background-color: #F3F4F6;
        color: #1A1A1A;
        padding: 0.55rem 0.95rem;
        border-radius: 14px;
        max-width: 82%;
        font-size: 0.88rem;
        line-height: 1.45;
    }}
    </style>

    <div class="echo-topbar-wrapper">
        <h1 class="echo-title">{page_title}</h1>
    </div>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # 2. Native Multi-page Navigation via st.switch_page (Guarantees zero 404 errors)
    with st.sidebar:
        if st.button("🎛️", key="nav_btn_home", help="Executive Dashboard"):
            st.switch_page("app.py")

        if st.button("📝", key="nav_btn_mom", help="MoM Generator"):
            st.switch_page("pages/1_minutes_of_the_meeting.py")

        if st.button("📖", key="nav_btn_details", help="Meeting Browser"):
            st.switch_page("pages/2_meeting_details.py")

        if st.button("🤖", key="nav_btn_echo", help="Ask Echo AI"):
            st.switch_page("pages/5_ask_echo.py")

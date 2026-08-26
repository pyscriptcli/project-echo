import streamlit as st

def render_global_navbar(page_title="Project Echo &mdash; Executive Hub"):
    nav_html = f"""
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

    /* Completely suppress native sidebar elements */
    section[data-testid="stSidebar"],
    button[data-testid="stSidebarCollapseButton"],
    div[data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    /* Viewport spacing for fixed navigation rail */
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

    button[data-baseweb="tab"] p {{
        font-family: 'Playfair Display', serif !important;
        font-style: italic !important;
        font-weight: 400 !important;
        color: #1A2B4C !important;
        font-size: 1.05rem !important;
    }}

    /* Permanent Viewport Left Icon Rail */
    .echo-nav-rail {{
        position: fixed;
        top: 60px;
        left: 0;
        bottom: 0;
        width: 68px;
        background-color: #161616;
        border-right: 1px solid #2B2B2B;
        box-shadow: 4px 0 15px rgba(0,0,0,0.2);
        z-index: 999980;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1.25rem 0;
        gap: 1.25rem;
    }}

    .echo-nav-item {{
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background-color: #222222;
        border: 1px solid #333333;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        transition: all 0.2s ease;
        cursor: pointer;
    }}

    .echo-nav-item svg {{
        width: 22px;
        height: 22px;
        stroke: #C5A059;
        fill: none;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
        transition: all 0.2s ease;
    }}

    .echo-nav-item:hover {{
        background-color: #D4AF37;
        border-color: #D4AF37;
        transform: translateY(-1px);
    }}

    .echo-nav-item:hover svg {{
        stroke: #161616;
    }}

    /* Card Panels & Containers */
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

    /* Pill Action Buttons */
    .stButton > button, .stDownloadButton > button {{
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

    .stButton > button:hover, .stDownloadButton > button:hover {{
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

    <!-- Topbar -->
    <div class="echo-topbar-wrapper">
        <h1 class="echo-title">{page_title}</h1>
    </div>

    <!-- Left Rail -->
    <div class="echo-nav-rail">
        <a href="/" target="_self" class="echo-nav-item" title="Executive Dashboard">
            <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
        </a>
        <a href="/1_minutes_of_the_meeting" target="_self" class="echo-nav-item" title="MoM Generator">
            <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        </a>
        <a href="/2_meeting_details" target="_self" class="echo-nav-item" title="Meeting Browser">
            <svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
        </a>
        <a href="/5_ask_echo" target="_self" class="echo-nav-item" title="Ask Echo AI">
            <svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8.01" y2="16"></line><line x1="16" y1="16" x2="16.01" y2="16"></line></svg>
        </a>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)

import streamlit as st
import base64

def render_global_navbar(page_title="Project Echo"):
    # SVG icons (stroke="currentColor" so they inherit the button's color)
    svg_home = '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 12l9-9 9 9"/>
        <path d="M5 10v10a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v4a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1V10"/>
    </svg>
    '''
    svg_document = '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
    '''
    svg_book = '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
    </svg>
    '''
    svg_chat = '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
    '''

    # Encode SVGs to base64 for use in CSS data URIs
    def b64(svg):
        return base64.b64encode(svg.encode()).decode()

    b64_home = b64(svg_home)
    b64_doc = b64(svg_document)
    b64_book = b64(svg_book)
    b64_chat = b64(svg_chat)

    # 1. Inject Topbar Header & Global CSS
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

    /* Left Icon Buttons */
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

    /* ----- SVG Icon Overrides for Navigation Buttons ----- */
    #nav_btn_home, #nav_btn_mom, #nav_btn_details, #nav_btn_echo {{
        font-size: 0 !important;           /* hide the label text */
        color: #C5A059 !important;         /* inherit this color for the SVG (stroke="currentColor") */
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    #nav_btn_home::before,
    #nav_btn_mom::before,
    #nav_btn_details::before,
    #nav_btn_echo::before {{
        content: "";
        display: inline-block;
        width: 24px;
        height: 24px;
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        flex-shrink: 0;
    }}

    #nav_btn_home::before {{
        background-image: url('data:image/svg+xml;base64,{b64_home}');
    }}
    #nav_btn_mom::before {{
        background-image: url('data:image/svg+xml;base64,{b64_doc}');
    }}
    #nav_btn_details::before {{
        background-image: url('data:image/svg+xml;base64,{b64_book}');
    }}
    #nav_btn_echo::before {{
        background-image: url('data:image/svg+xml;base64,{b64_chat}');
    }}

    /* Main Content Cards & Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #FFFFFF !important; 
        border-radius: 12px !important;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1), 0 4px 10px -2px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important; 
        padding: 1.5rem !important; 
        margin-bottom: 1.25rem !important;
    }}

    /* Inputs */
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

    # 2. Native Multi-page Navigation via st.switch_page (Prevents 404 reloads)
    #    Each button now uses an empty label; the icon is provided by the CSS ::before.
    with st.sidebar:
        if st.button("", key="nav_btn_home", help="Executive Dashboard"):
            st.switch_page("app.py")

        if st.button("", key="nav_btn_mom", help="MoM Generator"):
            st.switch_page("pages/1_minutes_of_the_meeting.py")

        if st.button("", key="nav_btn_details", help="Meeting Browser"):
            st.switch_page("pages/2_meeting_details.py")

        if st.button("", key="nav_btn_echo", help="Ask Echo AI"):
            st.switch_page("pages/5_ask_echo.py")

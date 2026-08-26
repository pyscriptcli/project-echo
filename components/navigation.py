import os
import urllib.parse
import streamlit as st

def render_global_navigation():
    """Renders the persistent floating sidebar and injects global CSS."""
    
    # 1. Session State for Toggle
    if "sidebar_expanded" not in st.session_state:
        st.session_state["sidebar_expanded"] = False

    def toggle_sidebar():
        st.session_state["sidebar_expanded"] = not st.session_state["sidebar_expanded"]

    is_expanded = st.session_state["sidebar_expanded"]
    
    # 2. Dynamic CSS Variables
    sb_width = "240px" if is_expanded else "72px"
    justify = "flex-start" if is_expanded else "center"
    pad = "0 16px" if is_expanded else "0"
    opacity = "1" if is_expanded else "0"
    display = "inline-block" if is_expanded else "none"
    main_padding_left = f"calc(24px + {sb_width} + 24px)"

    # 3. SVG Icons
    def svg_uri(svg: str, color: str = "#C5A059") -> str:
        safe_svg = svg.replace('#C5A059', color).replace('#D4AF37', color)
        return f"url('data:image/svg+xml,{urllib.parse.quote(safe_svg)}')"

    svg_dash = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>'
    svg_mom = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
    svg_ask = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
    toggle_points = "15 18 9 12 15 6" if is_expanded else "9 18 15 12 9 6"
    svg_toggle = f'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="{toggle_points}"></polyline></svg>'

    # 4. Inject CSS
    CUSTOM_CSS = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

    html, body, [class*="css"] {{ font-family: 'Montserrat', sans-serif !important; }}
    .stApp {{ background-color: #F3EFE6; }}
    .stApp > header {{ display: none !important; }}

    .block-container {{ 
        padding-top: 5.5rem !important;
        padding-left: {main_padding_left} !important;
        padding-right: 2rem !important;
        transition: padding-left 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}

    .echo-topbar-wrapper {{
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background-color: #161616; border-bottom: 1px solid #333333;
        z-index: 999990; box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        display: flex; align-items: center; justify-content: flex-start; padding: 0 2rem;
    }}
    .echo-title {{
        font-family: 'Playfair Display', serif !important; font-style: italic !important; 
        font-weight: 400 !important; font-size: 1.35rem !important; 
        color: #FFFFFF !important; margin: 0 !important;
    }}
    .echo-title span {{ color: #D4AF37 !important; }}
    h3 {{
        font-family: 'Playfair Display', serif !important; font-style: italic !important; 
        font-weight: 400 !important; color: #1A2B4C !important; 
        letter-spacing: 0.02em; margin-bottom: 0.25rem; font-size: 1.25rem !important;
    }}

    /* Floating Sidebar */
    section[data-testid="stSidebar"] {{
        position: fixed !important; left: 24px !important; top: 84px !important;
        height: calc(100vh - 108px) !important;
        width: {sb_width} !important; min-width: {sb_width} !important; max-width: {sb_width} !important;
        background-color: #161616 !important; border-radius: 16px !important;
        border: 1px solid #2B2B2B !important; box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
        z-index: 999995 !important; overflow: hidden !important;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    section[data-testid="stSidebar"] > div {{ padding: 16px 12px !important; height: 100%; display: flex; flex-direction: column; }}
    section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{ gap: 8px !important; align-items: {justify} !important; flex: 1; }}

    /* Nav Links */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] {{
        width: 100% !important; height: 44px !important; min-height: 44px !important;
        padding: {pad} !important; display: flex !important; align-items: center !important;
        justify-content: {justify} !important; background-color: transparent !important;
        border: 1px solid transparent !important; border-radius: 8px !important;
        color: #ECE9DF !important; text-decoration: none !important; transition: all 0.2s ease !important;
    }}
    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {{ background-color: #222222 !important; border-color: #333333 !important; color: #D4AF37 !important; }}
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stIconMaterial"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"] {{ display: none !important; }}

    /* SVG Injections */
    section[data-testid="stSidebar"] a[href="/"]::before,
    section[data-testid="stSidebar"] a[href="/app.py"]::before {{
        content: ''; display: inline-block; width: 20px; height: 20px;
        background-image: {svg_uri(svg_dash)}; background-size: contain; background-repeat: no-repeat; min-width: 20px;
    }}
    section[data-testid="stSidebar"] a[href="/"]:hover::before,
    section[data-testid="stSidebar"] a[href="/app.py"]:hover::before {{ background-image: {svg_uri(svg_dash, '#D4AF37')}; }}

    section[data-testid="stSidebar"] a[href*="minutes"]::before,
    section[data-testid="stSidebar"] a[href*="mom"]::before {{
        content: ''; display: inline-block; width: 20px; height: 20px;
        background-image: {svg_uri(svg_mom)}; background-size: contain; background-repeat: no-repeat; min-width: 20px;
    }}
    section[data-testid="stSidebar"] a[href*="minutes"]:hover::before,
    section[data-testid="stSidebar"] a[href*="mom"]:hover::before {{ background-image: {svg_uri(svg_mom, '#D4AF37')}; }}

    section[data-testid="stSidebar"] a[href*="ask_echo"]::before {{
        content: ''; display: inline-block; width: 20px; height: 20px;
        background-image: {svg_uri(svg_ask)}; background-size: contain; background-repeat: no-repeat; min-width: 20px;
    }}
    section[data-testid="stSidebar"] a[href*="ask_echo"]:hover::before {{ background-image: {svg_uri(svg_ask, '#D4AF37')}; }}

    /* Text Injections */
    section[data-testid="stSidebar"] a[href="/"]::after,
    section[data-testid="stSidebar"] a[href="/app.py"]::after {{
        content: "Executive Dashboard"; margin-left: 12px; font-size: 0.9rem; font-weight: 500;
        white-space: nowrap; opacity: {opacity}; display: {display}; transition: opacity 0.2s ease; color: inherit;
    }}
    section[data-testid="stSidebar"] a[href*="minutes"]::after,
    section[data-testid="stSidebar"] a[href*="mom"]::after {{
        content: "MoM Generator"; margin-left: 12px; font-size: 0.9rem; font-weight: 500;
        white-space: nowrap; opacity: {opacity}; display: {display}; transition: opacity 0.2s ease; color: inherit;
    }}
    section[data-testid="stSidebar"] a[href*="ask_echo"]::after {{
        content: "Ask Echo AI"; margin-left: 12px; font-size: 0.9rem; font-weight: 500;
        white-space: nowrap; opacity: {opacity}; display: {display}; transition: opacity 0.2s ease; color: inherit;
    }}

    /* Toggle Button */
    section[data-testid="stSidebar"] button[key="toggle_sidebar"] {{
        margin-top: auto; width: 100% !important; height: 44px !important; min-height: 44px !important;
        background-color: transparent !important; border: 1px solid #333333 !important; border-radius: 8px !important;
        color: #C5A059 !important; display: flex !important; align-items: center !important;
        justify-content: {justify} !important; padding: {pad} !important; transition: all 0.2s ease !important;
        font-family: 'Montserrat', sans-serif !important; font-size: 0.9rem !important; font-weight: 500 !important;
    }}
    section[data-testid="stSidebar"] button[key="toggle_sidebar"]:hover {{ background-color: #222222 !important; border-color: #D4AF37 !important; color: #D4AF37 !important; }}
    section[data-testid="stSidebar"] button[key="toggle_sidebar"] span[data-testid="stIconMaterial"] {{ display: none !important; }}
    section[data-testid="stSidebar"] button[key="toggle_sidebar"]::before {{
        content: ''; display: inline-block; width: 20px; height: 20px;
        background-image: {svg_uri(svg_toggle)}; background-size: contain; background-repeat: no-repeat; min-width: 20px;
    }}
    section[data-testid="stSidebar"] button[key="toggle_sidebar"]:hover::before {{ background-image: {svg_uri(svg_toggle, '#D4AF37')}; }}
    </style>
    """
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # 5. Render Sidebar
    with st.sidebar:
        st.page_link("app.py", label="Executive Dashboard")
        
        # Dynamic path resolution for pages
        mom_page = "pages/1_minutes_of_the_meeting.py" if os.path.exists("pages/1_minutes_of_the_meeting.py") else "pages/mom_generator.py"
        ask_page = "pages/2_ask_echo.py" if os.path.exists("pages/2_ask_echo.py") else "pages/ask_echo.py"
        
        st.page_link(mom_page, label="MoM Generator")
        st.page_link(ask_page, label="Ask Echo AI")
        
        st.markdown("<div style='flex:1;'></div>", unsafe_allow_html=True)
        
        toggle_text = "Collapse" if is_expanded else "Expand"
        if st.button(toggle_text, key="toggle_sidebar", use_container_width=True, on_click=toggle_sidebar):
            pass

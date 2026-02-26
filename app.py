import streamlit as st
from src.database import db, logger
from src.ui_components import apply_custom_styles, sidebar_user_info
from src.views.login import show_login_view
from src.views.admin_panel import show_admin_panel
from src.views.dashboard import show_player_dashboard

# Application Setup
st.set_page_config(page_title="Mordheim Manager", layout="wide", page_icon="⚔️")
apply_custom_styles()

if "user" not in st.session_state:
    st.session_state.user = None

# Routing Logic
if not st.session_state.user:
    show_login_view()
else:
    try:
        # 1. Fetch Fresh User Profile
        profile_res = db.table("profiles").select("*").eq("id", st.session_state.user.id).single().execute()
        profile = profile_res.data
        
        if not profile:
            logger.error(f"No profile found for UID: {st.session_state.user.id}")
            st.error("Profile not found. Please contact the administrator.")
            st.stop()

        # 2. Render Sidebar
        sidebar_user_info(profile)

        # 3. Render View based on Role
        if profile['role'] == 'owner':
            show_admin_panel(profile)
        else:
            show_player_dashboard(profile)

    except Exception as e:
        logger.error(f"Main App Routing Error: {e}")
        st.error("A critical error occurred in the city. Re-entering...")
        if st.button("Retry Entry"):
            st.session_state.user = None
            st.rerun()

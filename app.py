import streamlit as st
from src.database import db, logger
from src.ui_components import apply_custom_styles, sidebar_user_info
from src.views.login import show_login_view

# 1. SETUP
st.set_page_config(page_title="Mordheim Manager", layout="wide")
apply_custom_styles()

if "user" not in st.session_state:
    st.session_state.user = None

# 2. ROUTING LOGIC
if not st.session_state.user:
    show_login_view()
else:
    try:
        # Fetch Profile
        profile_res = db.table("profiles").select("*").eq("id", st.session_state.user.id).single().execute()
        profile = profile_res.data
        
        # Global Sidebar
        sidebar_user_info(profile)

        # Content Routing
        if profile['role'] == 'owner':
            # We could move this to src/views/admin_panel.py
            st.header("👑 Grand Master's Quarters")
            st.write("Admin tools here...")
        else:
            st.header("📜 Warband Ledger")
            st.info("The city guards are inspecting your papers...")

    except Exception as e:
        logger.error(f"Routing Error: {e}")
        st.error("Something went wrong. Please try logging in again.")
        if st.button("Hard Reset"):
            st.session_state.user = None
            st.rerun()

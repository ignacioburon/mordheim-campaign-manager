import streamlit as st
from src.database import db, logger
from src.ui_components import apply_custom_styles, sidebar_user_info
from src.views.login import show_login_view
from src.views.admin_panel import show_admin_panel
from src.views.dashboard import show_player_dashboard
from src.views.recovery import show_recovery_view

# 1. SETUP
st.set_page_config(
    page_title="Mordheim Manager", 
    layout="wide", 
    page_icon="⚔️"
)
apply_custom_styles()

if "user" not in st.session_state:
    st.session_state.user = None

# 2. ROUTING ENGINE
# Check if the user is returning from a password reset email
is_recovery = st.query_params.get("type") == "recovery"

if is_recovery:
    show_recovery_view()

elif not st.session_state.user:
    show_login_view()

else:
    # AUTHENTICATED AREA
    try:
        # Fetch fresh profile data
        profile_res = db.table("profiles").select("*").eq("id", st.session_state.user.id).single().execute()
        profile = profile_res.data
        
        if not profile:
            st.error("Profile not found in archives.")
            if st.button("Logout"):
                st.session_state.user = None
                st.rerun()
            st.stop()

        # Render global sidebar
        sidebar_user_info(profile)

        # Content Routing by Role
        if profile['role'] == 'owner':
            show_admin_panel(profile)
        else:
            show_player_dashboard(profile)

    except Exception as e:
        logger.error(f"Routing Error: {e}")
        st.error("A shadow has fallen over the city. Please try entering again.")
        if st.button("Re-sync"):
            st.session_state.user = None
            st.rerun()

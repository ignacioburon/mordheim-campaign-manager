import streamlit as st
from src.database import logger

def show_player_dashboard(profile):
    """View for approved Captains to manage their warbands."""
    st.header("📜 Warband Ledger")
    
    if not profile.get('is_approved'):
        st.warning("⚔️ Access Denied: You are currently being held at the city gates for inspection.")
        st.info("Please wait for the Grand Master to approve your entry.")
        return

    st.success(f"Welcome back, Captain {profile['username']}.")
    
    # Placeholder for future modules
    tabs = st.tabs(["My Warband", "The Market", "Combat Logs"])
    
    with tabs[0]:
        st.subheader("Warband Management")
        st.write("Current Gold Crowns: 500")
        st.info("The Warband Creation module is under development.")
        
    with tabs[1]:
        st.subheader("Mordheim Marketplace")
        st.write("Buy weapons, armor, and strange artifacts.")
        
    with tabs[2]:
        st.subheader("Recent Skirmishes")
        st.write("No battles recorded yet.")

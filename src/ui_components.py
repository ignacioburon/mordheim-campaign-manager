import streamlit as st
from src.database import db

def apply_custom_styles():
    st.markdown("""
        <style>
        .main { background-color: #1a1a1a; color: #e0e0e0; }
        .stButton>button { width: 100%; background-color: #4a0000; color: white; }
        </style>
        """, unsafe_allow_html=True)

def sidebar_user_info(profile):
    st.sidebar.title(f"🎭 {profile['username']}")
    st.sidebar.caption(f"Rank: {profile['role'].upper()}")
    if st.sidebar.button("Leave the City"):
        db.auth.sign_out()
        st.session_state.user = None
        st.rerun()

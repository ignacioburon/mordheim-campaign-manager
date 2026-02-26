import streamlit as st
from src.database import db

def verify_invitation_token(token: str):
    """Checks if the token exists and is not yet used."""
    try:
        response = db.table("invitation_tokens").select("*").eq("token", token).eq("is_used", False).execute()
        return response.data if hasattr(response, 'data') else []
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

def process_registration(email, password, username, token):
    """Handles user creation and burns the invitation token."""
    try:
        # Sign up in Supabase Auth
        db.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"username": username}}
        })
        # Mark token as used
        db.table("invitation_tokens").update({"is_used": True}).eq("token", token).execute()
        return True
    except Exception as e:
        st.error(f"Registration failed: {e}")
        return False

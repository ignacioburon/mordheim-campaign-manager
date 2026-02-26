import streamlit as st
from src.database import supabase

def check_token_validity(token: str):
    """Verifies if an invitation token exists and is unused."""
    res = supabase.table("invitation_tokens").select("*").eq("token", token).eq("is_used", False).execute()
    return res.data if hasattr(res, 'data') else []

def register_user(email, password, username, token):
    """Registers a new user and marks the token as used."""
    try:
        # 1. Auth Sign up
        auth_res = supabase.auth.sign_up({
            "email": email, 
            "password": password, 
            "options": {"data": {"username": username}}
        })
        # 2. Burn the token
        supabase.table("invitation_tokens").update({"is_used": True}).eq("token", token).execute()
        return True, "Registration successful!"
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    """Authenticates the user and stores session state."""
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        return True, "Welcome back!"
    except Exception:
        return False, "Invalid credentials."

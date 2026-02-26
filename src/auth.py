import streamlit as st
from src.database import db, logger

def passwords_match(p1, p2):
    """Internal check for password consistency and length."""
    if p1 != p2:
        st.error("Passwords do not match.")
        return False
    if len(p1) < 6:
        st.error("Password must be at least 6 characters long.")
        return False
    return True

def verify_invitation_token(token: str):
    """Verifies token eligibility with generic error reporting."""
    try:
        clean_token = str(token).strip()
        response = db.table("invitation_tokens")\
            .select("*")\
            .eq("token", clean_token)\
            .eq("is_used", False)\
            .execute()
        return response.data if hasattr(response, 'data') else []
    except Exception as e:
        logger.error(f"Token Check Failed | Token: {token} | Error: {e}")
        st.error("The city gates are closed. (Invalid or expired invitation).")
        return []

def process_registration(email, password, confirm_password, username, token):
    """Handles new user creation and token consumption."""
    if not passwords_match(password, confirm_password):
        return False
    
    try:
        # 1. Sign up
        db.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"username": username}}
        })
        # 2. Burn token
        db.table("invitation_tokens").update({"is_used": True}).eq("token", token).execute()
        logger.info(f"Registration Successful | User: {username} | Email: {email}")
        return True
    except Exception as e:
        logger.error(f"Registration Failed | Email: {email} | Error: {e}")
        st.error("The registrar is unavailable. Please try again later.")
        return False

def login_user(email, password):
    """Authenticates user and handles session state."""
    try:
        res = db.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        logger.info(f"Login Success | User ID: {res.user.id}")
        return True
    except Exception as e:
        logger.warning(f"Login Attempt Failed | Email: {email} | Error: {e}")
        st.error("Authentication failed. Check your credentials.")
        return False

def request_password_reset(email):
    """Triggers the recovery flow with a specific redirect back to the Space."""
    try:
        # We explicitly set the redirectTo parameter
        redirect_url = "https://huggingface.co/spaces/ignacioburon/mordheim-campaign-manager"
        
        db.auth.reset_password_for_email(
            email, 
            options={"redirect_to": redirect_url}
        )
        
        logger.info(f"Recovery link sent to: {email}")
        st.success("The carrier pigeon is on its way. Check your inbox.")
        return True
    except Exception as e:
        logger.error(f"Recovery Request Failed: {e}")
        st.error("The messenger failed to leave the city. Try again later.")
        return False

def update_user_password(new_password, confirm_password):
    """Updates password for a user in a valid session (Recovery or Profile)."""
    if not passwords_match(new_password, confirm_password):
        return False
    
    try:
        db.auth.update_user({"password": new_password})
        logger.info("Password Updated Successfully")
        st.success("Your credentials have been updated.")
        return True
    except Exception as e:
        logger.error(f"Password Update Error | Error: {e}")
        st.error("The update failed. Your session may have expired.")
        return False

import streamlit as st
from src.database import db
from src.auth import verify_invitation_token, process_registration
import secrets

# UI Configuration
st.set_page_config(page_title="Mordheim Manager", layout="wide")

# Session State
if "user" not in st.session_state:
    st.session_state.user = None

# --- UNAUTHENTICATED FLOW ---
if not st.session_state.user:
    st.title("⚔️ MORDHEIM CAMPAIGN MANAGER")
    
    # Securely retrieve token from URL params
    token_param = st.query_params.get("token")
    current_token = str(token_param).strip() if token_param else None

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        with st.form("auth_login"):
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER THE CITY"):
                try:
                    res = db.auth.sign_in_with_password({"email": email, "password": pwd})
                    st.session_state.user = res.user
                    st.rerun()
                except:
                    st.error("Access denied. Check your credentials.")

    with tab_signup:
        if not current_token:
            st.warning("An invitation scroll is required to register.")
        else:
            records = verify_invitation_token(current_token)
            if not records:
                st.error("Invalid or expired scroll.")
            else:
                st.success(f"Scroll verified: {current_token}")
                with st.form("auth_reg"):
                    new_email = st.text_input("Email")
                    new_pwd = st.text_input("Password (min 6 chars)", type="password")
                    username = st.text_input("Captain Name")
                    if st.form_submit_button("FOUND WARBAND"):
                        if process_registration(new_email, new_pwd, username, current_token):
                            st.balloons()
                            st.success("Warband founded! You may now login.")

# --- AUTHENTICATED FLOW ---
else:
    try:
        # Fetching profile from the new non-recursive policy
        profile = db.table("profiles").select("*").eq("id", st.session_state.user.id).single().execute().data
        
        st.sidebar.title(f"🎭 {profile['username']}")
        st.sidebar.write(f"Rank: {profile['role'].upper()}")
        
        if st.sidebar.button("Logout"):
            db.auth.sign_out()
            st.session_state.user = None
            st.rerun()

        if profile['role'] == 'owner':
            st.header("👑 Grand Master's Quarters")
            if st.button("Generate New Invitation Token"):
                new_token = secrets.token_urlsafe(8)
                db.table("invitation_tokens").insert({"token": new_token}).execute()
                st.code(f"https://huggingface.co/spaces/ignacioburon/mordheim-campaign-manager?token={new_token}")
        else:
            st.header("📜 Warband Ledger")
            st.info("Your warband is currently being inspected by the city guards.")
            
    except Exception as e:
        st.error("Error loading profile. Check database RLS policies.")

import streamlit as st
from src.database import supabase
from src.auth import login_user, register_user, check_token_validity
import secrets

# Page Configuration
st.set_page_config(page_title="Mordheim: City of the Damned", layout="wide")

# Session Initialization
if "user" not in st.session_state:
    st.session_state.user = None

# 1. UNAUTHENTICATED VIEW
if not st.session_state.user:
    st.title("⚔️ MORDHEIM CAMPAIGN MANAGER")
    
    # Capture token from URL
    url_token = st.query_params.get("token", "").strip()
    
    tab_login, tab_reg = st.tabs(["[ Login ]", "[ Register ]"])
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Explorer Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER THE CITY"):
                success, msg = login_user(email, pwd)
                if success: st.rerun()
                else: st.error(msg)

    with tab_reg:
        if not url_token:
            st.warning("⚠️ A valid Invitation Scroll (Token) is required to join.")
        else:
            token_data = check_token_validity(url_token)
            if not token_data:
                st.error("Invalid or expired scroll.")
            else:
                st.success(f"Scroll verified: {url_token}")
                with st.form("registration_form"):
                    new_email = st.text_input("Email")
                    new_pwd = st.text_input("Password (min 6 chars)", type="password")
                    user_nm = st.text_input("Captain Name")
                    if st.form_submit_button("FOUND WARBAND"):
                        success, msg = register_user(new_email, new_pwd, user_nm, url_token)
                        if success: st.success(msg)
                        else: st.error(msg)

# 2. AUTHENTICATED VIEW
else:
    # Fetch user profile
    profile = supabase.table("profiles").select("*").eq("id", st.session_state.user.id).single().execute().data
    
    # Sidebar Navigation
    st.sidebar.title(f"🎭 {profile['username']}")
    st.sidebar.caption(f"Rank: {profile['role'].upper()}")
    
    if st.sidebar.button("Leave the City"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # OWNER DASHBOARD
    if profile['role'] == 'owner':
        st.header("👑 Grand Master's Quarters")
        col_inv, col_app = st.columns(2)
        
        with col_inv:
            st.subheader("Send Invitations")
            if st.button("Generate New Scroll"):
                new_t = secrets.token_urlsafe(8)
                supabase.table("invitation_tokens").insert({"token": new_t}).execute()
                invite_url = f"https://huggingface.co/spaces/ignacioburon/mordheim-campaign-manager?token={new_t}"
                st.code(invite_url, language="text")
        
        with col_app:
            st.subheader("Approve Recluits")
            pending = supabase.table("profiles").select("*").eq("is_approved", False).execute().data
            for p in pending:
                st.write(f"🔹 {p['username']}")
                if st.button(f"Approve {p['username']}", key=p['id']):
                    supabase.table("profiles").update({"is_approved": True}).eq("id", p['id']).execute()
                    st.rerun()

    # PLAYER DASHBOARD
    else:
        st.header("📜 Warband Ledger")
        if not profile['is_approved']:
            st.warning("Waiting for the Grand Master's approval to enter the city gates.")
        else:
            st.info("The city of Mordheim awaits your command. (Warband modules coming soon).")

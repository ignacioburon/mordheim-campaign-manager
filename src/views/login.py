import streamlit as st
from src.auth import login_user, verify_invitation_token, process_registration, request_password_reset

def show_login_view():
    st.title("⚔️ MORDHEIM CLUB DRAGON")
    
    # Check for token in URL
    token_val = st.query_params.get("token")
    current_token = str(token_val).strip() if token_val else None

    tab_login, tab_signup, tab_reset = st.tabs(["Login", "Join the War", "Forgot Password"])

    with tab_login:
        with st.form("auth_login"):
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER"):
                if login_user(email, pwd): st.rerun()

    with tab_signup:
        if not current_token:
            st.warning("You need a valid invitation scroll.")
        else:
            records = verify_invitation_token(current_token)
            if records:
                with st.form("auth_reg"):
                    new_email = st.text_input("Email")
                    username = st.text_input("Captain Name")
                    p1 = st.text_input("Password", type="password")
                    p2 = st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("FOUND WARBAND"):
                        if process_registration(new_email, p1, p2, username, current_token):
                            st.success("Warband founded! Switch to Login tab.")
                            
    with tab_reset:
        rec_email = st.text_input("Registered Email")
        if st.button("Send Recovery Pigeon"):
            request_password_reset(rec_email)

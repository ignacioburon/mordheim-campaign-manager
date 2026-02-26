import streamlit as st
from src.auth import update_user_password

def show_recovery_view():
    """Form to set a new password during a recovery session."""
    st.title("🛡️ Temple of Morr: Account Recovery")
    st.info("The heavens have granted you a second chance. Choose your new credentials wisely.")
    
    with st.form("recovery_form"):
        new_p = st.text_input("New Password", type="password")
        conf_p = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("REFORGE PASSWORD"):
            if update_user_password(new_p, conf_p):
                st.success("Your mind is cleared and your password is set.")
                # We show a button to clear the URL and go back to login
                if st.button("Return to the City Gates"):
                    st.query_params.clear()
                    st.rerun()

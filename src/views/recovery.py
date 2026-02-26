import streamlit as st
from src.database import db, logger

def show_recovery_view():
    st.title("🛡️ Temple of Morr: Account Recovery")
    
    # Get the token from the URL (?token=...)
    token_hash = st.query_params.get("token")
    
    if not token_hash:
        st.error("The recovery link is invalid or has expired.")
        if st.button("Return to Login"):
            st.query_params.clear()
            st.rerun()
        return

    st.info("The heavens have granted you a second chance.")
    
    with st.form("recovery_form"):
        new_p = st.text_input("New Password", type="password")
        conf_p = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("REFORGE PASSWORD"):
            if new_p != conf_p:
                st.error("Passwords do not match.")
            elif len(new_p) < 15:
                st.error("Password must be at least 15 characters.")
            else:
                try:
                    # Use the hash to verify and update the password
                    db.auth.verify_otp({
                        "token_hash": token_hash,
                        "type": "recovery"
                    })
                    db.auth.update_user({"password": new_p})
                    
                    st.success("Your credentials have been updated!")
                    st.balloons()
                    if st.button("Proceed to the City Gates"):
                        st.query_params.clear()
                        st.rerun()
                except Exception as e:
                    logger.error(f"Recovery Verification Failed: {e}")
                    st.error("This recovery link has expired or is invalid.")

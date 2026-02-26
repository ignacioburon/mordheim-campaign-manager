import streamlit as st
from src.database import db, logger

def show_recovery_view():
    st.title("🛡️ Temple of Shallya: Account Recovery")
    
    # DEBUG SECTION - visible only for troubleshooting
    with st.expander("🛠️ Debug Information (Internal Use)"):
        token_val = st.query_params.get("token")
        st.write(f"**Token Detected:** `{token_val}`")
        st.write(f"**Token Length:** {len(token_val) if token_val else 0}")
        st.write(f"**Query Params:** {st.query_params.to_dict()}")

    if not token_val:
        st.error("No recovery token found in the URL. Please use the link sent to your email.")
        return

    st.info("The heavens have granted you a second chance. Set your new password below.")
    
    with st.form("recovery_form"):
        new_p = st.text_input("New Password", type="password")
        conf_p = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("REFORGE PASSWORD"):
            if new_p != conf_p:
                st.error("Passwords do not match.")
            elif len(new_p) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    # STEP 1: Exchange the Token for a Session
                    # We use 'token_hash' because we used {{ .TokenHash }} in the template
                    db.auth.verify_otp({
                        "token_hash": token_val,
                        "type": "recovery"
                    })
                    
                    # STEP 2: Update the password now that we have an active session
                    db.auth.update_user({"password": new_p})
                    
                    logger.info("Password successfully reset via recovery token.")
                    st.success("Your credentials have been updated!")
                    st.balloons()
                    
                    # Manual redirect back to login
                    if st.button("Return to the City Gates"):
                        st.query_params.clear()
                        st.rerun()
                        
                except Exception as e:
                    logger.error(f"OTP Verification Failed: {e}")
                    # If you see "401" or "400" in logs, the token is dead
                    st.error(f"The link is invalid or expired. Technical details: {str(e)}")

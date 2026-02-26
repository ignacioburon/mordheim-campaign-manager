import streamlit as st
import secrets
from src.database import db, logger

def show_admin_panel(profile):
    """View for Owners and Admins to manage the campaign."""
    st.header("👑 Grand Master's Quarters")
    
    col_inv, col_recruit = st.columns(2)
    
    with col_inv:
        st.subheader("Diplomacy & Scrolls")
        st.write("Generate a new invitation link for a new Captain.")
        if st.button("Forge Invitation Scroll"):
            try:
                new_token = secrets.token_urlsafe(8)
                db.table("invitation_tokens").insert({"token": new_token}).execute()
                
                # Dynamic URL construction
                base_url = "https://huggingface.co/spaces/ignacioburon/mordheim-campaign-manager"
                invite_url = f"{base_url}?token={new_token}"
                
                st.success("New scroll forged!")
                st.code(invite_url, language="text")
                logger.info(f"Admin {profile['username']} generated token: {new_token}")
            except Exception as e:
                logger.error(f"Token Generation Failed: {e}")
                st.error("The forge is cold. Try again later.")

    with col_recruit:
        st.subheader("The Muster Roll")
        try:
            # Fetch unapproved captains
            pending = db.table("profiles").select("*").eq("is_approved", False).execute().data
            if not pending:
                st.info("No recruits awaiting approval.")
            else:
                for p in pending:
                    with st.container(border=True):
                        st.write(f"**Captain:** {p['username']}")
                        if st.button(f"Approve {p['username']}", key=p['id']):
                            db.table("profiles").update({"is_approved": True}).eq("id", p['id']).execute()
                            logger.info(f"Captain {p['username']} approved by {profile['username']}")
                            st.rerun()
        except Exception as e:
            logger.error(f"Recruit Load Error: {e}")
            st.error("Could not retrieve the muster roll.")

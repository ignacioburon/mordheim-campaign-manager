import streamlit as st
from supabase import create_client, Client
import os
import secrets
import urllib.parse

# 1. CONFIGURACION
st.set_page_config(page_title="Mordheim Club Dragon", layout="wide")

# Estilo visual
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4a0000; color: white; border: none; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXION
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 3. TOKEN URL
try:
    token_val = st.query_params.get("token")
    url_token = str(token_val).strip() if token_val else None
except:
    url_token = None

if "user" not in st.session_state:
    st.session_state.user = None

# 4. ACCESO
if not st.session_state.user:
    st.title("⚔️ MORDHEIM CLUB DRAGON")
    t1, t2 = st.tabs(["[ Entrar ]", "[ Alistarse ]"])
    
    with t1:
        with st.form("f_login"):
            em = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("RECLAMAR BOTIN"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": em, "password": pw})
                    st.session_state.user = res.user
                    st.rerun()
                except:
                    st.error("Credenciales incorrectas")

    with t2:
        if not url_token:
            st.warning("⚠️ Necesitas un token de invitacion.")
        else:
            res = supabase.table("invitation_tokens").select("*").eq("token", url_token).eq("is_used", False).execute()
            data = res.data if hasattr(res, 'data') else []
            if not data:
                st.error("Token invalido o usado")
            else:
                st.success(f"Pergamino verificado: {url_token}")
                with st.form("f_reg"):
                    n_em = st.text_input("Email")
                    n_pw = st.text_input("Password (min 6)", type="password")
                    u_nm = st.text_input("Nombre Capitan")
                    if st.form_submit_button("FUNDAR BANDA"):
                        try:
                            supabase.auth.sign_up({"email": n_em, "password": n_pw, "options": {"data": {"username": u_nm}}})
                            supabase.table("invitation_tokens").update({"is_used": True}).eq("token", url_token).execute()
                            st.success("¡Registrado! Ya puedes entrar.")
                        except Exception as e:
                            st.error(f"Error: {e}")

# 5. DASHBOARD
else:
    u_id = st.session_state.user.id
    profile = supabase.table("profiles").select("*").eq("id", u_id).single().execute().data
    
    st.sidebar.title(f"🎭 {profile['username']}")
    st.sidebar.info(f"Rango: {profile['role'].upper()}")
    
    if st.sidebar.button("Cerrar Sesion"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # --- VISTA DE OWNER ---
    if profile['role'] == 'owner':
        st.header("👑 Cuartel General del Gran Maestre")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Invitaciones")
            target = st.text_input("Email destino")
            if st.button("Generar nuevo Token"):
                nt = secrets.token_urlsafe(8)
                supabase.table("invitation_tokens").insert({"token": nt}).execute()
                link = f"https://huggingface.co/spaces/ignacioburon/mordheim-campaign-manager?token={nt}"
                st.code(link)
        
        with col2:
            st.subheader("Gestion de Reclutas")
            # Lista de usuarios pendientes de aprobar
            pendientes = supabase.table("profiles").select("*").eq("is_approved", False).execute().data
            if pendientes:
                for p in pendientes:
                    st.write(f"🔹 {p['username']} ({p['role']})")
                    if st.button(f"Aprobar a {p['username']}", key=p['id']):
                        supabase.table("profiles").update({"is_approved": True}).eq("id", p['id']).execute()
                        st.rerun()
            else:
                st.write("No hay reclutas pendientes.")

    # --- VISTA DE JUGADOR ---
    else:
        st.header("📜 Diario de Guerra")
        if not profile['is_approved']:
            st.warning("Tu entrada a la ciudad esta bloqueada. Espera aprobacion del Maestre.")
        else:
            st.success("¡Bienvenido! La ciudad de Mordheim te espera.")
            st.info("Próximamente: Gestión de bandas y equipo.")

import streamlit as st
from supabase import create_client, Client
import os

# 1. Page configuration(skull icon for Mordheim)
st.set_page_config(page_title="Mordheim Club Dragón | Campaña", page_icon="💀", layout="centered")

# Custom CSS for grimdark
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4a0000; color: white; border: none; }
    .stButton>button:hover { background-color: #8b0000; border: 1px solid #ff0000; }
    </style>
    """, unsafe_allow_html=True)

# 2. Infra connectivity
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

query_params = st.query_params
url_token = query_params.get("token")

# 3. session logic
if "user" not in st.session_state:
    st.session_state.user = None

# 4. Welcome page / auth
if not st.session_state.user:
    st.image("https://logodix.com/logo/1057406.jpg", width=200) # Or some Mordheim image
    st.title("⚔️ MORDHEIM CLUB DRAGÓN")
    st.markdown("""
    *“La cometa de dos colas ha caído, y la Ciudad de los Condenados nos llama. 
    Solo los más fuertes, o los más dementes, reclamarán la Piedra Bruja entre las cenizas.”*
    """)
    
    tab1, tab2 = st.tabs(["[ Entrar en la Ciudad ]", "[ Alistarse ]"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email del Explorador")
            password = st.text_input("Salvoconducto (Password)", type="password")
            if st.form_submit_button("RECLAMAR BOTÍN"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.rerun()
                except:
                    st.error("Los guardias de la ciudad no reconocen tus credenciales.")

    with tab2:
        if not url_token:
            st.warning("⚠️ **¡ALTO!** Necesitas un pergamino de invitación (Token) para entrar en esta expedición.")
            st.info("Habla con el Gran Maestre del Club para recibir tu enlace de acceso.")
        else:
            token_query = supabase.table("invitation_tokens").select("*").eq("token", url_token).eq("is_used", False).execute()
            if not token_query.data:
                st.error("Este pergamino de invitación es falso o ya ha sido usado.")
            else:
                st.success("📝 **Pergamino verificado.** Escribe tu nombre en los anales de la ciudad.")
                with st.form("reg_form"):
                    new_email = st.text_input("Email")
                    new_pw = st.text_input("Password", type="password")
                    username = st.text_input("Nombre del Capitán / Jugador")
                    if st.form_submit_button("FUNDAR BANDA"):
                        try:
                            auth_res = supabase.auth.sign_up({
                                "email": new_email, 
                                "password": new_pw,
                                "options": {"data": {"username": username}}
                            })
                            # El trigger de la DB hará el resto, pero marcamos el token usado
                            supabase.table("invitation_tokens").update({"is_used": True}).eq("token", url_token).execute()
                            # Autorización automática por tener token válido
                            supabase.table("profiles").update({"is_approved": True}).eq("id", auth_res.user.id).execute()
                            st.success("¡Tu banda ha sido inscrita! Ahora entra por las puertas de la ciudad (Login).")
                        except Exception as e:
                            st.error(f"Error en la inscripción: {e}")

# 5. DASHBOARD (LOGGED IN)
else:
    user_id = st.session_state.user.id
    profile = supabase.table("profiles").select("*").eq("id", user_id).single().execute().data
    
    st.sidebar.title(f"🎭 {profile['username']}")
    st.sidebar.markdown(f"**Rango:** {profile['role'].capitalize()}")
    
    if st.sidebar.button("Abandonar la Ciudad"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    if profile['role'] == 'admin':
        st.header("🛡️ Cuartel del Gran Maestre")
        # Aquí irán tus herramientas de Admin
    else:
        st.header("📜 Diario de la Banda")
        st.info("Próximamente: Crea tu banda y empieza a recolectar Piedra Bruja.")

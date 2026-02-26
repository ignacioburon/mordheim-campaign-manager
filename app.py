import streamlit as st
from supabase import create_client, Client
import os
import secrets
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Mordheim Club Dragón", page_icon="💀", layout="centered")

# Estilo visual Mordheim
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4a0000; color: white; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #8b0000; border: 1px solid #ff0000; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #262626; border-radius: 5px; padding: 10px 20px; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN A SUPABASE
# Asegúrate de tener SUPABASE_URL y SUPABASE_KEY en los Secrets de Hugging Face
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 3. CAPTURA SEGURA DEL TOKEN (PARCHE DE COMPATIBILIDAD)
try:
    # Usamos .get() y forzamos la conversión a string para evitar errores de tipo 'list' o 'dict'
    token_param = st.query_params.get("token")
    if token_param:
        url_token = str(token_param).strip()
    else:
        url_token = None
except Exception:
    url_token = None

# Inicializar sesión
if "user" not in st.session_state:
    st.session_state.user = None

# 4. INTERFAZ DE LOGUEO / REGISTRO
if not st.session_state.user:
    st.image("https://logodix.com/logo/1057406.jpg", width=150) # Logo temporal
    st.title("⚔️ MORDHEIM CLUB DRAGÓN")
    st.markdown("### _“Bienvenido a la Ciudad de los Condenados”_")
    
    tab1, tab2 = st.tabs(["[ Entrar en la Ciudad ]", "[ Alistarse ]"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email del Explorador")
            password = st.text_input("Salvoconducto (Password)", type="password")
            submit_login = st.form_submit_button("RECLAMAR BOTÍN")
            
            if submit_login:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.rerun()
                except Exception:
                    st.error("Los guardias no reconocen tus credenciales. Revisa email/password.")

    with tab2:
        if not url_token:
            st.warning("⚠️ **¡ALTO!** Necesitas un pergamino de invitación (Token) para entrar en esta expedición.")
            st.info("Habla con el Gran Maestre del Club para recibir tu enlace de acceso.")
        else:
            # Consulta a la base de datos para verificar el token
            token_query = supabase.table("invitation_tokens").select("*").eq("token", url_token).eq("is_used", False).execute()
            
            if not token_query.data:
                st.error(f"El pergamino '{url_token}' es falso o ya ha sido usado.")
                if st.button("🔄 Reintentar"):
                    st.rerun()
            else:
                st.success(f"📝 **Pergamino verificado.** ({url_token})")
                with st.form("reg_form"):
                    new_email = st.text_input("Tu Email")
                    new_pw = st.text_input("Crea tu Password (min. 6 caracteres)", type="password")
                    username = st.text_input("Nombre de tu Capitán / Jugador")
                    
                    if st.form_submit_button("FUNDAR BANDA"):
                        if len(new_pw) < 6:
                            st.warning("La password es demasiado corta.")
                        elif not username:
                            st.warning("Debes elegir un nombre para ser recordado.")
                        else:
                            try:
                                # Registrar usuario en Auth
                                auth_res = supabase.auth.sign_up({
                                    "email": new_email, 
                                    "password": new_pw,
                                    "options": {"data": {"username": username}}
                                })
                                # Marcar token como usado
                                supabase.table("invitation_tokens").update({"is_used": True}).eq("token", url_token).execute()
                                st.balloons()
                                st.success("¡Inscripción completada! Ve a la pestaña 'Entrar' para loguearte.")
                            except Exception as e:
                                st.error(f"Error en el registro: {e}")

# 5. DASHBOARD (CUANDO YA ESTÁS LOGUEADO)
else:
    user_id = st.session_state.user.id
    # Obtenemos el perfil para saber el ROL
    profile_query = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    profile = profile_query.data
    
    # BARRA LATERAL
    st.sidebar.title(f"🎭 {profile['username']}")
    st.sidebar.write(f"**Rango:** {profile['role'].upper()}")
    
    if st.sidebar.button("Abandonar la Ciudad"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # PANEL ESPECIAL SEGÚN ROL
    if profile['role'] in ['owner', 'admin']:
        st.header("👑 Cuartel General del Gran Maestre")
        
        with st.expander("✉

import streamlit as st
from supabase import create_client, Client
import os
import secrets
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Mordheim Club Dragón", page_icon="💀", layout="centered")

# Estilo visual oscuro
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4a0000; color: white; border: none; }
    .stButton>button:hover { background-color: #8b0000; border: 1px solid #ff0000; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN A SUPABASE
# Recuerda tener estas variables en Settings > Secrets de Hugging Face
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 3. CAPTURA ROBUSTA DEL TOKEN
# En versiones nuevas de Streamlit, st.query_params se comporta como un diccionario
raw_token = st.query_params.get("token")
url_token = str(raw_token).strip() if raw_token else None

# Lógica de sesión
if "user" not in st.session_state:
    st.session_state.user = None

# 4. INTERFAZ DE ACCESO (LOGIN / REGISTRO)
if not st.session_state.user:
    st.image("https://logodix.com/logo/1057406.jpg", width=200) # Reemplazar por logo del club
    st.title("⚔️ MORDHEIM CLUB DRAGÓN")
    st.markdown("_“La cometa de dos colas ha caído. Solo los valientes reclamarán la Piedra Bruja.”_")
    
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
                    st.error("Los guardias no reconocen tus credenciales.")

    with tab2:
        if not url_token:
            st.warning("⚠️ **¡ALTO!** Necesitas un pergamino de invitación para entrar.")
            st.info("Solicita tu enlace al Gran Maestre del Club.")
        else:
            # Consultar si el token existe y no ha sido usado
            token_query = supabase.table("invitation_tokens").select("*").eq("token", url_token).eq("is_used", False).execute()
            
            if not token_query.data or len(token_query.data) == 0:
                st.error(f"El pergamino '{url_token}' es falso o ya ha sido usado.")
            else:
                st.success("📝 **Pergamino verificado.** Escribe tu nombre en los anales.")
                with st.form("reg_form"):
                    new_email = st.text_input("Email")
                    new_pw = st.text_input("Password (min. 6 caracteres)", type="password")
                    username = st.text_input("Nombre del Capitán / Jugador")
                    
                    if st.form_submit_button("FUNDAR BANDA"):
                        try:
                            # 1. Crear usuario en Auth
                            auth_res = supabase.auth.sign_up({
                                "email": new_email, 
                                "password": new_pw,
                                "options": {"data": {"username": username}}
                            })
                            # 2. Marcar token como usado
                            supabase.table("invitation_tokens").update({"is_used": True}).eq("token", url_token).execute()
                            
                            st.success("¡Inscripción completada! Ahora puedes entrar en la ciudad (Login).")
                        except Exception as e:
                            st.error(f"Error: {e}")

# 5. DASHBOARD (USUARIO LOGUEADO)
else:
    # Obtener perfil del usuario
    user_id = st.session_state.user.id
    profile_res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    profile = profile_res.data
    
    # BARRA LATERAL
    st.sidebar.title(f"🎭 {profile['username']}")
    st.sidebar.markdown(f"**Rango:** {profile['role'].upper()}")
    
    if st.sidebar.button("Abandonar la Ciudad"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # CONTENIDO SEGÚN ROL
    if profile['role'] in ['owner', 'admin']:
        st.header("👑 Cuartel General")
        
        # Herramienta de Invitación para el Owner
        with st.expander("✉️ Enviar Nueva Invitación"):
            target_email = st.text_input("Email del nuevo socio")
            if st.button("Generar y Preparar Email"):
                new_token = secrets.token_urlsafe(8)
                supabase.table("invitation_tokens").insert({"token": new_token}).execute()
                
                # Construir link y mailto
                # Ajusta la URL base a la tuya de Hugging Face
                base_url = "https://huggingface.co/spaces/ignacioburon/mordheim-campaign-manager"
                invite_url = f"{base_url}?token={new_token}"
                
                subject = urllib.parse.quote("Invitación: Campaña Mordheim Club Dragón")
                body = urllib.parse.quote(f"Saludos, Capitán.\n\nHas sido invitado a unirte a la campaña. Regístrate aquí:\n{invite_url}")
                mailto_link = f"mailto:{target_email}?subject={subject}&body={body}"
                
                st.info(f"Token: {new_token}")
                st.markdown(f"""
                    <a href="{mailto_link}" target="_blank">
                        <button style="width:100%; background-color:#4a0000; color:white; padding:10px; border:none; border-radius:5px; cursor:pointer;">
                            📧 Abrir Correo de Invitación
                        </button>
                    </a>
                """, unsafe_allow_html=True)

    else:
        st.header("📜 Diario de tu Banda")
        if not profile['is_approved']:
            st.warning("Tu entrada a la ciudad está pendiente de aprobación por el Gran Maestre.")
        else:
            st.info("Próximamente: Registra aquí tus bandas y gestiona tu Piedra Bruja.")

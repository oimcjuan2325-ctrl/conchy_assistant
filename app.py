import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime
from google import genai

# Page configuration
st.set_page_config(
    page_title="Conchy - Asistente Escolar",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE LA API KEY Y CLIENTE DE GEMINI ---
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")

client = None
if GOOGLE_API_KEY:
    try:
        # Inicialización del cliente oficial de Google GenAI
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.sidebar.error(f"Error al inicializar el cliente de IA: {e}")

# 1. Inicialización segura de Session State
if "users" not in st.session_state:
    st.session_state.users = {
        "alumno": {"password": hashlib.sha256("1234".encode()).hexdigest(), "role": "Alumno", "name": "Estudiante Ejemplo"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.name = ""

if "tasks" not in st.session_state:
    st.session_state.tasks = {} 

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function to add tasks anywhere safely
def render_task_creation_expander(user_key_suffix=""):
    with st.expander("➕ Añadir nueva tarea o evaluación"):
        with st.form(key=f"task_form_{user_key_suffix}"):
            t_title = st.text_input("Título de la tarea o examen")
            t_date = st.date_input("Fecha límite / Examen", key=f"date_{user_key_suffix}")
            submitted = st.form_submit_button("Guardar Registro")
            if submitted:
                if t_title:
                    curr_user = st.session_state.username
                    if "tasks" not in st.session_state:
                        st.session_state.tasks = {}
                    if curr_user not in st.session_state.tasks:
                        st.session_state.tasks[curr_user] = []
                    st.session_state.tasks[curr_user].append({
                        "title": t_title,
                        "due": str(t_date),
                        "status": "Pendiente"
                    })
                    st.success("¡Añadido con éxito!")
                    st.rerun()
                else:
                    st.warning("Escribe un título válido.")

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #1e3d59;'>🎓 CONCHY</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #438a5e; font-size: 1.1em;'>Tu asistente virtual inteligente para estudiantes.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
        
        with tab_login:
            st.subheader("Acceso de Alumnos")
            login_user = st.text_input("Usuario", key="login_user")
            login_pass = st.text_input("Contraseña", type="password", key="login_pass")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Iniciar Sesión", type="primary"):
                if login_user in st.session_state.users and st.session_state.users[login_user]["password"] == hash_password(login_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.session_state.role = st.session_state.users[login_user]["role"]
                    st.session_state.name = st.session_state.users[login_user]["name"]
                    st.success(f"¡Bienvenido/a, {st.session_state.name}!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
                    
        with tab_register:
            st.subheader("Registro de Nueva Cuenta")
            reg_user = st.text_input("Nombre de usuario único", key="reg_user")
            reg_name = st.text_input("Tu Nombre y Apellidos", key="reg_name")
            reg_pass = st.text_input("Contraseña", type="password", key="reg_pass")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Registrarse", type="secondary"):
                if not reg_user or not reg_pass or not reg_name:
                    st.warning("Por favor, completa todos los campos.")
                elif reg_user in st.session_state.users:
                    st.error("This username already exists.")
                else:
                    st.session_state.users[reg_user] = {
                        "password": hash_password(reg_pass),
                        "role": "Alumno",
                        "name": reg_name
                    }
                    st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")

else:
    # --- MAIN APPLICATION (ALUMNO) ---
    st.sidebar.markdown(f"### 👤 {st.session_state.name}")
    st.sidebar.markdown(f"**Perfil:** `Alumno 🎓`")
    
    if client:
        st.sidebar.success("🔌 Gemini 3.6 Flash Conectado")
    else:
        st.sidebar.warning("⚠️ Falta configurar GOOGLE_API_KEY en Secrets")
        
    st.sidebar.markdown("---")
    
    # Navegación estricta a las 2 secciones solicitadas + Cuenta
    menu = st.sidebar.radio("Navegación", [
        "📚 Tareas y evaluaciones", 
        "🤖 Conchy IA",
        "⚙️ Mi Cuenta"
    ])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.name = ""
        st.rerun()

    current_user = st.session_state.username
    user_tasks = st.session_state.tasks.get(current_user, [])

    # 1. Tareas y evaluaciones
    if menu == "📚 Tareas y evaluaciones":
        st.title("📚 Tareas y Evaluaciones")
        st.write("Gestiona y consulta tus próximas entregas y exámenes.")
        
        if user_tasks:
            df = pd.DataFrame(user_tasks)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No has agregado ninguna tarea o evaluación todavía.")

        st.markdown("---")
        render_task_creation_expander("seccion_tareas")

    # 2. Conchy IA (Impulsado por gemini-3.6-flash)
    elif menu == "🤖 Conchy IA":
        st.title("🤖 Asistente Conchy IA")
        st.write("Hola, soy **Conchy**, tu asistente inteligente impulsada por **Gemini 3.6 Flash**. Puedo ayudarte a resolver dudas, planificar tus estudios y organizarte mejor.")
        
        if current_user not in st.session_state.chat_history:
            st.session_state.chat_history[current_user] = [
                {"role": "assistant", "content": f"¡Hola {st.session_state.name}! Soy Conchy. Veo que tienes {len(user_tasks)} tareas o evaluaciones registradas. ¿En qué te puedo ayudar hoy?"}
            ]
        
        for message in st.session_state.chat_history[current_user]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if prompt := st.chat_input("Pregúntale a Conchy sobre tus materias, exámenes u organización..."):
            st.session_state.chat_history[current_user].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            response_text = ""
            
            if client:
                try:
                    # Contexto del estudiante para la IA
                    contexto_sistema = (
                        f"Eres Conchy, una asistente escolar virtual inteligente y amable para el estudiante {st.session_state.name}. "
                        f"Tareas actuales del alumno: {user_tasks}. "
                        "Ayúdale a organizarse, resolver dudas de estudio y motivarle."
                    )
                    
                    # Llamada oficial al modelo gemini-3.6-flash
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=f"{contexto_sistema}\n\nPregunta del alumno: {prompt}"
                    )
                    response_text = response.text
                except Exception as e:
                    response_text = f"Hubo un error al conectar con Gemini 3.6 Flash: {e}"
            else:
                # Modo de respaldo si no hay clave introducida
                prompt_lower = prompt.lower()
                if "tarea" in prompt_lower or "examen" in prompt_lower:
                    response_text = f"Tienes {len(user_tasks)} tareas registradas. Configura tu GOOGLE_API_KEY en los Secrets para activar el razonamiento avanzado de Gemini 3.6 Flash."
                else:
                    response_text = "¡Hola! Para hablar conmigo mediante IA avanzada, por favor configura tu clave API en los secretos de Streamlit."

            st.session_state.chat_history[current_user].append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)

        st.markdown("---")
        render_task_creation_expander("seccion_ia")

    # 3. Mi Cuenta
    elif menu == "⚙️ Mi Cuenta":
        st.title("⚙️ Mi Cuenta")
        st.write(f"**Usuario:** {st.session_state.username}")
        st.write(f"**Nombre:** {st.session_state.name}")
        st.write(f"**Total de tareas/evaluaciones tuyas:** {len(user_tasks)}")

        st.markdown("---")
        st.subheader("Estado de la conexión IA")
        if client:
            st.success("Conectado correctamente con el modelo `gemini-3.6-flash`.")
        else:
            st.warning("No se detectó una clave API válida de Google.")

        st.markdown("---")
        render_task_creation_expander("seccion_cuenta")

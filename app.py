import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime

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

# Initialize Session State
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
    st.session_state.tasks = {} # {username: [{"title": ..., "due": ...}]}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function to add tasks anywhere
def render_task_creation_expander(user_key_suffix=""):
    with st.expander("➕ Añadir nueva tarea o evaluación"):
        with st.form(key=f"task_form_{user_key_suffix}"):
            t_title = st.text_input("Título de la tarea o examen")
            t_date = st.date_input("Fecha límite / Examen", key=f"date_{user_key_suffix}")
            submitted = st.form_submit_button("Guardar Registro")
            if submitted:
                if t_title:
                    curr_user = st.session_state.username
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
                    st.error("Este usuario ya existe.")
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
    st.sidebar.markdown("---")
    
    # Navigation strictly limited to the 2 requested sections + Account config
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

    # 2. Conchy IA
    elif menu == "🤖 Conchy IA":
        st.title("🤖 Asistente Conchy IA")
        st.write("Hola, soy **Conchy**. Puedo aconsejarte sobre cómo organizarte y revisar los datos de tu cuenta para ayudarte a estudiar mejor.")
        
        if current_user not in st.session_state.chat_history:
            st.session_state.chat_history[current_user] = [
                {"role": "assistant", "content": f"¡Hola {st.session_state.name}! Soy Conchy. Veo que tienes {len(user_tasks)} tareas o evaluaciones registradas. ¿En qué te puedo ayudar hoy?"}
            ]
        
        for message in st.session_state.chat_history[current_user]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if prompt := st.chat_input("Pregúntale a Conchy sobre tus exámenes, organización o hábitos de estudio..."):
            st.session_state.chat_history[current_user].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            prompt_lower = prompt.lower()
            if "tarea" in prompt_lower or "examen" in prompt_lower or "pendiente" in prompt_lower:
                if user_tasks:
                    task_list_str = ", ".join([f"{t['title']} (Fecha: {t['due']})" for t in user_tasks])
                    response_text = f"Consultando tu cuenta, tus registros actuales son: {task_list_str}. ¡Organiza bien tu tiempo para llegar a todo!"
                else:
                    response_text = f"He revisado tu perfil y actualmente no tienes ninguna tarea o evaluación registrada. ¡Puedes añadir una desde el panel inferior!"
            elif "consejo" in prompt_lower or "organizar" in prompt_lower or "estudiar" in prompt_lower:
                response_text = "Mi mejor consejo es que dividas el temario en bloques pequeños diarios y evites dejarlo todo para la última noche. ¡Tú puedes con ello!"
            else:
                response_text = f"Entendido. Como tu asistente Conchy, estoy aquí para apoyarte en tus estudios. ¿Quieres que te ayude a planificar tus próximos objetivos?"
                
            st.session_state.chat_history[current_user].append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)

        st.markdown("---")
        render_task_creation_expander("seccion_ia")

    # 3. Mi Cuenta (Ajustes rápidos)
    elif menu == "⚙️ Mi Cuenta":
        st.title("⚙️ Mi Cuenta")
        st.write(f"**Usuario:** {st.session_state.username}")
        st.write(f"**Nombre:** {st.session_state.name}")
        st.write(f"**Total de tareas/evaluaciones tuyas:** {len(user_tasks)}")

        st.markdown("---")
        render_task_creation_expander("seccion_cuenta")

import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Conchy - Asistente Escolar Inteligente",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
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

# Initialize Session State for users and data
if "users" not in st.session_state:
    st.session_state.users = {
        "profesor": {"password": hashlib.sha256("1234".encode()).hexdigest(), "role": "Profesor", "name": "Profesor Titular"},
        "alumno": {"password": hashlib.sha256("1234".encode()).hexdigest(), "role": "Alumno", "name": "Estudiante Ejemplo"},
        "padre": {"password": hashlib.sha256("1234".encode()).hexdigest(), "role": "Padre/madre", "name": "Tutor Legal"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.name = ""

# Tasks dictionary per user username or global empty list by default
if "tasks" not in st.session_state:
    st.session_state.tasks = {} # Format: {username: [{"title": ..., "due": ..., "status": ...}]}

if "announcements" not in st.session_state:
    st.session_state.announcements = [
        {"author": "Profesor Titular", "text": "Bienvenidos al nuevo trimestre escolar. Consulten el calendario de tareas.", "date": "2026-09-16"}
    ]

# Chat history storage per user
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function to render a task creation form anywhere
def render_task_creation_expander(user_key_suffix=""):
    with st.expander("➕ Añadir nueva tarea"):
        with st.form(key=f"task_form_{user_key_suffix}"):
            t_title = st.text_input("Título de la tarea")
            t_date = st.date_input("Fecha límite", key=f"date_{user_key_suffix}")
            submitted = st.form_submit_button("Guardar Tarea")
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
                    st.success("¡Tarea añadida con éxito!")
                    st.rerun()
                else:
                    st.warning("Escribe un título para la tarea.")

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #1e3d59;'>🎓 CONCHY</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #438a5e; font-size: 1.1em;'>Tu asistente virtual inteligente para la gestión académica y escolar.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
        
        with tab_login:
            st.subheader("Acceso de Usuarios")
            login_user = st.text_input("Usuario", key="login_user")
            login_pass = st.text_input("Contraseña", type="password", key="login_pass")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Iniciar Sesión", type="primary"):
                if login_user in st.session_state.users and st.session_state.users[login_user]["password"] == hash_password(login_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.session_state.role = st.session_state.users[login_user]["role"]
                    st.session_state.name = st.session_state.users[login_user]["name"]
                    st.success(f"Bienvenido/a, {st.session_state.name}")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
                    
        with tab_register:
            st.subheader("Registro de Nueva Cuenta")
            reg_user = st.text_input("Nombre de usuario único", key="reg_user")
            reg_name = st.text_input("Nombre y Apellidos", key="reg_name")
            reg_pass = st.text_input("Contraseña", type="password", key="reg_pass")
            reg_role = st.selectbox("Seleccione su tipo de cuenta", ["Alumno", "Profesor", "Padre/madre"], key="reg_role")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Registrarse", type="secondary"):
                if not reg_user or not reg_pass or not reg_name:
                    st.warning("Por favor, complete todos los campos obligatorios.")
                elif reg_user in st.session_state.users:
                    st.error("Este nombre de usuario ya está registrado.")
                else:
                    st.session_state.users[reg_user] = {
                        "password": hash_password(reg_pass),
                        "role": reg_role,
                        "name": reg_name
                    }
                    st.success("¡Cuenta registrada con éxito! Ya puede iniciar sesión en la pestaña contigua.")

else:
    # --- MAIN APPLICATION INTERFACE (POST-LOGIN) ---
    st.sidebar.markdown(f"### 👤 {st.session_state.name}")
    st.sidebar.markdown(f"**Perfil:** `{st.session_state.role}`")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("Navegación", [
        "🏠 Panel Principal", 
        "📚 Tareas y Evaluaciones", 
        "🤖 Hablar con Conchy AI", 
        "📢 Comunicados", 
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

    # Dashboard - Panel Principal
    if menu == "🏠 Panel Principal":
        st.title(f"Panel de Control - {st.session_state.role}")
        st.info("🤖 **Asistente Conchy:** Aquí tienes un resumen de tu actividad. Puedes agregar nuevas tareas en cualquier momento.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📝 Tus Tareas Pendientes")
            if user_tasks:
                for idx, t in enumerate(user_tasks):
                    st.write(f"- **{t['title']}** (Vence: {t['due']})")
            else:
                st.write("No hay tareas registradas actualmente.")
        with col2:
            st.subheader("📊 Resumen Rápido")
            st.metric("Tareas totales creadas", len(user_tasks))
            st.metric("Rol en Conchy", st.session_state.role)

        st.markdown("---")
        render_task_creation_expander("panel_principal")

    # Tareas y Evaluaciones
    elif menu == "📚 Tareas y Evaluaciones":
        st.title("📚 Gestión de Tareas")
        st.write("Consulta y administra tus tareas pendientes.")
        
        if user_tasks:
            df = pd.DataFrame(user_tasks)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Todavía no has agregado ninguna tarea.")

        st.markdown("---")
        render_task_creation_expander("tareas_evaluaciones")

    # Hablar con Conchy AI
    elif menu == "🤖 Hablar con Conchy AI":
        st.title("🤖 Chat con Conchy AI")
        st.write("Hola, soy **Conchy**, tu asistente virtual inteligente. Puedo aconsejarte sobre cómo usar la plataforma, organizarte mejor y revisar la información de tu cuenta.")
        
        if current_user not in st.session_state.chat_history:
            st.session_state.chat_history[current_user] = [
                {"role": "assistant", "content": f"¡Hola {st.session_state.name}! Soy Conchy. Veo que tienes {len(user_tasks)} tareas registradas en tu cuenta con rol de {st.session_state.role}. ¿En qué te puedo ayudar hoy?"}
            ]
        
        # Display chat messages
        for message in st.session_state.chat_history[current_user]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Chat input
        if prompt := st.chat_input("Pregúntale a Conchy sobre tus tareas, organización o uso de la web..."):
            st.session_state.chat_history[current_user].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            # Generate Conchy AI response based on context and user info
            prompt_lower = prompt.lower()
            if "tarea" in prompt_lower or "pendiente" in prompt_lower:
                if user_tasks:
                    task_titles = ", ".join([t['title'] for t in user_tasks])
                    response_text = f"Revisando tu cuenta, veo que tienes las siguientes tareas: {task_titles}. ¡Te recomiendo organizarlas por fecha de entrega!"
                else:
                    response_text = f"He revisado tu cuenta ({st.session_state.name}) y veo que actualmente no tienes ninguna tarea registrada. ¡Puedes usar el formulario inferior para añadir alguna!"
            elif "consejo" in prompt_lower or "organizar" in prompt_lower or "ayuda" in prompt_lower:
                response_text = f"Como usuari@ con perfil de **{st.session_state.role}**, te sugiero revisar regularmente el panel principal y mantener al día tus registros para aprovechar al máximo Conchy."
            else:
                response_text = f"Entiendo perfectamente. Como tu asistente Conchy, estoy aquí para ayudarte con tu rol de {st.session_state.role}. ¿Te gustaría que te ayude a planificar tus próximos objetivos o añadir una tarea?"
                
            st.session_state.chat_history[current_user].append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)

        st.markdown("---")
        render_task_creation_expander("chat_conchy")

    # Comunicados
    elif menu == "📢 Comunicados":
        st.title("📢 Tablón de Comunicados Oficiales")
        
        if st.session_state.announcements:
            for ann in st.session_state.announcements:
                st.markdown("**{ann['author']}** — *{ann['date']}*

{ann['text']}")
                st.markdown("---")
        else:
            st.info("No hay comunicados oficiales en este momento.")

        st.markdown("---")
        render_task_creation_expander("comunicados")

    # Mi Cuenta
    elif menu == "⚙️ Mi Cuenta":
        st.title("⚙️ Configuración de Cuenta")
        st.write(f"**Nombre de usuario:** {st.session_state.username}")
        st.write(f"**Nombre completo:** {st.session_state.name}")
        st.write(f"**Rol asignado:** {st.session_state.role}")
        st.write(f"**Total de tareas personales:** {len(user_tasks)}")

        st.markdown("---")
        render_task_creation_expander("mi_cuenta")

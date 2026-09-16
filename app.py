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

# Custom CSS for a professional assistant look
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
    # Default pre-configured accounts for testing each role
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

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"title": "Entrega de proyecto trimestral", "due": "2026-09-30", "status": "Pendiente", "assigned_by": "Profesor Titular"}
    ]

if "announcements" not in st.session_state:
    st.session_state.announcements = [
        {"author": "Profesor Titular", "text": "Bienvenidos al nuevo trimestre escolar. Consulten el calendario de tareas.", "date": "2026-09-16"}
    ]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
                    st.warning("Por favor,complete todos los campos obligatorios.")
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
    
    menu = st.sidebar.radio("Navegación", ["🏠 Panel Principal", "📚 Tareas y Evaluaciones", "📢 Comunicados", "⚙️ Mi Cuenta"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.name = ""
        st.rerun()

    # Dashboard - Alumno
    if menu == "🏠 Panel Principal":
        st.title(f"Panel de Control - {st.session_state.role}")
        
        if st.session_state.role == "Alumno":
            st.info("🤖 **Asistente Conchy:** Tienes 1 tarea pendiente para las próximas semanas. Revisa el apartado correspondiente para mantenerte al día.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📝 Tareas Próximas")
                pending = [t for t in st.session_state.tasks if t["status"] != "Completada"]
                for t in pending:
                    st.write(f"- **{t['title']}** (Vence: {t['due']})")
            with col2:
                st.subheader("📊 Resumen Académico")
                st.metric("Asistencia registrada", "100%")
                st.metric("Tareas completadas", "0 / 1")

        elif st.session_state.role == "Profesor":
            st.info("🤖 **Asistente Conchy (Panel Docente):** Gestión centralizada de alumnos y publicaciones.")
            st.metric("Total de Alumnos en el sistema", len([u for u, d in st.session_state.users.items() if d["role"] == "Alumno"]))
            
            st.subheader("Publicar nueva tarea")
            task_title = st.text_input("Título de la tarea")
            task_date = st.date_input("Fecha límite de entrega")
            if st.button("Guardar y Publicar"):
                if task_title:
                    st.session_state.tasks.append({
                        "title": task_title,
                        "due": str(task_date),
                        "status": "Pendiente",
                        "assigned_by": st.session_state.name
                    })
                    st.success("Tarea publicada correctamente.")

        elif st.session_state.role == "Padre/madre":
            st.info("🤖 **Asistente Conchy (Portal de Familias):** Información y seguimiento escolar.")
            st.write("Consulte las calificaciones y avisos oficiales publicados por el centro docente.")

    elif menu == "📚 Tareas y Evaluaciones":
        st.title("📚 Gestión de Tareas")
        if st.session_state.tasks:
            df = pd.DataFrame(st.session_state.tasks)
            st.dataframe(df, use_container_width=True)

    elif menu == "📢 Comunicados":
        st.title("📢 Tablón de Anuncios Oficiales")
        for ann in st.session_state.announcements:
            st.markdown(f"**{ann['author']}** — *{ann['date']}*\n\n{ann['text']}")
            st.markdown("---")

    elif menu == "⚙️ Mi Cuenta":
        st.title("⚙️ Configuración")
        st.write(f"**Nombre de usuario:** {st.session_state.username}")
        st.write(f"**Nombre completo:** {st.session_state.name}")
        st.write(f"**Rol asignado:** {st.session_state.role}")

import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Conchi - Asistente Escolar",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling the app
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.name = ""

if "tasks" not in st.session_state:
    st.session_state.tasks = 
        {"title": "Entregar trabajo de matemáticas", "due": "2026-09-20", "status": "Pendiente", "assigned_by": "Prof. Propietario"},
        {"title": "Revisar promesas de paz de Xavi", "due": "2026-09-25", "status": "En proceso", "assigned_by": "Juan"}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication Flow
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🤖 CONCHI: Tu Asistente Escolar Inteligente</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>La plataforma definitiva para organizar el caos del aula, los exámenes...</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
        
        with tab_login:
            st.subheader("Acceso a tu cuenta")
            login_user = st.text_input("Nombre de usuario", key="login_user")
            login_pass = st.text_input("Contraseña", type="password", key="login_pass")
            
            if st.button("Entrar", type="primary"):
                if login_user in st.session_state.users and st.session_state.users[login_user]["password"] == hash_password(login_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.session_state.role = st.session_state.users[login_user]["role"]
                    st.session_state.name = st.session_state.users[login_user]["name"]
                    st.success(f"¡Bienvenido de nuevo, {st.session_state.name}!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
                    
        with tab_register:
            st.subheader("Regístrate en Conchi")
            reg_user = st.text_input("Elige un nombre de usuario", key="reg_user")
            reg_name = st.text_input("Tu Nombre Completo / Apodo", key="reg_name")
            reg_pass = st.text_input("Elige una contraseña", type="password", key="reg_pass")
            reg_role = st.selectbox("Tipo de cuenta", ["Alumno", "Profesor", "Padre/madre"], key="reg_role")
            
            if st.button("Registrarse", type="secondary"):
                if not reg_user or not reg_pass or not reg_name:
                    st.warning("Por favor, rellena todos los campos.")
                elif reg_user in st.session_state.users:
                    st.error("El nombre de usuario ya existe. Elige otro.")
                else:
                    st.session_state.users[reg_user] = {
                        "password": hash_password(reg_pass),
                        "role": reg_role,
                        "name": reg_name
                    }
                    st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión en la pestaña de al lado.")

else:
    # Sidebar navigation & User Info
    st.sidebar.markdown(f"### 👋 Hola, {st.session_state.name}")
    st.sidebar.markdown(f"**Rol:** `👤 {st.session_state.role}`")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("Navegación", ["🏠 Panel Principal", "📚 Tareas y Exámenes", "📢 Tablón de la Clase", "⚙️ Ajustes de Cuenta"])
    
    if st.sidebar.button("Cerrar Sesión", type="primary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.name = ""
        st.rerun()

    # --- PANEL PRINCIPAL ---
    if menu == "🏠 Panel Principal":
        st.title(f"Panel de Control - {st.session_state.role}")
        
        # Role-based dashboard content
        if st.session_state.role == "Alumno":
            st.info("💡 **Consejo de Conchi:** ¡Cuidado con el examen de matemáticas! Recuerda que Xavi prometió paz, pero más vale estudiar por si acaso.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📝 Tus Tareas Pendientes")
                pending = [t for t in st.session_state.tasks if t["status"] != "Completada"]
                if pending:
                    for t in pending:
                        st.markdown(f"- **{t['title']}** (Fecha límite: {t['due']})")
                else:
                    st.success("¡Estás al día con todo! Buen trabajo.")
            with col2:
                st.markdown("### 🗳️ Estado del Aula")
                st.markdown("- **Delegado actual:** Xavi 🤡")
                st.markdown("- **Promesa principal:** Paz en clase y cero agobios.")
                st.markdown("- **Alianza secreta:** Activa (Pacto mutuo).")

        elif st.session_state.role == "Profesor":
            st.info("👨‍🏫 **Panel Docente:** Desde aquí puedes supervisar las actividades y lanzar avisos a los alumnos.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Alumnos registrados", len([u for u, d in st.session_state.users.items() if d["role"] == "Alumno"]))
            with col2:
                st.metric("Tareas activas", len(st.session_state.tasks))
                
            st.subheader("Crear nueva tarea o aviso")
            new_task_title = st.text_input("Título de la tarea / examen")
            new_task_date = st.date_input("Fecha límite")
            if st.button("Publicar Tarea"):
                if new_task_title:
                    st.session_state.tasks.append({
                        "title": new_task_title,
                        "due": str(new_task_date),
                        "status": "Pendiente",
                        "assigned_by": st.session_state.name
                    })
                    st.success("¡Tarea publicada correctamente para todos los alumnos!")

        elif st.session_state.role == "Padre/madre":
            st.info("👪 **Portal Familiar:** Seguimiento del rendimiento y avisos escolares.")
            st.subheader("Resumen de actividad del estudiante")
            st.markdown("- **Estado general:** Excelente comportamiento y colaboración en clase.")
            st.markdown("- **Próximas entregas:** Consulta la pestaña de tareas para ver los plazos.")

    # --- TAREAS Y EXÁMENES ---
    elif menu == "📚 Tareas y Exámenes":
        st.title("📚 Gestión de Tareas y Exámenes")
        
        # Display tasks table
        if st.session_state.tasks:
            df_tasks = pd.DataFrame(st.session_state.tasks)
            st.dataframe(df_tasks, use_container_width=True)
        else:
            st.write("No hay tareas registradas por el momento.")
            
        if st.session_state.role in ["Profesor", "Alumno"]:
            st.subheader("Añadir nueva tarea rápida")
            custom_task = st.text_input("Descripción de la tarea")
            custom_date = st.date_input("Fecha de entrega", key="custom_date")
            if st.button("Añadir Tarea"):
                if custom_task:
                    st.session_state.tasks.append({
                        "title": custom_task,
                        "due": str(custom_date),
                        "status": "Pendiente",
                        "assigned_by": st.session_state.name
                    })
                    st.success("¡Añadido con éxito!")
                    st.rerun()

    # --- TABLÓN DE LA CLASE ---
    elif menu == "📢 Tablón de la Clase":
        st.title("📢 Tablón de Anuncios y Salseo Escolar")
        st.write("El espacio oficial (y no tan oficial) para enterarte de lo que se cuece en clase.")
        
        for ann in st.session_state.announcements:
            st.markdown(f"> **{ann['author']}** *({ann['date']})*:\n> {ann['text']}")
            st.markdown("---")
            
        st.subheader("Publicar un aviso en el tablón")
        new_ann = st.text_area("Escribe tu mensaje...")
        if st.button("Publicar en el tablón"):
            if new_ann:
                st.session_state.announcements.insert(0, {
                    "author": st.session_state.name,
                    "text": new_ann,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("¡Mensaje publicado!")
                st.rerun()

    # --- AJUSTES DE CUENTA ---
    elif menu == "⚙️ Ajustes de Cuenta":
        st.title("⚙️ Configuración de la Cuenta")
        st.write(f"**Usuario:** `{st.session_state.username}`")
        st.write(f"**Nombre:** {st.session_state.name}")
        st.write(f"**Rol:** {st.session_state.role}")
        st.warning("Próximamente podrás cambiar tu contraseña y personalizar tu avatar de Conchi.")

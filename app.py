import streamlit as st
import hashlib
import pandas as pd
import sqlite3
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

# --- CONFIGURACIÓN DE LA BASE DE DATOS SQLITE (Persistencia real) ---
def init_db():
    conn = sqlite3.connect('conchy_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            due TEXT NOT NULL,
            status TEXT NOT NULL,
            grade REAL DEFAULT NULL
        )
    ''')
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# Usuario por defecto si está vacía
cursor.execute("SELECT COUNT(*) FROM users")
if cursor.fetchone()[0] == 0:
    default_pass = hashlib.sha256("1234".encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                   ("alumno", default_pass, "Alumno", "Estudiante Ejemplo"))
    conn.commit()

# --- CONFIGURACIÓN DE LA API KEY Y CLIENTE DE GEMINI ---
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")

client = None
if GOOGLE_API_KEY:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.sidebar.error(f"Error al inicializar el cliente de IA: {e}")

# Inicialización de Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.name = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function to add tasks
def render_task_creation_expander(user_key_suffix=""):
    with st.expander("➕ Añadir nueva tarea o evaluación"):
        with st.form(key=f"task_form_{user_key_suffix}"):
            t_title = st.text_input("Título de la tarea o examen")
            t_date = st.date_input("Fecha límite / Examen", key=f"date_{user_key_suffix}")
            submitted = st.form_submit_button("Guardar Registro")
            if submitted:
                if t_title:
                    curr_user = st.session_state.username
                    cursor.execute("INSERT INTO tasks (username, title, due, status, grade) VALUES (?, ?, ?, ?, ?)",
                                   (curr_user, t_title, str(t_date), "Pendiente", None))
                    conn.commit()
                    st.success("¡Añadido y guardado con éxito!")
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
                cursor.execute("SELECT password, role, name FROM users WHERE username = ?", (login_user,))
                user_record = cursor.fetchone()
                
                if user_record and user_record[0] == hash_password(login_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.session_state.role = user_record[1]
                    st.session_state.name = user_record[2]
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
                else:
                    cursor.execute("SELECT username FROM users WHERE username = ?", (reg_user,))
                    if cursor.fetchone():
                        st.error("Este usuario ya existe.")
                    else:
                        cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                                       (reg_user, hash_password(reg_pass), "Alumno", reg_name))
                        conn.commit()
                        st.success("¡Cuenta creada y guardada con éxito! Ya puedes iniciar sesión.")

else:
    # --- MAIN APPLICATION (ALUMNO) ---
    st.sidebar.markdown(f"### 👤 {st.session_state.name}")
    st.sidebar.markdown(f"**Perfil:** `Alumno 🎓`")
    
    if client:
        st.sidebar.success("🔌 Gemini 3.6 Flash Conectado")
    else:
        st.sidebar.warning("⚠️ Falta configurar GOOGLE_API_KEY")
        
    st.sidebar.markdown("---")
    
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
    
    # Cargar tareas con ID desde la base de datos
    cursor.execute("SELECT id, title, due, status, grade FROM tasks WHERE username = ?", (current_user,))
    db_tasks = cursor.fetchall()
    user_tasks = [{"id": row[0], "title": row[1], "due": row[2], "status": row[3], "grade": row[4]} for row in db_tasks]

    # 1. Tareas y evaluaciones
    if menu == "📚 Tareas y evaluaciones":
        st.title("📚 Tareas y Evaluaciones")
        st.write("Gestiona, evalúa y consulta tus entregas de forma permanente.")
        
        if user_tasks:
            # Mostrar tabla informativa
            df_display = pd.DataFrame([{
                "ID": t["id"],
                "Título": t["title"],
                "Fecha Vencimiento": t["due"],
                "Estado": t["status"],
                "Nota": t["grade"] if t["grade"] is not None else "Sin calificar"
            } for t in user_tasks])
            st.dataframe(df_display, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🛠️ Gestión de Registros (Notas y Borrado)")
            
            # Selector para gestionar tarea individual
            task_options = {f"{t['title']} (Vence: {t['due']})": t['id'] for t in user_tasks}
            selected_task_label = st.selectbox("Selecciona una tarea o examen para actualizar o borrar:", list(task_options.keys()))
            selected_task_id = task_options[selected_task_label]
            
            # Buscar tarea seleccionada
            current_t = next((t for t in user_tasks if t['id'] == selected_task_id), None)
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                with st.form(key=f"grade_form_{selected_task_id}"):
                    new_grade = st.number_input("Poner o actualizar nota (0 - 10):", min_value=0.0, max_value=10.0, step=0.1, value=float(current_t['grade']) if current_t['grade'] is not None else 5.0)
                    submit_grade = st.form_submit_button("Guardar Nota")
                    if submit_grade:
                        cursor.execute("UPDATE tasks SET grade = ?, status = 'Completado' WHERE id = ?", (new_grade, selected_task_id))
                        conn.commit()
                        st.success("¡Nota guardada con éxito!")
                        st.rerun()
            with col_g2:
                st.write("")
                st.write("")
                if st.button("🗑️ Borrar esta tarea o examen", type="secondary"):
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (selected_task_id,))
                    conn.commit()
                    st.success("¡Registro borrado correctamente!")
                    st.rerun()

            # --- ESTADÍSTICAS BASADAS EN LA MEDIA DE ESPAÑA ---
            st.markdown("---")
            st.subheader("📈 Estadísticas Académicas vs. Media de España")
            
            # Calcular nota media del alumno (solo tareas con nota asignada)
            notas_validas = [t['grade'] for t in user_tasks if t['grade'] is not None]
            media_alumno = sum(notas_valids) / len(notas_valids) if notas_valids else 0.0
            media_espana = 6.2  # Referencia media estimada estándar en España
            
            col_est1, col_est2, col_est3 = st.columns(3)
            with col_est1:
                st.metric("Tu Nota Media", f"{media_alumno:.2f}" if notas_valids else "Sin notas")
            with col_est2:
                st.metric("Media de Referencia en España", f"{media_espana} / 10")
            with col_est3:
                diferencia = media_alumno - media_espana
                st.metric("Diferencia", f"{diferencia:+.2f} pts" if notas_valids else "N/D", delta_color="normal" if notas_valids else "off")
            
            if notas_valids:
                if media_alumno >= media_espana:
                    st.success("🌟 ¡Enhorabuena! Tu rendimiento medio se encuentra por encima de la media de referencia estimada en España.")
                else:
                    st.info("💪 ¡Sigue esforzándote! Estás un poco por debajo de la media estándar; Conchy IA puede ayudarte a preparar tus próximos exámenes.")
            else:
                st.warning("⚠️ Asigna una nota numérica a tus tareas o exámenes calificados para ver la comparativa estadística completa.")

        else:
            st.info("No has agregado ninguna tarea o evaluación todavía.")

        st.markdown("---")
        render_task_creation_expander("seccion_tareas")

    # 2. Conchy IA
    elif menu == "🤖 Conchy IA":
        st.title("🤖 Asistente Conchy IA")
        st.write("Hola, soy **Conchy**, tu asistente inteligente impulsada por **Gemini 3.6 Flash**. Puedo ayudarte a resolver dudas, planificar tus estudios y organizarte mejor.")
        
        if current_user not in st.session_state.chat_history:
            st.session_state.chat_history[current_user] = [
                {"role": "assistant", "content": f"¡Hola {st.session_state.name}! Soy Conchy. Veo que tienes {len(user_tasks)} tareas o evaluaciones guardadas. ¿En qué te puedo ayudar hoy?"}
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
                    contexto_sistema = (
                        f"Eres Conchy, una asistente escolar virtual inteligente y amable para el estudiante {st.session_state.name}. "
                        f"Tareas y notas guardadas del alumno: {user_tasks}. "
                        "Ayúdale a organizarse, resolver dudas de estudio y motivarle."
                    )
                    
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=f"{contexto_sistema}\n\nPregunta del alumno: {prompt}"
                    )
                    response_text = response.text
                except Exception as e:
                    response_text = f"Hubo un error al conectar con Gemini 3.6 Flash: {e}"
            else:
                prompt_lower = prompt.lower()
                if "tarea" in prompt_lower or "examen" in prompt_lower:
                    response_text = f"Tienes {len(user_tasks)} tareas guardadas permanentemente. Configura tu GOOGLE_API_KEY para activar la IA avanzada."
                else:
                    response_text = "¡Hola! Configura tu clave API para conversar con el modelo de Gemini."

            st.session_state.chat_history[current_user].append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)

    # 3. Mi Cuenta
    elif menu == "⚙️ Mi Cuenta":
        st.title("⚙️ Mi Cuenta")
        st.write(f"**Usuario:** {st.session_state.username}")
        st.write(f"**Nombre:** {st.session_state.name}")
        st.write(f"**Total de tareas/evaluaciones guardadas:** {len(user_tasks)}")

        st.markdown("---")
        st.subheader("Estado de la persistencia y la IA")
        st.success("💾 Base de datos SQLite activa: Todas las cuentas, notas y tareas se guardan de forma permanente.")
        if client:
            st.success("🔌 Conectado correctamente con el modelo `gemini-3.6-flash`.")
        else:
            st.warning("⚠️ No se detectó una clave API válida de Google.")

import streamlit as st
from dotenv import load_dotenv
import os

# Importar funciones de lógica RAG
from rag_logic import initialize_vector_db, get_qa_chain, answer_question

# Cargar variables de entorno (como OPENAI_API_KEY)
load_dotenv()

# Configuración de la página (ideal para iframes: sin sidebar, layout wide)
st.set_page_config(
    page_title="Asistente Corporativo",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar menú de Streamlit y barra de pie de página para que luzca mejor incrustado
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* Eliminar el relleno superior de la app para aprovechar el iframe */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# El bot leerá los PDFs que pongas en la carpeta 'docs' que está en la raíz del proyecto.

WELCOME_MESSAGE = """Hola, soy el asistente de ADIL México.
Estoy aquí para ayudarte a encontrar información contenida en nuestros documentos y materiales internos.

Escríbeme tu duda de forma concreta (por ejemplo: '¿Qué talleres ofrecen para empresas grandes?' o 'Resume los beneficios del programa X') y te responderé usando solo la información disponible en esos documentos."""

def init_app():
    """Inicializa la cadena QA y la guarda en la sesión."""
    if "qa_chain" not in st.session_state:
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("⚠️ La clave GOOGLE_API_KEY no está configurada. Revisa el archivo .env")
            st.stop()
            
        with st.spinner("Inicializando la base de conocimientos con los PDFs locales... (esto puede tomar unos segundos)"):
            try:
                vector_db = initialize_vector_db("docs")
                st.session_state.qa_chain = get_qa_chain(vector_db)
            except Exception as e:
                st.error(f"Error cargando documentos: {e}")
                st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE}
        ]

init_app()

# Título de la interfaz
st.title("Asistente Virtual")

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar input del usuario
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Añadir mensaje de usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostrar mensaje de usuario
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner("Buscando en los documentos..."):
            result = answer_question(st.session_state.qa_chain, prompt)
            respuesta = result["answer"]
            fuentes = result["sources"]

            # Formatear fuentes opcionalmente
            respuesta_formateada = respuesta
            """
            if fuentes and respuesta != "No encuentro esa información en los documentos disponibles.":
                respuesta_formateada += "\n\n---\n*Fuentes: " + ", ".join(fuentes) + "*"
            """
            st.markdown(respuesta_formateada)
            
    # Añadir respuesta al historial
    st.session_state.messages.append({"role": "assistant", "content": respuesta_formateada})

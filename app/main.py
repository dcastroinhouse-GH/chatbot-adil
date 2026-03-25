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
Estoy aquí para responder a tus preguntas basándome **exclusivamente** en nuestros catálogos y documentos oficiales:

- [Catálogo de Contenidos](https://adilmexico.com/pdf-adil/ADIL-CatalogoContenidos.pdf)
- [Catálogo de Contenidos 25 NPc DVIH Salud Mental](https://adilmexico.com/pdf-adil/ADIL-CatalogoContenidos25NPcDVIHSaludMental.pdf)
- [Catálogo Generalidades DEI](https://adilmexico.com/pdf-adil/ADIL-CatalogoGeneralidadesDEI.pdf)
- [Catálogo Generalidades DEI Presupuesto](https://adilmexico.com/pdf-adil/ADIL-CatalogoGeneralidadesDEIPresupuesto.pdf)
- [Catálogo de Género](https://adilmexico.com/pdf-adil/ADIL-CatalogoGenero.pdf)
- [Catálogo Rumbo Al Orgullo](https://adilmexico.com/pdf-adil/ADIL-CatalogoRumboAlOrgullo.pdf)
- [Conferencias Magistrales](https://adilmexico.com/pdf-adil/ADIL-ConferenciasMagistrales.pdf)

Escríbeme tu duda de forma concreta (por ejemplo: '¿Qué talleres ofrecen para empresas grandes?' o 'Resume los beneficios del programa X') y te responderé usando solo la información disponible en esos documentos."""

@st.cache_resource(show_spinner=False)
def load_qa_chain_globally():
    """Inicializa la cadena QA una sola vez y la guarda en caché global para todos los usuarios."""
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("⚠️ La clave GOOGLE_API_KEY no está configurada. Revisa el archivo .env o Render variables.")
        st.stop()
    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        st.error("⚠️ La clave HUGGINGFACEHUB_API_TOKEN no está configurada en Render.")
        st.stop()
        
    try:
        vector_db = initialize_vector_db("docs")
        return get_qa_chain(vector_db)
    except Exception as e:
        st.error(f"Error cargando documentos: {e}")
        st.stop()

with st.spinner("Cargando la base de datos (esto solo toma unos segundos extra la primerísima vez)..."):
    qa_chain = load_qa_chain_globally()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]

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
            result = answer_question(qa_chain, prompt)
            respuesta = result["answer"]
            fuentes = result["sources"]

            # Formatear fuentes
            respuesta_formateada = respuesta
            if fuentes and "No encuentro esa información" not in respuesta:
                respuesta_formateada += "\n\n---\n**Fuentes:** " + ", ".join(fuentes)
            st.markdown(respuesta_formateada)
            
    # Añadir respuesta al historial
    st.session_state.messages.append({"role": "assistant", "content": respuesta_formateada})

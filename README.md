# RAG Chatbot para WordPress (PDF Inteligente)

Este es un chatbot basado en Recuperación de Generación Aumentada (RAG) diseñado para leer una lista específica de PDFs alojados en tu dominio y responder exclusivamente usando esa información.

## Características
- **Zero Hallucination:** Si la información no está en los PDF, responde estrictamente: "No encuentro esa información en los documentos disponibles."
- **Tecnologías:** Construido en Python 3 con **Streamlit** (UI rápida y limpia), **LangChain** (Lógica RAG), **FAISS** (Base de datos vectorial en memoria) y los embeddings/LLMs más recientes de Google Gemini (`gemini-2.5-flash`).
- **Incrustable (Widget):** Interfaz optimizada para ser embebida como un `iframe` dentro de Elementor o cualquier constructor web en WordPress.

---

## 🚀 Preparar el entorno local y probar

### 1. Clonar o descargar el código
Descarga los archivos del proyecto y abre una terminal en esta carpeta.

### 2. Crear y activar un entorno virtual (Recomendado)
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar tu clave API
1. Copia el archivo de propiedades `.env.example` y renómbralo a `.env`.
2. Edítalo e ingresa tu clave API de Google:
```env
GOOGLE_API_KEY=AIzaSy...tu_apikey_secreta
```

### 5. Añadir TUS documentos PDF
Abre el archivo `app/main.py` y busca y modifica la variable `PDF_URLS`. Añade las URL exactas de los documentos alojados en tu dominio:

```python
PDF_URLS = [
    "https://tusitio.com/docs/manual-corporativo.pdf",
    "https://tusitio.com/docs/servicios-2026.pdf"
]
```
*(Durante el desarrollo puedes dejar la url de prueba que viene por defecto y reemplazarla después).*

### 6. Ejecutar la App en Local
Ejecuta el siguiente comando desde la raíz del proyecto para iniciar la interfaz de Streamlit:

```bash
streamlit run app/main.py
```
Se abrirá automáticamente en tu navegador por lo general en `http://localhost:8501`.

---

## 🌍 Desplegar la app (Para Producción)

HostGator (en planes de hosting compartido corporativo estándar) **no soporta aplicaciones persistentes de Python** de forma robusta.
Para publicar este bot, la práctica estándar de la industria es utilizar plataformas "Platform-as-a-Service" (PaaS) que soportan nativamente Streamlit o Python sin configuraciones complejas y que ofrecen niveles gratuitos o muy baratos:

### Opción Recomendada: Render (render.com) o Railway.app
Ambos servicios pueden conectar con un repositorio de GitHub y lanzar tu app.

**En Render (por ejemplo):**
1. Sube este código a un repositorio en Github.
2. Inicia sesión en Render y crea un nuevo **"Web Service"**.
3. Conecta tu repositorio.
4. Establece el **Build Command**: `pip install -r requirements.txt`
5. Establece el **Start Command**: `streamlit run app/main.py --server.port $PORT`
6. Ve a las variables de entorno de Render e introduce `GOOGLE_API_KEY` con tu clave de la API.
7. Haz clic en desplegar, y Render procesará tu código y te entregará una URL en la que la web vivirá encendida (por ejemplo: `https://chat- Adil.onrender.com`).

---

## 🧩 Incrustar el Chatbot en WordPress/Elementor

Una vez que tengas tu aplicación corriendo en producción con tu URL (por ejemplo: `https://chat- Adil.onrender.com`), puedes incluir la experiencia directamente en una página o modal dentro de WordPress/Elementor utilizando el elemento "HTML" o "Shortcode" nativo de WordPress.

Coloca el siguiente fragmento HTML dentro del widget HTML de Elementor:

```html
<iframe 
    src="https://TU_URL_DE_PRODUCCION" 
    width="100%" 
    height="650" 
    style="border:1px solid #e1e1e1; border-radius: 10px; overflow:hidden;" 
    loading="lazy"
    title="Asistente Virtual IA">
</iframe>
```

*Nota: La altura ("height") la puedes ajustar desde código HTML (ej: "700") o en configuración de Elementor, el ancho quedará al 100% responsivo para celulares o pantallas grandes.*

import os
import tempfile
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

import glob

def initialize_vector_db(pdf_dir: str = "docs") -> FAISS:
    """Lee PDFs de una carpeta local, los divide en fragmentos y crea un índice vectorial FAISS."""
    documents = []
    
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        
    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    
    # PARA PRUEBAS: Usar solo el primer PDF para acelerar enormemente la carga inicial
    pdf_files = pdf_files[:1]
    
    for filepath in pdf_files:
        print(f"Procesando localmente: {filepath}")
        loader = PyPDFLoader(filepath)
        documents.extend(loader.load())
    
    if not documents:
        raise ValueError("No hay PDFs en la carpeta 'docs'. Sube tus archivos .pdf allí antes de desplegar.")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    
    # Usar el modelo actual de embeddings de Google Gemini especificando el task_type
    embeddings = GoogleGenerativeAIEmbeddings(
        model="text-embedding-004",
        task_type="retrieval_document"
    )
    
    # Crear el VectorStore
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store

def get_qa_chain(vector_store: FAISS):
    """Crea la cadena de recuperación y generación con prompts restrictivos."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # Configurar el retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    
    # Prompt estricto del sistema para evitar alucinaciones
    system_prompt = (
        "Eres un asistente corporativo virtual útil, profesional y cercano. "
        "Tu objetivo es responder dudas de los usuarios utilizando ÚNICAMENTE la "
        "información proporcionada en el siguiente contexto extraído de los documentos de la empresa.\n\n"
        "REGLA MUY IMPORTANTE: Si la respuesta a la pregunta no se encuentra en el contexto proporcionado, "
        "o si no tienes contexto suficiente, DEBES responder textualmente con la siguiente frase: "
        "'No encuentro esa información en los documentos disponibles.'\n\n"
        "Bajo ninguna circunstancia debes inventar datos, cifras, ejemplos ni nombres que no estén "
        "explícitamente incluidos en el contexto.\n"
        "Responde de forma concisa y clara, utilizando párrafos cortos o viñetas si es necesario.\n"
        "Responde en el mismo idioma en el que se te hace la pregunta.\n\n"
        "Contexto:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    qa_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return qa_chain

def answer_question(qa_chain, question: str) -> dict:
    """Ejecuta la pregunta a través de la cadena QA y devuelve respuesta y fuentes."""
    result = qa_chain.invoke({"input": question})
    
    # Extraer las páginas de origen como metadatos útiles
    sources = set()
    for doc in result.get("context", []):
        source = doc.metadata.get("source", "Documento desconocido")
        page = doc.metadata.get("page", 0) + 1  # 0-indexed a 1-indexed
        filename = os.path.basename(source)
        sources.add(f"{filename} (Pág. {page})")
        
    return {
        "answer": result.get("answer", ""),
        "sources": list(sources)
    }

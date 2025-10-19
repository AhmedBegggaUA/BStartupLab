import os
import glob
import dotenv
from time import time
import streamlit as st
import json
import requests

from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders import (
    WebBaseLoader, 
    PyPDFLoader, 
    Docx2txtLoader,
    PyMuPDFLoader,
)
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

dotenv.load_dotenv()

os.environ["USER_AGENT"] = "StartupLab_Agent"
DB_DOCS_LIMIT = 50
PERSIST_DIR = "./chroma_db"
METADATA_FILE = os.path.join(PERSIST_DIR, "metadata.json")

# ALIA Configuration
ALIA_API_KEY = "zpka_068cd9869c454da6a184ca01df297660_0beb56e9"
ALIA_MODEL_URL = "https://api.publicai.co/v1/chat/completions"
ALIA_MODEL = "BSC-LT/ALIA-40b-instruct_Q8_0"


def load_persistent_vector_db(api_key):
    """Carga la base de datos vectorial persistente si existe, sino la crea vacía"""
    try:
        if not os.path.exists(PERSIST_DIR):
            os.makedirs(PERSIST_DIR, exist_ok=True)
        
        rag_sources = []
        if os.path.exists(METADATA_FILE):
            try:
                with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    rag_sources = metadata.get('sources', [])
            except:
                pass
        
        embedding = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-small"
        )
        
        vector_db = Chroma(
            embedding_function=embedding,
            persist_directory=PERSIST_DIR,
            collection_name="startup_docs"
        )
        
        return vector_db, rag_sources
    
    except Exception as e:
        st.error(f"❌ Error cargando base de datos persistente: {str(e)}")
        return None, []


def save_metadata():
    """Guarda los metadatos de los documentos cargados"""
    try:
        os.makedirs(PERSIST_DIR, exist_ok=True)
        metadata = {
            'sources': st.session_state.rag_sources,
            'timestamp': str(time())
        }
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"⚠️ Error guardando metadatos: {str(e)}")


def call_alia(messages, temperature=0.1, language="es", stream=False):
    """Llama al modelo ALIA con los mensajes proporcionados"""
    
    formatted_messages = []
    
    for msg in messages:
        if msg["role"] == "system":
            lang_info = ""
            if language == "ca":
                lang_info = "\n\nRESPON EN CATALÀ."
            elif language == "eu":
                lang_info = "\n\nRESPON EN EUSKARA."
            elif language == "gl":
                lang_info = "\n\nRESPON EN GALEGO."
            elif language == "va":
                lang_info = "\n\nRESPON EN VALENCIÀ."
            
            formatted_messages.append({
                "role": "system",
                "content": msg["content"] + lang_info
            })
        else:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    payload = {
        "model": ALIA_MODEL,
        "messages": formatted_messages,
        "temperature": temperature,
        "seed": 42,
        "stream": stream
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ALIA_API_KEY}",
        "User-Agent": "StartupLab/1.0"
    }
    
    try:
        if stream:
            response = requests.post(ALIA_MODEL_URL, headers=headers, json=payload, timeout=120, stream=True)
            
            if response.status_code == 200:
                return response
            else:
                st.error(f"Error ALIA {response.status_code}: {response.text}")
                return None
        else:
            response = requests.post(ALIA_MODEL_URL, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                st.error(f"Error ALIA {response.status_code}: {response.text}")
                return None
    except Exception as e:
        st.error(f"❌ Error llamando a ALIA: {str(e)}")
        return None


def rephrase_query(query, conversation_history, language="es"):
    """Usa ALIA para reformular la query y obtener mejores resultados de búsqueda"""
    
    rephrase_prompt = """Reformula esta consulta para búsqueda de documentos legales españoles.

Extrae términos clave: formas jurídicas, trámites, impuestos, financiación.
Devuelve SOLO los términos de búsqueda optimizados."""

    history_text = ""
    if conversation_history:
        for msg in conversation_history[-2:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                history_text += f"\nUsuario: {content[:100]}"
    
    if history_text:
        user_message = f"Contexto:{history_text}\n\nConsulta: {query}"
    else:
        user_message = f"Consulta: {query}"
    
    messages = [
        {"role": "system", "content": rephrase_prompt},
        {"role": "user", "content": user_message}
    ]
    
    rephrased = call_alia(messages, temperature=0.0, language=language, stream=False)
    return rephrased if rephrased else query


def rerank_documents(query, documents, top_k=5, language="es"):
    """Usa ALIA para reordenar documentos por relevancia"""
    
    if not documents or len(documents) <= top_k:
        return documents[:top_k]
    
    rerank_prompt = """Evalúa relevancia (0-10) de cada documento.
Responde SOLO con números separados por comas.
Ejemplo: 8,3,9,2,7"""

    docs_text = ""
    for i, doc in enumerate(documents[:10]):
        content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
        docs_text += f"\nDOC{i+1}: {content[:800]}"
    
    messages = [
        {"role": "system", "content": rerank_prompt},
        {"role": "user", "content": f"Query: {query}\nDocs:{docs_text}\nScores:"}
    ]
    
    scores_text = call_alia(messages, temperature=0.0, language=language, stream=False)
    
    if not scores_text:
        return documents[:top_k]
    
    try:
        scores = []
        for part in scores_text.split(','):
            try:
                score = float(part.strip().split()[0])
                scores.append(score)
            except:
                scores.append(0)
        
        doc_scores = list(zip(documents, scores[:len(documents)]))
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in doc_scores[:top_k]]
    except Exception as e:
        return documents[:top_k]


def stream_llm_rag_response(messages, language="es"):
    """Stream respuestas RAG usando ALIA - VERSIÓN OPTIMIZADA"""
    
    try:
        user_query = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        
        # Preparar historial
        conversation_history = []
        for m in messages[:-1]:
            role = m.type if hasattr(m, 'type') else m.get("role", "user")
            content = m.content if hasattr(m, 'content') else m.get("content", "")
            if "Bienvenido a StartupLab" not in content:
                conversation_history.append({"role": role, "content": content})
        
        # Buscar documentos
        context = ""
        if "vector_db" in st.session_state:
            # REPHRASING
            rephrased_query = rephrase_query(user_query, conversation_history, language)
            
            retriever = st.session_state.vector_db.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 15}
            )
            
            retrieved_docs = retriever.get_relevant_documents(rephrased_query)
            
            if retrieved_docs:
                # RERANKING
                reranked_docs = rerank_documents(user_query, retrieved_docs, top_k=5, language=language)
                
                # Construir contexto
                context_parts = []
                for i, doc in enumerate(reranked_docs):
                    content = doc.page_content[:1200]
                    context_parts.append(f"[DOC{i+1}]\n{content}")
                context = "\n\n".join(context_parts)
        
        # System prompt SIMPLE
        if context:
            system_prompt = f"""Eres gestor experto en creación de empresas en España.

DOCUMENTOS LEGALES:
{context}

INSTRUCCIONES:
Proporciona información CONCRETA sobre trámites legales, fiscales y financiación:
- NO SE RESPONDE CON UNA SOLA PREGUNTA.

- Formas jurídicas (SL, Autónomo) con COSTES y CAPITAL mínimo
- Trámites específicos: Hacienda (036/037), Seguridad Social (RETA), Registro Mercantil
- Modelos fiscales (303 IVA, 130 IRPF) con PLAZOS de presentación
- Obligaciones tributarias concretas
- Productos financiación Banco Sabadell

USA FORMATO:
**Título**
- Dato concreto (coste: X€, plazo: X días)
- Dato concreto (coste: X€, plazo: X días)

**Pasos:**
1. Acción específica (coste/plazo)
2. Acción específica (coste/plazo)
NO preguntes al usuario. DA TODA LA INFO DIRECTAMENTE.
**Importante:** Detalle legal/fiscal clave

¿Necesitas info sobre [tema]?

PROHIBIDO:
- Frases genéricas tipo "desarrolla un plan"
- Repetir palabras continuamente
- Respuestas sin datos concretos"""
        else:
            system_prompt = """Eres gestor experto en creación de empresas en España.

Proporciona información CONCRETA sobre:
- Formas jurídicas (SL/Autónomo) + costes reales
- Trámites: Hacienda (036/037), Seguridad Social, Registro Mercantil
- Modelos fiscales (303 IVA, 130 IRPF) + plazos
- Capital necesario y obligaciones

Formato con DATOS CONCRETOS:
**Tema**
- Punto (coste/plazo)

**Pasos:**
1. Acción (X€, X días)

¿Más info sobre [tema]?"""

        # Construir mensaje usuario
        full_user_message = user_query
        
        formatted_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_message}
        ]
        
        # Llamar a ALIA
        response_stream = call_alia(formatted_messages, temperature=0.3, language=language, stream=True)
        
        if response_stream:
            full_response = ""
            word_count = {}
            
            for line in response_stream.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    
                    if line_text.startswith('data: '):
                        data_str = line_text[6:]
                        
                        if data_str == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    # Control anti-bucle
                                    words = content.lower().split()
                                    for w in words:
                                        if len(w) > 4:
                                            word_count[w] = word_count.get(w, 0) + 1
                                            if word_count[w] > 8:
                                                full_response += "\n\n[Respuesta completada]"
                                                raise StopIteration
                                    
                                    full_response += content
                                    yield content
                                    
                        except StopIteration:
                            break
                        except json.JSONDecodeError:
                            continue
            
            st.session_state.messages.append({"role": "system", "content": full_response})
        else:
            error_msg = "Error al procesar la consulta."
            st.session_state.messages.append({"role": "system", "content": error_msg})
            yield error_msg
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        yield "Error procesando consulta."


def load_default_docs():
    """Carga automáticamente todos los documentos de la carpeta docs/"""
    api_key = st.session_state.get('openai_api_key') or os.getenv("OPENAI_API_KEY")
    if not api_key or "sk-" not in api_key:
        return
    
    docs_folder = "docs"
    
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder, exist_ok=True)
        st.info(f"📁 Carpeta '{docs_folder}' creada.")
        return
    
    # Verificar persistencia
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                existing_sources = metadata.get('sources', [])
                
                if existing_sources:
                    st.info(f"✅ Base ya inicializada con {len(existing_sources)} documentos")
                    return
        except:
            pass
    
    supported_extensions = ['*.pdf', '*.docx', '*.txt', '*.md']
    docs_to_load = []
    
    for extension in supported_extensions:
        docs_to_load.extend(glob.glob(os.path.join(docs_folder, extension)))
    
    if not docs_to_load:
        st.info("📚 No hay documentos en 'docs'.")
        return
    
    docs = []
    loaded_count = 0
    
    with st.spinner(f"📖 Cargando {len(docs_to_load)} documentos..."):
        for file_path in docs_to_load:
            file_name = os.path.basename(file_path)
            
            try:
                if file_path.endswith('.pdf'):
                    loader = PyMuPDFLoader(file_path)
                elif file_path.endswith('.docx'):
                    loader = Docx2txtLoader(file_path)
                elif file_path.endswith(('.txt', '.md')):
                    loader = TextLoader(file_path, encoding='utf-8')
                else:
                    continue
                
                file_docs = loader.load()
                docs.extend(file_docs)
                st.session_state.rag_sources.append(file_name)
                loaded_count += 1
                
            except Exception as e:
                st.error(f"❌ Error cargando {file_name}: {str(e)}")
    
    if docs:
        st.info(f"🔄 Procesando {loaded_count} documentos...")
        _split_and_load_docs(docs)
        save_metadata()


def load_doc_to_db():
    """Carga documentos adicionales subidos por el usuario"""
    if "rag_docs" in st.session_state and st.session_state.rag_docs:
        docs = []
        loaded_count = 0
        
        for doc_file in st.session_state.rag_docs:
            if doc_file.name not in st.session_state.rag_sources:
                if len(st.session_state.rag_sources) < DB_DOCS_LIMIT:
                    os.makedirs("temp_uploads", exist_ok=True)
                    file_path = f"./temp_uploads/{doc_file.name}"
                    
                    try:
                        with open(file_path, "wb") as file:
                            file.write(doc_file.read())

                        if doc_file.type == "application/pdf":
                            loader = PyMuPDFLoader(file_path)
                        elif doc_file.name.endswith(".docx"):
                            loader = Docx2txtLoader(file_path)
                        elif doc_file.type in ["text/plain", "text/markdown"]:
                            loader = TextLoader(file_path, encoding='utf-8')
                        else:
                            st.warning(f"⚠️ Tipo no soportado.")
                            continue

                        file_docs = loader.load()
                        docs.extend(file_docs)
                        st.session_state.rag_sources.append(doc_file.name)
                        loaded_count += 1

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                    
                    finally:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                else:
                    st.error(f"❌ Límite alcanzado ({DB_DOCS_LIMIT}).")
                    break

        if docs and loaded_count > 0:
            _split_and_load_docs(docs)
            save_metadata()
            st.success(f"✅ {loaded_count} documento(s) procesados")


def initialize_vector_db(docs, api_key):
    """Inicializa la base de datos vectorial con persistencia"""
    try:
        os.makedirs(PERSIST_DIR, exist_ok=True)
        
        embedding = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-small"
        )

        vector_db = Chroma.from_documents(
            documents=docs,
            embedding=embedding,
            persist_directory=PERSIST_DIR,
            collection_name="startup_docs"
        )
        
        return vector_db
    
    except Exception as e:
        st.error(f"❌ Error inicializando DB: {str(e)}")
        return None


def _split_and_load_docs(docs):
    """Divide documentos en chunks y los carga por lotes"""
    api_key = st.session_state.get('openai_api_key') or os.getenv("OPENAI_API_KEY")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
        separators=["\n\n", "\n", ". ", ".", " ", ""],
        length_function=len,
    )

    document_chunks = text_splitter.split_documents(docs)
    
    BATCH_SIZE = 100
    total_chunks = len(document_chunks)
    
    if "vector_db" not in st.session_state:
        first_batch = document_chunks[:BATCH_SIZE]
        st.session_state.vector_db = initialize_vector_db(first_batch, api_key)
        
        for i in range(BATCH_SIZE, total_chunks, BATCH_SIZE):
            batch = document_chunks[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (total_chunks // BATCH_SIZE) + 1
            
            try:
                with st.spinner(f"📦 Lote {batch_num}/{total_batches}..."):
                    st.session_state.vector_db.add_documents(batch)
            except Exception as e:
                st.error(f"❌ Error lote {batch_num}: {str(e)}")
                break
    else:
        for i in range(0, total_chunks, BATCH_SIZE):
            batch = document_chunks[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (total_chunks // BATCH_SIZE) + 1
            
            try:
                with st.spinner(f"📦 Agregando lote {batch_num}/{total_batches}..."):
                    st.session_state.vector_db.add_documents(batch)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                break
    
    st.success(f"✅ {total_chunks} chunks procesados")


def clear_persistent_db():
    """Limpia la base de datos vectorial persistente"""
    try:
        if os.path.exists(PERSIST_DIR):
            import shutil
            shutil.rmtree(PERSIST_DIR)
        st.session_state.rag_sources.clear()
        if "vector_db" in st.session_state:
            del st.session_state.vector_db
        st.success("✅ Base reiniciada")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def get_rag_stats():
    """Obtiene estadísticas de la base RAG"""
    if "vector_db" in st.session_state:
        try:
            collection = st.session_state.vector_db._collection
            count = collection.count()
            return {
                "documentos_cargados": len(st.session_state.rag_sources),
                "chunks_procesados": count,
                "estado": "✅ Activa"
            }
        except:
            return {
                "documentos_cargados": len(st.session_state.rag_sources),
                "chunks_procesados": "No disponible",
                "estado": "⚠️ Error"
            }
    else:
        return {
            "documentos_cargados": 0,
            "chunks_procesados": 0,
            "estado": "❌ No inicializada"
        }
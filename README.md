# 🚀 BStartupLab - Sistema Multi-Agente Inteligente

<div align="center">

![BStartupLab](https://img.shields.io/badge/BStartupLab-v1.0-blue?style=for-the-badge)
![ALIA-40b](https://img.shields.io/badge/ALIA--40b-BSC-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=for-the-badge&logo=streamlit)

**Asistente Virtual Multi-Agente para Banco Sabadell**

*Asesoramiento especializado en onboarding bancario, creación de empresas y trámites administrativos españoles*

[🎬 Demo](#demo) • [📖 Documentación](#características) • [🚀 Instalación](#instalación) • [🤖 Arquitectura](#arquitectura-multi-agente)

</div>

---

## 📋 Tabla de Contenidos

- [Sobre el Proyecto](#sobre-el-proyecto)
- [Características](#características)
- [Arquitectura Multi-Agente](#arquitectura-multi-agente)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías](#tecnologías)
- [Casos de Uso](#casos-de-uso)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

---

## 🎯 Sobre el Proyecto

**BStartupLab** es un sistema avanzado de agentes inteligentes desarrollado para el **Innovation Banking Hack Fest 2025** de Banco Sabadell. Utiliza el modelo **ALIA-40b** del Barcelona Supercomputing Center (BSC) para ofrecer asesoramiento personalizado en:

- 🏦 **Onboarding bancario completo**
- 🏢 **Creación y constitución de empresas** (SL, SA, Autónomo, Startup)
- 📋 **Trámites administrativos** cotidianos
- 📚 **Normativa legal y fiscal española**
- 💼 **Productos y servicios** de Banco Sabadell

### ✨ Características Destacadas

- **Sistema Multi-Agente**: 3 agentes especializados trabajando en paralelo
- **RAG Avanzado**: Búsqueda semántica con ChromaDB y OpenAI Embeddings
- **Multilingüe**: Español, Catalán, Euskera, Gallego y Valenciano
- **Streaming en Tiempo Real**: Respuestas progresivas para mejor UX
- **Base de Conocimientos Persistente**: ChromaDB con almacenamiento local
- **Interface Moderna**: Diseño responsive con modo oscuro/claro

---

## 🤖 Arquitectura Multi-Agente

BStartupLab utiliza una arquitectura de **4 agentes especializados** que trabajan en secuencia:

```
┌─────────────────┐
│  Usuario Query  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ 1️⃣ AGENTE DE REPHRASING    │
│ ─────────────────────────── │
│ • Reformula la consulta     │
│ • Extrae términos clave     │
│ • Añade contexto legal      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 2️⃣ SISTEMA RAG              │
│ ─────────────────────────── │
│ • Embeddings (OpenAI)       │
│ • ChromaDB (búsqueda)       │
│ • Recupera 15 documentos    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 3️⃣ AGENTE DE RERANKING      │
│ ─────────────────────────── │
│ • Evalúa relevancia (0-10)  │
│ • Selecciona top 5-8 docs   │
│ • Elimina información noise │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 4️⃣ AGENTE PRINCIPAL (ALIA)  │
│ ─────────────────────────── │
│ • Genera respuesta final    │
│ • Streaming en tiempo real  │
│ • Multilingüe (ES/CA/EU/GL) │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────┐
│  Respuesta UI   │
└─────────────────┘
```

---

## 📦 Requisitos

### Requisitos del Sistema

- **Python**: 3.10 o superior
- **Sistema Operativo**: Linux, macOS, Windows
- **RAM**: Mínimo 4GB (recomendado 8GB)
- **Disco**: 2GB libres (para ChromaDB y documentos)

### API Keys Necesarias

- **OpenAI API Key**: Para generar embeddings (`text-embedding-3-small`)
  - Obtén tu API Key en: https://platform.openai.com/api-keys
- **ALIA API Key**: Incluida en el código (API pública del BSC)

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/bstartuplab.git
cd bstartuplab
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Edita `.env` y añade tu API Key de OpenAI:

```env
OPENAI_API_KEY=sk-tu-api-key-aqui
```

### 5. Preparar Documentos (Opcional)

Coloca tus documentos legales/bancarios en la carpeta `docs/`:

```bash
mkdir -p docs
# Copia tus PDFs, DOCX, TXT, MD a docs/
```

Los formatos soportados son: `.pdf`, `.docx`, `.txt`, `.md`

---

## ⚙️ Configuración

### Estructura de Carpetas

```
bstartuplab/
├── app.py                 # Aplicación principal Streamlit
├── utils.py              # Funciones RAG y agentes
├── requirements.txt      # Dependencias Python
├── .env                  # Variables de entorno (no commitear)
├── .env.example         # Plantilla de variables
├── docs/                # Documentos para RAG (auto-cargados)
│   ├── documento1.pdf
│   ├── documento2.docx
│   └── guia.md
├── chroma_db/           # Base de datos vectorial (generada automáticamente)
├── images/              # Recursos visuales
│   └── logo.png
└── README.md
```

### Configuración de ChromaDB

ChromaDB se configura automáticamente al iniciar la aplicación:
- **Directorio**: `./chroma_db`
- **Colección**: `startup_docs`
- **Modelo de Embeddings**: `text-embedding-3-small` (OpenAI)
- **Persistencia**: Sí (los datos se guardan entre sesiones)

---

## 🎮 Uso

### Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Navegación

La aplicación tiene 3 secciones principales:

#### 🏠 **Inicio**
- Presentación del proyecto
- Características principales
- Casos de uso
- Sistema multi-agente

#### ⚙️ **Funcionamiento**
- Arquitectura detallada
- Explicación de cada agente
- Tecnologías utilizadas
- Seguridad y privacidad

#### 🎬 **Demo & Chat**
- Chat interactivo en tiempo real
- Selector de idioma (ES, CA, EU, GL, VA)
- Carga de documentos personalizados
- Gestión de base de conocimientos
- Estadísticas del chat

### Funcionalidades del Chat

1. **Consultas Generales**: Pregunta sobre trámites, documentación, normativas
2. **Onboarding**: Guía paso a paso para apertura de cuentas
3. **Creación de Empresas**: Asesoramiento en SL, SA, Autónomo
4. **Multilingüe**: Cambia el idioma de respuesta en cualquier momento
5. **Cargar Documentos**: Sube PDFs, DOCX, TXT para ampliar la base de conocimientos

### Ejemplos de Consultas

```
💬 "¿Qué necesito para abrir una cuenta en Banco Sabadell?"

💬 "Quiero crear una SL, ¿cuáles son los pasos y costes?"

💬 "¿Qué documentación necesito para solicitar un préstamo ICO?"

💬 "Diferencias entre autónomo y sociedad limitada"

💬 "¿Cómo domiciliar una nómina en Banco Sabadell?"
```

---

## 🗂️ Estructura del Proyecto

```
bstartuplab/
│
├── 📄 app.py                      # Aplicación Streamlit principal
│   ├── initialize_session_state() # Estado de la aplicación
│   ├── apply_custom_css()         # Estilos personalizados
│   ├── render_sidebar()           # Navegación lateral
│   ├── page_home()               # Página de inicio
│   ├── page_how_it_works()       # Página de funcionamiento
│   ├── page_demo()               # Página de demo y chat
│   └── render_footer()           # Footer de la aplicación
│
├── 🛠️ utils.py                    # Funciones RAG y agentes
│   ├── call_alia()               # Llamadas al modelo ALIA
│   ├── rephrase_query()          # Agente de rephrasing
│   ├── rerank_documents()        # Agente de reranking
│   ├── stream_llm_rag_response() # Stream de respuestas
│   ├── load_persistent_vector_db() # Carga ChromaDB
│   ├── load_default_docs()       # Carga docs/ automáticamente
│   ├── load_doc_to_db()          # Procesa docs subidos
│   └── initialize_vector_db()    # Inicializa ChromaDB
│
├── 📋 requirements.txt            # Dependencias del proyecto
├── 🔐 .env                        # Variables de entorno (gitignored)
├── 📝 .env.example               # Plantilla de variables
├── 📚 docs/                      # Documentos para RAG
├── 💾 chroma_db/                 # Base de datos vectorial
├── 🖼️ images/                    # Recursos visuales
└── 📖 README.md                  # Este archivo
```

---

## 🔧 Tecnologías

### Core Technologies

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.10+ | Lenguaje principal |
| **Streamlit** | 1.32+ | Framework web interactivo |
| **LangChain** | 0.1.0+ | Orquestación de agentes |
| **ChromaDB** | 0.4.24+ | Base de datos vectorial |
| **OpenAI** | 1.12+ | Embeddings semánticos |
| **ALIA-40b** | BSC-LT | Modelo de lenguaje principal |

### Librerías Principales

```python
streamlit>=1.32.0          # UI framework
langchain>=0.1.0           # RAG orchestration
langchain-community>=0.0.20
langchain-openai>=0.0.5
chromadb>=0.4.24           # Vector database
openai>=1.12.0             # Embeddings
python-dotenv>=1.0.0       # Environment variables
requests>=2.31.0           # HTTP requests
Pillow>=10.0.0            # Image processing
pysqlite3-binary>=0.5.0   # SQLite for ChromaDB
```

### Procesamiento de Documentos

```python
pypdf>=4.0.0              # PDFs
PyMuPDF>=1.23.0           # PDFs avanzados
docx2txt>=0.8             # Word documents
```

---

## 💼 Casos de Uso

### 1️⃣ Emprendedores y Startups

**Escenario**: Crear una Sociedad Limitada (SL)

```
Usuario: "Quiero crear una SL, ¿cuáles son los pasos?"

BStartupLab:
📋 CREACIÓN DE SOCIEDAD LIMITADA (SL)

**Requisitos iniciales:**
- Capital mínimo: 3.000€
- Mínimo 1 socio
- Denominación social disponible

**Pasos:**
1. Certificado negativo de denominación (Registro Mercantil)
   → Coste: 13,52€ | Plazo: 24-48h

2. Apertura cuenta bancaria y depósito capital
   → Banco Sabadell: Cuenta empresa con 0€ comisiones primer año
   
3. Redacción de estatutos sociales
   → Notario: 150-300€

4. Escritura pública de constitución
   → Notario: 300-600€

...
```

### 2️⃣ Particulares

**Escenario**: Apertura de cuenta

```
Usuario: "¿Qué necesito para abrir una cuenta?"

BStartupLab:
🏦 APERTURA DE CUENTA - BANCO SABADELL

**Documentación necesaria:**
- DNI/NIE en vigor
- Justificante de ingresos (nómina, pensión)
- Certificado de empadronamiento (menos de 3 meses)

**Proceso:**
1. Online: App Banco Sabadell (15 min)
2. Presencial: Oficina más cercana
3. Videollamada: Identificación remota

**Productos disponibles:**
- Cuenta Expansión: 0€ comisiones
- Cuenta Nómina: Bonificaciones por domiciliación
...
```

### 3️⃣ Empresas

**Escenario**: Financiación ICO

```
Usuario: "¿Qué líneas ICO tiene Banco Sabadell?"

BStartupLab:
💰 LÍNEAS ICO - BANCO SABADELL 2025

**ICO Empresas y Emprendedores:**
- Importe: hasta 12,5 millones €
- Plazo: hasta 20 años
- Carencia: hasta 2 años
- TIN: desde 3,25%

**Requisitos:**
- Autónomo o PYME
- Plan de negocio viable
- Garantías adecuadas
...
```

---

## 🔒 Seguridad y Privacidad

### Datos Locales
- ✅ **ChromaDB local**: Los embeddings se almacenan en tu máquina
- ✅ **Sin telemetría**: No se envían datos de uso a terceros
- ✅ **Sesiones aisladas**: Cada usuario tiene su propia sesión

### API Keys
- 🔐 **Encriptadas en .env**: Nunca se commitean al repositorio
- 🔐 **HTTPS**: Todas las comunicaciones encriptadas
- 🔐 **Rate limiting**: Protección contra uso abusivo

### Cumplimiento
- ✅ **GDPR**: Cumplimiento normativa europea
- ✅ **Sin almacenamiento persistente**: Las conversaciones no se guardan
- ✅ **Anonimización**: No se recopilan datos personales

---

## 🚀 Despliegue

### Despliegue Local

```bash
streamlit run app.py --server.port 8501
```

### Despliegue en Streamlit Cloud

1. Sube el proyecto a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. Añade `OPENAI_API_KEY` en Secrets:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-tu-api-key"
```

5. Despliega automáticamente

### Despliegue con Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

```bash
docker build -t bstartuplab .
docker run -p 8501:8501 bstartuplab
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Para contribuir:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Add nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto fue desarrollado para el **Innovation Banking Hack Fest 2025** (#IBHF25) de Banco Sabadell.

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

---

## 👥 Autores

**BStartupLab Team** - Innovation Banking Hack Fest 2025

- 🏦 Banco Sabadell
- 🤖 Barcelona Supercomputing Center (ALIA-40b)
- ⚡ Powered by LangChain & Streamlit

---

## 📞 Contacto

- 🌐 **Web**: [Banco Sabadell](https://www.bancsabadell.com)
- 📧 **Email**: hackfest@bancsabadell.com
- 🐦 **Twitter**: [@BancoSabadell](https://twitter.com/bancosabadell)
- 💼 **LinkedIn**: [Banco Sabadell](https://www.linkedin.com/company/banco-sabadell)

---

## 🙏 Agradecimientos

- **Barcelona Supercomputing Center (BSC)** por el modelo ALIA-40b
- **Banco Sabadell** por organizar el Innovation Banking Hack Fest
- **OpenAI** por los embeddings de alta calidad
- **Streamlit** por el framework de desarrollo rápido
- **LangChain** por la orquestación de agentes

---

<div align="center">

**[⬆ Volver arriba](#-bstartuplab---sistema-multi-agente-inteligente)**

Made with ❤️ for Innovation Banking Hack Fest 2025

🚀 **BStartupLab** | 🤖 **ALIA-40b** | 🏦 **Banco Sabadell**

</div>
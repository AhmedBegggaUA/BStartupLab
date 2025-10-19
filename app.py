import streamlit as st
import os
import dotenv
import uuid
from pathlib import Path
from PIL import Image
import io
import base64

from utils import (
    stream_llm_rag_response,
    load_doc_to_db, 
    load_persistent_vector_db,
    load_default_docs
)

__import__('pysqlite3')
import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules["pysqlite3"]

dotenv.load_dotenv()

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="BStartupLab - Banco Sabadell",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ESTADO DE LA APLICACIÓN ====================
def initialize_session_state():
    """Inicializa el estado de la sesión"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "rag_sources" not in st.session_state:
        st.session_state.rag_sources = []
    
    if "language" not in st.session_state:
        st.session_state.language = "es"
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": """¡Bienvenido a BStartupLab! 🚀

Soy tu asistente inteligente multi-agente especializado en ayudarte con tu onboarding en Banco Sabadell y acompañarte en todos tus trámites cotidianos.

**🤖 Sistema Multi-Agente:**
- **Agente de Rephrasing:** Optimiza tus consultas para búsquedas más precisas
- **Agente de Reranking:** Selecciona los documentos más relevantes
- **Agente Principal (ALIA):** Responde con información actualizada y precisa

**💼 ¿En qué puedo ayudarte?**
- Onboarding completo en Banco Sabadell
- Apertura de cuentas y productos bancarios
- Trámites administrativos cotidianos
- Normativa y documentación legal española
- Asesoramiento en creación de negocios

¿Qué necesitas saber?"""
        }]
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Inicio"

# ==================== UTILIDADES ====================
def load_logo():
    """Carga el logo de la aplicación"""
    logo_path = Path("./images/logo.png")
    if logo_path.exists():
        return Image.open(logo_path)
    return None

def get_logo_base64():
    """Obtiene el logo en formato base64"""
    logo = load_logo()
    if logo:
        buffered = io.BytesIO()
        logo.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    return None

# ==================== ESTILOS CSS ====================
def apply_custom_css():
    """Aplica los estilos CSS personalizados"""
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        :root {{
            --bg-primary: {'#0f172a' if st.session_state.dark_mode else '#ffffff'};
            --bg-secondary: {'#1e293b' if st.session_state.dark_mode else '#f8fafc'};
            --bg-card: {'#1e293b' if st.session_state.dark_mode else '#ffffff'};
            --bg-gradient-start: {'#004B87' if st.session_state.dark_mode else '#004B87'};
            --bg-gradient-end: {'#1B73B7' if st.session_state.dark_mode else '#1B73B7'};
            
            --text-primary: {'#f1f5f9' if st.session_state.dark_mode else '#0f172a'};
            --text-secondary: {'#cbd5e1' if st.session_state.dark_mode else '#475569'};
            --text-tertiary: {'#94a3b8' if st.session_state.dark_mode else '#64748b'};
            
            --border-color: {'#334155' if st.session_state.dark_mode else '#e2e8f0'};
            --shadow-color: {'rgba(0, 0, 0, 0.5)' if st.session_state.dark_mode else 'rgba(0, 0, 0, 0.1)'};
            
            --accent-color: #1B73B7;
            --success-color: #10b981;
        }}
        
        * {{
            font-family: 'Inter', sans-serif;
        }}
        
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        .stApp {{
            background: {'linear-gradient(135deg, #004B87 0%, #1B73B7 100%)' if st.session_state.dark_mode else 'linear-gradient(135deg, #e0e7ff 0%, #dbeafe 100%)'};
            transition: background 0.5s ease;
        }}
        
        .main-container {{
            background: var(--bg-card);
            border-radius: 24px;
            padding: 2rem;
            margin: 1rem auto;
            max-width: 1200px;
            box-shadow: 0 20px 60px var(--shadow-color);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            animation: fadeInUp 0.6s ease-out;
        }}
        
        .header-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 2rem;
            gap: 1.5rem;
            flex-wrap: wrap;
            animation: fadeIn 0.8s ease-out;
        }}
        
        .logo-container {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: {'rgba(255, 255, 255, 0.1)' if st.session_state.dark_mode else '#ffffff'};
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 30px var(--shadow-color);
            flex-shrink: 0;
            transition: transform 0.3s ease;
        }}
        
        .logo-container:hover {{
            transform: scale(1.05) rotate(5deg);
        }}
        
        .logo-emoji {{
            font-size: 3.5rem;
        }}
        
        .main-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -1px;
            text-align: center;
            color: var(--text-primary) !important;
        }}
        
        .subtitle {{
            font-size: 1.1rem;
            color: var(--text-secondary);
            font-weight: 400;
            margin-top: 0.5rem;
            text-align: center;
        }}
        
        .feature-card {{
            background: var(--bg-secondary);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 2px solid var(--border-color);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            animation: slideIn 0.5s ease-out;
        }}
        
        .feature-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
        }}
        
        .feature-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px var(--shadow-color);
            border-color: var(--accent-color);
        }}
        
        .feature-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}
        
        .feature-icon {{
            font-size: 1.8rem;
            flex-shrink: 0;
            animation: bounce 2s infinite;
        }}
        
        .feature-text {{
            color: var(--text-secondary);
            font-size: 1rem;
            line-height: 1.7;
        }}
        
        .feature-text p {{
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
        }}
        
        .feature-text ul {{
            color: var(--text-secondary);
        }}
        
        .feature-text li {{
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}
        
        .section-badge {{
            display: inline-block;
            background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 1rem;
            box-shadow: 0 4px 10px var(--shadow-color);
            animation: slideInLeft 0.5s ease-out;
        }}
        
        .process-step {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 1.5rem;
            position: relative;
            animation: slideInRight 0.6s ease-out;
        }}
        
        .step-number {{
            width: 45px;
            height: 45px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.2rem;
            box-shadow: 0 4px 15px var(--shadow-color);
            flex-shrink: 0;
        }}
        
        .step-content {{
            margin-left: 1rem;
            flex: 1;
        }}
        
        .step-title {{
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }}
        
        .step-description {{
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 0.95rem;
        }}
        
        .tech-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }}
        
        .tech-card {{
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px var(--shadow-color);
            transition: all 0.3s ease;
            animation: fadeInScale 0.6s ease-out;
        }}
        
        .tech-card:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 25px var(--shadow-color);
            border-color: var(--accent-color);
        }}
        
        .tech-icon {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        
        .tech-name {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }}
        
        .tech-description {{
            color: var(--text-secondary);
            line-height: 1.5;
            font-size: 0.9rem;
        }}
        
        /* CHAT STYLES */
        .stChatMessage {{
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }}
        
        .stChatMessage [data-testid="stMarkdownContainer"] {{
            color: var(--text-primary) !important;
        }}
        
        .stChatInputContainer {{
            border-top: 2px solid var(--border-color) !important;
            background: var(--bg-card) !important;
            padding: 1rem !important;
        }}
        
        /* SIDEBAR */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
        }}
        
        section[data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            color: white !important;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px var(--shadow-color);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 25px var(--shadow-color);
        }}
        
        button[kind="header"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            color: var(--text-primary) !important;
            background: var(--bg-card) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
            margin: 0.5rem !important;
            box-shadow: 0 2px 8px var(--shadow-color) !important;
            transition: all 0.3s ease !important;
        }}
        
        button[kind="header"]:hover {{
            background: var(--accent-color) !important;
            color: white !important;
            transform: scale(1.05) !important;
        }}
        
        .doc-counter {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            display: inline-block;
            margin: 0.2rem;
            backdrop-filter: blur(10px);
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes fadeInScale {{
            from {{ opacity: 0; transform: scale(0.9); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(-20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        @keyframes slideInLeft {{
            from {{ opacity: 0; transform: translateX(-30px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        @keyframes slideInRight {{
            from {{ opacity: 0; transform: translateX(30px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-5px); }}
        }}
        
        @media (max-width: 768px) {{
            .main-container {{ padding: 1rem; margin: 0.25rem; }}
            .main-title {{ font-size: 1.75rem; }}
            .subtitle {{ font-size: 0.95rem; }}
        }}
    </style>
    """, unsafe_allow_html=True)

# ==================== COMPONENTES ====================
def render_header(title, subtitle=None):
    """Renderiza el header con logo y título"""
    logo_base64 = get_logo_base64()
    
    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="BStartupLab Logo" style="width: 80px; height: 80px; object-fit: contain;">'
    else:
        logo_html = '<div class="logo-emoji">🚀</div>'
    
    subtitle_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else '<p></p>'
    
    st.markdown(f"""
    <div class="header-container">
        <div class="logo-container">
            {logo_html}
        </div>
        <div>
            <h1 class="main-title">{title}</h1>
            {subtitle_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderiza el sidebar con navegación"""
    with st.sidebar:
        logo_base64 = get_logo_base64()
        
        if logo_base64:
            logo_display = f'<img src="data:image/png;base64,{logo_base64}" style="width: 60px; height: 60px; object-fit: contain;">'
        else:
            logo_display = '<div style="font-size: 2.5rem;">🚀</div>'
        
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem 0 1rem;'>
            <div style='background: rgba(255, 255, 255, 0.2); border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
                {logo_display}
            </div>
            <h2 style='color: white; margin: 0; font-size: 1.5rem;'>BStartupLab</h2>
            <p style='color: rgba(255,255,255,0.8); font-size: 0.85rem; margin-top: 0.5rem;'>Sistema Multi-Agente Inteligente</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navegación
        if st.button("🏠 Inicio", key="nav_home", use_container_width=True, 
                     type="primary" if st.session_state.current_page == "🏠 Inicio" else "secondary"):
            st.session_state.current_page = "🏠 Inicio"
            st.rerun()
        
        if st.button("⚙️ Funcionamiento", key="nav_how", use_container_width=True,
                     type="primary" if st.session_state.current_page == "⚙️ Funcionamiento" else "secondary"):
            st.session_state.current_page = "⚙️ Funcionamiento"
            st.rerun()
        
        if st.button("🎬 Demo & Chat", key="nav_demo", use_container_width=True,
                     type="primary" if st.session_state.current_page == "🎬 Demo & Chat" else "secondary"):
            st.session_state.current_page = "🎬 Demo & Chat"
            st.rerun()
        
        st.markdown("---")
        
        # Idioma
        st.markdown("### 🌐 Idioma")
        language_options = {
            "Español": "es",
            "Català": "ca",
            "Euskara": "eu",
            "Galego": "gl",
            "Valencià": "va"
        }
        
        selected_lang = st.selectbox(
            "Selecciona idioma",
            options=list(language_options.keys()),
            index=0,
            label_visibility="collapsed"
        )
        st.session_state.language = language_options[selected_lang]
        
        st.markdown("---")
        
        # Toggle modo
        mode_icon = "🌙 Modo Oscuro" if st.session_state.dark_mode else "☀️ Modo Claro"
        if st.button(mode_icon, key="theme_toggle", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Info proyecto
        st.markdown("""
        <div style='color: rgba(255,255,255,0.9); font-size: 0.8rem; text-align: center; padding: 0 0.5rem;'>
            <p style='margin-bottom: 0.5rem;'><strong>Innovation Banking Hack Fest 2025</strong></p>
            <p style='margin: 0;'>#IBHF25</p>
            <p style='margin-top: 0.5rem; opacity: 0.8;'>🤖 Powered by ALIA-40b</p>
        </div>
        """, unsafe_allow_html=True)
        
        return st.session_state.current_page

# ==================== PÁGINAS ====================
def page_home():
    """Página de Inicio"""
    st.markdown('<div class="main-container fade-in">', unsafe_allow_html=True)
    
    render_header("BStartupLab", "Tu asistente inteligente multi-agente para Banco Sabadell")
    
    st.markdown('<span class="section-badge">💡 NUESTRA MISIÓN</span>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">
            <span class="feature-icon">🎯</span>
            <span>¿Qué es BStartupLab?</span>
        </div>
        <div class="feature-text">
            <p>BStartupLab es un sistema avanzado de <strong>agentes inteligentes especializados</strong> que revoluciona tu experiencia con Banco Sabadell.</p>
            <p>Utilizando tecnología ALIA-40b del Barcelona Supercomputing Center, te acompañamos desde el onboarding inicial hasta tus trámites bancarios cotidianos, optimizando cada consulta mediante un sistema multi-agente de última generación.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <span class="feature-icon">🤖</span>
                <span>Multi-Agente</span>
            </div>
            <div class="feature-text">
                <p><strong>3 agentes especializados</strong> trabajando en paralelo:</p>
                <ul style='margin-left: 1.5rem; font-size: 0.9rem;'>
                    <li>Rephrasing: Optimiza consultas</li>
                    <li>Reranking: Filtra información</li>
                    <li>ALIA: Responde con precisión</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <span class="feature-icon">🎓</span>
                <span>Onboarding</span>
            </div>
            <div class="feature-text">
                <p><strong>Proceso guiado completo:</strong></p>
                <ul style='margin-left: 1.5rem; font-size: 0.9rem;'>
                    <li>Apertura de cuentas</li>
                    <li>Productos bancarios</li>
                    <li>Documentación necesaria</li>
                    <li>Configuración inicial</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <span class="feature-icon">📋</span>
                <span>Trámites</span>
            </div>
            <div class="feature-text">
                <p><strong>Asistencia cotidiana:</strong></p>
                <ul style='margin-left: 1.5rem; font-size: 0.9rem;'>
                    <li>Transferencias</li>
                    <li>Consultas de saldo</li>
                    <li>Domiciliaciones</li>
                    <li>Gestión de tarjetas</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<br><span class="section-badge">🚀 CASOS DE USO</span>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">
            <span class="feature-icon">🏢</span>
            <span>Emprendedores y Startups</span>
        </div>
        <div class="feature-text">
            <ul style='margin-left: 1.5rem;'>
                <li>Creación de negocios: SL, SA, Autónomo, Startup</li>
                <li>Trámites legales: Registro Mercantil, Notaría, Hacienda</li>
                <li>Financiación: Créditos ICO, garantías, microcréditos</li>
                <li>Asesoramiento normativo continuo</li>
            </ul>
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-title">
            <span class="feature-icon">👤</span>
            <span>Particulares</span>
        </div>
        <div class="feature-text">
            <ul style='margin-left: 1.5rem;'>
                <li>Apertura de cuenta: Documentación, requisitos, proceso</li>
                <li>Productos de ahorro: Depósitos, fondos, planes de pensiones</li>
                <li>Hipotecas y préstamos personales</li>
                <li>Servicios digitales y banca móvil</li>
            </ul>
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-title">
            <span class="feature-icon">🏦</span>
            <span>Empresas</span>
        </div>
        <div class="feature-text">
            <ul style='margin-left: 1.5rem;'>
                <li>Cuenta empresa: Configuración y gestión</li>
                <li>Productos corporativos: Confirming, factoring, leasing</li>
                <li>Comercio internacional: Cartas de crédito, cobros</li>
                <li>Asesoramiento financiero especializado</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def page_how_it_works():
    """Página de Funcionamiento"""
    st.markdown('<div class="main-container fade-in">', unsafe_allow_html=True)
    render_header("¿Cómo Funciona?")
    
    st.markdown('<span class="section-badge">🤖 ARQUITECTURA MULTI-AGENTE</span>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">
            <span class="feature-icon">🧠</span>
            <span>Sistema de 3 Agentes Especializados</span>
        </div>
        <div class="feature-text">
            <p>BStartupLab utiliza una arquitectura avanzada donde <strong>múltiples agentes trabajan en colaboración</strong> para ofrecerte las respuestas más precisas y relevantes:</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Agente 1: Rephrasing
    st.markdown("""
    <div class="process-step">
        <div class="step-number">1</div>
        <div class="step-content">
            <div class="step-title">🔄 Agente de Rephrasing</div>
            <div class="step-description">
                <strong>Optimiza tu consulta para búsquedas más efectivas</strong><br><br>
                Este agente analiza tu pregunta y la reformula utilizando terminología legal y bancaria española. 
                Extrae términos clave, añade sinónimos relevantes y contexto del historial de conversación 
                para maximizar la precisión en la búsqueda de documentos.
                <br><br>
                <em>Ejemplo:</em> "¿Cómo abro una empresa?" → "Constitución sociedad limitada SL requisitos documentación registro mercantil trámites creación empresa España"
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Agente 2: RAG + Búsqueda
    st.markdown("""
    <div class="process-step">
        <div class="step-number">2</div>
        <div class="step-content">
            <div class="step-title">📚 Sistema RAG (Retrieval Augmented Generation)</div>
            <div class="step-description">
                <strong>Búsqueda semántica en base de conocimientos</strong><br><br>
                Utilizando embeddings de OpenAI (text-embedding-3-small), el sistema busca en la base de datos 
                vectorial persistente (ChromaDB) los 15 documentos más relevantes. La búsqueda es semántica, 
                no por palabras clave, lo que permite encontrar información relacionada incluso si no usa exactamente tus términos.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Agente 3: Reranking
    st.markdown("""
    <div class="process-step">
        <div class="step-number">3</div>
        <div class="step-content">
            <div class="step-title">⚖️ Agente de Reranking</div>
            <div class="step-description">
                <strong>Selecciona los documentos más relevantes</strong><br><br>
                De los 15 documentos recuperados, este agente usa ALIA para evaluar la relevancia de cada uno 
                específicamente para tu pregunta. Asigna una puntuación de 0-10 a cada documento y selecciona 
                los 8 mejores, eliminando información irrelevante y reduciendo "ruido" en la respuesta.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Agente 4: ALIA Principal
    st.markdown("""
    <div class="process-step">
        <div class="step-number">4</div>
        <div class="step-content">
            <div class="step-title">🚀 Agente Principal (ALIA-40b)</div>
            <div class="step-description">
                <strong>Genera la respuesta final personalizada</strong><br><br>
                Con el contexto de los documentos rerankeados y tu historial de conversación, ALIA genera 
                una respuesta en streaming en el idioma seleccionado (español, catalán, euskera, gallego o valenciano). 
                Combina información de múltiples fuentes, mantiene coherencia con el contexto previo y 
                proporciona respuestas concisas y accionables.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<br><span class="section-badge">🧩 TECNOLOGÍAS CORE</span>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-icon">🤖</div>
            <div class="tech-name">ALIA-40b</div>
            <div class="tech-description">
                LLM del Barcelona Supercomputing Center, optimizado para español y lenguas cooficiales
            </div>
        </div>

        <div class="tech-card">
            <div class="tech-icon">💾</div>
            <div class="tech-name">ChromaDB</div>
            <div class="tech-description">
                Base de datos vectorial persistente para almacenamiento y búsqueda eficiente
            </div>
        </div>

        <div class="tech-card">
            <div class="tech-icon">⚡</div>
            <div class="tech-name">Streamlit</div>
            <div class="tech-description">
                Interface web interactiva con streaming en tiempo real
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-icon">🔍</div>
            <div class="tech-name">OpenAI Embeddings</div>
            <div class="tech-description">
                text-embedding-3-small para vectorización semántica de documentos
            </div>
        </div>

        <div class="tech-card">
            <div class="tech-icon">🔗</div>
            <div class="tech-name">LangChain</div>
            <div class="tech-description">
                Framework para orquestación de agentes y procesamiento de documentos
            </div>
        </div>

        <div class="tech-card">
            <div class="tech-icon">🇪🇸</div>
            <div class="tech-name">Multilingüe</div>
            <div class="tech-description">
                Soporte nativo para ES, CA, EU, GL, VA
            </div>
        </div>
        """, unsafe_allow_html=True)

    
    st.markdown('<br><span class="section-badge">🛡️ SEGURIDAD & PRIVACIDAD</span>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <span class="feature-icon">🔐</span>
                <span>Datos Encriptados</span>
            </div>
            <div class="feature-text">
                <ul style='margin-left: 1.5rem; font-size: 0.9rem;'>
                    <li>Embeddings almacenados localmente</li>
                    <li>Sin envío de datos sensibles a terceros</li>
                    <li>Sesiones aisladas por usuario</li>
                    <li>Cumplimiento GDPR</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <span class="feature-icon">🔒</span>
                <span>API Segura</span>
            </div>
            <div class="feature-text">
                <ul style='margin-left: 1.5rem; font-size: 0.9rem;'>
                    <li>Conexiones HTTPS</li>
                    <li>API Keys encriptadas</li>
                    <li>Rate limiting implementado</li>
                    <li>Auditoría de consultas</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def page_demo():
    """Página de Demo con chat integrado - VERSIÓN COMPLETA"""
    st.markdown('<div class="main-container fade-in">', unsafe_allow_html=True)
    
    render_header("Demo & Chat Inteligente", "Prueba el sistema multi-agente en tiempo real")
    
    # Verificar API Key de OpenAI
    default_openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_api_key = st.session_state.get('openai_api_key', default_openai_api_key)
    
    # Panel de configuración compacto
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<span class="section-badge">🌐 Configuración del Chat</span>', unsafe_allow_html=True)
    
    with col2:
        # Selector de idioma compacto
        language_options = {
            "🇪🇸 ES": "es",
            "🇪🇸 CA": "ca",
            "🇪🇸 EU": "eu",
            "🇪🇸 GL": "gl",
            "🇪🇸 VA": "va"
        }
        
        current_lang_key = [k for k, v in language_options.items() if v == st.session_state.language][0]
        selected_lang = st.selectbox(
            "Idioma",
            options=list(language_options.keys()),
            index=list(language_options.keys()).index(current_lang_key),
            label_visibility="collapsed"
        )
        st.session_state.language = language_options[selected_lang]
    
    # Gestión de documentos
    with st.expander("📄 Gestión de Documentos", expanded=False):
        col_doc1, col_doc2 = st.columns([1, 1])
        
        with col_doc1:
            st.markdown("#### 📚 Base de Conocimientos")
            if st.session_state.rag_sources:
                st.success(f"✅ {len(st.session_state.rag_sources)} documentos cargados")
                for i, source in enumerate(st.session_state.rag_sources[:5]):
                    source_name = source.split('/')[-1] if '/' in source else source
                    if len(source_name) > 35:
                        source_name = source_name[:32] + "..."
                    st.markdown(f'<span class="doc-counter">{i+1}. {source_name}</span>', unsafe_allow_html=True)
                
                if len(st.session_state.rag_sources) > 5:
                    st.info(f"... y {len(st.session_state.rag_sources) - 5} documentos más")
            else:
                st.info("📁 No hay documentos adicionales cargados")
        
        with col_doc2:
            st.markdown("#### 📥 Cargar Nuevos Documentos")
            uploaded_files = st.file_uploader(
                "Sube documentos (PDF, DOCX, TXT, MD)",
                type=['pdf', 'docx', 'txt', 'md'],
                accept_multiple_files=True,
                help="Arrastra archivos o haz clic para seleccionar"
            )
            
            if uploaded_files:
                st.session_state.rag_docs = uploaded_files
                if st.button("📥 Procesar Documentos", type="primary", use_container_width=True):
                    with st.spinner("🔄 Procesando documentos..."):
                        load_doc_to_db()
                    st.success("✅ Documentos procesados correctamente")
                    st.rerun()
    
    # Verificar si falta API Key
    missing_openai = not openai_api_key or "sk-" not in openai_api_key
    
    if missing_openai:
        st.markdown("""
        <div class="feature-card" style="background: #fff3cd; border-left-color: #ffc107;">
            <div class="feature-title">
                <span class="feature-icon">⚠️</span>
                <span>API Key de OpenAI Requerida</span>
            </div>
            <div class="feature-text">
                <p>Para usar la funcionalidad RAG con documentos, necesitas configurar tu API Key de OpenAI.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulario de API Key
        with st.form("api_key_form"):
            api_key_input = st.text_input(
                "Introduce tu OpenAI API Key",
                type="password",
                placeholder="sk-...",
                help="Solo se usa para generar embeddings de documentos"
            )
            
            submit_key = st.form_submit_button("💾 Guardar API Key", type="primary")
            
            if submit_key and api_key_input and "sk-" in api_key_input:
                st.session_state.openai_api_key = api_key_input
                st.success("✅ API Key guardada correctamente")
                st.rerun()
    else:
        # Inicializar base de datos vectorial
        st.session_state.openai_api_key = openai_api_key
        
        if "vector_db" not in st.session_state:
            with st.spinner("🔄 Inicializando base de conocimientos..."):
                vector_db, rag_sources = load_persistent_vector_db(openai_api_key)
                if vector_db:
                    st.session_state.vector_db = vector_db
                    st.session_state.rag_sources = rag_sources
                
                # Cargar documentos por defecto
                load_default_docs()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Controles de chat
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("🔄 Nuevo Chat", type="primary", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "¡Hola de nuevo! 🚀 ¿En qué puedo ayudarte hoy?"
            }]
            st.rerun()
    
    with col2:
        if st.button("📊 Estadísticas", type="secondary", use_container_width=True):
            total_msgs = len(st.session_state.messages)
            total_docs = len(st.session_state.rag_sources)
            st.toast(f"💬 {total_msgs} mensajes | 📚 {total_docs} documentos", icon="📊")
    
    with col3:
        st.markdown(f"**🌐 {st.session_state.language.upper()}**")
    
    st.markdown('<br><span class="section-badge">💬 Chat con BStartupLab</span>', unsafe_allow_html=True)
    
    # Área de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("💬 Escribe tu consulta sobre Banco Sabadell..."):
        # Añadir mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Respuesta del asistente
        with st.chat_message("assistant"):
            with st.spinner("🤔 Procesando con sistema multi-agente..."):
                # Convertir mensajes al formato esperado
                messages = []
                for m in st.session_state.messages:
                    msg_obj = type('Message', (), {
                        'type': m["role"],
                        'content': m["content"]
                    })()
                    messages.append(msg_obj)
                
                # Stream de respuesta
                st.write_stream(stream_llm_rag_response(messages, st.session_state.language))
    
    # Información adicional
    with st.expander("ℹ️ Información sobre el Sistema Multi-Agente", expanded=False):
        st.markdown("""
        **🤖 Arquitectura de 3 Agentes:**
        
        1. **Agente de Rephrasing:** Reformula tu consulta usando terminología bancaria y legal española
        2. **Sistema RAG:** Busca en la base de conocimientos los documentos más relevantes (15 documentos)
        3. **Agente de Reranking:** Evalúa y selecciona los 5-8 documentos más pertinentes
        4. **Agente Principal (ALIA):** Genera la respuesta final en el idioma seleccionado
        
        **📚 Base de Conocimientos:**
        - Documentos legales españoles
        - Normativa bancaria y mercantil
        - Guías de trámites administrativos
        - Información de productos Banco Sabadell
        
        **🔐 Privacidad:**
        - Conversaciones no almacenadas permanentemente
        - Documentos procesados localmente
        - API Keys encriptadas
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_footer():
    """Renderiza el footer"""
    st.markdown(f"""
    <div style='text-align: center; padding: 3rem 1rem 1rem; color: {'rgba(255,255,255,0.7)' if st.session_state.dark_mode else 'rgba(15,23,42,0.6)'}; margin-top: 2rem;'>
        <p style='font-size: 0.9rem;'>
            <strong>BStartupLab</strong> - Sistema Multi-Agente Inteligente
        </p>
        <p style='font-size: 0.85rem; margin-top: 0.5rem;'>
            🏦 Banco Sabadell | 🎓 Innovation Banking Hack Fest 2025 | 🤖 Powered by ALIA-40b (BSC)
        </p>
        <p style='font-size: 0.8rem; margin-top: 1rem; opacity: 0.6;'>
            © 2025 BStartupLab. #IBHF25 | 
            <a href='#' style='color: inherit; text-decoration: none;'>Privacidad</a> | 
            <a href='#' style='color: inherit; text-decoration: none;'>Términos</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


# ==================== MAIN ====================
def main():
    """Función principal de la aplicación"""
    initialize_session_state()
    apply_custom_css()
    
    page = render_sidebar()
    
    if page == "🏠 Inicio":
        page_home()
    elif page == "⚙️ Funcionamiento":
        page_how_it_works()
    elif page == "🎬 Demo & Chat":
        page_demo()
    
    render_footer()


if __name__ == "__main__":
    main()
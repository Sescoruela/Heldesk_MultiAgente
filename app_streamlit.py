"""
Streamlit frontend para el sistema multi-agente de Helpdesk.
Ejecutar con: streamlit run app_streamlit.py
"""

import asyncio
import os
import sys
import uuid

# ── Path setup — DEBE ir antes de cualquier import local ─────────────────────
# En Streamlit Cloud __file__ = /mount/src/<repo>/app_streamlit.py
# sys.path NO incluye ese directorio por defecto, hay que añadirlo
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
# También añadimos el CWD por si acaso
_CWD = os.getcwd()
if _CWD not in sys.path:
    sys.path.insert(0, _CWD)

import streamlit as st

# Carga .env solo si existe (entorno local); en Streamlit Cloud no es necesario
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── ADK imports ───────────────────────────────────────────────────────────────
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from manager.agent import root_agent

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🛠️ Helpdesk Multi-Agente",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Chat message bubbles */
    .stChatMessage { border-radius: 12px; }
    /* Hide default Streamlit footer */
    footer { visibility: hidden; }
    /* Sidebar title */
    .sidebar-title { font-size: 1.3rem; font-weight: 700; margin-bottom: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state initialisation ──────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": "user"|"assistant", "content": str}

# API key: la del sidebar tiene prioridad; el .env puede estar vacío
if "api_key" not in st.session_state:
    st.session_state.api_key = ""  # el usuario la introduce por el sidebar

# Asegurarse de que os.environ refleja siempre la clave en sesión
if st.session_state.api_key:
    os.environ["GOOGLE_API_KEY"] = st.session_state.api_key


def _init_runner():
    """(Re)create the ADK session service and runner."""
    svc = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="helpdesk_app",
        session_service=svc,
    )
    st.session_state.adk_session_service = svc
    st.session_state.runner = runner


if "runner" not in st.session_state:
    _init_runner()

# ── Helper: call agent ────────────────────────────────────────────────────────

async def _call_agent(user_message: str) -> str:
    """Send a message to root_agent and return the final text response."""
    runner: Runner = st.session_state.runner
    svc: InMemorySessionService = st.session_state.adk_session_service
    session_id: str = st.session_state.session_id

    # Ensure the ADK session exists (create if missing — handles async API)
    existing = await svc.get_session(
        app_name="helpdesk_app",
        user_id="streamlit_user",
        session_id=session_id,
    )
    if existing is None:
        await svc.create_session(
            app_name="helpdesk_app",
            user_id="streamlit_user",
            session_id=session_id,
        )

    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=user_message)],
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="streamlit_user",
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = "".join(
                part.text for part in event.content.parts if hasattr(part, "text")
            )

    return final_response or "_(Sin respuesta del agente)_"


def call_agent(user_message: str) -> str:
    """Sync wrapper around the async ADK call."""
    return asyncio.run(_call_agent(user_message))


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛠️ Helpdesk Multi-Agente")
    st.markdown("Sistema de gestión de incidencias potenciado por **Google ADK** y **Gemini 2.0 Flash**.")
    st.divider()

    # ── API Key ────────────────────────────────────────────────────────────────
    st.markdown("### 🔑 Google API Key")
    api_key_input = st.text_input(
        label="Introduce tu API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="AIza…",
        help="Obtenla en https://aistudio.google.com/app/apikey",
    )

    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        os.environ["GOOGLE_API_KEY"] = api_key_input
        # Reset runner and chat so the new key is picked up
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        _init_runner()
        st.rerun()

    if st.session_state.api_key:
        os.environ["GOOGLE_API_KEY"] = st.session_state.api_key
        st.success("✅ API Key configurada", icon="🔑")
    else:
        st.warning("⚠️ Introduce tu API Key para empezar.", icon="🔑")

    st.divider()

    st.markdown("### 🤖 Agentes disponibles")
    st.markdown(
        """
        - 🔍 **DiagnosticAgent** — Análisis de causa raíz
        - 🚦 **TriageAgent** — Clasificación y asignación
        - 📋 **DocumentationAgent** — Tickets y postmortems
        """
    )
    st.divider()

    st.markdown("### 💡 Ejemplos de consultas")
    examples = [
        "Error 500 en /api/AddOrder con 250 usuarios afectados en producción",
        "Quiero el diagnóstico completo + ticket Jira + triage del error anterior",
        "Genera un postmortem del incidente",
        "¿Cuál es el impacto económico si son 500 usuarios con severidad CRITICAL?",
        "Notifica al equipo por Slack con resumen del incidente",
    ]
    for example in examples:
        if st.button(example, use_container_width=True, key=f"ex_{example[:20]}"):
            st.session_state["prefill_input"] = example

    st.divider()

    if st.button("🗑️ Nueva conversación", use_container_width=True, type="secondary"):
        # Reset chat — la sesión ADK se creará lazy en _call_agent
        new_session_id = str(uuid.uuid4())
        st.session_state.session_id = new_session_id
        st.session_state.chat_history = []
        _init_runner()
        st.rerun()

    st.caption(f"Session ID: `{st.session_state.session_id[:8]}…`")

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("🛠️ Helpdesk Multi-Agente")
st.markdown(
    "Describe un incidente técnico y el sistema orquestará automáticamente los agentes "
    "de **diagnóstico**, **triage** y **documentación**."
)
st.divider()

# Render chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill_input", "")

if not st.session_state.api_key:
    st.info("🔑 Introduce tu **Google API Key** en la barra lateral para comenzar.", icon="ℹ️")
    st.stop()

user_input = st.chat_input(
    "Describe el incidente o escribe tu consulta…",
    key="chat_input",
)

# Accept either typed input or sidebar button prefill
prompt = user_input or prefill

if prompt:
    # Show user message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Call agent with spinner
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("⏳ Procesando con los agentes especializados…"):
            response = call_agent(prompt)
        st.markdown(response)

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()

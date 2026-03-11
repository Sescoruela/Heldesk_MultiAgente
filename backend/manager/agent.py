"""
Orquestación de agentes para el sistema de Helpdesk Multi-Agente.
Utiliza Google ADK para definir y coordinar los agentes.
"""

from google.adk.agents import Agent

# --- Agentes Hijos ---

# 1. DiagnosticAgent: Analiza la causa raíz de un incidente.
diagnostic_agent = Agent(
    name="DiagnosticAgent",
    instruction="""
    Eres un experto en diagnóstico de sistemas. Tu objetivo es analizar la descripción del incidente,
    identificar posibles causas raíz y sugerir pasos de investigación.
    Proporciona un análisis técnico detallado basado en la información recibida.
    """,
    model="gemini-2.0-flash",
)

# 2. TriageAgent: Clasifica y asigna prioridades.
triage_agent = Agent(
    name="TriageAgent",
    instruction="""
    Eres un gestor de incidentes. Tu objetivo es clasificar los incidentes por severidad (LOW, MEDIUM, HIGH, CRITICAL),
    estimar el impacto y proponer el equipo adecuado para su resolución.
    """,
    model="gemini-2.0-flash",
)

# 3. DocumentationAgent: Genera tickets y postmortems.
documentation_agent = Agent(
    name="DocumentationAgent",
    instruction="""
    Eres un documentador técnico. Tu objetivo es transformar los hallazgos de diagnóstico y triage
    en un formato de ticket estructurado (estilo Jira) o un borrador de postmortem si el incidente es grave.
    """,
    model="gemini-2.0-flash",
)

# --- Agente Raíz (Orquestador) ---

root_agent = Agent(
    name="HelpdeskRoot",
    instruction="""
    Eres el orquestador del sistema de Helpdesk. Tu función es recibir las incidencias de los usuarios
    y delegar el trabajo a los agentes especializados:
    - DiagnosticAgent para análisis técnico.
    - TriageAgent para clasificación y severidad.
    - DocumentationAgent para generar el resumen final o ticket.

    Coordina las respuestas de estos agentes para devolver una solución integral al usuario.
    """,
    model="gemini-2.0-flash",
    sub_agents=[diagnostic_agent, triage_agent, documentation_agent],
)

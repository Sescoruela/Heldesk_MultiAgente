# 🛠️ Heldesk_MultiAgente (Modern Refactor)

Sistema multi-agente de Helpdesk con arquitectura desacoplada: **React** (Frontend) + **FastAPI** (Backend + Google ADK).

## 🚀 Arquitectura

-   **Frontend**: React (Vite + TS) con diseño "Premium Glassmorphism".
-   **Backend**: FastAPI orquestando agentes de **Google ADK** y **Gemini 2.0 Flash**.

## 🛠️ Instalación y Uso

### 1. Preparar el Backend

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor
python backend/main.py
```
El servidor estará disponible en `http://localhost:8000`.

### 2. Preparar el Frontend

```bash
cd frontend
npm install
npm run dev
```
La aplicación estará disponible en `http://localhost:3000` (con proxy al backend).

## 📂 Estructura del Proyecto

- `backend/`: Código del servidor API.
    - `main.py`: Endpoints y lógica de orquestación.
- `frontend/`: Aplicación React.
    - `src/App.tsx`: Interfaz de chat premium.
- `manager/`: Lógica central de los agentes.
    - `agent.py`: Definición de agentes ADK.
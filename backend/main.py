import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import asyncio

# ADK imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from dotenv import load_dotenv

# Local imports
from manager.agent import root_agent

load_dotenv()

app = FastAPI(title="Helpdesk Multi-Agente API")

# Configure CORS for React frontend
frontend_url = os.environ.get("FRONTEND_URL", "https://helpdesk-multi-agente.onrender.com")
origins = [
    "http://localhost:5173",
    frontend_url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state (In-memory for simplicity)
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="helpdesk_app",
    session_service=session_service,
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = "default_user"
    api_key: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Set API Key if provided in request OR use environment
    api_key = request.api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Google API Key is required")
    
    os.environ["GOOGLE_API_KEY"] = api_key
    
    session_id = request.session_id or str(uuid.uuid4())
    
    # Ensure session exists
    existing = await session_service.get_session(
        app_name="helpdesk_app",
        user_id=request.user_id,
        session_id=session_id,
    )
    if existing is None:
        await session_service.create_session(
            app_name="helpdesk_app",
            user_id=request.user_id,
            session_id=session_id,
        )

    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=request.message)],
    )

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = "".join(
                    part.text for part in event.content.parts if hasattr(part, "text")
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        response=final_response or "(Sin respuesta del agente)",
        session_id=session_id
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

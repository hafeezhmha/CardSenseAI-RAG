import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from rag import ask, get_or_create_vector_store

# Initialize the FastAPI app
app = FastAPI(
    title="CardSense AI API",
    description="API for interacting with the CardSense AI assistant.",
    version="1.0.0"
)

# --- API Models ---
class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's question for the assistant.")
    previous_response_id: Optional[str] = Field(None, description="The ID of the previous response to maintain conversation context.")

class ChatResponse(BaseModel):
    response_text: str = Field(..., description="The assistant's text response.")
    response_id: str = Field(..., description="The ID of the current response.")


# --- API Endpoints ---
@app.on_event("startup")
def startup_event():
    """
    On startup, ensure the vector store is initialized.
    This prevents the first API call from being slow due to setup.
    """
    print("Server starting up...")
    get_or_create_vector_store()
    print("Vector store is ready.")

@app.get("/", summary="Health Check", description="A simple health check endpoint to confirm the server is running.")
async def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse, summary="Chat with Assistant")
async def chat_with_assistant(request: ChatRequest):
    """
    Sends a question to the assistant and gets a response, maintaining conversation history.
    """
    response_text, new_response_id = ask(
        request.question, 
        previous_response_id=request.previous_response_id
    )
    return ChatResponse(response_text=response_text, response_id=new_response_id) 
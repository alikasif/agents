"""
FastAPI Client for LiteLLM Proxy.
Makes POST calls to the LiteLLM inference service.
"""
import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="LiteLLM Client",
    description="Client API for making inference calls to LiteLLM proxy",
    version="1.0.0",
)

# LiteLLM proxy URL (default: localhost:4000)
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")


class Message(BaseModel):
    """Chat message."""
    role: str = "user"
    content: str


class ChatRequest(BaseModel):
    """Request to send to LiteLLM."""
    model: str = "gpt5"  # Uses the model name from config.yaml
    messages: list[Message] = None
    prompt: str = None  # Alternative: simple prompt string
    temperature: float = 0.7
    max_tokens: int = 1024

    def model_post_init(self, __context):
        # Convert simple prompt to messages format
        if self.prompt and not self.messages:
            self.messages = [Message(role="user", content=self.prompt)]


class ChatResponse(BaseModel):
    """Response from LiteLLM."""
    content: str
    model: str
    usage: dict = None


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat completion request to LiteLLM proxy.
    
    Example:
        POST /chat
        {
            "prompt": "What is the capital of France?",
            "model": "gpt5"
        }
    """
    # Prepare messages
    if request.prompt and not request.messages:
        messages = [{"role": "user", "content": request.prompt}]
    else:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    # Build LiteLLM request payload
    payload = {
        "model": request.model,
        "messages": messages,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{LITELLM_PROXY_URL}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            
            return ChatResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", request.model),
                usage=data.get("usage"),
            )
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"LiteLLM proxy unavailable: {e}")


@app.get("/health")
async def health():
    """Check if LiteLLM proxy is reachable."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{LITELLM_PROXY_URL}/health")
            return {"status": "ok", "proxy": LITELLM_PROXY_URL}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/")
async def root():
    """API info."""
    return {
        "name": "LiteLLM Client",
        "proxy_url": LITELLM_PROXY_URL,
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

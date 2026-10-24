from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.locate import router as locate_router

app = FastAPI(
    title="LookDo Backend API",
    description="Multimodal AI-powered interface assistant backend",
    version="0.1.0",
)

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(locate_router)


from app.services.ai_service import get_ai_service

@app.get("/health")
@app.get("/api/health")
def health_check():
    from app.services.ai_service import GemmaAIService, GeminiAIService
    ai_service = get_ai_service()
    if isinstance(ai_service, GemmaAIService):
        model = ai_service.model
        provider = "gemma"
        display = f"Gemma 4 Configured ({model})"
    elif isinstance(ai_service, GeminiAIService):
        model = ai_service.model
        provider = "gemini"
        display = f"Gemini Connected ({model})"
    else:
        provider = "mock"
        display = "Mock AI Mode (set GEMINI_API_KEY to enable Gemma 4)"
    return {
        "status": "ok",
        "service": "LookDo API",
        "provider": provider,
        "provider_display": display,
    }



@app.get("/")
def root():
    return {
        "message": "Welcome to LookDo API. Helping users interact with confusing interfaces.",
        "docs_url": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

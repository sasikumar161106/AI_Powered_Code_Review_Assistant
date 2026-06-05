from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="AI-Powered Code Review Assistant",
    description="An AI agent that integrates with GitHub to review pull requests in real-time.",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "AI Code Review Assistant is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

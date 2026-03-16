import uvicorn
from app.main import app

if __name__ == "__main__":
    print("\n   Study Assistant API running on http://localhost:8000")
    print("   FastAPI + MongoDB + local Ollama")
    print("  Open index.html in your browser\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

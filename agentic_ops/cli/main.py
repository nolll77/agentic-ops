from fastapi import FastAPI
from agentic_ops.entrypoints.slack_webhook import router as slack_router

app = FastAPI(title="Agentic-Ops Control Plane")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    # En production, on pourrait vérifier Redis ici
    return {"status": "ready"}

app.include_router(slack_router)

def start_server():
    import uvicorn
    uvicorn.run("agentic_ops.cli.main:app", host="0.0.0.0", port=8001)

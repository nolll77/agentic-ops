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

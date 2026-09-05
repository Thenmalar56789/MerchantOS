from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import evaluate_purchase


app = FastAPI(
    title="MerchantOS AI Agent"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "service": "MerchantOS AI Agent",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/agent/recommend")
def agent_recommend(
    request: AgentRequest
):
    result = evaluate_purchase(
        request.message
    )

    return result
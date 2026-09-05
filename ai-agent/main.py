from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from agent import evaluate_purchase


app = FastAPI(
    title="MerchantOS AI Agent",
    description=(
        "Merchant-side AI commerce service that accepts "
        "purchase intents from external buyer agents."
    ),
    version="1.0.0"
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


class PurchaseIntentRequest(BaseModel):
    product: str
    maxPrice: Optional[float] = None
    minPrice: Optional[float] = None
    requirements: List[str] = []


@app.get("/")
def root():
    return {
        "service": "MerchantOS AI Agent",
        "status": "running",
        "capability": "external buyer-agent purchase intent"
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


@app.post("/agent/purchase-intent")
def external_purchase_intent(
    request: PurchaseIntentRequest
):
    """
    External Buyer Agent contract.

    A real external AI shopping agent can send a
    structured purchase intent directly to MerchantOS.
    """

    requirements_text = ""

    if request.requirements:
        requirements_text = (
            " Requirements: "
            + ", ".join(request.requirements)
            + "."
        )

    if request.maxPrice is not None:
        budget_text = (
            f" Maximum budget: ₹{request.maxPrice}."
        )
    else:
        budget_text = ""

    message = (
        f"I want {request.product}."
        f"{budget_text}"
        f"{requirements_text}"
    )

    result = evaluate_purchase(
        message
    )

    return {
        "protocol": "MerchantOS-PurchaseIntent-v1",
        "intentSource": "external_buyer_agent",
        "purchaseIntent": {
            "product": request.product,
            "maxPrice": request.maxPrice,
            "minPrice": request.minPrice,
            "requirements": request.requirements
        },
        "merchantDecision": result
    }
import json
import re
import ollama
from bson import ObjectId

from intent_parser import parse_intent
from product_matcher import match_products
from decision_engine import evaluate_decision
from offer_engine import calculate_offer
from intent_verifier import verify_intent
from tools import get_merchant_policy, db


# =====================================================
# AGENT DECISION LOGGING
# =====================================================

def save_agent_decision(
    intent,
    product=None,
    decision="reject",
    reasoning="",
    guardrail_result="blocked"
):
    """
    Persist the Merchant Agent's decision to MongoDB.

    Logging failures must never break the commerce flow.
    The agent should continue working even if analytics
    logging temporarily fails.
    """

    try:
        merchant = db.merchants.find_one({
            "name": "MerchantOS Demo Store"
        })

        if not merchant:
            print(
                "[Decision Log] Merchant not found"
            )
            return

        decision_data = {
            "merchantId": merchant["_id"],
            "intent": intent,
            "decision": decision,
            "reasoning": reasoning,
            "guardrailResult": guardrail_result
        }

        if product and product.get("id"):
            try:
                decision_data["productId"] = ObjectId(
                    product["id"]
                )
            except Exception:
                pass

        result = db.agentdecisions.insert_one(
            decision_data
        )

        print(
            "[Decision Log] Saved:",
            str(result.inserted_id)
        )

    except Exception as error:
        print(
            "[Decision Log] Failed:",
            str(error)
        )


# =====================================================
# CUSTOMER-FACING RESPONSE CLEANUP
# =====================================================

def clean_agent_response(response):
    """
    Remove common Ollama formatting artifacts
    from the customer-facing response.
    """

    if not response:
        return ""

    response = response.strip()

    # Remove accidental role prefixes such as:
    # assistant
    # assistant:
    response = re.sub(
        r"^\s*assistant\s*:?\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    # Remove accidental markdown code fences.
    response = response.replace(
        "```text",
        ""
    ).replace(
        "```",
        ""
    )

    return response.strip()


# =====================================================
# MERCHANT AGENT
# =====================================================

def evaluate_purchase(customer_message):
    """
    Complete MerchantOS purchase evaluation.

    Returns structured data that the frontend/backend
    can safely use for the next commerce step.
    """

    print("\n================================")
    print("       MERCHANT AGENT")
    print("================================")

    # -------------------------------------------------
    # 1. UNDERSTAND
    # -------------------------------------------------

    print("\n[1] Understanding purchase intent...")

    intent = parse_intent(customer_message)

    print(
        json.dumps(
            intent,
            indent=2,
            ensure_ascii=False
        )
    )

    product_query = intent.get(
        "product",
        ""
    )

    max_price = intent.get(
        "maxPrice"
    )

    requirements = intent.get(
        "requirements",
        []
    )

    # -------------------------------------------------
    # 2. INVESTIGATE
    # -------------------------------------------------

    print("\n[2] Searching verified catalogue...")

    matched_products = match_products(
        product_query=product_query,
        max_price=max_price,
        requirements=requirements,
        limit=10
    )

    # If the customer's budget is below the catalogue price,
    # do not hide the product from the agent. Find the verified
    # product first, then let merchant guardrails decide whether
    # the requested price can be safely offered.
    if not matched_products and max_price is not None:
        matched_products = match_products(
            product_query=product_query,
            max_price=None,
            requirements=requirements,
            limit=10
        )

    print(
        f"[Catalogue] Found "
        f"{len(matched_products)} candidate products"
    )

    if not matched_products:

        save_agent_decision(
            intent=intent,
            decision="reject",
            reasoning=(
                "No matching product was found "
                "within the customer's constraints."
            ),
            guardrail_result="blocked"
        )

        return {
            "success": True,
            "canPurchase": False,
            "stage": "catalogue",
            "intent": intent,
            "product": None,
            "offer": None,
            "decision": {
                "action": "reject",
                "approved": False
            },
            "verification": {
                "verified": False,
                "status": "blocked",
                "violations": [
                    "No matching product was found "
                    "within the customer's constraints."
                ]
            },
            "response": (
                "I couldn't find a verified product "
                "matching your request."
            )
        }

    # -------------------------------------------------
    # 3. LOAD MERCHANT POLICY
    # -------------------------------------------------

    policy = get_merchant_policy()

    print(
        "[System] Merchant policy loaded"
    )

    if not policy:

        save_agent_decision(
            intent=intent,
            decision="reject",
            reasoning=(
                "Merchant policy is unavailable, "
                "so the transaction cannot be safely evaluated."
            ),
            guardrail_result="blocked"
        )

        return {
            "success": True,
            "canPurchase": False,
            "stage": "policy",
            "intent": intent,
            "product": None,
            "offer": None,
            "decision": {
                "action": "reject",
                "approved": False
            },
            "verification": {
                "verified": False,
                "status": "blocked",
                "violations": [
                    "Merchant policy is unavailable."
                ]
            },
            "response": (
                "I can't complete this purchase "
                "because the merchant policy is unavailable."
            )
        }

    # -------------------------------------------------
    # 4. VERIFY REQUIREMENTS
    # -------------------------------------------------

    if requirements:

        verified_products = []

        for product in matched_products:

            matched_requirements = set(
                product.get(
                    "matchedRequirements",
                    []
                )
            )

            requested_requirements = set(
                requirements
            )

            if requested_requirements.issubset(
                matched_requirements
            ):
                verified_products.append(
                    product
                )

        if not verified_products:

            print(
                "[Guardrail] Requirement verification failed"
            )

            save_agent_decision(
                intent=intent,
                decision="reject",
                reasoning=(
                    "Requested requirements could not be "
                    "verified from catalogue data."
                ),
                guardrail_result="blocked"
            )

            return {
                "success": True,
                "canPurchase": False,
                "stage": "requirement_verification",
                "intent": intent,
                "product": None,
                "offer": None,
                "decision": {
                    "action": "reject",
                    "approved": False
                },
                "verification": {
                    "verified": False,
                    "status": "blocked",
                    "violations": [
                        "Requested requirements "
                        "could not be verified "
                        "from catalogue data."
                    ]
                },
                "response": (
                    "I found products within your budget, "
                    "but I could not verify all of your "
                    "requested requirements from the "
                    "available catalogue data. I won't "
                    "recommend a product as a confirmed match."
                )
            }

        matched_products = verified_products

    # -------------------------------------------------
    # 5. MERCHANT DECISION
    # -------------------------------------------------

    selected_product = matched_products[0]

    print(
        "[System] Selected product:",
        selected_product["name"]
    )

    # -------------------------------------------------
    # 6. DETERMINISTIC GUARDRAILS
    # -------------------------------------------------

    print(
        "\n[3] Applying merchant guardrails..."
    )

    # Default AI offer.
    proposed_discount = 5

    # If the requested budget is below the merchant price,
    # calculate the discount that would be required to reach
    # the customer's requested maximum price. The deterministic
    # guardrail engine will then decide whether that discount
    # is actually allowed by merchant policy.
    if (
        max_price is not None
        and selected_product["price"] > max_price
    ):
        proposed_discount = (
            (1 - (max_price / selected_product["price"]))
            * 100
        )

    decision = evaluate_decision(
        product=selected_product,
        policy=policy,
        proposed_discount=proposed_discount
    )

    if not decision["approved"]:

        print(
            "[Guardrail] BLOCKED"
        )

        save_agent_decision(
            intent=intent,
            product=selected_product,
            decision="reject",
            reasoning="; ".join(
                decision.get(
                    "violations",
                    []
                )
            ),
            guardrail_result="blocked"
        )

        return {
            "success": True,
            "canPurchase": False,
            "stage": "guardrails",
            "intent": intent,
            "product": {
                "id": selected_product["id"],
                "name": selected_product["name"],
                "brand": selected_product.get("brand"),
                "price": selected_product["price"],
                "inventory": selected_product["inventory"]
            },
            "offer": None,
            "decision": decision,
            "verification": {
                "verified": False,
                "status": "blocked",
                "violations": decision["violations"]
            },
            "response": (
                "I can't offer this product at the "
                "requested price because doing so would "
                "violate the merchant's business policies."
            )
        }

    print(
        "[System] Guardrails passed"
    )

    # -------------------------------------------------
    # 7. OFFER ENGINE
    # -------------------------------------------------

    print(
        "\n[4] Calculating merchant-approved offer..."
    )

    offer = calculate_offer(
        product=selected_product,
        policy=policy,
        customer_intent=intent
    )

    print(
        json.dumps(
            offer,
            indent=2,
            ensure_ascii=False
        )
    )

    if not offer.get("approved", False):

        save_agent_decision(
            intent=intent,
            product=selected_product,
            decision="reject",
            reasoning=(
                "Merchant-approved offer could not be created."
            ),
            guardrail_result="blocked"
        )

        return {
            "success": True,
            "canPurchase": False,
            "stage": "offer",
            "intent": intent,
            "product": {
                "id": selected_product["id"],
                "name": selected_product["name"],
                "brand": selected_product.get("brand"),
                "price": selected_product["price"],
                "inventory": selected_product["inventory"]
            },
            "offer": offer,
            "decision": {
                "action": "reject",
                "approved": False
            },
            "verification": {
                "verified": False,
                "status": "blocked",
                "violations": [
                    "Merchant-approved offer "
                    "could not be created."
                ]
            },
            "response": (
                "I couldn't create a merchant-approved "
                "offer for this product."
            )
        }

    # -------------------------------------------------
    # 8. PURCHASE INTENT VERIFICATION
    # -------------------------------------------------

    print(
        "\n[5] Verifying final purchase intent..."
    )

    verification = verify_intent(
        intent=intent,
        product=selected_product,
        offer=offer
    )

    print(
        json.dumps(
            verification,
            indent=2,
            ensure_ascii=False
        )
    )

    if not verification["verified"]:

        print(
            "[Intent Verification] BLOCKED"
        )

        save_agent_decision(
            intent=intent,
            product=selected_product,
            decision="reject",
            reasoning="; ".join(
                verification.get(
                    "violations",
                    []
                )
            ),
            guardrail_result="blocked"
        )

        return {
            "success": True,
            "canPurchase": False,
            "stage": "intent_verification",
            "intent": intent,
            "product": {
                "id": selected_product["id"],
                "name": selected_product["name"],
                "brand": selected_product.get("brand"),
                "price": selected_product["price"],
                "inventory": selected_product["inventory"]
            },
            "offer": offer,
            "decision": {
                "action": "reject",
                "approved": False
            },
            "verification": verification,
            "response": (
                "I couldn't verify that the final offer "
                "matches your purchase requirements."
            )
        }

    print(
        "[Intent Verification] PASSED"
    )

    # -------------------------------------------------
    # 9. FINAL PRODUCT DATA
    # -------------------------------------------------

    product_data = {
        "id": selected_product["id"],
        "name": selected_product["name"],
        "brand": selected_product.get("brand"),
        "category": selected_product.get("category"),
        "originalPrice": selected_product["price"],
        "inventory": selected_product["inventory"]
    }

    offer_data = {
        "originalPrice": offer.get(
            "originalPrice",
            selected_product["price"]
        ),
        "discountPercent": offer.get(
            "discountPercent",
            0
        ),
        "finalPrice": offer.get(
            "finalPrice",
            selected_product["price"]
        ),
        "marginPercent": offer.get(
            "marginPercent"
        ),
        "approved": offer.get(
            "approved",
            False
        )
    }

    # -------------------------------------------------
    # 10. AI RESPONSE
    # -------------------------------------------------

    response_prompt = f"""
You are the customer-facing Merchant Agent for MerchantOS.

The system has already verified the transaction.

Return a concise response to the customer.

Verified information:

Product:
{product_data["name"]}

Brand:
{product_data["brand"]}

Original price:
₹{product_data["originalPrice"]}

Final price:
₹{offer_data["finalPrice"]}

Discount:
{offer_data["discountPercent"]}%

Inventory:
{product_data["inventory"]}

Customer request:
{json.dumps(intent, ensure_ascii=False)}

Rules:

- Only mention verified information.
- Do not reveal cost price.
- Do not reveal internal margin.
- Do not invent product benefits.
- Do not invent reviews or warranties.
- Do not claim unsupported availability.
- Do not mention internal system details.
- Do not describe this as a return, refund, or support request.
- This is a purchase request.
- Clearly state whether the product can be purchased.
- Keep the response concise.

Return only the customer-facing response.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": response_prompt
            }
        ]
    )

    final_response = clean_agent_response(
        response["message"]["content"]
    )

    print(
        "\n[Merchant Agent Response]"
    )

    print(
        final_response
    )

    # -------------------------------------------------
    # 11. SAVE SUCCESSFUL AGENT DECISION
    # -------------------------------------------------

    save_agent_decision(
        intent=intent,
        product=selected_product,
        decision=offer.get(
            "action",
            "offer"
        ),
        reasoning=(
            "Product matched customer intent, "
            "merchant guardrails passed, "
            "merchant-approved offer was created, "
            "and final purchase intent was verified."
        ),
        guardrail_result="passed"
    )

    # -------------------------------------------------
    # 12. STRUCTURED RESULT
    # -------------------------------------------------

    return {
        "success": True,

        "canPurchase": True,

        "stage": "verified",

        "intent": intent,

        "product": product_data,

        "offer": offer_data,

        "decision": {
            "action": offer.get(
                "action",
                "offer"
            ),
            "approved": True
        },

        "verification": verification,

        "response": final_response
    }


# =====================================================
# BACKWARD COMPATIBILITY
# =====================================================

def run_merchant_agent(customer_message):
    """
    Backward-compatible function used by the
    existing FastAPI endpoint.
    """

    result = evaluate_purchase(
        customer_message
    )

    return result["response"]
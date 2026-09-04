import json
import ollama

from tools import search_products, get_merchant_policy
from decision_engine import evaluate_decision
from intent_parser import parse_intent


SYSTEM_PROMPT = """
You are MerchantOS, an AI merchant agent.

Your job is to help merchants convert customer purchase intent into
profitable purchases while respecting merchant-defined business policies.

Rules:
- Use only verified catalogue data.
- Never invent products, prices, inventory, or policies.
- Never expose cost price.
- Never claim a product passed unless Python guardrails verified it.
- Respect the customer's requirements.
- Respect the customer's maximum price.
- Prefer products that satisfy the customer's requirements.
- Give a concise final recommendation.
"""


def run_merchant_agent(customer_message):

    # ---------------------------------------------
    # STEP 1: Parse customer purchase intent
    # ---------------------------------------------

    intent = parse_intent(customer_message)

    print("\n[Intent Parser]")
    print(json.dumps(
        intent,
        indent=2,
        ensure_ascii=False
    ))

    # ---------------------------------------------
    # STEP 2: Search merchant catalogue
    # ---------------------------------------------

    products = search_products(
        query=intent["product"],
        max_price=intent["maxPrice"],
        limit=10
    )

    print(
        f"\n[Catalogue] Found {len(products)} candidate products"
    )

    # ---------------------------------------------
    # STEP 3: Load merchant policy
    # ---------------------------------------------

    policy = get_merchant_policy()

    print("[System] Merchant policy loaded")

    # ---------------------------------------------
    # STEP 4: Deterministic guardrails
    # ---------------------------------------------

    verified_products = []

    for product in products:

        decision = evaluate_decision(
            product=product,
            policy=policy,
            proposed_discount=0
        )

        if decision["approved"]:

            verified_products.append({
                "id": product["id"],
                "name": product["name"],
                "brand": product.get("brand"),
                "category": product.get("category"),
                "price": product["price"],
                "inventory": product["inventory"],
                "marginPercent": decision["marginPercent"],
                "guardrailResult": "passed"
            })

        else:

            print(
                f"[Guardrail blocked] "
                f"{product['name']}"
            )

    print(
        f"[System] Guardrails passed for "
        f"{len(verified_products)} products"
    )

    # ---------------------------------------------
    # STEP 5: Let LLM choose from verified products
    # ---------------------------------------------

    if not verified_products:

        return (
            "I couldn't find a product that satisfies both "
            "your requirements and the merchant's policies."
        )

    prompt = f"""
Customer request:
{customer_message}

Parsed intent:
{json.dumps(intent, ensure_ascii=False)}

Verified products:
{json.dumps(verified_products, ensure_ascii=False)}

Choose the best product for the customer.

Customer requirements:
{intent["requirements"]}

Important:
- Only choose from the verified products.
- Do not invent information.
- Do not mention internal cost price or internal margin.
- Stay within the customer's maximum price.
- Explain briefly why the selected product fits.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


if __name__ == "__main__":

    print("\n================================")
    print("      MerchantOS AI Agent")
    print("================================")

    customer_message = input(
        "\nCustomer intent: "
    )

    print("\nAgent is thinking...\n")

    result = run_merchant_agent(
        customer_message
    )

    print("\n================================")
    print("        AGENT DECISION")
    print("================================")

    print(result)
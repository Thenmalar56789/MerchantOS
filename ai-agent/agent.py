import json
import ollama

from tools import (
    search_products,
    get_product,
    get_merchant_policy
)

from decision_engine import evaluate_decision


SYSTEM_PROMPT = """
You are MerchantOS, an AI merchant agent.

Your job is to help merchants convert customer purchase intent into
profitable purchases while respecting merchant-defined business policies.

RULES:
- Never invent products, prices, inventory, or policies.
- Use only catalogue data returned by tools.
- Never expose cost price to the customer.
- Never claim a policy passed unless the Python guardrail result says so.
- Never bypass merchant policies.
- Prefer products that satisfy the customer's requirements.
- Give a concise final recommendation.

The Python application is the final authority for merchant safety.
"""


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search the merchant product catalogue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Product, brand, ingredient, or category."
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum customer-facing price."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum products to return."
                    }
                },
                "required": ["query", "max_price", "limit"]
            }
        }
    }
]


def run_merchant_agent(user_intent):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_intent
        }
    ]

    while True:

        response = ollama.chat(
            model="llama3.2",
            messages=messages,
            tools=tools
        )

        assistant_message = response["message"]

        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls", [])

        if not tool_calls:
            return assistant_message.get(
                "content",
                "I could not produce a verified recommendation."
            )

        for tool_call in tool_calls:

            function = tool_call["function"]

            tool_name = function["name"]
            arguments = function.get("arguments", {})

            print(f"\n[Agent Tool Call] {tool_name}")

            if tool_name == "search_products":

                products = search_products(
                    query=arguments.get("query"),
                    max_price=arguments.get("max_price"),
                    limit=arguments.get("limit", 10)
                )

                policy = get_merchant_policy()

                print("[System] Merchant policy loaded")

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
                            "discountPercent": 0,
                            "finalPrice": decision["finalPrice"],
                            "marginPercent": decision["marginPercent"],
                            "guardrailResult": "passed"
                        })

                    else:

                        print(
                            f"[Guardrail blocked] "
                            f"{product['name']}: "
                            f"{decision['violations']}"
                        )

                result = {
                    "customer_request": user_intent,
                    "merchant_policy_verified": True,
                    "verified_products": verified_products
                }

                print(
                    f"[System] Guardrails passed for "
                    f"{len(verified_products)} products"
                )

                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(result)
                    }
                )


if __name__ == "__main__":

    print("\n================================")
    print("      MerchantOS AI Agent")
    print("================================")

    user_intent = input(
        "\nCustomer intent: "
    )

    print("\nAgent is thinking...\n")

    result = run_merchant_agent(user_intent)

    print("\n================================")
    print("        AGENT DECISION")
    print("================================")

    print(result)
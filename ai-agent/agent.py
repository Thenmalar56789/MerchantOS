import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from tools import search_products, get_product, get_merchant_policy
from decision_engine import evaluate_decision


# Load environment variables
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """
You are MerchantOS, an AI merchant agent.

Your job is to help a merchant convert legitimate customer purchase intent
into profitable purchases while respecting merchant policies.

You can:
1. Search the merchant catalogue.
2. Inspect a specific product.
3. Read merchant policies.
4. Evaluate a proposed discount using deterministic guardrails.

IMPORTANT:
- Never invent products, prices, inventory, discounts, or policies.
- Always use catalogue data.
- Never bypass merchant policies.
- Never directly approve a discount without the decision engine.
- The decision engine is the final authority for discount safety.
- Never expose cost price to the customer.
- If an action violates a policy, explain why and reject or clarify.
- Keep decisions concise and commercially useful.

Your decision should contain:
- selected product
- recommended action
- discount
- final price
- reasoning
- guardrail result
"""


def run_merchant_agent(user_intent: str):

    tools = [
        {
            "type": "function",
            "name": "search_products",
            "description": "Search the merchant's product catalogue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": ["string", "null"],
                        "description": "Product or category search query."
                    },
                    "max_price": {
                        "type": ["number", "null"],
                        "description": "Maximum customer-facing price."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of products to return."
                    }
                },
                "required": ["query", "max_price", "limit"],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "get_product",
            "description": "Get complete internal information for one product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string"
                    }
                },
                "required": ["product_id"],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "get_merchant_policy",
            "description": "Get the merchant's business policies.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    ]

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=SYSTEM_PROMPT,
        input=user_intent,
        tools=tools
    )

    # Process tool calls
    while True:

        tool_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not tool_calls:
            break

        tool_outputs = []

        for call in tool_calls:

            arguments = json.loads(call.arguments)

            if call.name == "search_products":
                result = search_products(
                    query=arguments.get("query"),
                    max_price=arguments.get("max_price"),
                    limit=arguments.get("limit", 10)
                )

            elif call.name == "get_product":
                result = get_product(
                    arguments["product_id"]
                )

            elif call.name == "get_merchant_policy":
                result = get_merchant_policy()

            else:
                result = {"error": "Unknown tool"}

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result)
            })

        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=SYSTEM_PROMPT,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools
        )

    return response.output_text


if __name__ == "__main__":

    print("\nMerchantOS AI Agent")
    print("------------------")

    intent = input(
        "\nCustomer intent: "
    )

    result = run_merchant_agent(intent)

    print("\nAgent Decision:")
    print(result)
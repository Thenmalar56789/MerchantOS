import json
import ollama


SYSTEM_PROMPT = """
You are a Buyer Agent in an AI commerce system.

Your job is to convert a customer's shopping request into
structured purchase intent.

Return ONLY valid JSON with these fields:
- product
- maxPrice
- minPrice
- requirements

STRICT RULES:

1. Extract ONLY information explicitly stated by the customer.

2. Never invent requirements.

3. Never invent a budget.

4. Never infer a minimum price when the customer only gives
   a maximum price.

5. If the customer says "under", "below", "less than", or
   "up to" a price:
   - put that value in maxPrice
   - set minPrice to null

6. If the customer explicitly gives a price range, extract
   both minPrice and maxPrice.

7. Do not convert product names into separate requirements.
   Example:
   "vitamin C serum" means product = "vitamin C serum".
   Do NOT add "Vitamin C ingredient" to requirements.

8. Only add "oily skin" if the customer explicitly says
   oily skin.

9. Only add "dry skin" if the customer explicitly says
   dry skin.

10. Only add "natural ingredients" if the customer explicitly
    says natural ingredients.

11. Keep requirements concise.

12. If there are no explicit requirements, return an empty
    requirements array.

Return ONLY JSON.
"""


def create_purchase_intent(customer_message):

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": customer_message
            }
        ],
        format={
            "type": "object",
            "properties": {
                "product": {
                    "type": "string"
                },
                "maxPrice": {
                    "type": ["number", "null"]
                },
                "minPrice": {
                    "type": ["number", "null"]
                },
                "requirements": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "product",
                "maxPrice",
                "minPrice",
                "requirements"
            ]
        }
    )

    intent = json.loads(
        response["message"]["content"]
    )

    # Safety correction:
    # If the model incorrectly assigns the same value
    # to minPrice and maxPrice, treat it as a maximum only.
    if (
        intent["minPrice"] is not None
        and intent["minPrice"] == intent["maxPrice"]
    ):
        intent["minPrice"] = None

    return intent


if __name__ == "__main__":

    print("\n================================")
    print("          BUYER AGENT")
    print("================================")

    customer_message = input(
        "\nCustomer request: "
    )

    intent = create_purchase_intent(
        customer_message
    )

    print("\nPurchase Intent:")

    print(
        json.dumps(
            intent,
            indent=2,
            ensure_ascii=False
        )
    )
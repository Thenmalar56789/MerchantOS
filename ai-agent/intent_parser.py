import json
import ollama


SYSTEM_PROMPT = """
You are a purchase intent parser for MerchantOS.

Convert a customer's shopping request into structured JSON.

Extract:
- product: the product the customer wants
- maxPrice: maximum price if specified, otherwise null
- minPrice: minimum price if specified, otherwise null
- requirements: important customer requirements such as skin type,
  ingredient preference, use case, size, or other constraints

Rules:
- Do not invent information.
- If something is not mentioned, use null or an empty list.
- Return ONLY valid JSON.
"""


def parse_intent(customer_message):

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

    return json.loads(
        response["message"]["content"]
    )


if __name__ == "__main__":

    print("\nMerchantOS Purchase Intent Parser")
    print("---------------------------------")

    message = input("\nCustomer request: ")

    intent = parse_intent(message)

    print("\nParsed Intent:")
    print(json.dumps(
        intent,
        indent=2,
        ensure_ascii=False
    ))
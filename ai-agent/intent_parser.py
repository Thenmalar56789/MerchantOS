import json
import re
import ollama


SYSTEM_PROMPT = """
You are a strict purchase intent parser for MerchantOS.

Convert the customer's message into structured JSON.

Return ONLY these fields:
- product
- maxPrice
- minPrice
- requirements

Rules:

1. Extract ONLY information explicitly stated by the customer.

2. NEVER put price phrases into requirements.

3. These are price phrases and are NOT requirements:
   - under ₹1000
   - below ₹1000
   - less than ₹1000
   - up to ₹1000
   - above ₹500
   - over ₹500
   - between ₹500 and ₹1000

4. If the customer says "under", "below", "less than",
   "up to", "over", or "above" a price:
   - extract the price into the correct field
   - do NOT add the price phrase to requirements

5. If the customer explicitly gives a price range:
   - extract both minPrice and maxPrice

6. Product names are NOT separate requirements.

Example:
"I need a vitamin C serum under ₹1000."

Correct:
{
  "product": "vitamin C serum",
  "maxPrice": 1000,
  "minPrice": null,
  "requirements": []
}

Do NOT return:
{
  "requirements": ["vitamin C serum"]
}

7. Only add a requirement when the customer explicitly states it.

8. Examples:
   "for oily skin" → "oily skin"
   "for dry skin" → "dry skin"
   "for sensitive skin" → "sensitive skin"
   "natural ingredients" → "natural ingredients"

9. If there are no explicit non-price requirements,
   return an empty requirements array.

10. Never infer information.

Return ONLY valid JSON.
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
                    "type": [
                        "number",
                        "null"
                    ]
                },
                "minPrice": {
                    "type": [
                        "number",
                        "null"
                    ]
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

    product = (
        intent.get("product") or ""
    ).strip()

    product_lower = product.lower()

    cleaned_requirements = []

    for requirement in intent.get(
        "requirements",
        []
    ):

        requirement = (
            requirement or ""
        ).strip()

        if not requirement:
            continue

        requirement_lower = (
            requirement.lower()
        )

        # Remove price phrases
        if re.search(
            r"(under|below|less than|up to|above|over)"
            r"\s*₹?\s*\d+",
            requirement,
            re.IGNORECASE
        ):
            continue

        # Remove explicit price ranges
        if re.search(
            r"between\s*₹?\s*\d+"
            r"\s*(and|to|-)\s*₹?\s*\d+",
            requirement,
            re.IGNORECASE
        ):
            continue

        # Never allow the product itself
        # to become a requirement.
        if requirement_lower == product_lower:
            continue

        # Also remove requirements that are
        # simply the product name with extra
        # wording such as "vitamin C serum product".
        if (
            product_lower
            and product_lower in requirement_lower
        ):
            continue

        cleaned_requirements.append(
            requirement
        )

    intent["product"] = product
    intent["requirements"] = (
        cleaned_requirements
    )

    # "under ₹1000" sometimes causes the model
    # to put 1000 in both fields.
    if (
        intent["minPrice"] is not None
        and intent["minPrice"]
        == intent["maxPrice"]
    ):
        intent["minPrice"] = None

    return intent
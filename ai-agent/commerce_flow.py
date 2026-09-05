import json

from buyer_agent import create_purchase_intent
from agent import run_merchant_agent


def run_commerce_flow(customer_message):

    print("\n================================")
    print("      AGENTIC COMMERCE FLOW")
    print("================================")

    # Step 1: Buyer Agent understands customer
    print("\n[1] Buyer Agent")
    
    intent = create_purchase_intent(
        customer_message
    )

    print(
        json.dumps(
            intent,
            indent=2,
            ensure_ascii=False
        )
    )

    # Step 2: Merchant Agent receives the request
    print("\n[2] Merchant Agent")
    print("Processing purchase intent...")

    result = run_merchant_agent(
        customer_message
    )

    # Step 3: Final response
    print("\n================================")
    print("       MERCHANT RESPONSE")
    print("================================")

    print(result)


if __name__ == "__main__":

    customer_message = input(
        "\nCustomer request: "
    )

    run_commerce_flow(
        customer_message
    )
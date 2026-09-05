from typing import Dict, Any


def verify_intent(
    intent: Dict[str, Any],
    product: Dict[str, Any],
    offer: Dict[str, Any]
) -> Dict[str, Any]:

    violations = []

    # 1. Product verification
    requested_product = intent.get("product", "").lower()
    actual_product = product.get("name", "").lower()

    if requested_product not in actual_product and actual_product not in requested_product:
        violations.append(
            "Selected product does not match the customer's requested product."
        )

    # 2. Minimum price
    min_price = intent.get("minPrice")

    if (
        min_price is not None
        and offer["finalPrice"] < min_price
    ):
        violations.append(
            "Final price is below the customer's minimum price."
        )

    # 3. Maximum price
    max_price = intent.get("maxPrice")

    if (
        max_price is not None
        and offer["finalPrice"] > max_price
    ):
        violations.append(
            "Final price exceeds the customer's maximum budget."
        )

    # 4. Inventory
    if product.get("inventory", 0) <= 0:
        violations.append(
            "Product is out of stock."
        )

    # 5. Offer approval
    if not offer.get("approved", False):
        violations.append(
            "Merchant has not approved the offer."
        )

    # Final decision
    if violations:

        return {
            "verified": False,
            "status": "blocked",
            "violations": violations
        }

    return {
        "verified": True,
        "status": "approved",
        "violations": []
    }


if __name__ == "__main__":

    product = {
        "name": "Vitamin C serum",
        "inventory": 35
    }

    offer = {
        "approved": True,
        "originalPrice": 799,
        "finalPrice": 759.05,
        "discountPercent": 5
    }

    intent = {
        "product": "vitamin C serum",
        "minPrice": None,
        "maxPrice": 500,
        "requirements": []
    }

    result = verify_intent(
        intent,
        product,
        offer
    )

    print("\nIntent Verification:")
    print(result)
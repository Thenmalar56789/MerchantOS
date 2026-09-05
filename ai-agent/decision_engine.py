from typing import Dict, Any


def evaluate_decision(
    product: Dict[str, Any],
    policy: Dict[str, Any],
    proposed_discount: float = 0
) -> Dict[str, Any]:

    price = product["price"]
    cost_price = product["costPrice"]
    inventory = product["inventory"]

    minimum_margin = policy["minimumMarginPercent"]
    maximum_discount = policy["maximumDiscountPercent"]
    minimum_inventory = policy["minimumInventory"]

    # Keep financial calculations precise internally.
    discounted_price = (
        price * (1 - proposed_discount / 100)
    )

    margin_percent = (
        (
            (discounted_price - cost_price)
            / discounted_price
        ) * 100
        if discounted_price > 0
        else 0
    )

    violations = []

    # Discount guardrail
    if proposed_discount > maximum_discount:
        violations.append(
            f"Discount {proposed_discount:.2f}% exceeds "
            f"maximum allowed {maximum_discount:.2f}%."
        )

    # Margin guardrail
    if margin_percent < minimum_margin:
        violations.append(
            f"Final price would produce a "
            f"{margin_percent:.2f}% margin, below the "
            f"merchant minimum of {minimum_margin:.2f}%."
        )

    # Inventory guardrail
    if inventory < minimum_inventory:
        violations.append(
            f"Inventory {inventory} is below the "
            f"merchant minimum of {minimum_inventory} units."
        )

    if violations:
        return {
            "approved": False,
            "action": "reject",
            "discountPercent": round(
                proposed_discount,
                2
            ),
            "finalPrice": round(
                discounted_price,
                2
            ),
            "marginPercent": round(
                margin_percent,
                2
            ),
            "minimumMarginPercent":
                minimum_margin,
            "maximumDiscountPercent":
                maximum_discount,
            "minimumInventory":
                minimum_inventory,
            "violations":
                violations
        }

    return {
        "approved": True,
        "action":
            "offer"
            if proposed_discount > 0
            else "recommend",

        "discountPercent":
            round(
                proposed_discount,
                2
            ),

        "finalPrice":
            round(
                discounted_price,
                2
            ),

        "marginPercent":
            round(
                margin_percent,
                2
            ),

        "minimumMarginPercent":
            minimum_margin,

        "maximumDiscountPercent":
            maximum_discount,

        "minimumInventory":
            minimum_inventory,

        "violations": []
    }
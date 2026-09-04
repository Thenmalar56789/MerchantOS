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

    discounted_price = price * (1 - proposed_discount / 100)

    margin_percent = (
        ((discounted_price - cost_price) / discounted_price) * 100
        if discounted_price > 0
        else 0
    )

    violations = []

    # Guardrail 1: maximum discount
    if proposed_discount > maximum_discount:
        violations.append(
            f"Discount {proposed_discount}% exceeds "
            f"maximum allowed {maximum_discount}%"
        )

    # Guardrail 2: minimum margin
    if margin_percent < minimum_margin:
        violations.append(
            f"Margin {margin_percent:.2f}% is below "
            f"minimum required {minimum_margin}%"
        )

    # Guardrail 3: inventory
    if inventory < minimum_inventory:
        violations.append(
            f"Inventory {inventory} is below "
            f"minimum required {minimum_inventory}"
        )

    if violations:
        return {
            "approved": False,
            "action": "reject",
            "discountPercent": proposed_discount,
            "finalPrice": round(discounted_price, 2),
            "marginPercent": round(margin_percent, 2),
            "violations": violations
        }

    return {
        "approved": True,
        "action": "offer" if proposed_discount > 0 else "recommend",
        "discountPercent": proposed_discount,
        "finalPrice": round(discounted_price, 2),
        "marginPercent": round(margin_percent, 2),
        "violations": []
    }
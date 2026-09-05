from typing import Dict, Any


def calculate_offer(
    product: Dict[str, Any],
    policy: Dict[str, Any],
    customer_intent: Dict[str, Any]
) -> Dict[str, Any]:

    price = product["price"]
    cost_price = product["costPrice"]

    max_discount = policy.get(
        "maximumDiscountPercent",
        0
    )

    minimum_margin = policy.get(
        "minimumMarginPercent",
        20
    )

    allow_discounts = policy.get(
        "allowDiscounts",
        True
    )

    # Default merchant-approved offer.
    # MerchantOS currently uses a conservative 5%
    # offer when discounts are allowed.
    proposed_discount = 5 if allow_discounts else 0

    # Never exceed merchant policy.
    proposed_discount = min(
        proposed_discount,
        max_discount
    )

    discounted_price = (
        price *
        (1 - proposed_discount / 100)
    )

    if discounted_price <= 0:
        return {
            "approved": False,
            "action": "reject",
            "discountPercent": proposed_discount,
            "originalPrice": price,
            "finalPrice": 0,
            "marginPercent": 0,
            "reason": "Invalid final price."
        }

    margin_percent = (
        (
            discounted_price -
            cost_price
        ) / discounted_price
    ) * 100

    # Merchant minimum-margin guardrail.
    if margin_percent < minimum_margin:

        return {
            "approved": False,
            "action": "reject",
            "discountPercent": proposed_discount,
            "originalPrice": price,
            "finalPrice": round(
                discounted_price,
                2
            ),
            "marginPercent": round(
                margin_percent,
                2
            ),
            "reason": (
                "Offer would violate the "
                "merchant's minimum margin policy."
            )
        }

    return {
        "approved": True,
        "action": (
            "offer"
            if proposed_discount > 0
            else "recommend"
        ),
        "discountPercent": proposed_discount,
        "originalPrice": price,
        "finalPrice": round(
            discounted_price,
            2
        ),
        "marginPercent": round(
            margin_percent,
            2
        ),
        "reason": (
            "Offer approved within merchant-defined "
            "discount and margin limits."
        )
    }
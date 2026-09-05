from typing import Dict, Any, List


REQUIRED_FIELDS = [
    "name",
    "price",
    "costPrice",
    "inventory"
]


def validate_product(product: Dict[str, Any]) -> Dict[str, Any]:
    violations: List[str] = []

    for field in REQUIRED_FIELDS:
        if product.get(field) is None:
            violations.append(
                f"Missing required field: {field}"
            )

    if not product.get("name"):
        violations.append(
            "Product name is empty."
        )

    if product.get("price", 0) <= 0:
        violations.append(
            "Product price must be greater than zero."
        )

    if product.get("costPrice", 0) < 0:
        violations.append(
            "Cost price cannot be negative."
        )

    if (
        product.get("price") is not None
        and product.get("costPrice") is not None
        and product["costPrice"] > product["price"]
    ):
        violations.append(
            "Cost price cannot exceed selling price."
        )

    if product.get("inventory", 0) < 0:
        violations.append(
            "Inventory cannot be negative."
        )

    attributes = product.get(
        "attributes",
        {}
    )

    if not attributes.get("brand"):
        violations.append(
            "Brand information is missing."
        )

    if not attributes.get("source"):
        violations.append(
            "Catalogue source is missing."
        )

    if violations:
        return {
            "verified": False,
            "violations": violations
        }

    return {
        "verified": True,
        "violations": []
    }
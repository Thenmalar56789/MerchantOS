from tools import search_products


REQUIREMENT_KEYWORDS = {
    "oily skin": [
        "oil-free",
        "oil free",
        "non-comedogenic",
        "lightweight",
        "gel",
        "water-based",
        "water based",
        "matte"
    ],
    "dry skin": [
        "hydrating",
        "moisturizing",
        "moisturising",
        "hyaluronic",
        "ceramide",
        "glycerin",
        "nourishing"
    ],
    "sensitive skin": [
        "gentle",
        "fragrance-free",
        "fragrance free",
        "hypoallergenic",
        "sensitive"
    ],
        "vitamin c ingredient": [
        "ascorbic acid",
        "sodium ascorbyl phosphate",
        "magnesium ascorbyl phosphate",
        "ascorbyl glucoside",
        "3-o-ethyl ascorbic acid",
        "tetrahexyldecyl ascorbate"
    ]
}


def match_products(
    product_query,
    max_price=None,
    requirements=None,
    limit=10
):
    """
    Search products and rank them according to
    customer requirements.
    """

    requirements = requirements or []

    products = search_products(
        query=product_query,
        max_price=max_price,
        limit=limit
    )

    ranked_products = []

    for product in products:

        searchable_text = " ".join([
            str(product.get("name", "")),
            str(product.get("category", "")),
            str(product.get("ingredients", "")),
            str(product.get("brand", ""))
        ]).lower()

        score = 0
        matched_requirements = []

        for requirement in requirements:

            requirement = requirement.lower()

            keywords = REQUIREMENT_KEYWORDS.get(
                requirement,
                [requirement]
            )

            matches = [
                keyword
                for keyword in keywords
                if keyword in searchable_text
            ]

            if matches:
                score += len(matches) * 10
                matched_requirements.append(requirement)

        # Prefer products with healthy inventory
        if product.get("inventory", 0) >= 10:
            score += 2

        product["matchScore"] = score
        product["matchedRequirements"] = matched_requirements

        ranked_products.append(product)

    ranked_products.sort(
        key=lambda product: product["matchScore"],
        reverse=True
    )

    return ranked_products


if __name__ == "__main__":

    print("\nMerchantOS Product Matcher")
    print("--------------------------")

    results = match_products(
        product_query="Vitamin C Serum",
        max_price=1000,
        requirements=["oily skin"],
        limit=10
    )

    print(f"\nFound {len(results)} products\n")

    for product in results:

        print(
            f"{product['name']} | "
            f"₹{product['price']} | "
            f"Score: {product['matchScore']} | "
            f"Matched: {product['matchedRequirements']}"
        )
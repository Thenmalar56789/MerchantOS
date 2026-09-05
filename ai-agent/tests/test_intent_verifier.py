from intent_verifier import verify_intent


BASE_PRODUCT = {
    "name": "Vitamin C serum",
    "inventory": 34
}


def approved_offer(price=759.05):
    return {
        "approved": True,
        "finalPrice": price
    }


def test_valid_intent_is_approved():

    intent = {
        "product": "vitamin C serum",
        "maxPrice": 1000,
        "minPrice": None
    }

    result = verify_intent(
        intent,
        BASE_PRODUCT,
        approved_offer()
    )

    assert result["verified"] is True
    assert result["status"] == "approved"
    assert result["violations"] == []


def test_budget_violation_is_blocked():

    intent = {
        "product": "vitamin C serum",
        "maxPrice": 700,
        "minPrice": None
    }

    result = verify_intent(
        intent,
        BASE_PRODUCT,
        approved_offer()
    )

    assert result["verified"] is False
    assert result["status"] == "blocked"
    assert any(
        "maximum budget" in violation
        for violation in result["violations"]
    )


def test_product_mismatch_is_blocked():

    intent = {
        "product": "moisturizer",
        "maxPrice": 1000,
        "minPrice": None
    }

    result = verify_intent(
        intent,
        BASE_PRODUCT,
        approved_offer()
    )

    assert result["verified"] is False
    assert result["status"] == "blocked"
    assert any(
        "does not match" in violation
        for violation in result["violations"]
    )


def test_out_of_stock_is_blocked():

    product = {
        "name": "Vitamin C serum",
        "inventory": 0
    }

    intent = {
        "product": "vitamin C serum",
        "maxPrice": 1000,
        "minPrice": None
    }

    result = verify_intent(
        intent,
        product,
        approved_offer()
    )

    assert result["verified"] is False
    assert result["status"] == "blocked"
    assert any(
        "out of stock" in violation
        for violation in result["violations"]
    )


def test_unapproved_offer_is_blocked():

    intent = {
        "product": "vitamin C serum",
        "maxPrice": 1000,
        "minPrice": None
    }

    offer = {
        "approved": False,
        "finalPrice": 759.05
    }

    result = verify_intent(
        intent,
        BASE_PRODUCT,
        offer
    )

    assert result["verified"] is False
    assert result["status"] == "blocked"
    assert any(
        "not approved" in violation
        for violation in result["violations"]
    )


def test_multiple_intent_constraints_are_checked():

    intent = {
        "product": "moisturizer",
        "maxPrice": 700,
        "minPrice": 800
    }

    result = verify_intent(
        intent,
        BASE_PRODUCT,
        approved_offer()
    )

    assert result["verified"] is False
    assert len(result["violations"]) >= 2
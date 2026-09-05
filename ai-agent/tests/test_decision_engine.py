from decision_engine import evaluate_decision


BASE_PRODUCT = {
    "price": 799,
    "costPrice": 500,
    "inventory": 34
}

BASE_POLICY = {
    "minimumMarginPercent": 25,
    "maximumDiscountPercent": 10,
    "minimumInventory": 5
}


def test_valid_offer_is_approved():
    result = evaluate_decision(
        BASE_PRODUCT,
        BASE_POLICY,
        proposed_discount=5
    )

    assert result["approved"] is True
    assert result["action"] == "offer"
    assert result["finalPrice"] == 759.05
    assert result["marginPercent"] == 34.13
    assert result["violations"] == []


def test_excessive_discount_is_blocked():
    result = evaluate_decision(
        BASE_PRODUCT,
        BASE_POLICY,
        proposed_discount=20
    )

    assert result["approved"] is False
    assert result["action"] == "reject"
    assert any(
        "exceeds maximum allowed" in violation
        for violation in result["violations"]
    )


def test_low_margin_is_blocked():
    result = evaluate_decision(
        BASE_PRODUCT,
        BASE_POLICY,
        proposed_discount=37.42
    )

    assert result["approved"] is False
    assert result["action"] == "reject"
    assert any(
        "below the merchant minimum" in violation
        for violation in result["violations"]
    )


def test_low_inventory_is_blocked():
    product = {
        **BASE_PRODUCT,
        "inventory": 3
    }

    result = evaluate_decision(
        product,
        BASE_POLICY,
        proposed_discount=5
    )

    assert result["approved"] is False
    assert result["action"] == "reject"
    assert any(
        "below the merchant minimum" in violation
        for violation in result["violations"]
    )


def test_multiple_guardrails_can_fail_together():
    result = evaluate_decision(
        BASE_PRODUCT,
        BASE_POLICY,
        proposed_discount=37.42
    )

    assert result["approved"] is False
    assert len(result["violations"]) >= 2
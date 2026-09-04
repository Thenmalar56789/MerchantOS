from decision_engine import evaluate_decision


policy = {
    "minimumMarginPercent": 25,
    "maximumDiscountPercent": 10,
    "minimumInventory": 5
}


# Test product with healthy margin and inventory
good_product = {
    "price": 1000,
    "costPrice": 600,
    "inventory": 20
}


# Test 1: normal recommendation
result = evaluate_decision(
    good_product,
    policy,
    proposed_discount=0
)

print("\nTEST 1: Normal recommendation")
print(result)


# Test 2: valid discount
result = evaluate_decision(
    good_product,
    policy,
    proposed_discount=5
)

print("\nTEST 2: Valid 5% discount")
print(result)


# Test 3: excessive discount
result = evaluate_decision(
    good_product,
    policy,
    proposed_discount=20
)

print("\nTEST 3: Excessive discount")
print(result)


# Test 4: low inventory
low_inventory_product = {
    "price": 1000,
    "costPrice": 600,
    "inventory": 3
}

result = evaluate_decision(
    low_inventory_product,
    policy,
    proposed_discount=5
)

print("\nTEST 4: Low inventory")
print(result)


# Test 5: low-margin product
low_margin_product = {
    "price": 1000,
    "costPrice": 800,
    "inventory": 20
}

result = evaluate_decision(
    low_margin_product,
    policy,
    proposed_discount=5
)

print("\nTEST 5: Low margin")
print(result)
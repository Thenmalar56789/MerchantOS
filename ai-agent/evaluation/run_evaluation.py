from statistics import mean


# ============================================================
# MerchantOS Synthetic Business Evaluation
# ============================================================
#
# IMPORTANT:
# These are synthetic evaluation results.
# They are NOT claims about real merchant performance.
#
# Baseline:
#   Merchant sells only at catalogue price.
#
# MerchantOS:
#   Merchant Agent can provide a bounded 5% offer
#   when it remains within merchant-defined policies.
#
# Merchant policy:
#   Catalogue price       = ₹799
#   Cost price            = ₹500
#   Maximum discount      = 10%
#   Minimum margin        = 25%
#
# This evaluation specifically tests whether MerchantOS can:
#   1. Recover near-budget purchases
#   2. Protect merchant margin
#   3. Block economically unsafe requests
# ============================================================


PRODUCT_PRICE = 799
COST_PRICE = 500

MIN_MARGIN = 25
MAX_DISCOUNT = 10

PROPOSED_DISCOUNT = 5

DISCOUNTED_PRICE = PRODUCT_PRICE * (
    1 - PROPOSED_DISCOUNT / 100
)


# ------------------------------------------------------------
# Synthetic customer intents
# ------------------------------------------------------------
#
# 8 normal customers:
#   Can already afford the product.
#
# 7 near-budget customers:
#   Cannot afford ₹799 but can afford the safe
#   MerchantOS price of ₹759.05.
#
# 5 too-low-budget customers:
#   Cannot afford even the safe offer.
#
# Total = 20
# ------------------------------------------------------------

TEST_CASES = [
    # Normal buyers
    {"segment": "normal", "budget": 1000},
    {"segment": "normal", "budget": 950},
    {"segment": "normal", "budget": 900},
    {"segment": "normal", "budget": 1000},
    {"segment": "normal", "budget": 850},
    {"segment": "normal", "budget": 900},
    {"segment": "normal", "budget": 999},
    {"segment": "normal", "budget": 850},

    # Near-budget buyers
    {"segment": "near_budget", "budget": 780},
    {"segment": "near_budget", "budget": 775},
    {"segment": "near_budget", "budget": 790},
    {"segment": "near_budget", "budget": 765},
    {"segment": "near_budget", "budget": 780},
    {"segment": "near_budget", "budget": 770},
    {"segment": "near_budget", "budget": 795},

    # Too-low-budget buyers
    {"segment": "too_low", "budget": 600},
    {"segment": "too_low", "budget": 550},
    {"segment": "too_low", "budget": 500},
    {"segment": "too_low", "budget": 700},
    {"segment": "too_low", "budget": 650},
]


def calculate_margin(price):
    if price <= 0:
        return 0

    return (
        (price - COST_PRICE) /
        price
    ) * 100


def run_baseline():

    revenue = 0
    profit = 0
    converted = 0
    discount_cost = 0

    segment_results = {
        "normal": 0,
        "near_budget": 0,
        "too_low": 0
    }

    for case in TEST_CASES:

        # Baseline merchant behavior:
        # sell only at catalogue price.
        if case["budget"] >= PRODUCT_PRICE:

            converted += 1

            revenue += PRODUCT_PRICE

            profit += (
                PRODUCT_PRICE -
                COST_PRICE
            )

            segment_results[
                case["segment"]
            ] += 1

    return {
        "intents": len(TEST_CASES),
        "converted": converted,
        "revenue": revenue,
        "profit": profit,
        "discount_cost": discount_cost,
        "segment_results": segment_results
    }


def run_merchant_os():

    revenue = 0
    profit = 0
    converted = 0
    discount_cost = 0
    blocked = 0

    segment_results = {
        "normal": 0,
        "near_budget": 0,
        "too_low": 0
    }

    margin = calculate_margin(
        DISCOUNTED_PRICE
    )

    for case in TEST_CASES:

        budget = case["budget"]

        # ----------------------------------------------------
        # MerchantOS bounded offer
        # ----------------------------------------------------

        # The offer must satisfy:
        #
        # 1. Maximum discount
        # 2. Minimum merchant margin
        # 3. Customer budget
        #

        if PROPOSED_DISCOUNT > MAX_DISCOUNT:
            blocked += 1
            continue

        if margin < MIN_MARGIN:
            blocked += 1
            continue

        # Customer cannot afford the safe offer.
        if DISCOUNTED_PRICE > budget:
            blocked += 1
            continue

        # Safe purchase
        converted += 1

        revenue += DISCOUNTED_PRICE

        profit += (
            DISCOUNTED_PRICE -
            COST_PRICE
        )

        discount_cost += (
            PRODUCT_PRICE -
            DISCOUNTED_PRICE
        )

        segment_results[
            case["segment"]
        ] += 1

    return {
        "intents": len(TEST_CASES),
        "converted": converted,
        "revenue": revenue,
        "profit": profit,
        "discount_cost": discount_cost,
        "blocked": blocked,
        "segment_results": segment_results
    }


def percentage(value, total):

    if total == 0:
        return 0

    return (
        value /
        total
    ) * 100


def calculate_uplift(
    baseline_value,
    merchant_value
):

    if baseline_value == 0:
        return 0

    return (
        (
            merchant_value -
            baseline_value
        ) /
        baseline_value
    ) * 100


def print_results(
    baseline,
    merchant_os
):
    margin = calculate_margin(
        DISCOUNTED_PRICE
    )
    baseline_conversion = percentage(
        baseline["converted"],
        baseline["intents"]
    )

    merchant_conversion = percentage(
        merchant_os["converted"],
        merchant_os["intents"]
    )

    baseline_aov = (
        baseline["revenue"] /
        baseline["converted"]
        if baseline["converted"]
        else 0
    )

    merchant_aov = (
        merchant_os["revenue"] /
        merchant_os["converted"]
        if merchant_os["converted"]
        else 0
    )

    baseline_profit_per_intent = (
        baseline["profit"] /
        baseline["intents"]
    )

    merchant_profit_per_intent = (
        merchant_os["profit"] /
        merchant_os["intents"]
    )

    revenue_uplift = calculate_uplift(
        baseline["revenue"],
        merchant_os["revenue"]
    )

    profit_uplift = calculate_uplift(
        baseline["profit"],
        merchant_os["profit"]
    )

    conversion_uplift = (
        merchant_conversion -
        baseline_conversion
    )

    incremental_conversions = (
        merchant_os["converted"] -
        baseline["converted"]
    )

    incremental_revenue = (
        merchant_os["revenue"] -
        baseline["revenue"]
    )

    incremental_profit = (
        merchant_os["profit"] -
        baseline["profit"]
    )

    print()
    print("==============================================")
    print("          MERCHANTOS EVALUATION")
    print("==============================================")

    print()
    print("Synthetic intents:", len(TEST_CASES))

    print()
    print("PRODUCT ECONOMICS")
    print("----------------------------------------------")
    print(
        "Catalogue price:      ₹",
        f"{PRODUCT_PRICE:.2f}"
    )
    print(
        "Cost price:           ₹",
        f"{COST_PRICE:.2f}"
    )
    print(
        "MerchantOS discount:  ",
        f"{PROPOSED_DISCOUNT:.2f}%"
    )
    print(
        "MerchantOS price:     ₹",
        f"{DISCOUNTED_PRICE:.2f}"
    )
    print(
        "Margin after offer:   ",
        f"{margin:.2f}%"
    )
    print(
        "Minimum margin:       ",
        f"{MIN_MARGIN:.2f}%"
    )

    print()
    print("BASELINE")
    print("----------------------------------------------")
    print(
        "Converted:            ",
        baseline["converted"]
    )
    print(
        "Conversion rate:      ",
        f"{baseline_conversion:.2f}%"
    )
    print(
        "Revenue:              ₹",
        f"{baseline['revenue']:.2f}"
    )
    print(
        "AOV:                  ₹",
        f"{baseline_aov:.2f}"
    )
    print(
        "Profit:               ₹",
        f"{baseline['profit']:.2f}"
    )
    print(
        "Discount cost:        ₹",
        f"{baseline['discount_cost']:.2f}"
    )

    print()
    print("MERCHANTOS")
    print("----------------------------------------------")
    print(
        "Converted:            ",
        merchant_os["converted"]
    )
    print(
        "Conversion rate:      ",
        f"{merchant_conversion:.2f}%"
    )
    print(
        "Revenue:              ₹",
        f"{merchant_os['revenue']:.2f}"
    )
    print(
        "AOV:                  ₹",
        f"{merchant_aov:.2f}"
    )
    print(
        "Profit:               ₹",
        f"{merchant_os['profit']:.2f}"
    )
    print(
        "Discount cost:        ₹",
        f"{merchant_os['discount_cost']:.2f}"
    )
    print(
        "Blocked unsafe actions:",
        merchant_os["blocked"]
    )

    print()
    print("INCREMENTAL BUSINESS VALUE")
    print("----------------------------------------------")
    print(
        "Additional conversions:",
        incremental_conversions
    )
    print(
        "Additional revenue:    ₹",
        f"{incremental_revenue:.2f}"
    )
    print(
        "Additional profit:     ₹",
        f"{incremental_profit:.2f}"
    )
    print(
        "Revenue uplift:        ",
        f"{revenue_uplift:.2f}%"
    )
    print(
        "Profit uplift:         ",
        f"{profit_uplift:.2f}%"
    )
    print(
        "Conversion uplift:     ",
        f"{conversion_uplift:.2f} pp"
    )

    print()
    print("PROFIT EFFICIENCY")
    print("----------------------------------------------")
    print(
        "Baseline profit/intent:",
        f"₹{baseline_profit_per_intent:.2f}"
    )
    print(
        "MerchantOS profit/intent:",
        f"₹{merchant_profit_per_intent:.2f}"
    )

    print()
    print("SEGMENT RESULTS")
    print("----------------------------------------------")

    for segment in [
        "normal",
        "near_budget",
        "too_low"
    ]:

        baseline_count = (
            baseline["segment_results"][segment]
        )

        merchant_count = (
            merchant_os["segment_results"][segment]
        )

        print()
        print(
            segment.replace("_", " ").title()
        )

        print(
            "  Baseline:",
            baseline_count,
            "converted"
        )

        print(
            "  MerchantOS:",
            merchant_count,
            "converted"
        )

    print()
    print("==============================================")
    print("INTERPRETATION")
    print("==============================================")

    print(
        "\nMerchantOS uses bounded offers to recover "
        "near-budget purchases while preserving "
        "merchant-defined margin limits."
    )

    print(
        "\nRequests below the safe offer price are "
        "blocked instead of forcing an economically "
        "unsafe transaction."
    )

    print(
        "\nIMPORTANT: Results are from a synthetic "
        "evaluation dataset and must not be presented "
        "as real merchant performance."
    )


if __name__ == "__main__":

    baseline = run_baseline()

    merchant_os = run_merchant_os()

    print_results(
        baseline,
        merchant_os
    )
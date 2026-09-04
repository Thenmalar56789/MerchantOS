import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


# Project root
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load root .env
load_dotenv(ROOT_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in .env")


# Import catalogue loader
sys.path.append(str(Path(__file__).resolve().parent))

from services.catalogue_service import load_catalogue


def calculate_merchant_data(index):
    """
    Merchant-controlled commercial data.
    In a real merchant system, these values would come
    from the merchant's inventory/pricing system.
    """

    selling_prices = [
        799,
        999,
        549,
        899,
        699,
        849,
        1199,
        649,
        749,
        1099
    ]

    cost_percentages = [
        0.60,
        0.65,
        0.70,
        0.75,
        0.55
    ]

    inventory_values = [
        35,
        20,
        12,
        7,
        3
    ]

    price = selling_prices[index % len(selling_prices)]

    cost_percentage = cost_percentages[index % len(cost_percentages)]
    cost_price = round(price * cost_percentage, 2)

    inventory = inventory_values[index % len(inventory_values)]

    margin = round(
        ((price - cost_price) / price) * 100,
        2
    )

    return price, cost_price, inventory, margin


def main():

    print("Loading real skincare catalogue...")

    catalogue = load_catalogue()

    print(f"Found {len(catalogue)} products")

    client = MongoClient(MONGODB_URI)
    db = client["merchantos"]

    print("Connected to MongoDB")

    # Clear previous MerchantOS demo data
    db.products.delete_many({})
    db.merchants.delete_many({})
    db.policies.delete_many({})

    # Create merchant
    merchant = {
        "name": "MerchantOS Demo Store",
        "category": "Skincare",
        "description": "AI-powered skincare merchant for agentic commerce",
        "currency": "INR"
    }

    merchant_result = db.merchants.insert_one(merchant)
    merchant_id = merchant_result.inserted_id

    print("Created merchant:", merchant["name"])

    # Merchant policy
    policy = {
        "merchantId": merchant_id,
        "minimumMarginPercent": 25,
        "maximumDiscountPercent": 10,
        "minimumInventory": 5,
        "allowDiscounts": True,
        "objective": "maximize_revenue"
    }

    db.policies.insert_one(policy)

    inserted = 0

    for index, product in enumerate(catalogue):

        if not product["name"] or not product["name"].strip():
            continue

        price, cost_price, inventory, margin = calculate_merchant_data(index)

        mongo_product = {
            "merchantId": merchant_id,

            "name": product["name"].strip(),

            "category": product["category"] or "Skincare",

            "description": product["ingredients"] or "",

            # Merchant-controlled selling price
            "price": price,

            # Merchant-private business data
            "costPrice": cost_price,
            "margin": margin,
            "inventory": inventory,

            "attributes": {
                "brand": product["brand"],
                "barcode": product["barcode"],
                "ingredients": product["ingredients"],

                # Important for explaining our data architecture
                "source": "INCIDB",
                "publicRetailPriceUSD": product["priceUSD"],
                "merchantPriceSource": "demo_merchant_data"
            },

            "active": True
        }

        db.products.insert_one(mongo_product)

        inserted += 1

    print()
    print("================================")
    print("MerchantOS catalogue imported!")
    print("================================")
    print(f"Products inserted : {inserted}")
    print("Merchant policy   : created")
    print()


if __name__ == "__main__":
    main()
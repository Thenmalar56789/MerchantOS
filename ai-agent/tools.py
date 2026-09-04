import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


# Load root .env
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in .env")


client = MongoClient(MONGODB_URI)
db = client["merchantos"]


def search_products(query=None, max_price=None, limit=10):
    """
    Search the merchant catalogue for products.
    """

    filters = {
        "active": True
    }

    if query:
        filters["$or"] = [
            {
                "name": {
                    "$regex": query,
                    "$options": "i"
                }
            },
            {
                "category": {
                    "$regex": query,
                    "$options": "i"
                }
            },
            {
                "description": {
                    "$regex": query,
                    "$options": "i"
                }
            }
        ]

    if max_price is not None:
        filters["price"] = {
            "$lte": max_price
        }

    products = list(
        db.products
        .find(filters)
        .limit(limit)
    )

    results = []

    for product in products:
        results.append({
            "id": str(product["_id"]),
            "name": product["name"],
            "category": product.get("category"),
            "price": product["price"],
            "costPrice": product["costPrice"],
            "margin": product["margin"],
            "inventory": product["inventory"],
            "brand": product.get("attributes", {}).get("brand"),
            "ingredients": product.get("attributes", {}).get("ingredients")
        })

    return results


def get_product(product_id):
    """
    Get complete information about one product.
    """

    from bson import ObjectId

    product = db.products.find_one({
        "_id": ObjectId(product_id)
    })

    if not product:
        return None

    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "category": product.get("category"),
        "price": product["price"],
        "costPrice": product["costPrice"],
        "margin": product["margin"],
        "inventory": product["inventory"],
        "brand": product.get("attributes", {}).get("brand"),
        "ingredients": product.get("attributes", {}).get("ingredients")
    }


def get_merchant_policy():
    """
    Get the merchant's business rules.
    """

    policy = db.policies.find_one({})

    if not policy:
        return None

    return {
        "minimumMarginPercent": policy["minimumMarginPercent"],
        "maximumDiscountPercent": policy["maximumDiscountPercent"],
        "minimumInventory": policy["minimumInventory"],
        "allowDiscounts": policy["allowDiscounts"],
        "objective": policy["objective"]
    }
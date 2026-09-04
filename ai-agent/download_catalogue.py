import csv
import requests
from pathlib import Path


OUTPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "openbeautyfacts_products.csv"
)

BASE_URL = "https://world.openbeautyfacts.org/api/v2/search"

TARGET_PRODUCTS = 1000
PAGE_SIZE = 100

# Multiple skincare-related categories
CATEGORIES = [
    "skin-care",
    "face-care",
    "body-care",
    "moisturizers",
    "cleansers",
    "serums",
    "sunscreens",
]


def download_products():

    products = []
    seen_codes = set()

    for category in CATEGORIES:

        if len(products) >= TARGET_PRODUCTS:
            break

        page = 1

        print()
        print(f"Searching category: {category}")

        while len(products) < TARGET_PRODUCTS:

            print(f"Fetching page {page}...")

            params = {
                "categories_tags_en": category,
                "page": page,
                "page_size": PAGE_SIZE,
                "fields": "code,product_name,brands,categories,ingredients_text,quantity"
            }

            response = requests.get(
                BASE_URL,
                params=params,
                headers={
                    "User-Agent": "MerchantOS/1.0"
                },
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            batch = data.get("products", [])

            if not batch:
                break

            added_this_page = 0

            for product in batch:

                code = product.get("code", "")
                name = product.get("product_name", "").strip()

                if not name:
                    continue

                if code and code in seen_codes:
                    continue

                clean_product = {
                    "code": code,
                    "product_name": name,
                    "brands": product.get("brands", ""),
                    "categories": product.get("categories", ""),
                    "ingredients_text": product.get("ingredients_text", ""),
                    "quantity": product.get("quantity", "")
                }

                products.append(clean_product)

                if code:
                    seen_codes.add(code)

                added_this_page += 1

                if len(products) >= TARGET_PRODUCTS:
                    break

            print(f"Total collected: {len(products)}")

            if added_this_page == 0:
                break

            page += 1

    products = products[:TARGET_PRODUCTS]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "code",
        "product_name",
        "brands",
        "categories",
        "ingredients_text",
        "quantity"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(products)

    print()
    print("================================")
    print("MerchantOS catalogue downloaded")
    print("================================")
    print(f"Products saved: {len(products)}")
    print(f"File: {OUTPUT_FILE}")


if __name__ == "__main__":
    download_products()
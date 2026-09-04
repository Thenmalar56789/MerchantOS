import csv
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def read_csv(filename):
    file_path = DATA_DIR / filename

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def load_catalogue():

    products = read_csv("cleaned_products.csv")

    catalogue = []

    for product in products:

        catalogue.append({
            "externalProductId": product.get("code", ""),
            "brand": product.get("brands", "") or "Unknown Brand",
            "name": product.get("product_name", ""),
            "category": product.get("categories", "") or "Skincare",

            # Open Beauty Facts does not provide the merchant's
            # selling price for our catalogue.
            # MerchantOS will supply that separately.
            "priceUSD": 0,

            "barcode": product.get("code", ""),
            "ingredients": product.get("ingredients_text", ""),
            "quantity": product.get("quantity", "")
        })

    return catalogue


if __name__ == "__main__":

    catalogue = load_catalogue()

    print(f"Loaded {len(catalogue)} products")

    for product in catalogue[:5]:
        print(product)
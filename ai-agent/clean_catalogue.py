import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "openbeautyfacts_products.csv"
OUTPUT_FILE = BASE_DIR / "data" / "cleaned_products.csv"


# Terms that strongly indicate actual skincare products
KEEP_TERMS = [
    "skin care",
    "skincare",
    "face care",
    "facial",
    "face cream",
    "face wash",
    "cleanser",
    "cleansing",
    "serum",
    "moisturizer",
    "moisturiser",
    "moisturizing",
    "moisturising",
    "sunscreen",
    "sun cream",
    "sun protection",
    "spf",
    "toner",
    "face mask",
    "facial mask",
    "acne",
    "anti-aging",
    "anti ageing",
    "body lotion",
    "body cream",
    "body butter",
    "body oil",
    "eye cream",
    "eye serum",
    "lip balm",
    "exfoliant",
    "exfoliating",
    "scrub",
    "micellar",
    "essence"
]


# Terms that indicate products we definitely don't want
EXCLUDE_TERMS = [
    "candle",
    "insect",
    "mosquito",
    "repellent",
    "pool",
    "swimming",
    "air freshener",
    "detergent",
    "dishwasher",
    "laundry",
    "cleaning product",
    "floor",
    "toilet",
    "shampoo",
    "conditioner",
    "hair dye",
    "hair color",
    "deodorant",
    "perfume",
    "fragrance",
    "makeup",
    "mascara",
    "lipstick",
    "foundation",
    "eyeshadow",
    "nail polish",
    "toothpaste",
    "mouthwash",
    "baby food",
    "pet food"
]


def contains_term(text, terms):
    text = text.lower()

    return any(term in text for term in terms)


def clean_catalogue():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        rows = list(csv.DictReader(file))

    cleaned = []
    seen_codes = set()

    for row in rows:

        name = row.get("product_name", "").strip()
        categories = row.get("categories", "").strip()
        ingredients = row.get("ingredients_text", "").strip()

        if not name:
            continue

        # Combine searchable information
        searchable_text = f"{name} {categories}"

        # Remove obvious irrelevant products first
        if contains_term(searchable_text, EXCLUDE_TERMS):
            continue

        # Keep only products that look relevant to skincare
        if not contains_term(searchable_text, KEEP_TERMS):
            continue

        code = row.get("code", "").strip()

        # Remove duplicate products
        if code and code in seen_codes:
            continue

        if code:
            seen_codes.add(code)

        cleaned.append({
            "code": code,
            "product_name": name,
            "brands": row.get("brands", "").strip(),
            "categories": categories,
            "ingredients_text": ingredients,
            "quantity": row.get("quantity", "").strip()
        })

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
        writer.writerows(cleaned)

    print()
    print("================================")
    print("MerchantOS catalogue cleaned")
    print("================================")
    print(f"Raw products     : {len(rows)}")
    print(f"Clean products   : {len(cleaned)}")
    print(f"Removed products : {len(rows) - len(cleaned)}")
    print(f"Output file      : {OUTPUT_FILE}")


if __name__ == "__main__":
    clean_catalogue()
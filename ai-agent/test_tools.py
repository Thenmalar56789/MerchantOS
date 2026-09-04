from tools import search_products, get_merchant_policy


print("\nMERCHANT POLICY")
print(get_merchant_policy())


print("\nPRODUCT SEARCH")
products = search_products(
    query="serum",
    max_price=1500,
    limit=5
)

for product in products:
    print(product)
ILLEGAL_KEYWORDS = {"weapon", "gun", "sword", "blade"}

def validate(product):
    name = product.get("productName", "").lower()
    desc = product.get("productDescription", "").lower()
    for keyword in ILLEGAL_KEYWORDS:
        if keyword in name or keyword in desc:
            return False, f"Illegal product detected: {keyword}"
    return True, ""
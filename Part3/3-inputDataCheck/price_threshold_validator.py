def validate(product):
    try:
        price = float(product.get("price", 0))
        if price > 100000:
            return False, "Price exceeds threshold"
        return True, ""
    except (ValueError, TypeError):
        return False, "Invalid price format"
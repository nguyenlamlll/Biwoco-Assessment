import json
import re
import requests

class HttpTransientError(Exception):
    """Custom exception for transient HTTP errors."""
    pass

def extract_price_and_currency(price_str):
    # Extract numeric price and currency (e.g., "12.99 USD" -> "12.99", "USD")
    match = re.match(r"([\d\.]+)\s*([A-Za-z]+)?", price_str)
    if match:
        price = match.group(1)
        currency = match.group(2) if match.group(2) else ""
        return price, currency
    return price_str, ""

def mock_openai_cleansing(data):
    # Mock HTTP call to OpenAI ChatGPT endpoint
    try:
        # This is a fake call; in real use, replace with actual endpoint and payload
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": "Bearer FAKE_API_KEY"},
            json={"messages": [{"role": "user", "content": str(data)}]}
        )
        # For now, just return the data unchanged
        return data
    except Exception as e:
        print("Mock OpenAI call failed:", e)
        raise HttpTransientError("Mock OpenAI call failed")

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    results = []
    for product in event:
        price, currency = extract_price_and_currency(product.get("price", ""))
        transformed = {
            "price": price,
            "currency": currency,
            "id": product.get("idNumber", ""),
            "category": product.get("categoryModule", {}).get("category", ""),
            "subcategory": product.get("categoryModule", {}).get("subcategory", ""),
            "productName": product.get("productModule", {}).get("productName", ""),
            "productDescription": product.get("productModule", {}).get("productDescription", "")
        }
        cleansed = mock_openai_cleansing(transformed)
        results.append(cleansed)
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
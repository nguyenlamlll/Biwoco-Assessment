import json
from price_threshold_validator import validate as price_validate
from illegal_product_validator import validate as illegal_validate

def lambda_handler(event, context):
    """
    AWS Lambda function to validate product data.
    :param event: List of product dictionaries to validate
    :param context: AWS Lambda context object
    :return: JSON response with validation results
    """
    print("Received event:", json.dumps(event))
    results = []
    for product in event:
        valid, reason = price_validate(product)
        if not valid:
            results.append({"id": product.get("id"), "status": "denied", "reason": reason})
            continue
        valid, reason = illegal_validate(product)
        if not valid:
            results.append({"id": product.get("id"), "status": "denied", "reason": reason})
            continue
        results.append({"id": product.get("id"), "status": "approved"})
    return {
        'statusCode': 200,
        'validationResults': json.dumps(results),
        'mappedProducts': event,
    }
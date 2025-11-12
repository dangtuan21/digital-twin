import json

def lambda_handler(event, context):
    try:
        import pydantic_core
        result = {
            "success": True,
            "version": getattr(pydantic_core, "__version__", "unknown"),
            "so_file": getattr(pydantic_core, "__file__", "unknown")
        }
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }

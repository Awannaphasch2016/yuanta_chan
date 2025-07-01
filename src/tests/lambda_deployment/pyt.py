import json

def handler(event, context):
    """
    Lambda function to return a simple greeting.
    """
    print("Lambda function 'testFunction' received an event.")
    print(f"Event: {json.dumps(event)}")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda! This is a test function.')
    }

import json
from handler import lambda_handler


event = {
    "tool_calls": [
        {
            "name": "weather",
            "args": {"city": "São Paulo"}
        }
    ],
    "httpMethod": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": "{\"id\": \"12345\", \"jsonrpc\": \"2.0\", \"method\": \"tools/list\", \"params\": {\"city\": \"São Paulo\"}}"
}
context = {}
response = lambda_handler(event, context)
print(json.dumps(response, indent=2))
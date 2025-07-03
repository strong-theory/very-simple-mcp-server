from mcp_lambda_handler import MCPLambdaHandler
from city import get_lat_lon, get_weather

mcp = MCPLambdaHandler(name="mcp-lambda-server", version="1.0.0")

@mcp.tool()
def weather(city: str) -> str:
    """
    Consulta o clima atual informando apenas o nome da cidade.
    Exemplo: clima("São Paulo")
    """
    lat, lon, error = get_lat_lon(city)
    if error:
        return error
    return get_weather(lat, lon)

def lambda_handler(event, context):
    """AWS Lambda handler function."""
    return mcp.handle_request(event, context)

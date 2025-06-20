from fastmcp import FastMCP
from city import get_lat_lon, get_weather

mcp = FastMCP("Starting mcp server...")

@mcp.tool
def weather(city: str) -> str:
    """
    Consulta o clima atual informando apenas o nome da cidade.
    Exemplo: clima("São Paulo")
    """
    lat, lon, error = get_lat_lon(city)
    if error:
        return error
    return get_weather(lat, lon)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",           # Bind to all interfaces
        port=9000,                # Custom port
        log_level="DEBUG",        # Override global log level
        path="/weather"
    )
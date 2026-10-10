from mcp.server.mcpserver import MCPServer

mcp = MCPServer("http-weather")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city. Returns temperature in Celsius."""
    data = {"Delhi": "38°C, sunny", "Mumbai": "31°C, humid"}
    return data.get(city, f"no data for '{city}'")

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
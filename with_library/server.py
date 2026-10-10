from mcp.server.mcpserver import MCPServer

mcp = MCPServer("library-weather")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city. Returns temperature in Celsius."""
    data = {"Delhi": "38°C, sunny", "Mumbai": "31°C, humid"}
    return data.get(city, f"no data for '{city}'")


@mcp.tool()
def get_calculator(expression: str) -> str:
    """Evaluate a math expression, e.g. '2 * (3 + 4)'."""
    return str(eval(expression, {"__builtins__": {}}))


if __name__ == "__main__":
    mcp.run()
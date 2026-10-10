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

@mcp.resource("weather://cities")
def list_cities() -> str:
    """The cities this server has weather data for."""
    return "Delhi, Mumbai"

@mcp.resource("weather://city/{name}")
def city_report(name: str) -> str:
    """A short weather report for one city."""
    data = {"Delhi": "38°C, sunny", "Mumbai": "31°C, humid"}
    return f"Weather report for {name}: {data.get(name, 'no data')}"

@mcp.prompt() 
def weather_summary(city: str) -> str:
    """Ask the AI for a friendly weather summary and packing tip for a city."""
    return (
        f"Use the get_weather tool to check the weather in {city}. "
        f"Then write a 2-line friendly summary with one packing tip."
    )
if __name__ == "__main__":
    mcp.run()
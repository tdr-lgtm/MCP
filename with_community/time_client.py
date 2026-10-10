import asyncio
from mcp import Client, StdioServerParameters

# Someone else's server: uvx downloads and runs it for us
server = StdioServerParameters(command="uvx", args=["mcp-server-time"])

async def main():
    async with Client(server) as client:
        tools = await client.list_tools()
        print("Tools on mcp-server-time:")
        for t in tools.tools:
            print(f"\n  - {t.name}: {t.description}")
            print(f"    inputs: {list(t.input_schema.get('properties', {}).keys())}")

        result = await client.call_tool("get_current_time", {"timezone": "Asia/Kolkata"})
        print("\nget_current_time(Asia/Kolkata) ->", result.content[0].text)

asyncio.run(main())
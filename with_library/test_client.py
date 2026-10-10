import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server = StdioServerParameters(command=sys.executable, args=["with_library/server.py"])

async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected!")

            tools = await session.list_tools()
            print("\nTools on this server:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")
                print(f"    input_schema: {t.input_schema}")

            result = await session.call_tool("get_weather", {"city": "Delhi"})
            print("\nget_weather(Delhi) ->", result.content[0].text)


asyncio.run(main())
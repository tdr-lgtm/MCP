import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Start YOUR hand-made server, using the same Python that runs this script
server = StdioServerParameters(command=sys.executable, args=["by_hand/hand_server.py"])

async def main():
    # start server, connect stdin/stdout
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            # sends "initialize" for you
            await session.initialize()
            print("Connected!")

            # sends "tools/list" for you
            tools = await session.list_tools()
            print("\nTools on your server:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            # sends "tools/call"
            result = await session.call_tool("get_weather", {"city": "Delhi"})
            print("\nget_weather(Delhi) ->", result.content[0].text)

            result = await session.call_tool("get_calculator", {"expression": "38 * 9 / 5 + 32"})
            print("get_calculator(...) ->", result.content[0].text)

asyncio.run(main())

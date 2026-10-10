import asyncio
from mcp import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        tools = await client.list_tools()
        print("Tools:", [t.name for t in tools.tools])

        result = await client.call_tool("get_weather", {"city": "Delhi"})
        print("get_weather(Delhi) ->", result.content[0].text)

asyncio.run(main())
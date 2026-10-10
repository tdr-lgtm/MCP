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

            result = await session.call_tool("get_weather", {"city": "Delhi"})
            print("\nget_weather(Delhi) ->", result.content[0].text)

            resources = await session.list_resources()
            print("\nResources:")
            for r in resources.resources:
                print(f"  - {r.uri}: {r.description}")

            templates = await session.list_resource_templates()
            print("\nResource templates:")
            for t in templates.resource_templates:
                print(f"  - {t.uri_template}: {t.description}")

            result = await session.read_resource("weather://cities")
            print("\nread weather://cities ->", result.contents[0].text)

            result = await session.read_resource("weather://city/Mumbai")
            print("read weather://city/Mumbai ->", result.contents[0].text)

            prompts = await session.list_prompts()
            print("\nPrompts:")
            for p in prompts.prompts:
                args = [a.name for a in p.arguments]
                print(f"  - {p.name}({', '.join(args)}): {p.description}")

            result = await session.get_prompt("weather_summary", {"city": "Delhi"})
            print("\nget_prompt(weather_summary, Delhi) ->")
            for m in result.messages:
                print(f"  [{m.role}] {m.content.text}")
            

asyncio.run(main())
import sys
import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server = StdioServerParameters(command=sys.executable, args=["with_library/server.py"])

def mcp_tool_to_openai(tool):
    """Convert one MCP tool into the format the LLM API expects."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema,
        },
    }

async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            schemas = [mcp_tool_to_openai(t) for t in tools.tools]

            print(json.dumps(schemas, indent=2, ensure_ascii=False))

asyncio.run(main())
import os
import sys
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv()
model = ChatOpenAI(
    model=os.environ["LLM_MODEL"],
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
)

server = StdioServerParameters(command=sys.executable, args=["with_library/server.py"])

def mcp_to_langchain(session, mcp_tool):
    async def call_server(**kwargs):
        result = await session.call_tool(mcp_tool.name, kwargs)   # same as Step 6
        return result.content[0].text

    return StructuredTool(
        name=mcp_tool.name,
        description=mcp_tool.description,
        args_schema=mcp_tool.input_schema,
        coroutine=call_server,
    )

async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()
            tools = [mcp_to_langchain(session, t) for t in mcp_tools.tools]
            print("Tools from server:", [t.name for t in tools])

            agent = create_agent(
                model=model,
                tools=tools,
                system_prompt="You are a helpful assistant. Use tools. Never do math in your head.",
            )

            question = "What's the weather in Delhi, in Fahrenheit?"
            print(f"\nQUESTION: {question}")
            result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})

            for m in result["messages"]:
                if m.type == "tool":
                    print(f"  [tool] {m.name} -> {m.content}")

            print(f"ANSWER: {result['messages'][-1].content}")

asyncio.run(main())
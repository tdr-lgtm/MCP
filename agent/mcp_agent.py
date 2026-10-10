import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
llm = AsyncOpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
MODEL = os.environ["LLM_MODEL"]

server = StdioServerParameters(command=sys.executable, args=["with_library/server.py"])

def mcp_tool_to_openai(tool):
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema,
        },
    }

async def run_agent(session, schemas, question, max_steps=5):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when needed. Never do math in your head."},
        {"role": "user", "content": question},
    ]

    for step in range(1, max_steps + 1):
        # 1. THINK: the LLM sees the tools that came from the MCP server
        res = await llm.chat.completions.create(model=MODEL, messages=messages, tools=schemas)
        msg = res.choices[0].message

        if not msg.tool_calls:
            return msg.content

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })

        # 2. ACT: ask the MCP SERVER to run the tool
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
                result = await session.call_tool(tc.function.name, args)    # ← the MCP call
                text = result.content[0].text
            except Exception as e:
                text = f"ERROR: {e}"
            print(f"  [step {step}] {tc.function.name}({tc.function.arguments}) -> {text}")

            # 3. OBSERVE: the result goes back to the LLM
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": text})

    return "Stopped: hit max steps"

async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            schemas = [mcp_tool_to_openai(t) for t in tools.tools]
            print("Tools from server:", [t.name for t in tools.tools])

            for question in [
                "What's the weather in Delhi, in Fahrenheit?",
                "Is Mumbai hotter than Delhi? By how many degrees?",
            ]:
                print(f"\nQUESTION: {question}")
                answer = await run_agent(session, schemas, question)
                print(f"ANSWER: {answer}")

asyncio.run(main())
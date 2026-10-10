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

weather_server = StdioServerParameters(command=sys.executable, args=["with_library/server.py"])
time_server = StdioServerParameters(command="uvx", args=["mcp-server-time"])

def mcp_tool_to_openai(tool):
    return {"type": "function",
            "function": {"name": tool.name, "description": tool.description,
                         "parameters": tool.input_schema}}

async def run_agent(name, system_prompt, question, session=None, schemas=None, max_steps=5):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": question}]

    for step in range(1, max_steps + 1):
        kwargs = {"model": MODEL, "messages": messages}
        if schemas:
            kwargs["tools"] = schemas
        res = await llm.chat.completions.create(**kwargs)
        msg = res.choices[0].message
        if not msg.tool_calls:
            return msg.content

        messages.append({"role": "assistant", "content": msg.content,
                         "tool_calls": [{"id": tc.id, "type": "function",
                                         "function": {"name": tc.function.name,
                                                      "arguments": tc.function.arguments}}
                                        for tc in msg.tool_calls]})

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
                result = await session.call_tool(tc.function.name, args)
                text = result.content[0].text
            except Exception as e:
                text = f"ERROR: {e}"
            print(f"  [{name}] {tc.function.name} -> {text}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": text})

    return "Stopped: hit max steps"

async def main():
    # Open BOTH servers at the same time: one session each
    async with stdio_client(weather_server) as (r1, w1), stdio_client(time_server) as (r2, w2):
        async with ClientSession(r1, w1) as weather_session, ClientSession(r2, w2) as time_session:
            await weather_session.initialize()
            await time_session.initialize()

            weather_tools = [mcp_tool_to_openai(t) for t in (await weather_session.list_tools()).tools]
            time_tools = [mcp_tool_to_openai(t) for t in (await time_session.list_tools()).tools]
            print("Weather agent tools:", [t["function"]["name"] for t in weather_tools])
            print("Time agent tools:   ", [t["function"]["name"] for t in time_tools])

            # Agent 1: weather (only the weather server)
            weather_facts = await run_agent(
                "WeatherAgent",
                "You check weather. Use your tools. Reply with one short line of facts.",
                "What's the weather in Delhi?",
                weather_session, weather_tools,
            )

            # Agent 2: time (only the time server)
            time_facts = await run_agent(
                "TimeAgent",
                "You handle time zones. Use your tools. Reply with one short line of facts.",
                "If it's 18:00 in Europe/London today, what time is it in Asia/Kolkata?",
                time_session, time_tools,
            )

            # Agent 3: writer (no server, no tools)
            note = await run_agent(
                "Writer",
                "You write short, friendly messages. Use ONLY the facts given.",
                f"Facts:\n- {weather_facts}\n- {time_facts}\n\n"
                f"Write a 2-line message to a friend in London about a 6 PM London-time call, "
                f"saying what time that is in Delhi and what the Delhi weather is.",
            )
            print(f"\n=== FINAL ===\n{note}")


asyncio.run(main())
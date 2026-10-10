# MCP From Scratch

A small learning project about **MCP (Model Context Protocol)**.

MCP is a standard way for an AI app to use tools. One program (the **server**) has the tools. Another program (the **client**, usually your AI agent) asks the server what tools it has and then asks it to run them.

This repo builds MCP step by step: first by hand with plain Python, then with the official library, then over HTTP, and finally with real AI agents that use the tools.

## The idea in one picture

Think of a restaurant:

- **Server = the kitchen.** It has the tools and runs them. It has no AI inside.
- **Client = the customer.** It is your agent or app. The AI (LLM) lives here.

```
 CLIENT (your agent)                 SERVER (has get_weather)
       │  "Hello, can we talk?"           │   initialize
       │ ───────────────────────────────▶ │
       │  "What tools do you have?"       │   tools/list
       │ ───────────────────────────────▶ │
       │  "I have get_weather"            │
       │ ◀─────────────────────────────── │
       │  "Run get_weather for Delhi"     │   tools/call
       │ ───────────────────────────────▶ │
       │  "38°C, sunny"                   │
       │ ◀─────────────────────────────── │
```

Every message is a small piece of JSON (the format is called JSON-RPC), for example:

```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
```

The `id` connects a question to its answer, like a token number at a bank counter.

## What is in this repo

| Folder | What it shows |
|---|---|
| `by_hand/` | An MCP server written with **only plain Python** (no MCP library). It reads JSON from stdin and writes answers to stdout. Good for seeing what really happens. |
| `with_library/` | The same server built with the official `mcp` library. Adds **resources** (data the client can read) and **prompts** (ready-made instructions). |
| `with_http/` | A server that talks over **HTTP** instead of stdin/stdout. |
| `with_community/` | A client that uses a server someone else made (`mcp-server-time`), downloaded and started with `uvx`. |
| `agent/` | Real AI agents that use MCP tools: a plain OpenAI-style agent, a LangChain agent, and a team of 3 agents that each use their own server. |

## Every file explained (read in this order)

Each step builds on the one before it, so it is best to read them top to bottom.

**Step 1: MCP by hand** (`by_hand/`)

| File | What it does |
|---|---|
| `by_hand/hand_server.py` | An MCP server made with plain Python only. It reads one JSON message per line from stdin, handles `initialize`, `tools/list` and `tools/call`, and writes the answer to stdout. If a message is broken, it sends back an error instead of crashing. |
| `by_hand/test_client.py` | Starts the hand-made server, connects to it, lists its tools, and calls `get_weather` and `get_calculator`. This shows that a server made by hand works with the official client. |

**Step 2: MCP with the official library** (`with_library/`)

| File | What it does |
|---|---|
| `with_library/server.py` | The same server, but the `mcp` library does the JSON work for you. You just write normal functions and add `@mcp.tool()`. It also adds 2 **resources** (`weather://cities` and `weather://city/{name}`, which hold data the client can read) and 1 **prompt** (`weather_summary`, a ready-made instruction for the AI). |
| `with_library/test_client.py` | Connects to that server and tries everything: lists and calls tools, lists and reads resources, and lists and gets prompts. |

**Step 3: MCP over HTTP** (`with_http/`)

| File | What it does |
|---|---|
| `with_http/http_server.py` | A weather server that runs as a web server at `http://localhost:8000/mcp` instead of using stdin/stdout. You start it yourself and it keeps running. |
| `with_http/http_client.py` | Connects to that web address, lists the tools, and calls `get_weather`. |

**Step 4: Using someone else's server** (`with_community/`)

| File | What it does |
|---|---|
| `with_community/time_client.py` | Uses `mcp-server-time`, a server that other people wrote. `uvx` downloads and starts it. The client prints its tools and asks for the current time in India. You never see the server's code, and you don't need to. |

**Step 5: AI agents that use MCP tools** (`agent/`)

| File | What it does |
|---|---|
| `agent/mcp_to_openai.py` | Gets the tools from the server and converts them into the format an LLM API expects (OpenAI "function" format), then prints them. No LLM is called. This is the bridge between MCP and the AI. |
| `agent/mcp_agent.py` | A full agent with no framework. The LLM sees the MCP tools and chooses one, the agent runs it on the server, and the result goes back to the LLM. This repeats until the LLM gives a final answer, up to 5 rounds. |
| `agent/langchain_agent.py` | The same agent built with LangChain. Each MCP tool is wrapped as a LangChain `StructuredTool`, and LangChain runs the loop. |
| `agent/multi_agent_mcp.py` | 3 agents work together. **WeatherAgent** uses only the weather server, and **TimeAgent** uses only the time server. **Writer** has no tools; it takes the other two agents' answers and writes a short message to a friend. |

**Project files**

| File | What it does |
|---|---|
| `pyproject.toml` | Project settings and the list of libraries it needs (`mcp`, `openai`, `langchain`, `python-dotenv`). |
| `uv.lock` | Exact library versions, so `uv sync` installs the same versions every time. Don't edit it by hand. |
| `.python-version` | Tells uv to use Python 3.12. |
| `.gitignore` | Files git should not save, like `.venv` and `.env` (your API key). |
| `.env` | Your LLM settings and API key. You create it yourself (see Setup). It is not in git. |
| `src/mcp_from_scratch/__init__.py` | Leftover from the project template (it only prints "Hello"). It is not used by any example. |

The demo servers have two simple tools:

- `get_weather(city)`: fake weather for Delhi and Mumbai.
- `get_calculator(expression)`: does math, like `38 * 9 / 5 + 32`.

## Setup

You need **Python 3.12+** and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

The scripts in `agent/` need an LLM. Make a file called `.env` in the project folder:

```
LLM_BASE_URL=https://your-provider/v1
LLM_API_KEY=your-key-here
LLM_MODEL=your-model-name
```

Any provider with an OpenAI-compatible API works. The `.env` file is ignored by git, so your key stays private.

## How to run

Run every command from the project root folder.

**1. Hand-made server** (no library):

```bash
uv run by_hand/test_client.py
```

**2. Library server** (tools, resources and prompts):

```bash
uv run with_library/test_client.py
```

**3. HTTP server** (needs two terminals):

```bash
# terminal 1
uv run with_http/http_server.py

# terminal 2
uv run with_http/http_client.py
```

**4. Someone else's server** (time zones):

```bash
uv run with_community/time_client.py
```

**5. AI agents** (need the `.env` file):

```bash
uv run agent/mcp_to_openai.py    # shows how MCP tools become LLM tool definitions (no LLM call)
uv run agent/mcp_agent.py        # an agent that answers questions using the MCP tools
uv run agent/langchain_agent.py  # the same idea, built with LangChain
uv run agent/multi_agent_mcp.py  # 3 agents: weather, time, and a writer that combines their answers
```

You don't start the stdio servers yourself. Each client starts its server in the background.

## Things worth knowing

- **stdout is only for messages.** In a stdio server, a normal `print()` breaks the connection, because the client expects JSON. Print debug text to stderr instead:
  ```python
  print("debug info", file=sys.stderr)
  ```
- **One message = one line.** The server reads one line, answers with one line, and repeats.
- **The calculator is for learning only.** It uses `eval()`, which is not safe for input from people you don't trust.

## Useful links

- [MCP documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

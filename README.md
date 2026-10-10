Example first: a restaurant.

The kitchen has the food and cooks it.

The customer doesn’t cook. They ask for what they want.

In MCP:

Server = the kitchen. It has the tools and runs them.

Client = the customer. It’s your agent or app. It asks the server for tools.

 CLIENT (your agent)                SERVER (has get_weather)
       │  "What tools do you have?"      │
       │ ──────────────────────────────▶ │
       │  "I have get_weather"           │
       │ ◀────────────────────────────── │
       │  "Run get_weather for Delhi"    │
       │ ──────────────────────────────▶ │
       │  "38°C, sunny"                  │
       │ ◀────────────────────────────── │


Important: the server has no LLM and no brain; it only has tools. The LLM lives on the client side, inside your agent.

Lesson 1, Part 3: the 3 things a client asks

When a client talks to a server, it always asks these 3 things, in this order:

1. “Hello, can we talk?”
Like a customer sitting down and the waiter saying “Welcome!” They agree to talk before anything else.
→ The method name is initialize.

2. “What tools do you have?”
Like asking “Can I see the menu?”
→ The method name is tools/list.
The server answers with each tool’s name, description, and what inputs it needs.

3. “Run this tool with these inputs.”
Like ordering “One masala dosa, please.”
→ The method name is tools/call.
The server runs the tool and sends back the result.

1. initialize   →  "Hello"            →  "Hello, I'm weather-tools"
2. tools/list   →  "Menu please"      →  "get_weather (needs: city)"
3. tools/call   →  "get_weather Delhi" →  "38°C, sunny"

Each of those 3 asks is sent as a small piece of JSON text. Here’s the “menu please” message:

json
{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

Only 3 parts:

"jsonrpc": "2.0" is always the same. It just means “this message follows the standard format.” (Jargon: JSON-RPC is the name of this message format.)
"method" is what you’re asking for: initialize, tools/list, or tools/call.
"id" is a number for this question.

And the server’s answer:

json
{"jsonrpc": "2.0", "id": 2, "result": {"tools": [...]}}

Look at the id: the question had 2, and the answer has 2. That’s how the client knows which answer belongs to which question, like a token number at a bank counter: you take token 2, and when “token 2” is called, you know it’s yours. (You saw this idea before as tool_call_id in Stage 0.)


Lesson 1, Part 5: how the messages travel (stdio)

The messages are text. But how does text get from the client to the server?

Example first: two people passing notes through two pipes.

Pipe 1: the client pushes notes into the server.
Pipe 2: the server pushes notes back out to the client.

Every program already has these pipes built in:

stdin (“standard input”): text going into a program. When you type in a terminal, you’re using stdin.
stdout (“standard output”): text coming out. A normal print() goes here.

(Jargon: using these two pipes to talk is called the stdio transport.)

CLIENT ──── stdin ────▶ SERVER      (questions go in)
CLIENT ◀─── stdout ──── SERVER      (answers come out)

The rule: one message = one line. The server reads one line, answers with one line, and repeats.

The danger: stdout is only for messages. If your server does a normal print("hello"), that line goes into the same pipe as the answers. The client expects JSON, gets hello, can’t understand it, and the connection breaks.

So where do debug messages go? Into a third pipe called stderr (“standard error”). The client ignores it, but you can still see it in the terminal:

python
print("debug info", file=sys.stderr)   # safe: goes to stderr, not the message pipe
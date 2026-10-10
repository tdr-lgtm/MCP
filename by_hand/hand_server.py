import json
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

def log(text):
    print(text, file=sys.stderr, flush=True)

def get_weather(city: str) -> str:
    data = {"Delhi": "38°C, sunny", "Mumbai": "31°C, humid"}
    return data.get(city, f"no data for '{city}'")

def get_calculator(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}))

TOOLS = {"get_weather": get_weather, "get_calculator": get_calculator}

TOOL_LIST = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city. Returns temperature in Celsius.",
        "inputSchema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },


    {
        "name": "get_calculator",
        "description": "Evaluate a math expression, e.g. '2 * (3 + 4)'.",
        "inputSchema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    }
]

def handle(request):
    method = request["method"]

    if method == "initialize":
        return {
            "protocolVersion": request["params"]["protocolVersion"],
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "hand-made-weather", "version": "0.1"},
        }

    if method == "tools/list":
        return {"tools": TOOL_LIST}

    if method == "tools/call":
        name = request["params"]["name"]
        args = request["params"]["arguments"]
        if name not in TOOLS:
            raise LookupError(f"Unknown tool: {name}")
        text = TOOLS[name](**args)
        return {"content": [{"type": "text", "text": text}]}

    raise NotImplementedError(f"Unknown method: {method}")

log("[server] waiting for messages...")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    # 1. Broken JSON? Answer with an error, don't crash
    try:
        request = json.loads(line)
    except json.JSONDecodeError:
        log("[server] got broken JSON")
        error = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Broken JSON"}}
        print(json.dumps(error), flush=True)
        continue

    # 2. No id = a notification: the client expects NO answer
    if "id" not in request:
        continue

    # 3. Try to answer; if anything fails, answer with an error instead of crashing
    try:
        response = {"jsonrpc": "2.0", "id": request["id"], "result": handle(request)}
    except NotImplementedError as e:
        response = {"jsonrpc": "2.0", "id": request["id"], "error": {"code": -32601, "message": str(e)}}
    except Exception as e:
        response = {"jsonrpc": "2.0", "id": request["id"], "error": {"code": -32602, "message": str(e)}}

    print(json.dumps(response, ensure_ascii=False), flush=True)
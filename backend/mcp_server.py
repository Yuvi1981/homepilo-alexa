import sys
import json
import logging
from typing import Dict, Any
from homebrain.mcp_tools import MCP_TOOL_DEFINITIONS, HomeBrainToolEngine
from homebrain.state_manager import state_manager

# Set up logging to stderr so stdout remains purely clean JSON-RPC
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(asctime)s [%(levelname)s] %(message)s")

def handle_initialize(msg_id: Any) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": "homebrain-mcp-server",
                "version": "1.0.0",
                "description": "HomeBrain Goal-Driven Smart Home Agent Protocol for Alexa+"
            }
        }
    }

def handle_tools_list(msg_id: Any) -> Dict[str, Any]:
    tools = []
    for tool_def in MCP_TOOL_DEFINITIONS:
        tools.append({
            "name": tool_def.name,
            "description": f"[{tool_def.domain}] {tool_def.description}",
            "inputSchema": tool_def.parameters
        })
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "tools": tools
        }
    }

def handle_tools_call(msg_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    logging.info(f"Executing MCP Tool: {tool_name} with params: {arguments}")

    result = HomeBrainToolEngine.execute_tool(tool_name, arguments, initiator="Alexa+ MCP Client")

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ],
            "isError": not result.get("success", True) if "success" in result else False
        }
    }

def main():
    logging.info("Starting HomeBrain MCP Stdio Server (12 Tools Registered)...")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "initialize":
                resp = handle_initialize(msg_id)
            elif method == "tools/list":
                resp = handle_tools_list(msg_id)
            elif method == "tools/call":
                resp = handle_tools_call(msg_id, req.get("params", {}))
            elif method == "ping":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            elif method == "notifications/initialized":
                continue
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            logging.error(f"Error handling message: {e}")
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()

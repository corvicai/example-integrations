import asyncio
import json
import argparse
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Load environment variables from .env file
load_dotenv()

class MCPExplorer:
    def __init__(self, url: str, token: str):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": token,
        }

    async def list_tools(self):
        """Lists all available tools and their schemas."""
        async with streamablehttp_client(self.url, headers=self.headers) as (read, write, session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                
                print("\n=== Available Tools ===")
                # list_tools returns a ListToolsResult object, which has a 'tools' attribute
                for tool in tools_result.tools:
                    print(f"\nTool: {tool.name}")
                    print(f"Description: {tool.description}")
                    print(f"Input Schema: {json.dumps(tool.inputSchema, indent=2)}")
                print("\n=======================")

    async def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None):
        """Calls a specific tool with arguments."""
        async with streamablehttp_client(self.url, headers=self.headers) as (read, write, session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print(f"\nExecuting tool: {tool_name}")
                if arguments:
                    print(f"Arguments: {json.dumps(arguments, indent=2)}")
                
                try:
                    result = await session.call_tool(tool_name, arguments=arguments or {})
                    print("\n--- Result ---")
                    print(result)
                    print("--------------")
                except Exception as e:
                    print(f"\nError calling tool '{tool_name}': {e}")

async def main():
    parser = argparse.ArgumentParser(description="MCP Tool Explorer")
    
    # Get defaults from environment variables
    env_url = os.getenv("MCP_URL")
    env_token = os.getenv("MCP_TOKEN")

    parser.add_argument("--url", default=env_url, help="MCP Server URL (can also be set via MCP_URL env var)")
    parser.add_argument("--token", default=env_token, help="Authorization Token (can also be set via MCP_TOKEN env var)")
    parser.add_argument("--list", action="store_true", help="List all available tools")
    parser.add_argument("--tool", type=str, help="Tool name to call")
    parser.add_argument("--args", type=str, help="JSON string of arguments for the tool")

    args = parser.parse_args()

    if not args.url or not args.token:
        print("Error: URL and Token are required. Provide them via CLI arguments or set MCP_URL and MCP_TOKEN in a .env file.")
        parser.print_help()
        return

    explorer = MCPExplorer(args.url, args.token)

    if args.list:
        await explorer.list_tools()
    elif args.tool:
        tool_args = {}
        if args.args:
            try:
                tool_args = json.loads(args.args)
            except json.JSONDecodeError:
                print("Error: --args must be a valid JSON string.")
                return
        await explorer.call_tool(args.tool, tool_args)
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())

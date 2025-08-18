import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def run():
    url = "<YOUR_CORVIC_AI_MCP_ENDPOINT>"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": "<YOUR_CORVIC_API_TOKEN>"
    }
    async with streamablehttp_client(url=url, headers=headers) as (read, write, session_id):
        async with ClientSession(read, write) as session:
            tools = await session.list_tools()
            print(tools)
            # Call a tool
            result = await session.call_tool(
                "query", arguments={"query_content": "What is the MPG for Valiant?"}
            )
            all_content = ''
            for content in result.content:
                all_content += content.text
                print(content.text)
            return all_content


if __name__ == "__main__":
    asyncio.run(run())

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run():
    async with sse_client(
            "<YOUR_CORVIC_AI_MCP_ENDPOINT>",  # Replace with your deployed agent's endpoint
            headers={
                "Authorization": "<YOUR_CORVIC_API_TOKEN>"  # Replace with your API token
            },
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(tools)

            # Call a tool
            result = await session.call_tool(
                "query", arguments={"query_content": "Map the NAICS code 441228 from 2017 to the 2022 NAICS code."}
            )
            # Save results to Markdown
            with open("naics_query.md", "a") as file:
                for content in result.content:
                    file.write(content.text)

if __name__ == "__main__":
    asyncio.run(run())

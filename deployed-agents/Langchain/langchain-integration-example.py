import asyncio
import os
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_community.agent_toolkits import FileManagementToolkit
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run():
    os.environ['OPENAI_API_KEY'] = 'YOUR-OPENAPI-KEY'
    token = 'YOUR-CORVIC-API-TOKEN'

    async with sse_client(
            "<YOUR_CORVIC_AI_MCP_ENDPOINT>",  # Replace with your deployed agent's endpoint
            headers={
                "Authorization": f"{token}"
            },
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            tools_lg = await load_mcp_tools(session)

            # Append the file management tools
            file_management_tools = FileManagementToolkit().get_tools()
            tools_lg.extend(file_management_tools)

            # Create and run a react agent with the tools
            agent = create_react_agent("openai:gpt-4.1", tools_lg)
            
            # Invoke the agent with a message
            agent_response = await agent.ainvoke({
                "messages": "As per NAICS codes, Describe wheat farming. Use tools to answer this question. "
                            "The answer should be written to a file named results.md. "
                            "Write the date and time of the response in the file."
            })

            print(agent_response)

if __name__ == "__main__":
    asyncio.run(run())

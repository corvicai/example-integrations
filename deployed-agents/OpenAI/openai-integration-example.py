from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams

async def run():
    params = MCPServerStreamableHttpParams(
        url="MCP_ENDPOINT",
        # Replace with your deployed agent's endpoint
        headers={
            "Authorization": "YOUR_CORVIC_API_TOKEN",
            # Replace with your API token
        },
        timeout=500
    )
    corvic_mcp_server = MCPServerStreamableHttp(name="corvic agent", params=params, client_session_timeout_seconds=500)
    print('connecting')
    await corvic_mcp_server.connect()
    tools = await corvic_mcp_server.list_tools()
    print(tools)

    #
    agent = Agent(
        name="Analyst",
        instructions="Use the tools to achieve the task",
        mcp_servers=[corvic_mcp_server]
    )
    #
    result = await Runner.run(agent, "YOUR QUERY HERE")
    print(result.final_output)
    await corvic_mcp_server.cleanup()

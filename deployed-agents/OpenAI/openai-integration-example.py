from agents import Agent, Runner
from agents.mcp import MCPServerSseParams, MCPServerSse

async def run():
    params = MCPServerSseParams(
        url="<YOUR_CORVIC_AI_MCP_ENDPOINT>",  # Replace with your deployed agent's endpoint
        headers={
            "Authorization": "<YOUR_CORVIC_API_TOKEN>"  # Replace with your API token
        },
        timeout=500,
        sse_read_timeout=500
    )
    corvic_mcp_server = MCPServerSse(name="corvic agent", params=params, client_session_timeout_seconds=500)
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
    result = await Runner.run(agent, "Group all the data by name and find the top titles by "
                                     "global sales. Output the name and the total global sales in a "
                                     "tabular format.")
    print(result.final_output)
    await corvic_mcp_server.cleanup()

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
        name = "Assistant",
        instructions = "Use the tools to answer the questions. Do not add any additional information.",
        mcp_servers=[corvic_mcp_server]
    )
    #
    result = await Runner.run(agent, "As per NAICS codes, Describe wheat farming.")
    print(result.final_output)

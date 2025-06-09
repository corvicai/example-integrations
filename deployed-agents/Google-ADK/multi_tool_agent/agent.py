import asyncio
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from mcp import ClientSession
from mcp.client.sse import sse_client
import nest_asyncio

nest_asyncio.apply()


async def run(customer_id):
    async with sse_client(
            "YOUR-CORVIC-MCP-SSE-ENDPOINT-GOES-HERE",
            headers={
                "Authorization": "YOUR-API-TOKEN-GOES-HERE"
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
                "query", arguments={"query_content": f"Provide the total sales amount for customer id {customer_id}"}
            )
            return result


def get_sales_data(customer_id: str) -> dict:
    """Retrieves the sales data for the customer id.

        Args:
            customer_id (str): The id of the customer.

        Returns:
            dict: status and result or error msg.
        """
    final_response = asyncio.run(run(customer_id))

    return {
        "status": "success",
        "report": (
            f"Corvic response: {repr(final_response)}"
        ),
    }


root_agent = Agent(
    name="Sales_Reporting_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to provide sales data for a given customer id."
    ),
    instruction=(
        "Only answer based on the tool, and dont add any information of your own. You are a helpful agent who can answer user questions about sales to a customer."
    ),
    tools=[get_sales_data],
)

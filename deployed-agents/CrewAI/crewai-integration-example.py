#!/usr/bin/env python
import warnings

from crewai import Agent, Crew, Process, Task
from crewai_tools import MCPServerAdapter

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    token = 'YOUR-CORVIC-TOKEN-HERE'
    server_params = {
        "url": "YOUR-MCP-URL-HERE",
        # Replace with your actual Streamable HTTP server URL
        "headers": {
            "Authorization": f"{token}"
        },
        "timeout": 6000,
        "transport": "streamable-http"
    }

    try:
        with MCPServerAdapter(server_params) as tools:
            print(f"Available tools (manual Streamable HTTP): {[tool.name for tool in tools]}")

            http_agent = Agent(
                role="HTTP Service Integrator",
                goal="Utilize tools from a remote MCP server via Streamable HTTP.",
                backstory="An AI agent adept at interacting with complex web services.",
                tools=tools,
                verbose=True,
            )

            http_task = Task(
                description="What is the mpg for valiant?",
                expected_output="The result of the complex data query.",
                agent=http_agent,
            )

            http_crew = Crew(
                agents=[http_agent],
                tasks=[http_task],
                verbose=True,
                process=Process.sequential
            )
            """Creates the CrewWithCorvic crew"""
            result = http_crew.kickoff()
            print(result)

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


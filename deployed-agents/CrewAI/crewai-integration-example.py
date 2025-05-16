from crewai import Agent, Task, Crew, Process
from tools.serper import SerperDevTool
from tools.file_writer import FileWriterTool
from mcp_adapter import MCPServerAdapter

token = "YOUR-CORVIC-API-TOKEN"

serverparams = {
    "url": "<YOUR_CORVIC_AI_MCP_ENDPOINT>",  # Replace with your deployed agent's endpoint
    "headers": {
        "Authorization": f"{token}"
    }
}

with MCPServerAdapter(serverparams) as tools:
    print('configuring agent')

    analyst = Agent(
        role='Customer service agent',
        goal="Pass the following question to the tool as is (do not convert to SQL): Group all the data by Genre and find the top titles by global sales. Provide the top 1 genre in a tabular format.",
        backstory='You are a customer service expert',
        verbose=True,
        allow_delegation=False,
        tools=tools
    )

    content_tool = SerperDevTool()
    content_researcher = Agent(
        role="Content Researcher",
        goal="Look for genre information in the data returned by the analyst and find relevant content for that genre. Return top 3 hits",
        backstory="You are a content recommender",
        tools=[content_tool],
        verbose=True,
    )

    fw_tool = FileWriterTool()
    writer = Agent(
        role='Creative writer',
        goal="Data from content_researcher should be written to a file named results_with_content.md in markdown format.",
        backstory='You are a documentation expert',
        verbose=True,
        allow_delegation=False,
        tools=[fw_tool]
    )

    print('configuring tasks')
    corvic_task = Task(
        description="Understand the question and provide response after using tools",
        agent=analyst,
        expected_output='Give a correct response'
    )

    content_recommender_task = Task(
        description="Search and recommend content based on response from analyst",
        agent=content_researcher,
        expected_output="Interesting content"
    )

    writing_task = Task(
        description="Write all the data from the content_researcher to a file",
        agent=writer,
        expected_output='Status of writing to file'
    )

    print('configuring crew')
    crew = Crew(
        agents=[analyst, content_researcher, writer],
        tasks=[corvic_task, content_recommender_task, writing_task],
        process=Process.sequential,
        verbose=True
    )

    print('running')
    result = crew.kickoff()
    print(result)

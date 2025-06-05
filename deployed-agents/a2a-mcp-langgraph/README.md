# Corvic MCP with A2A Protocol: Featuring LangGraph 

This sample demonstrates a sales reporting agent built with [LangGraph](https://langchain-ai.github.io/langgraph/) and exposed through the A2A protocol.

## How It Works

This agent leverages a Corvic agent, orchestrated by LangGraph with Google Gemini to sales information through a ReAct agent pattern. The A2A protocol enables standardized interaction with the agent, allowing clients to send requests and receive updates.

## Prerequisites

- Python 3.12 or higher
- [UV](https://docs.astral.sh/uv/)
- Access to an LLM and API Key
- A Corvic agent that provides sales data given some customer ids. You will need the sse-endpoint and the authorization token


## Configuration 
- The LangGraph ReAct agent is provided two tools, the `get_duplicates` tool and the `answer_sales_query` tool. The `get_duplicates` is a mock tool that just returns two customer ids
- The `answer_sales_query` invokes a deployed agent using Model Context Protocol (MCP). This agent is able to provide total sales data for customer based on their ids. You are free to create the Corvic agent anyway you like, but it should respond this sales data.
- When you run the client, the LangGraph agent is passed the following question: `Provide sales data for customer 1234`
- The LangGraph will first call the `get_duplicates` tool to get duplicates. The LangGraph agent will then pass all customer and duplicates and get the total sales data


## Setup & Running

1. Navigate to the directory and run uv sync:
   ```bash
   uv sync
   ```

2. Create an environment file with your API key:

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3. Run the agent:

   ```bash
   # Basic run on default port 10000
   uv run app

   # On custom host/port
   uv run app --host 0.0.0.0 --port 8080
   ```

4. In a separate terminal, run the test client:

   ```bash
   uv run app/test_client.py
   ```


## Learn More

- [A2A Protocol Documentation](https://google-a2a.github.io/A2A/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Google Gemini API](https://ai.google.dev/gemini-api)
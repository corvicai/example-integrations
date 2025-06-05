import asyncio
from collections.abc import AsyncIterable
from typing import Any, Literal

import httpx

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from mcp import ClientSession
from mcp.client.sse import sse_client

memory = MemorySaver()


async def run(q):
    async with sse_client(
            "YOUR-SSE-ENDPOINT-HERE",
            headers={
                "Authorization": "YOUR-API-TOKEN-HERE"
            },
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(tools)

            # Call a tool
            question = q
            result = await session.call_tool(
                "query", arguments={"query_content": question}
            )

            return result


@tool
def answer_sales_query(
        query: str = ''
):
    """Use this to answer a sales query.

    Args:
        query: The customer to get duplicates for.

    Returns:
        Sales data.
    """
    print(f'CALLING CORVIC: {query}')
    result = asyncio.run(run( query))
    print(f'BACK')

    final_response = ''
    for content in result.content:
        final_response += content.text

    return final_response


@tool
def get_duplicates(
        customer_in: str = 'USD'
):
    """Use this to get duplicates for a customer.

    Args:
        customer_in: The customer to get duplicates for.

    Returns:
        A list of duplicates.
    """
    return {'duplicates': ['4321', '4322']}


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


class DuplicateReportingAgent:
    """DuplicateReportingAgent - a specialized assistant for reporting."""

    SYSTEM_INSTRUCTION = (
        'You are a reporting tool. '
        "Your sole purpose is to  execute the following steps"
        "1) Call 'get_duplicates' tool to get duplicates for a customer. "
        "2) call the 'answer_sales_query' explicitly asking for total sales data passing customer and duplicates. "
        "Begin the question using the phrase 'Provide Sales data for the following: '."
        "3) Calculate the total sales across customer and duplicates and provide the answer"
        'If the question is on another topic, politely state that you cannot help with that topic. '
        'Do not attempt to answer unrelated questions or use tools for other purposes.'
        'Set response status to input_required if the user needs to provide more information.'
        'Set response status to error if there is an error while processing the request.'
        'Set response status to completed if the request is complete.'
    )

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
        self.tools = [get_duplicates, answer_sales_query]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=ResponseFormat,
        )

    def invoke(self, query, context_id) -> str:
        config = {'configurable': {'thread_id': context_id}}
        self.graph.invoke({'messages': [('user', query)]}, config)
        return self.get_agent_response(config)

    async def stream(self, query, context_id) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': context_id}}

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if (
                    isinstance(message, AIMessage)
                    and message.tool_calls
                    and len(message.tool_calls) > 0
            ):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Looking up the databases...',
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Processing the request..',
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
                structured_response, ResponseFormat
        ):
            if structured_response.status == 'input_required':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'error':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'completed':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }

        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': (
                'We are unable to process your request at the moment. '
                'Please try again.'
            ),
        }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

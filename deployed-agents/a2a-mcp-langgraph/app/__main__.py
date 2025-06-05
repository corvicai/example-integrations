import logging
import os
import sys

import click
import httpx
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv

from app.agent import DuplicateReportingAgent
from app.agent_executor import SalesAgentExecutor


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10000)
def main(host, port):
    """Starts the Currency Agent server."""
    try:
        if not os.getenv('GOOGLE_API_KEY'):
            raise MissingAPIKeyError(
                'GOOGLE_API_KEY environment variable not set.'
            )

        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
        skill = AgentSkill(
            id='get_duplicates',
            name='Tool to get Duplicate customers',
            description='Helps with getting duplicate customers',
            tags=['duplicate customers', 'Duplicate reporting'],
            examples=['Provide duplicates for customer 1234'],
        )
        skill_sales = AgentSkill(
            id='answer_sales_query',
            name='Tool to get Sales data for customers ',
            description='Helps with getting sales data for customers',
            tags=['Sales data', 'Sales data for customer'],
            examples=['Provide sales data for customer 1234'],
        )
        agent_card = AgentCard(
            name='Reporting Agent',
            description='Helps with reporting customer data',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=DuplicateReportingAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=DuplicateReportingAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill, skill_sales],
        )

        # --8<-- [start:DefaultRequestHandler]
        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=SalesAgentExecutor(),
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(httpx_client),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        uvicorn.run(server.build(), host=host, port=port)
        # --8<-- [end:DefaultRequestHandler]

    except MissingAPIKeyError as e:
        logger.error(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()

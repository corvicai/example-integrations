import asyncio
import httpx
from fastapi import FastAPI, Form, BackgroundTasks
from mcp import ClientSession
from mcp.client.sse import sse_client

app = FastAPI()

async def process_query_and_respond(text: str, response_url: str):
    try:
        async with sse_client(
            "<YOUR_CORVIC_AI_MCP_ENDPOINT>",  # Replace with your Corvic MCP agent URL
            headers={
                "Authorization": "YOUR-CORVIC-API-TOKEN"
            },
        ) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("query", arguments={"query_content": text})
                response_text = (
                    result.content[0].text if result.content else "No content found."
                )

        async with httpx.AsyncClient() as client:
            await client.post(
                response_url,
                json={
                    "response_type": "in_channel",
                    "text": response_text,
                },
                headers={"Content-Type": "application/json"},
            )
    except Exception as e:
        async with httpx.AsyncClient() as client:
            await client.post(
                response_url,
                json={
                    "response_type": "ephemeral",
                    "text": f"Failed to process your request: {str(e)}",
                },
                headers={"Content-Type": "application/json"},
            )

@app.post("/mcp/ask")
async def mcp_handler(
    text: str = Form(...),
    response_url: str = Form(...),
    background_tasks: BackgroundTasks = None
):
    background_tasks.add_task(process_query_and_respond, text, response_url)
    return {
        "response_type": "ephemeral",
        "text": "Processing your request..."
    }

@app.get("/")
def root():
    return {"status": "ok"}

import asyncio
import pandas as pd
from mcp import ClientSession
from mcp.client.sse import sse_client

# Paths
# Input schema: id, question, expected_answer, ...
INPUT_CSV_PATH = "<PATH/TO/Question_CSV_file.csv>"

# Output schema: id, question, expected_answer, response, 
OUTPUT_PATH = "/PATH_TO_STORE_RESPONSES/output.xlsx"

# Corvic MCP setup
MCP_URL = "<YOUR_CORVIC_AI_MCP_ENDPOINT>"
HEADERS = {
    "Authorization": "YOUR-CORVIC-API-TOKEN"
}

async def query_agent(session, question):
    try:
        result = await session.call_tool(
            "query", arguments={"query_content": question}
        )

        if result.content and len(result.content) > 0:
            return result.content[0].text
        return "No content returned"
    except Exception as e:
        return f"Error: {e}"

async def run():
    df = pd.read_csv(INPUT_CSV_PATH)
    results = []

    async with sse_client(MCP_URL, headers=HEADERS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            for _, row in df.iterrows():
                query = row['question']
                id_ = row['id']
                expected = row['expected_answer']

                print(f"Querying ID {id_}: {query}")
                response = await query_agent(session, query)
                print(f"Response: {response}")

                results.append({
                    "id": id_,
                    "question": query,
                    "expected_answer": expected,
                    "response": response
                })

    pd.DataFrame(results).to_excel(OUTPUT_PATH, index=False)
    print(f"✅ Done. Results saved to {OUTPUT_PATH}")

# To run inside notebook
# await run()

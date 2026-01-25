# MCP Tool Explorer

A utility script to explore and interact with Model Context Protocol (MCP) tools provided by the Corvic API.

## Features

- **List Tools**: Dynamically fetch and display all available tools, their descriptions, and input schemas.
- **Call Tools**: Invoke specific tools with custom JSON arguments via the command line.
- **Environment Support**: Securely load your MCP URL and Authorization Token from a `.env` file.

## Setup

1. **Clone or copy the files** to your project directory.

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install mcp python-dotenv
   ```

4. **Configure Environment Variables**:
   Copy the example environment file and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set your `MCP_URL` and `MCP_TOKEN`.

## Usage

### List Available Tools
To see all tools supported by the agent:
```bash
python3 explore_mcp_tools.py --list
```

### Call a Specific Tool
To execute a tool, provide its name and a JSON string for the arguments:
```bash
python3 explore_mcp_tools.py --tool query --args '{"query_content": "Who are you?"}'
```

### Override Configuration
You can also pass the URL and Token directly via CLI arguments:
```bash
python3 explore_mcp_tools.py --url <YOUR_URL> --token <YOUR_TOKEN> --list
```

## Detailed Tool Examples

Here are examples of how to call each available tool using the CLI:

### 1. Query
Ask a question to the agent:
```bash
python3 explore_mcp_tools.py --tool query --args '{"query_content": "Tell me more about the data.", "with_citation": true}'
```

### 2. Get Resource Download URL
Get URLs for specific resource IDs (usually obtained from citations in a query result):
```bash
python3 explore_mcp_tools.py --tool get_resource_download_url --args '{"resource_ids": ["res_123", "res_456"]}'
```

### 3. Get Resources
Inquire about specific file paths:
```bash
python3 explore_mcp_tools.py --tool get_resources --args '{
  "original_paths": [
    "corvic-test-container/micheldizTest/Developer_Manual.pdf",
    "corvic-test-container/micheldizTest/CorvicAPI.pdf"
  ]
}'
```

### 4. Sync Agent Data App
Trigger a synchronization of the data application:
```bash
python3 explore_mcp_tools.py --tool sync_agent_data_app
```

### 5. Deploy Agent
Deploy the agent to apply the latest changes/data:
```bash
python3 explore_mcp_tools.py --tool deploy_agent
```

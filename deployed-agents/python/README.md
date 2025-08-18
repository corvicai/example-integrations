# 🐍 Corvic AI Python Integration Example using MCP (HTTP Streamable)

This example demonstrates how to use the Corvic AI MCP (HTTP) protocol in Python to query a deployed agent that processes PDF-based enterprise data.

---


## 🧰 Integration Steps

1. Use the `mcp` Python package to create an `streamablehttp_client` connection to the deployed agent.
2. Pass the MCP endpoint and your API token in the request headers.
3. Initialize the session and retrieve the list of available tools (Corvic currently supports a single tool: `query`).
4. Call the `query` tool with your question via the `query_content` argument.
5. Save the response to a markdown file for review.

---

## 🧠 Question Asked

```text
What is the MPG for Valiant?
```

## 📤 Response

The response will look as below. 

The MPG for Valiant is 18
---

## 📄 Notes

- The `query_content` argument is **required**.
- Replace the placeholder token with your actual Corvic API token and Agent URI.
---

Need help? Contact [support@corvic.ai](mailto:support@corvic.ai) or visit [https://www.corvic.ai](https://www.corvic.ai).

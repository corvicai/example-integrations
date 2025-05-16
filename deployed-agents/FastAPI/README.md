# 🌐 Wrapping Corvic MCP with FastAPI for Web Integrations

This example demonstrates how to expose Corvic's MCP protocol through a FastAPI web endpoint. This makes it easy to integrate Corvic-powered agents into external services like Slack, Discord, webhooks, or custom UIs.

---

## 📘 Use Case

You want to expose a Corvic agent to external clients (e.g., Slack command, customer service UI, webhooks) via a simple HTTP endpoint. This FastAPI app acts as a bridge between those services and Corvic's MCP-based query interface.

---

## ✅ Key Points

1. The `slack_handler` (general-purpose POST endpoint) receives a user query via HTTP POST.
2. The `process_query_and_respond` method:
   - Initializes an `sse_client` connection to your deployed Corvic agent.
   - Sends a `query_content` to Corvic via the `ClientSession`.
   - Forwards the response to a webhook (e.g., `response_url`).
3. The `response_url` mechanism enables compatibility with asynchronous platforms like Slack or others expecting delayed responses.

---

Need help? Contact [support@corvic.ai](mailto:support@corvic.ai) or visit [https://www.corvic.ai](https://www.corvic.ai).
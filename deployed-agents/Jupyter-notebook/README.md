# 🧪 Corvic MCP for GenAI Agent Testing

This example demonstrates how to build a lightweight GenAI testing framework using Corvic MCP and a Jupyter notebook. It reads structured test queries from a CSV file, invokes a Corvic-powered agent, and saves the responses alongside expected answers for comparison.

---

## 📘 Use Case

You want to automatically evaluate the output of a Corvic agent across a list of test questions with known expected answers. This is useful for regression testing, QA, and validation of LLM-based applications.

---

## ✅ Steps

1. **Configure Corvic Agent Endpoint**:
   - Set `MCP_URL` to your deployed Corvic agent's endpoint.
   - Set the `HEADERS` with your Corvic API token.

2. **Prepare the Input Dataset**:
   - Create a CSV file with at least the following columns:
     - `id`
     - `question`
     - `expected_answer`
   - Set the `INPUT_CSV_PATH` to the location of this CSV file.

3. **Configure Output**:
   - Set the `OUTPUT_PATH` where the agent’s responses will be written as an Excel file.

---

## 📄 Input Format (CSV)

```
id,question,expected_answer
1,What is the NAICS code for wheat farming?,111140
2,How is retail defined in NAICS?,Retail involves selling goods directly to customers,...
```

## 📤 Output

An Excel file containing the following columns:

- `id`
- `question`
- `expected_answer` (expected answer)
- `response` (from Corvic)

---

Need help? Contact [support@corvic.ai](mailto:support@corvic.ai) or visit [https://www.corvic.ai](https://www.corvic.ai).
# 🎮 Corvic AI + OpenAI Integration: Structured Data Example

This example demonstrates how to integrate Corvic AI with an OpenAI agent framework to analyze structured data from a parquet file containing video game sales information.

---

## 📘 Use Case

In this tutorial, you'll upload a parquet file containing data about video game sales and ask Corvic to provide a report.

---

## ✅ Prerequisites

1. **Download the CSV Dataset**: Obtain the video game sales data from [Kaggle](https://www.kaggle.com/datasets/gregorut/videogamesales).

2. **Convert CSV to Parquet**: Use Python to convert the CSV file to Parquet format:

   ```python
   import pandas as pd

   df = pd.read_csv("vgsales.csv")
   df.to_parquet("vgsales.parquet", index=False)
   ```

3. **Upload to Corvic**: Follow the documentation [here](https://app.corvic.ai/docs/howToUseCorvic#create-pipelines) to create an agent using this parquet file.

4. **Deploy the Agent**: Deploy the agent and obtain the MCP endpoint and access token.

---

## 🧠 Question Asked

```text
Group all the data by name and find the top titles by global sales. 
Output the name and the total global sales in a tabular format."
```

## 📤 Response

The Corvic agent will process the parquet data and return a report including the top-performing video game titles.

| Title                       | Total Global Sales |
| --------------------------- | ------------------ |
| Grand Theft Auto V          | 64.29              |
| Call of Duty: Black Ops     | 30.99              |
| Call of Duty: Modern Warfare 3 | 30.71              |
| Call of Duty: Black Ops II    | 29.59              |
| Call of Duty: Ghosts          | 28.80              |
| Call of Duty: Black Ops 3     | 26.72              |
| Call of Duty: Modern Warfare 2 | 25.02              |
| Minecraft                   | 24.01              |
| Grand Theft Auto IV         | 22.53              |
| Call of Duty: Advanced Warfare| 21.78              |

---

## 📄 Notes

- Ensure that the `vgsales.parquet` file is correctly formatted and uploaded to the Corvic platform.
- Replace `<MCP_ENDPOINT>` and `<YOUR_CORVIC_API_TOKEN>` with your actual endpoint and token.
- The agent is instructed to use tools exclusively for answering queries.

---

Need help? Contact [support@corvic.ai](mailto:support@corvic.ai) or visit [https://www.corvic.ai](https://www.corvic.ai).
# 1 Installation Steps #

Install Ragas
```shell
pip install ragas
```

Install MCP
```shell
pip install mcp
```

Install langchain-openai
```shell
pip install langchain-openai
```

Install polars
```shell
pip install polars
```

Install tqdm (progress meter)
```shell
pip install tqdm
```

# 2 Provide the questions  #
Provide the questions in a json format as shown in the example below

```json
[
  {"id": 1,"query": "question 1","ground_truth": "ground truth for question 1"},
  {"id": 2,"query": "question 2","ground_truth": "ground truth for question 2"}
]
```

# 3 Launch the benchmark #
In order to launch the benchmark you need to provide a few arguments.
Apart from the questions file from step 2, you will need to pass the MCP endpoint and token
```shell
python run_bench_with_mcp.py --benchmark_file <QUESTIONS JSON FILE> --mcp_url <MCP URL> --token <<MCP URL>> 
```
Note: the current version of this script works with OpenAI. Please provide the key in os environment variable `OPENAI_API_KEY`
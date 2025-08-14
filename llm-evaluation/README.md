# 1 Installation Steps

Install all dependencies from `requirements.txt`:
```shell
pip install -r requirements.txt
```

# 2 Provide the questions
Provide the questions in a JSON format as shown in the example below:

```json
[
  {"id": 1, "query": "question 1", "ground_truth": "ground truth for question 1"},
  {"id": 2, "query": "question 2", "ground_truth": "ground truth for question 2"}
]
```
Note: Please make sure questions json file is in the same directory as the script.

# 3 Set OpenAI API Key
The current version of this script works with OpenAI. Please provide the key in the OS environment variable `OPENAI_API_KEY`:
```shell
export OPENAI_API_KEY="<your_openai_api_key>"
```

# 4 Launch the benchmark
In order to launch the benchmark you need to provide a few arguments. Apart from the questions file from step 2, you will need to pass the MCP endpoint and token:
```shell
python run_bench_with_mcp.py --benchmark_file <QUESTIONS JSON FILE> --mcp_url <MCP URL> --token <MCP TOKEN>
```

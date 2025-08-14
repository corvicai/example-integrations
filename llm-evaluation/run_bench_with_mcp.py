"""End-to-end benchmark script for the agent."""

import argparse
import asyncio
import dataclasses
import json
import time
from pathlib import Path
import os
import polars as pl
import structlog
from aiolimiter import AsyncLimiter
from langchain_openai import ChatOpenAI
from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt
from tqdm import tqdm


import argparse
import asyncio
from pathlib import Path
from typing import Any

import structlog
from langchain_google_vertexai import ChatVertexAI
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import AnswerAccuracy


_logger = structlog.get_logger()

MAX_PROBLEMS = 200

def get_llm_config(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "model": args.eval_model,
        "temperature": 0.4,
        "max_tokens": None,
        "top_p": 0.8,
    }


async def score_row(
    question, response, reference, evaluator_llm: LangchainLLMWrapper, llm_config: dict[str, Any]
) -> dict[str, Any]:
    # question = row["query"]
    # response = row["response"]
    # reference = row["ground_truth"]

    sample = SingleTurnSample(
        user_input=question,
        response=response,
        reference=reference,
    )
    scorer = AnswerAccuracy(llm=evaluator_llm)
    score = await scorer.single_turn_ascore(sample)

    # row.update({"evaluation_model": llm_config["model"], "score": score})
    return {"evaluation_model": llm_config["model"], "score": score}


@dataclasses.dataclass
class E2EBenchmarkProblem:
    """End-to-End Benchmark Problem."""

    id: int
    query: str
    ground_truth: str


class E2EBenchmarkResult(BaseModel):
    """End-to-End Benchmark Result."""

    id: int
    query: str
    response: str
    ground_truth: str
    score: float
    message_id: str | None = None
    latency: float | None = None


def load_checkpoint_results(checkpoint_path: Path) -> list[E2EBenchmarkResult]:
    if not checkpoint_path.exists():
        return []

    results: list[E2EBenchmarkResult] = []
    with checkpoint_path.open("r") as f:
        for line in f:
            result = json.loads(line)
            results.append(E2EBenchmarkResult.model_validate(result))
    return results


def load_checkpoint_ids(checkpoint_path: Path) -> set[int]:
    results = load_checkpoint_results(checkpoint_path)
    return {result.id for result in results}


def save_results(args: argparse.Namespace, results: list[E2EBenchmarkResult]):
    results_df = pl.from_records([result.model_dump() for result in results])
    output_file = Path(args.output_path)
    results_df.write_json(args.output_path)
    results_df = results_df.with_columns(
        [
            pl.col("response")
            .str.split("\n\n#### Visual Context", inclusive=False)
            .list.get(0)
            .alias("response")
        ]
    )
    results_df.write_csv(output_file.with_suffix(".csv"))
    _logger.info(
        "Benchmark results saved to",
        json_file=output_file,
        csv_file=output_file.with_suffix(".csv"),
    )
    checkpoint_path = Path(args.checkpoint_path)
    if checkpoint_path.exists():
        _logger.info("Deleting checkpoint file", path=checkpoint_path)
        checkpoint_path.unlink()


async def checkpoint_writer(
    result_queue: asyncio.Queue[E2EBenchmarkResult | None], checkpoint_path: Path
):
    _logger.info("Starting checkpoint writer", path=checkpoint_path)
    with checkpoint_path.open("a") as f:
        while True:
            result = await result_queue.get()
            if not result:
                break
            json.dump(result.model_dump(), f)
            _ = f.write("\n")
            f.flush()
            result_queue.task_done()

@retry(stop=stop_after_attempt(3))
async def _process_row_sse_with_retry(
    args: argparse.Namespace,  problem: E2EBenchmarkProblem, evaluator_llm, llm_config,index: int, total: int
) -> E2EBenchmarkResult:
    async with sse_client(
        args.mcp_url,
        headers={"Authorization": args.token},
    ) as (read, write):
        async with ClientSession(read, write) as session:
            ## Initialize the connection
            _ = await session.initialize()

            _logger.info("Asking agent via sse", query=problem.query, index=f"{index + 1}/{total}")

            latency = None
            message_id = None
            answer = ""
            time_start = time.time()
            try:
                response = await session.call_tool(
                    "query", arguments={"query_content": problem.query}
                )
                #now score the result
                scored_response=await score_row(problem.query, response.content[0].text,problem.ground_truth,evaluator_llm, llm_config)

            except Exception as e:
                _logger.exception(
                    "Error asking agent",
                    query=problem.query,
                    index=f"{index + 1}/{total}",
                    error=str(e),
                )
                _logger.info(
                    "Retrying agent query",
                    query=problem.query,
                    index=f"{index + 1}/{total}",
                )
                raise

            match response.content[0]:
                case types.TextContent() as text_content:
                    latency = time.time() - time_start
                    answer = text_content.text
                    if text_content.meta:
                        message_id = text_content.meta.get("message_id")
                case (
                types.ImageContent()
                | types.EmbeddedResource()
                | types.AudioContent()
                | types.ResourceLink()
                ):
                    answer = "Invalid response datatype"
                    _logger.exception(
                        "Agent returned incorrect datatype", query=problem.query
                    )
            score=float(scored_response["score"])
            return E2EBenchmarkResult(
                                id=problem.id,
                                query=problem.query,
                                response=answer,
                                score=score,
                                ground_truth=problem.ground_truth,
                                message_id=message_id,
                                latency=latency,
                            )




@retry(stop=stop_after_attempt(3))
async def _process_row_with_retry(
    args: argparse.Namespace, problem: E2EBenchmarkProblem, index: int, total: int
) -> E2EBenchmarkResult:
    async with (
        streamablehttp_client(
            args.mcp_url,
            headers={"Authorization": args.token},
            timeout=60,
        ) as (read, write, _),
        ClientSession(read, write) as session,
    ):
        _ = await session.initialize()
        _logger.info("Asking agent", query=problem.query, index=f"{index + 1}/{total}")
        latency = None
        message_id = None
        answer = ""
        time_start = time.time()
        try:
            response = await session.call_tool(
                "query", arguments={"query_content": problem.query}
            )
        except Exception as e:
            _logger.exception(
                "Error asking agent",
                query=problem.query,
                index=f"{index + 1}/{total}",
                error=str(e),
            )
            _logger.info(
                "Retrying agent query",
                query=problem.query,
                index=f"{index + 1}/{total}",
            )
            raise

        match response.content[0]:
            case types.TextContent() as text_content:
                latency = time.time() - time_start
                answer = text_content.text
                if text_content.meta:
                    message_id = text_content.meta.get("message_id")
            case (
                types.ImageContent()
                | types.EmbeddedResource()
                | types.AudioContent()
                | types.ResourceLink()
            ):
                answer = "Invalid response datatype"
                _logger.exception(
                    "Agent returned incorrect datatype", query=problem.query
                )
        return E2EBenchmarkResult(
            id=problem.id,
            query=problem.query,
            response=answer,
            ground_truth=problem.ground_truth,
            message_id=message_id,
            latency=latency,
        )


async def process_row(
    args: argparse.Namespace, problem: E2EBenchmarkProblem, index: int, total: int
):
    try:

        llm_config = get_llm_config(args)
        # evaluator_llm = LangchainLLMWrapper(ChatVertexAI(**llm_config))
        evaluator_llm = LangchainLLMWrapper(ChatOpenAI(**llm_config))
        _logger.info("LLM initialized", model=llm_config["model"])

        # return await _process_row_with_retry(args, problem, index, total)
        return await _process_row_sse_with_retry(args, problem, evaluator_llm,llm_config, index, total)
    except Exception as e:
        _logger.exception(
            "Retries exhausted for agent query",
            problem_id=problem.id,
            query=problem.query,
            index=f"{index + 1}/{total}",
            error=str(e),
        )
        return E2EBenchmarkResult(
            id=problem.id,
            query=problem.query,
            score=0.0,
            response=f"Error after all retries: {e}",
            ground_truth=problem.ground_truth,
        )


async def run_benchmark(
    problems: list[E2EBenchmarkProblem],
    args: argparse.Namespace,
    num_workers: int = 1,
    indices: list[int] | None = None,
):
    checkpoint_path = Path(args.checkpoint_path)
    completed_ids = load_checkpoint_ids(checkpoint_path)

    if indices is None:
        indices = list(range(len(problems)))

    total = len(indices)
    indices = [i for i in indices if problems[i].id not in completed_ids]
    completed = total - len(indices)

    if len(indices) < total:
        _logger.info(
            "Already completed problems",
            count=f"{completed}/{total}",
        )
        _logger.info(
            "Running benchmark on problems",
            count=f"{len(indices)}/{total}",
        )
    if not indices:
        _logger.info("All problems already completed")
        return

    pbar = tqdm(total=total, initial=completed, desc="Benchmarking")

    result_queue: asyncio.Queue[E2EBenchmarkResult | None] = asyncio.Queue()
    writer_task = [
        asyncio.create_task(checkpoint_writer(result_queue, checkpoint_path))
    ]

    queue: asyncio.Queue[tuple[int | None, int | None]] = asyncio.Queue()
    for task_idx, problem_idx in enumerate(indices):
        queue.put_nowait((completed + task_idx, problem_idx))
    for _ in range(num_workers):
        queue.put_nowait((None, None))

    limiter = AsyncLimiter(5, 10)

    async def worker_loop(worker_id: int):
        while True:
            task_idx, problem_idx = await queue.get()
            if task_idx is None or problem_idx is None:
                break
            async with limiter:
                result = await process_row(args, problems[problem_idx], task_idx, total)
                await result_queue.put(result)
                _ = pbar.update(1)

    workers = [asyncio.create_task(worker_loop(i)) for i in range(num_workers)]
    _ = await asyncio.gather(*workers)
    pbar.close()

    await result_queue.put(None)
    await writer_task[0]

    benchmark_results = load_checkpoint_results(checkpoint_path)
    benchmark_results.sort(key=lambda x: x.id)
    save_results(args, benchmark_results)


if __name__ == "__main__":

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ[
            "OPENAI_API_KEY"] = 'YOUR OPENAI_API_KEY HERE'

    # Initialize the parser
    parser = argparse.ArgumentParser()

    # Add arguments
    # _ = parser.add_argument("--sha", type=str, help="Git SHA")
    _ = parser.add_argument(
        "-m", "--message", type=str, help="Description of the change"
    )
    _ = parser.add_argument("--benchmark_file", type=str, default="bench.json")
    _ = parser.add_argument("--num_workers", type=int, default=8)
    _ = parser.add_argument("--mcp_url", type=str, help="MCP URL")
    _ = parser.add_argument("--token", type=str, help="MCP Token")
    _ = parser.add_argument("--eval_model", type=str, default="gpt-4o")

    args = parser.parse_args()

    benchmark_path = Path(__file__).parent / args.benchmark_file
    args.output_path = str(
        Path(__file__).parent / args.benchmark_file.replace(".json", "_results.json")
    )
    args.checkpoint_path = str(
        Path(__file__).parent
        / args.benchmark_file.replace(".json", "_checkpoint.jsonl")
    )

    with Path.open(benchmark_path, "r") as f:
        problems = [E2EBenchmarkProblem(**problem) for problem in json.load(f)]
    if len(problems) > MAX_PROBLEMS:
        _logger.info("Limiting to %d problems", MAX_PROBLEMS)
        problems = problems[:MAX_PROBLEMS]


    asyncio.run(
        run_benchmark(
            problems,
            args=args,
            num_workers=args.num_workers,
            indices=None,
        )
    )

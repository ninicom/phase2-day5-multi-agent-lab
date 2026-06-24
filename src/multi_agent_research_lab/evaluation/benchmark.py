"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.core.config import get_settings


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency, trace costs, and evaluate quality of a runner."""

    settings = get_settings()

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    # Extract total cost from trace
    total_cost = sum([event.get("payload", {}).get("cost_usd", 0.0) or 0.0 for event in state.trace])
    
    # Errors
    error_count = len(state.errors)
    notes = f"Errors: {error_count}"
    
    # Quality scoring using LLM-as-a-judge
    quality_score = None
    if state.final_answer:
        if settings.app_env == "local" and not settings.openai_api_key:
            from multi_agent_research_lab.services.mock_clients import MockLLMClient
            llm_client = MockLLMClient()
            quality_score = 8.5
        else:
            from multi_agent_research_lab.services.llm_client import LLMClient
            llm_client = LLMClient()
            system_prompt = "You are a Judge evaluating the quality of a research answer. Respond ONLY with a number between 0 and 10."
            user_prompt = f"Query: {query}\n\nAnswer: {state.final_answer}\n\nScore (0-10):"
            response = llm_client.complete(system_prompt, user_prompt)
            total_cost += response.cost_usd
            try:
                import re
                match = re.search(r"(\d+(\.\d+)?)", response.content)
                if match:
                    quality_score = float(match.group(1))
            except Exception:
                pass

    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        quality_score=quality_score,
        notes=notes
    )
    return state, metrics

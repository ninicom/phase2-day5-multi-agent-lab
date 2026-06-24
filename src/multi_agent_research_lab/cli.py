"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    
    _init()
    
    def baseline_runner(q: str) -> ResearchState:
        from multi_agent_research_lab.services.llm_client import LLMClient
        from multi_agent_research_lab.services.mock_clients import MockLLMClient
        from multi_agent_research_lab.core.config import get_settings
        
        state = ResearchState(request=ResearchQuery(query=q))
        settings = get_settings()
        
        if settings.app_env == "local" and not settings.openai_api_key:
            llm_client = MockLLMClient()
        else:
            llm_client = LLMClient()
            
        system_prompt = "You are a helpful research assistant. Answer the user's research query directly."
        response = llm_client.complete(system_prompt=system_prompt, user_prompt=q)
        
        state.final_answer = response.content
        state.add_trace_event("baseline", {"cost_usd": response.cost_usd})
        return state

    try:
        state, metrics = run_benchmark("baseline_single_agent", query, baseline_runner)
        
        console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline Result"))
        console.print(Panel.fit(metrics.model_dump_json(indent=2), title="Metrics", style="blue"))
        
    except Exception as exc:
        console.print(Panel.fit(str(exc), title="Error", style="red"))
        raise typer.Exit(code=1) from exc


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    
    _init()
    
    def multi_agent_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        return workflow.run(state)

    try:
        state, metrics = run_benchmark("multi_agent_workflow", query, multi_agent_runner)
        
        console.print(Panel.fit(state.final_answer or "No final answer.", title="Multi-Agent Result"))
        console.print(Panel.fit(metrics.model_dump_json(indent=2), title="Metrics", style="blue"))
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc


if __name__ == "__main__":
    app()

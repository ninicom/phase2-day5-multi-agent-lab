"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        from multi_agent_research_lab.observability.tracing import trace_span
        settings = get_settings()
        
        with trace_span(self.name) as span:
            if settings.app_env == "local" and not settings.openai_api_key:
                from multi_agent_research_lab.services.mock_clients import MockLLMClient
                llm_client = MockLLMClient()
            else:
                from multi_agent_research_lab.services.llm_client import LLMClient
                llm_client = LLMClient()
                
            system_prompt = "You are an Analyst. Extract key claims, verify facts, and structure insights from the research notes."
            user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}"
            
            response = llm_client.complete(system_prompt, user_prompt)
            state.analysis_notes = response.content
            
            state.agent_results.append(AgentResult(
                agent=AgentName.ANALYST,
                content=response.content,
                metadata={"cost_usd": response.cost_usd}
            ))
            
            span["attributes"]["cost_usd"] = response.cost_usd
            state.add_trace_event(self.name, span)
            
            return state

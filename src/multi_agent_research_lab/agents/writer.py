"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        from multi_agent_research_lab.observability.tracing import trace_span
        settings = get_settings()
        
        with trace_span(self.name) as span:
            if settings.app_env == "local" and not settings.openai_api_key:
                from multi_agent_research_lab.services.mock_clients import MockLLMClient
                llm_client = MockLLMClient()
            else:
                from multi_agent_research_lab.services.llm_client import LLMClient
                llm_client = LLMClient()
                
            system_prompt = f"You are a Writer. Draft a final response tailored for {state.request.audience}. Use the analysis and research provided."
            user_prompt = f"Query: {state.request.query}\n\nAnalysis:\n{state.analysis_notes}\n\nResearch:\n{state.research_notes}"
            
            response = llm_client.complete(system_prompt, user_prompt)
            state.final_answer = response.content
            
            state.agent_results.append(AgentResult(
                agent=AgentName.WRITER,
                content=response.content,
                metadata={"cost_usd": response.cost_usd}
            ))
            
            span["attributes"]["cost_usd"] = response.cost_usd
            state.add_trace_event(self.name, span)
            
            return state

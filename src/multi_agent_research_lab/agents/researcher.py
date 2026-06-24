"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        from multi_agent_research_lab.observability.tracing import trace_span
        settings = get_settings()
        
        with trace_span(self.name) as span:
            # Initialize clients
            if settings.app_env == "local" and not settings.openai_api_key:
                from multi_agent_research_lab.services.mock_clients import MockLLMClient, MockSearchClient
                llm_client = MockLLMClient()
                search_client = MockSearchClient()
            else:
                from multi_agent_research_lab.services.llm_client import LLMClient
                llm_client = LLMClient()
                
                try:
                    from multi_agent_research_lab.services.search_client import SearchClient
                    search_client = SearchClient()
                    _ = search_client.search("test", 1)
                except Exception:
                    from multi_agent_research_lab.services.mock_clients import MockSearchClient
                    search_client = MockSearchClient()
                    
            # 1. Search
            docs = search_client.search(state.request.query, state.request.max_sources)
            state.sources.extend(docs)
            
            # 2. Summarize findings
            system_prompt = "You are a Researcher. Summarize the following sources to answer the query."
            docs_text = "\n\n".join([f"Source: {d.url}\nContent: {d.snippet}" for d in docs])
            user_prompt = f"Query: {state.request.query}\n\nSources:\n{docs_text}"
            
            response = llm_client.complete(system_prompt, user_prompt)
            state.research_notes = response.content
            
            # 3. Add to agent results
            state.agent_results.append(AgentResult(
                agent=AgentName.RESEARCHER,
                content=response.content,
                metadata={"sources_found": len(docs), "cost_usd": response.cost_usd}
            ))
            
            # 4. Trace
            span["attributes"]["cost_usd"] = response.cost_usd
            state.add_trace_event(self.name, span)
            
            return state

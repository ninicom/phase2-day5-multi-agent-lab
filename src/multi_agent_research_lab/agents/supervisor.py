"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        import json
        from multi_agent_research_lab.core.config import get_settings
        from multi_agent_research_lab.observability.tracing import trace_span
        
        settings = get_settings()
        
        with trace_span(self.name) as span:
            # Enforce max iterations
            if state.iteration >= settings.max_iterations:
                state.record_route("done")
                span["attributes"] = {"decision": "done", "reason": "max_iterations_reached"}
                state.add_trace_event("supervisor", span)
                return state

            # Initialize LLM Client
            if settings.app_env == "local" and not settings.openai_api_key:
                from multi_agent_research_lab.services.mock_clients import MockLLMClient
                llm_client = MockLLMClient()
            else:
                from multi_agent_research_lab.services.llm_client import LLMClient
                llm_client = LLMClient()
                
            system_prompt = """You are a Supervisor agent for a multi-agent research team.
Your job is to decide which agent should act next.
The available agents are:
- 'researcher': gathers search results. Use this if research_notes is empty or incomplete.
- 'analyst': analyzes the research. Use this if research_notes exists but analysis_notes is empty.
- 'writer': writes the final answer. Use this if analysis is complete but final_answer is empty.
- 'done': Use this if the final_answer has been written and the task is complete.

Respond with ONLY a JSON object in this exact format: {"next_agent": "..."}"""

            user_prompt = f"""Current State:
- Iteration: {state.iteration} / {settings.max_iterations}
- Query: {state.request.query}
- Has research_notes: {bool(state.research_notes)}
- Has analysis_notes: {bool(state.analysis_notes)}
- Has final_answer: {bool(state.final_answer)}

Decide the next agent."""

            response = llm_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
            
            # Parse decision
            try:
                content = response.content.lower()
                if '{"next_agent"' in content:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    decision_json = json.loads(content[start:end])
                    next_node = decision_json.get("next_agent", "done")
                else:
                    if "researcher" in content: next_node = "researcher"
                    elif "analyst" in content: next_node = "analyst"
                    elif "writer" in content: next_node = "writer"
                    else: next_node = "done"
            except Exception:
                if not state.research_notes: next_node = "researcher"
                elif not state.analysis_notes: next_node = "analyst"
                elif not state.final_answer: next_node = "writer"
                else: next_node = "done"

            state.record_route(next_node)
            span["attributes"].update({
                "decision": next_node, 
                "llm_content": response.content,
                "cost_usd": response.cost_usd
            })
            state.add_trace_event("supervisor", span)
            
            return state

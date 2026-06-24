"""LangGraph workflow skeleton."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def build(self) -> object:
        """Create a LangGraph graph."""
        from langgraph.graph import StateGraph, END, START
        from multi_agent_research_lab.agents.supervisor import SupervisorAgent
        from multi_agent_research_lab.agents.researcher import ResearcherAgent
        from multi_agent_research_lab.agents.analyst import AnalystAgent
        from multi_agent_research_lab.agents.writer import WriterAgent
        
        builder = StateGraph(ResearchState)
        supervisor = SupervisorAgent()
        researcher = ResearcherAgent()
        analyst = AnalystAgent()
        writer = WriterAgent()
        
        # Add nodes
        builder.add_node("supervisor", supervisor.run)
        builder.add_node("researcher", researcher.run)
        builder.add_node("analyst", analyst.run)
        builder.add_node("writer", writer.run)
        
        # Edges
        builder.add_edge(START, "supervisor")
        
        # Conditional routing from supervisor
        def route_from_supervisor(state: ResearchState) -> str:
            if not state.route_history:
                return END
            last_route = state.route_history[-1]
            if last_route == "done":
                return END
            return last_route
            
        builder.add_conditional_edges(
            "supervisor", 
            route_from_supervisor,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                END: END
            }
        )
        
        # Agents loop back to supervisor
        builder.add_edge("researcher", "supervisor")
        builder.add_edge("analyst", "supervisor")
        builder.add_edge("writer", "supervisor")
        
        return builder.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        app = self.build()
        result = app.invoke(state)
        
        if isinstance(result, dict):
            return ResearchState.model_validate(result)
        return result

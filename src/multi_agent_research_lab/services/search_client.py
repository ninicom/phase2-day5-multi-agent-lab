"""Search client abstraction for ResearcherAgent."""

import httpx
from multi_agent_research_lab.core.schemas import SourceDocument
from multi_agent_research_lab.core.config import get_settings


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query using Tavily API, or fallback to Mock if no API key is provided."""
        settings = get_settings()
        
        if not settings.tavily_api_key:
            from multi_agent_research_lab.services.mock_clients import MockSearchClient
            return MockSearchClient().search(query, max_results)
            
        # Tavily implementation
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": settings.tavily_api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
            docs = []
            for item in data.get("results", []):
                docs.append(
                    SourceDocument(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        metadata={"score": item.get("score", 0.0), "source": "tavily"}
                    )
                )
            return docs
        except Exception as e:
            import logging
            logger = logging.getLogger("search")
            logger.error(f"Tavily search failed: {e}. Falling back to mock search.")
            # Fallback to mock on error
            from multi_agent_research_lab.services.mock_clients import MockSearchClient
            return MockSearchClient().search(query, max_results)

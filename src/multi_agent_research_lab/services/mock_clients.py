"""Mock implementations for API clients."""

from multi_agent_research_lab.core.schemas import SourceDocument
from multi_agent_research_lab.services.llm_client import LLMClient, LLMResponse
from multi_agent_research_lab.services.search_client import SearchClient


class MockLLMClient(LLMClient):
    """A local mock implementation of LLMClient using exact OpenAI API structure."""

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        prompt_lower = (system_prompt + user_prompt).lower()
        
        # 1. Generate exact OpenAI API response format
        if "supervisor" in prompt_lower:
            text = "Supervisor: I will delegate this query to the Researcher."
        elif "research" in prompt_lower:
            text = "Researcher: I have gathered the necessary information from search."
        elif "analyst" in prompt_lower:
            text = "Analyst: Here is the analysis of the research data."
        elif "writer" in prompt_lower:
            text = "Writer: Here is the final draft of the research report."
        elif "critic" in prompt_lower:
            text = "Critic: The report is good, but needs more citations."
        else:
            text = "Mock LLM response for query."

        raw_openai_response = {
            "id": "chatcmpl-12345mock",
            "object": "chat.completion",
            "created": 1700000000,
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

        # 2. Parse the raw API response into our internal LLMResponse
        return LLMResponse(
            content=raw_openai_response["choices"][0]["message"]["content"],
            input_tokens=raw_openai_response["usage"]["prompt_tokens"],
            output_tokens=raw_openai_response["usage"]["completion_tokens"],
            cost_usd=0.001
        )


class MockSearchClient(SearchClient):
    """A local mock implementation of SearchClient using exact Tavily API structure."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        # 1. Generate exact Tavily API response format
        raw_tavily_response = {
            "query": query,
            "results": [
                {
                    "title": f"Mock Article 1 about {query}",
                    "url": "https://mock.example.com/1",
                    "content": f"This is a mock snippet describing {query} in detail.",
                    "score": 0.95,
                    "raw_content": None
                },
                {
                    "title": f"Mock Article 2 about {query}",
                    "url": "https://mock.example.com/2",
                    "content": f"Another informative mock result for the query: {query}.",
                    "score": 0.88,
                    "raw_content": None
                }
            ],
            "response_time": 0.15
        }
        
        # 2. Parse the raw API response into our internal SourceDocument format
        docs = []
        for result in raw_tavily_response["results"][:max_results]:
            docs.append(SourceDocument(
                title=result["title"],
                url=result["url"],
                snippet=result["content"],
                metadata={"source": "mock_tavily", "score": result["score"]}
            ))
            
        return docs

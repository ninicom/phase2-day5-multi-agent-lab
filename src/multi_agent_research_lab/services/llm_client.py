"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from multi_agent_research_lab.core.errors import StudentTodoError


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""
    
    def __init__(self) -> None:
        from multi_agent_research_lab.core.config import get_settings
        import openai
        
        settings = get_settings()
        self.model = settings.openai_model
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        choice = response.choices[0]
        usage = response.usage
        
        cost_usd = 0.0
        if usage:
            if "gpt-4o-mini" in self.model:
                cost_usd = (usage.prompt_tokens / 1000000) * 0.150 + (usage.completion_tokens / 1000000) * 0.600
            elif "gpt-4o" in self.model:
                cost_usd = (usage.prompt_tokens / 1000000) * 5.0 + (usage.completion_tokens / 1000000) * 15.0
            
        return LLMResponse(
            content=choice.message.content or "",
            input_tokens=usage.prompt_tokens if usage else None,
            output_tokens=usage.completion_tokens if usage else None,
            cost_usd=cost_usd
        )

"""AI client abstraction for LLM integrations.

All AI calls across TakiOS (Eselsbrücken generation, free-text grading,
question generation, etc.) go through this abstraction. This keeps layers
decoupled from any specific AI provider.
"""

from typing import Protocol, runtime_checkable

from app.config import settings


@runtime_checkable
class AIClient(Protocol):
    """Protocol for AI client implementations."""

    async def generate_text(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        model: str | None = None,
    ) -> str:
        """Generate text from a prompt."""
        ...

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate a vector embedding for text."""
        ...


class AnthropicClient:
    """Anthropic Claude API client."""

    def __init__(self) -> None:
        self.api_key = settings.anthropic_api_key

    async def generate_text(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        model: str | None = None,
    ) -> str:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model or settings.sonnet_model,
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]

    async def generate_embedding(self, text: str) -> list[float]:
        # Anthropic doesn't have embeddings yet; use a fallback
        raise NotImplementedError("Use OpenAI or local model for embeddings")


class OpenAIClient:
    """OpenAI API client."""

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key

    async def generate_text(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        model: str | None = None,
    ) -> str:
        import httpx

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or "gpt-4o",
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate_embedding(self, text: str) -> list[float]:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": "text-embedding-3-small", "input": text},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]


def get_ai_client() -> AIClient:
    """Factory that returns the configured AI client."""
    if settings.ai_provider == "anthropic":
        return AnthropicClient()
    elif settings.ai_provider == "openai":
        return OpenAIClient()
    else:
        raise ValueError(f"Unknown AI provider: {settings.ai_provider}")

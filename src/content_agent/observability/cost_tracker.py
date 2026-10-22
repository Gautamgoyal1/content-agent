"""Token usage and estimated cost tracking."""

from dataclasses import dataclass, field


@dataclass
class CostTracker:
    """Tracks token consumption and estimated API costs across agent executions."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def record_usage(self, prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o-mini") -> None:
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens

        # Standard pricing: $0.15/1M input, $0.60/1M output for gpt-4o-mini
        cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.00000060)
        self.estimated_cost_usd += cost

    def summary(self) -> dict[str, float | int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.prompt_tokens + self.completion_tokens,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
        }

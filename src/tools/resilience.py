"""Retry helpers and simple cost accounting for tool / LLM calls."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, TypeVar

from src.logging_utils import get_logger

log = get_logger("chokepoint.resilience")
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class CostTracker:
    """Rough token/cost counters (estimates only)."""

    llm_calls: int = 0
    tool_calls: int = 0
    prompt_tokens_est: int = 0
    completion_tokens_est: int = 0
    retries: int = 0
    errors: list[str] = field(default_factory=list)

    def add_llm(self, prompt_chars: int = 0, completion_chars: int = 0) -> None:
        self.llm_calls += 1
        # ~4 chars/token rough heuristic
        self.prompt_tokens_est += max(1, prompt_chars // 4)
        self.completion_tokens_est += max(0, completion_chars // 4)

    def add_tool(self, name: str = "") -> None:
        self.tool_calls += 1

    def summary(self) -> dict[str, Any]:
        total_tok = self.prompt_tokens_est + self.completion_tokens_est
        # Placeholder blended price; user should override mentally
        est_usd = total_tok / 1_000_000 * 2.0
        return {
            "llm_calls": self.llm_calls,
            "tool_calls": self.tool_calls,
            "prompt_tokens_est": self.prompt_tokens_est,
            "completion_tokens_est": self.completion_tokens_est,
            "total_tokens_est": total_tok,
            "est_usd_blended_2_per_mtok": round(est_usd, 4),
            "retries": self.retries,
            "errors": self.errors[-10:],
            "note": "Estimates only — not vendor billing.",
        }


_GLOBAL_COST = CostTracker()


def get_cost_tracker() -> CostTracker:
    return _GLOBAL_COST


def reset_cost_tracker() -> CostTracker:
    global _GLOBAL_COST
    _GLOBAL_COST = CostTracker()
    return _GLOBAL_COST


def with_retry(
    *,
    attempts: int = 3,
    base_delay: float = 0.8,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[F], F]:
    def deco(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last: BaseException | None = None
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:  # noqa: PERF203
                    last = exc
                    _GLOBAL_COST.retries += 1
                    _GLOBAL_COST.errors.append(f"{fn.__name__}: {exc}")
                    if i + 1 >= attempts:
                        break
                    delay = base_delay * (2**i)
                    log.warning("retry %s/%s %s after %ss: %s", i + 1, attempts, fn.__name__, delay, exc)
                    time.sleep(delay)
            assert last is not None
            raise last

        return wrapper  # type: ignore[return-value]

    return deco

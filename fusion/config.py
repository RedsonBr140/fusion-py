from __future__ import annotations

from dataclasses import dataclass

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/148.0.0.0 Safari/537.36"
)


@dataclass(slots=True)
class FusionConfig:
    base_url: str = "https://fusiondms.com.br"
    timeout: float = 30.0
    max_retries: int = 2
    user_agent: str = DEFAULT_USER_AGENT

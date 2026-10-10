from typing import Protocol, TypeVar, Any
from pydantic import BaseModel
import instructor
import litellm
from tenacity import retry, stop_after_attempt, wait_exponential

T = TypeVar("T", bound=BaseModel)

class LLMPort(Protocol):
    def complete(self, *, system: str, user: str, response_model: type[T], temperature: float = 0.0) -> T: ...

class LiteLLMAdapter:
    def __init__(self, model: str = "gemini/gemini-1.5-pro-latest"):
        self.model = model
        self._client = instructor.from_litellm(litellm.completion)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, *, system: str, user: str, response_model: type[T], temperature: float = 0.0) -> T:
        return self._client.chat.completions.create(
            model=self.model,
            response_model=response_model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]
        )

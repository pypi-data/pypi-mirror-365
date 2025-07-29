from collections.abc import Callable
from typing import TypedDict


class Message(TypedDict):
    role: str
    content: str

class Request(TypedDict):
    name: str
    reward: float
    messages: list[Message]
    needs_action: bool

class TokenRequest(TypedDict):
    name: str
    reward: float
    prompt: list[int]
    messages: list[Message]
    needs_action: bool

class LLMEnv:
    agents: list[str]

    def __init__(self,
                 tokenize: Callable[[list[Message], ...], list[int]],
                 tokenize_kwargs: dict = None,
                 *args, **kwargs) -> None:
        self.tokenize = tokenize
        self.tokenize_kwargs = tokenize_kwargs or {}

    def _initialize(self) -> list[Request]:
        # User-defined initialization; override this method
        raise NotImplementedError

    def _parse_action(self, agent: str, completion: str) -> str:
        """
        Parses the completion from an agent to extract the action.
        The base implementation returns the completion stripped of whitespace.
        Subclasses can override this to implement environment-specific parsing.
        """
        return completion.strip()

    def _act(self, actions: dict[str, str]) -> list[Request]:
        # User-defined action; override this method
        raise NotImplementedError

    def initialize(self) -> list[TokenRequest]:
        requests: list[Request] = self._initialize()
        return [
            TokenRequest(
                name=request["name"],
                reward=0.0,
                prompt=self.tokenize(request["messages"], **self.tokenize_kwargs),
                messages=request["messages"],
                needs_action=request["needs_action"]
            )
            for request in requests
        ]

    def act(self, actions: dict[str, str]) -> list[TokenRequest]:
        requests = self._act(actions)
        return [
            TokenRequest(
                name=request["name"],
                reward=request["reward"],
                prompt=self.tokenize(request["messages"], **self.tokenize_kwargs),
                messages=request["messages"],
                needs_action=request["needs_action"]
            )
            for request in requests
        ]

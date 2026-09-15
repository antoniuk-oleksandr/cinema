from collections.abc import Iterable

from agentflow.models import AgentResult

from .base import Agent, AgentContext


class MockAgent(Agent):
    def __init__(self, name: str, results: Iterable[AgentResult]) -> None:
        self.name = name
        self.results = iter(results)
        self.calls = 0

    async def run(self, context: AgentContext):
        self.calls += 1
        return next(self.results)

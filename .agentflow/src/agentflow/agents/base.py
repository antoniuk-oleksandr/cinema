from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from agentflow.models import AgentResult, Task


@dataclass
class AgentContext:
    task: Task
    state: str
    iteration: int
    findings: list[AgentResult] = field(default_factory=list)
    production_changed: bool = False


class Agent(ABC):
    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult: ...

import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path

from agentflow.adapters.notifications import NotificationService
from agentflow.agents.base import Agent, AgentContext
from agentflow.config import Config
from agentflow.models import AgentStatus, Route, Task
from agentflow.state import PipelineState


class Orchestrator:
    def __init__(
        self,
        task: Task,
        agents: dict[str, Agent],
        root: Path,
        config: Config | None = None,
        notifier=None,
    ) -> None:
        self.task = task
        self.agents = agents
        self.root = root
        self.config = config or Config()
        self.notifier = notifier or NotificationService()
        self.run_id = str(uuid.uuid4())
        self.iteration = 0
        self.state = PipelineState.DEVELOPMENT
        self.history = []
        self.log = logging.getLogger("agentflow")
        self.result_signatures: list[str] = []

    def _event(self, old, new, agent, result, reason="") -> None:
        e = {
            "timestamp": datetime.now(UTC).isoformat(),
            "run_id": self.run_id,
            "iteration": self.iteration,
            "from": old.value,
            "to": new.value,
            "agent": agent,
            "route": result.route.value,
            "reason": reason,
        }
        self.history.append(e)
        self.root.joinpath("runtime").mkdir(parents=True, exist_ok=True)
        self.root.joinpath("runtime/events.jsonl").open("a").write(json.dumps(e) + "\n")

    async def run(self):
        findings = []
        self.root.joinpath("runtime").mkdir(parents=True, exist_ok=True)
        while self.state not in (PipelineState.DONE, PipelineState.HUMAN_REQUIRED):
            self.iteration += 1
            if self.iteration > self.config.pipeline.max_iterations:
                self.state = PipelineState.HUMAN_REQUIRED
                break
            agent_name = {
                PipelineState.DEVELOPMENT: "developer",
                PipelineState.TESTING: "tester",
                PipelineState.REVIEW: "reviewer",
            }[self.state]
            old = self.state
            try:
                result = await self.agents[agent_name].run(
                    AgentContext(self.task, self.state.value, self.iteration, findings)
                )
            except Exception:
                self.log.exception("agent failure")
                self.state = PipelineState.HUMAN_REQUIRED
                break
            findings.append(result)
            signature = result.model_dump_json(exclude_none=True, by_alias=True)
            self.result_signatures.append(signature)
            if len(self.result_signatures) >= 3 and self.result_signatures[-3:] == [signature] * 3:
                self.log.error("same agent result repeated three times; stopping safely")
                self.state = PipelineState.HUMAN_REQUIRED
                break
            route = result.route
            if self.state == PipelineState.DEVELOPMENT and route == Route.TESTER:
                new = PipelineState.TESTING
            elif self.state == PipelineState.TESTING and route == Route.DEVELOPER:
                new = PipelineState.DEVELOPMENT
            elif (
                self.state == PipelineState.TESTING
                and route == Route.TESTER
                and result.status == AgentStatus.CHANGES_REQUIRED
            ):
                new = PipelineState.TESTING
            elif self.state == PipelineState.TESTING and route == Route.REVIEWER:
                new = PipelineState.REVIEW
            elif self.state == PipelineState.REVIEW and route == Route.DEVELOPER:
                new = PipelineState.DEVELOPMENT
            elif self.state == PipelineState.REVIEW and route == Route.TESTER:
                new = PipelineState.TESTING
            elif self.state == PipelineState.REVIEW and route == Route.BOTH:
                new = PipelineState.DEVELOPMENT
            elif self.state == PipelineState.REVIEW and route == Route.DONE:
                new = PipelineState.DONE
            else:
                self.state = PipelineState.HUMAN_REQUIRED
                break
            self._event(old, new, agent_name, result, result.summary or "")
            self.state = new
        if self.state == PipelineState.DONE:
            await self.notifier.success(self.task.title)
        else:
            await self.notifier.attention(f"{self.task.title}: {self.state.value}")
        self.root.joinpath("runtime/current_run.json").write_text(
            json.dumps(
                {
                    "run_id": self.run_id,
                    "state": self.state.value,
                    "iteration": self.iteration,
                    "task": self.task.model_dump(),
                    "history": self.history,
                },
                indent=2,
            )
        )
        return self.state

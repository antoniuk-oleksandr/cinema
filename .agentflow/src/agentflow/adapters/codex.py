import asyncio
from pathlib import Path

from agentflow.agents.base import Agent, AgentContext
from agentflow.models import AgentResult


class AdapterError(Exception):
    pass


class AgentTimeoutError(AdapterError):
    pass


class InvalidAgentResultError(AdapterError):
    pass


class CodexAdapter(Agent):
    def __init__(
        self, role: str, cwd: Path, timeout: float = 3600, session_id: str | None = None
    ) -> None:
        self.role = role
        self.cwd = cwd
        self.timeout = timeout
        self.session_id = session_id

    async def run(self, context: AgentContext):
        prompt = f"Read .agentflow/roles/{self.role}.md. Task JSON: {context.task.model_dump_json()}. Return ONLY AgentResult JSON. State: {context.state}. Findings: {[x.model_dump() for x in context.findings]}"
        try:
            command = (
                ["codex", "exec"]
                + (["resume", self.session_id] if self.session_id else [])
                + ["--cd", str(self.cwd), "--sandbox", "workspace-write"]
                + ([] if self.session_id else ["--ephemeral"])
                + [prompt]
            )
            p = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await asyncio.wait_for(p.communicate(), self.timeout)
        except TimeoutError as e:
            raise AgentTimeoutError(self.role) from e
        if p.returncode != 0:
            raise AdapterError(out.decode(errors="replace"))
        try:
            return AgentResult.model_validate_json(out.decode())
        except Exception as e:
            raise InvalidAgentResultError(str(e)) from e

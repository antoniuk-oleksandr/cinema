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

    async def run(self, context: AgentContext) -> AgentResult:
        role_contract = {
            "developer": "Own production code only; do not modify tests. Finish with completed/tester.",
            "tester": "Own tests and coverage only; do not modify production code. Pass with completed/reviewer.",
            "reviewer": "Inspect actual files; modify nothing; never trust summaries; approve only after every rule is verified.",
        }[self.role]
        prompt = (
            f"You are the {self.role} agent. {role_contract}\n"
            f"Task JSON: {context.task.model_dump_json()}. Return ONLY AgentResult JSON. "
            f"State: {context.state}. Recent findings: {[x.model_dump() for x in context.findings[-3:]]}"
        )
        try:
            command = [
                "codex",
                "exec",
                "--cd",
                str(self.cwd),
                "--sandbox",
                "workspace-write",
            ]
            if self.session_id:
                command.extend(["resume", self.session_id])
            else:
                command.append("--ephemeral")
            command.append(prompt)
            p = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, err = await asyncio.wait_for(p.communicate(), self.timeout)
        except TimeoutError as e:
            raise AgentTimeoutError(self.role) from e
        if p.returncode != 0:
            stdout = out.decode(errors="replace").strip()
            stderr = err.decode(errors="replace").strip()
            details = stderr or stdout or f"codex exited with status {p.returncode}"
            raise AdapterError(
                f"Codex agent '{self.role}' failed with exit status {p.returncode}: {details}"
            )
        try:
            return AgentResult.model_validate_json(out.decode())
        except Exception as e:
            raise InvalidAgentResultError(str(e)) from e

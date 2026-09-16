import asyncio
import json
import subprocess

from agentflow.agents.base import Agent, AgentContext
from agentflow.models import AgentResult

from .codex import AdapterError, AgentTimeoutError, InvalidAgentResultError


class HerdrAdapter(Agent):
    """Run a persistent Codex agent through a Herdr pane."""

    def __init__(self, pane_id: str, timeout: float = 3600) -> None:
        self.pane_id = pane_id.removeprefix("herdr:pane:")
        self.timeout = timeout

    @staticmethod
    def _result_from_output(output: str) -> AgentResult:
        decoder = json.JSONDecoder()
        latest: AgentResult | None = None
        for index in (i for i, char in enumerate(output) if char == "{"):
            try:
                # Herdr's terminal reader can insert visual line breaks inside
                # long JSON strings. Whitespace is safe to normalize here;
                # Pydantic still performs the authoritative contract check.
                candidate = output[index:].replace("\r", " ").replace("\n", " ")
                value, _ = decoder.raw_decode(candidate)
                latest = AgentResult.model_validate(value)
            except (json.JSONDecodeError, ValueError):
                continue
        if latest is not None:
            return latest
        raise InvalidAgentResultError(
            "Herdr output did not contain a valid AgentResult JSON object"
        )

    def _run(self, prompt: str) -> AgentResult:
        self._submit(prompt)
        try:
            return self._read_result()
        except InvalidAgentResultError:
            repair = (
                "Your previous response did not match the required AgentResult contract. "
                "Reply with ONLY one valid JSON object containing exactly these fields: "
                "status, route, summary, issues, metadata. "
                "Do not include state, changes, verification, markdown, or explanations. "
                "For completed Developer work, use status completed and route tester."
            )
            self._submit(repair)
            return self._read_result()

    def _submit(self, prompt: str) -> None:
        command = [
            "herdr",
            "agent",
            "prompt",
            self.pane_id,
            prompt,
            "--wait",
            "--until",
            "idle",
            "--until",
            "done",
            "--until",
            "blocked",
            "--timeout",
            str(int(self.timeout * 1000)),
        ]
        try:
            subprocess.run(  # noqa: S603 - executable and arguments are controlled
                command, capture_output=True, text=True, check=True
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentTimeoutError(self.pane_id) from exc
        except (OSError, subprocess.CalledProcessError) as exc:
            details = getattr(exc, "stderr", "") or str(exc)
            raise AdapterError(f"Herdr agent failed: {details.strip()}") from exc

    def _read_result(self) -> AgentResult:
        try:
            read = subprocess.run(  # noqa: S603 - executable and arguments are controlled
                [  # noqa: S607 - executable is a controlled Herdr command
                    "herdr",
                    "agent",
                    "read",
                    self.pane_id,
                    "--source",
                    "recent-unwrapped",
                    "--lines",
                    "1000",
                    "--format",
                    "text",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentTimeoutError(self.pane_id) from exc
        except (OSError, subprocess.CalledProcessError) as exc:
            details = getattr(exc, "stderr", "") or str(exc)
            raise AdapterError(f"Herdr agent failed: {details.strip()}") from exc
        return self._result_from_output(read.stdout)

    async def run(self, context: AgentContext) -> AgentResult:
        role = {"development": "developer", "testing": "tester", "review": "reviewer"}[
            context.state
        ]
        handoff = {
            "development": "completed work must use status completed and route tester",
            "testing": (
                "a passing test run must use status completed and route reviewer; "
                "only test work still needed may use status changes_required and route tester"
            ),
            "review": "approval must use status approved and route done",
        }[context.state]
        prompt = (
            f"Read .agentflow/roles/{role}.md. "
            f"Task JSON: {context.task.model_dump_json()}. "
            f"Return ONLY AgentResult JSON. State: {context.state}. "
            f"Handoff rule: {handoff}. "
            f"Findings: {[item.model_dump() for item in context.findings]}"
        )
        return await asyncio.wait_for(asyncio.to_thread(self._run, prompt), self.timeout)
